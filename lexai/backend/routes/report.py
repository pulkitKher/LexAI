import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from services.extractor import extract_text
from services.analyzer import analyze_document
from services.report import generate_report

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "../uploads")
REPORTS_DIR = "./reports"


@router.post("/generate-report")
async def generate_risk_report(file: UploadFile = File(...)):
    """
    Upload document → analyze → generate downloadable PDF risk report
    """

    ext = os.path.splitext(file.filename)[1].lower()
    allowed = {".pdf", ".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp"}
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    session_id = str(uuid.uuid4()).replace("-", "")[:20]
    unique_filename = f"{session_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    report_path = os.path.join(REPORTS_DIR, f"LexAI_Report_{session_id}.pdf")

    try:
        # Save uploaded file
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        os.makedirs(REPORTS_DIR, exist_ok=True)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text
        extracted_text = extract_text(file_path, file.filename)
        if not extracted_text or len(extracted_text.strip()) < 50:
            raise HTTPException(
                status_code=422,
                detail="Could not extract readable text from document."
            )

        # Analyze with Gemini
        analysis = analyze_document(extracted_text)

        # Generate PDF report
        generate_report(analysis, report_path)

        # Return PDF as download
        return FileResponse(
            path=report_path,
            media_type="application/pdf",
            filename=f"LexAI_Risk_Report.pdf",
            background=None
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)