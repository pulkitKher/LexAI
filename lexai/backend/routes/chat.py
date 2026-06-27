import uuid
import shutil
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from services.extractor import extract_text
from services.analyzer import analyze_document
from services.rag import store_document, answer_question, delete_session

load_dotenv()

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "../uploads")


# Request/Response models
class QuestionRequest(BaseModel):
    session_id: str
    question: str


class QuestionResponse(BaseModel):
    session_id: str
    question: str
    answer: str


class UploadResponse(BaseModel):
    session_id: str
    document_type: str
    summary: str
    total_clauses_found: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    chunks_stored: int
    message: str


@router.post("/upload-and-analyze", response_model=UploadResponse)
async def upload_and_analyze(file: UploadFile = File(...)):
    """
    Upload document → analyze clauses + store in ChromaDB for chat
    Returns session_id which is used for follow-up questions
    """

    ext = os.path.splitext(file.filename)[1].lower()
    allowed = {".pdf", ".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp"}
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    session_id = str(uuid.uuid4()).replace("-", "")[:20]
    unique_filename = f"{session_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text
        extracted_text = extract_text(file_path, file.filename)

        if not extracted_text or len(extracted_text.strip()) < 50:
            raise HTTPException(
                status_code=422,
                detail="Could not extract readable text from document."
            )

        # Run clause analysis (Phase 1)
        analysis = analyze_document(extracted_text)

        # Store in ChromaDB for RAG chat (Phase 2)
        chunks_stored = store_document(session_id, extracted_text)

        return UploadResponse(
            session_id=session_id,
            document_type=analysis.document_type,
            summary=analysis.summary,
            total_clauses_found=analysis.total_clauses_found,
            high_risk_count=analysis.high_risk_count,
            medium_risk_count=analysis.medium_risk_count,
            low_risk_count=analysis.low_risk_count,
            chunks_stored=chunks_stored,
            message=f"Document analyzed and stored. You can now ask questions using session_id: {session_id}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@router.post("/chat", response_model=QuestionResponse)
async def chat(request: QuestionRequest):
    """
    Ask a question about the uploaded document using session_id
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if not request.session_id.strip():
        raise HTTPException(status_code=400, detail="session_id is required.")

    try:
        answer = answer_question(request.session_id, request.question)
        return QuestionResponse(
            session_id=request.session_id,
            question=request.question,
            answer=answer
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def end_session(session_id: str):
    """Clean up session data from ChromaDB"""
    deleted = delete_session(session_id)
    if deleted:
        return {"message": f"Session {session_id} deleted successfully."}
    return {"message": f"Session {session_id} not found or already deleted."}