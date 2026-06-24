# LexAI 🏛️⚖️
### AI-Powered Legal & Financial Document Analyzer for Indians

LexAI helps common Indians understand legal and financial documents 
by extracting key clauses, flagging risks, and explaining everything 
in plain English — powered by Google Gemini 2.5 Flash.

## Features
- Upload PDF or scanned image documents
- Auto-detects document type (rental agreement, offer letter, loan paper, etc.)
- Identifies and explains all important clauses
- Risk scoring: High / Medium / Low per clause
- Actionable recommendations per clause
- India-specific legal context (IPC, Consumer Protection Act, etc.)

## Tech Stack
- **Backend:** FastAPI + Python
- **AI:** Google Gemini 2.5 Flash
- **PDF Parsing:** PyMuPDF + pdfplumber
- **OCR:** EasyOCR (for scanned documents)
- **Validation:** Pydantic

## Run Locally
```bash
cd lexai/backend
source venv/Scripts/activate
uvicorn main:app --reload --port 8000
```
Visit http://127.0.0.1:8000/docs

## Project Phases
- ✅ Phase 1 — Document analysis + clause extraction
- 🔄 Phase 2 — RAG Chat (ChromaDB + Q&A)
- 🔄 Phase 3 — Risk Report PDF + React Frontend
- 🔄 Phase 4 — Docker + Deployment