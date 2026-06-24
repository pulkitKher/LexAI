import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from services.extractor import extract_text
from services.analyzer import analyze_document
from models.schemas import AnalysisResponse, ErrorResponse

load_dotenv()

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "../uploads")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 10))
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp"}


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(file: UploadFile = File(...)):

    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: PDF or image files."
        )

    # Save uploaded file temporarily
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File too large ({file_size_mb:.1f}MB). Max allowed: {MAX_FILE_SIZE_MB}MB."
            )

        # Extract text
        extracted_text = extract_text(file_path, file.filename)

        if not extracted_text or len(extracted_text.strip()) < 50:
            raise HTTPException(
                status_code=422,
                detail="Could not extract readable text from document. Try a clearer scan."
            )

        # Analyze with Gemini
        result = analyze_document(extracted_text)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Always cleanup uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)


@router.get("/health")
async def health():
    return {"status": "ok", "service": "LexAI Backend"}