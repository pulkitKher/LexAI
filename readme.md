# ⚖️ LexAI — AI-Powered Legal Document Analyzer

> **Helping common Indians understand legal documents before they sign them.**

LexAI is a full-stack Generative AI application that analyzes legal and financial documents — rental agreements, offer letters, loan papers, NDAs — and explains every clause in plain English, flags risks, and generates downloadable PDF reports.

---

## 🎯 Problem Statement

Most Indians sign legal documents without understanding what they're agreeing to. Legal consultation costs ₹2,000–5,000 per hour, and legal language is incomprehensible to the average person. LexAI solves this by making legal document analysis free, instant, and accessible to everyone.

---

## ✨ Features

- 📄 **Smart Document Extraction** — Three-layer pipeline: pdfplumber → PyMuPDF → EasyOCR (handles digital PDFs, scanned documents, and phone photographs)
- 🤖 **AI Clause Analysis** — Google Gemini 2.5 Flash identifies all important clauses, classifies risk (High/Medium/Low), and explains each in simple English
- 💬 **RAG-powered Chat** — Ask unlimited questions about your document using ChromaDB vector search + Gemini
- 📥 **PDF Risk Report** — Download a professionally formatted risk report with all clauses, explanations, and recommendations
- 🌐 **Clean Frontend** — Mobile-friendly HTML/CSS/JS interface with drag-and-drop upload
- 🐳 **Dockerized** — Single `docker run` command to deploy anywhere

---

## 🏗️ Architecture

```
User (Browser)
      │
      ▼
HTML/CSS/JS Frontend (port 3000)
      │
      ▼
FastAPI Backend (port 8000)
   ├── /api/v1/analyze          → Clause extraction + Gemini analysis
   ├── /api/v2/upload-and-analyze → Analysis + ChromaDB storage
   ├── /api/v2/chat             → RAG Q&A on document
   ├── /api/v2/session          → Session management
   └── /api/v3/generate-report  → PDF risk report generation
      │
   ┌──┴──────────────────┐
   │                     │
ChromaDB              Gemini 2.5 Flash
(vector store)        (Google AI Studio)
```

---

## 🔧 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **LLM** | Google Gemini 2.5 Flash | Clause analysis + RAG Q&A |
| **Backend** | FastAPI + Python | REST API |
| **PDF Parsing** | PyMuPDF + pdfplumber | Digital PDF text extraction |
| **OCR** | EasyOCR | Scanned document text extraction |
| **Vector Store** | ChromaDB | Document embeddings for RAG |
| **Text Splitting** | LangChain Text Splitters | Document chunking |
| **Report Generation** | ReportLab | PDF risk report |
| **Frontend** | HTML + CSS + JavaScript | Mobile-friendly UI |
| **Containerization** | Docker | Deployment |

---

## 🚀 Running Locally

### Prerequisites
- Python 3.10+
- Docker Desktop
- Google AI Studio API Key (free at [aistudio.google.com](https://aistudio.google.com))

### Option 1: Run with Docker (Recommended)

```bash
# Clone the repo
git clone https://github.com/pulkitKher/LexAI.git
cd LexAI

# Add your Gemini API key
echo "GEMINI_API_KEY=your_key_here" > lexai/backend/.env
echo "UPLOAD_DIR=../uploads" >> lexai/backend/.env
echo "MAX_FILE_SIZE_MB=10" >> lexai/backend/.env

# Build and run
cd lexai/backend
docker build -t lexai-backend .
docker run -p 8000:8000 --env-file .env lexai-backend
```

Backend runs at **http://localhost:8000**
API docs at **http://localhost:8000/docs**

### Option 2: Run without Docker

```bash
cd lexai/backend
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
python -m http.server 3000
```

Open **http://localhost:3000**

---

## 📁 Project Structure

```
LexAI/
├── lexai/
│   └── backend/
│       ├── main.py                 # FastAPI app entry point
│       ├── Dockerfile              # Docker configuration
│       ├── requirements.txt        # Python dependencies
│       ├── models/
│       │   └── schemas.py          # Pydantic data models
│       ├── routes/
│       │   ├── analyze.py          # v1 clause analysis endpoint
│       │   ├── chat.py             # v2 RAG chat endpoints
│       │   └── report.py           # v3 PDF report endpoint
│       └── services/
│           ├── extractor.py        # PDF + OCR text extraction
│           ├── analyzer.py         # Gemini AI integration
│           ├── rag.py              # ChromaDB RAG pipeline
│           └── report.py           # ReportLab PDF generation
└── frontend/
    └── index.html                  # Single-file frontend
```

---

## 🧠 Key Technical Concepts

### 1. Three-Layer Text Extraction
```
pdfplumber (digital PDFs)
    ↓ fails?
PyMuPDF (complex layouts)
    ↓ fails?
EasyOCR (scanned/photographed documents)
```
This handles all Indian document formats — digitally typed, scanned, or photographed.

### 2. Prompt Engineering
The Gemini prompt instructs the model to act as an Indian legal expert and return strictly validated JSON with clause types, risk levels, plain English explanations, and India-specific legal recommendations (IPC, Consumer Protection Act, Rent Control Act).

### 3. RAG Pipeline
```
Document → Chunked (500 chars, 50 overlap)
         → Stored in ChromaDB with embeddings
         → User asks question
         → Top 4 semantically similar chunks retrieved
         → Gemini answers based only on retrieved context
```
This enables unlimited Q&A without resending the full document to the LLM every time.

### 4. Structured Output Validation
All Gemini responses are validated through Pydantic schemas before being returned to the client — ensuring the API never returns malformed data even if the LLM output is inconsistent.

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/analyze` | Analyze document clauses |
| GET | `/api/v1/health` | Health check |
| POST | `/api/v2/upload-and-analyze` | Analyze + store for chat |
| POST | `/api/v2/chat` | Ask questions about document |
| DELETE | `/api/v2/session/{id}` | Clean up session |
| POST | `/api/v3/generate-report` | Generate PDF risk report |

---

## 🎯 Supported Document Types

- Rental / Lease Agreements
- Employment Offer Letters
- Non-Disclosure Agreements (NDAs)
- Loan Agreements
- Service Contracts
- Insurance Policy Documents
- College Fee / Hostel Agreements
- Builder-Buyer Agreements

---

## ⚠️ Disclaimer

LexAI is an AI-powered document assistant for informational purposes only. It does not constitute legal advice. Please consult a qualified lawyer for legal decisions.

---

## 👨‍💻 Built By

**Pulkit Kher** — Final year B.Tech CSE

- GitHub: [github.com/pulkitKher](https://github.com/pulkitKher)
- Project: Built for MNC placement portfolio demonstrating full-stack GenAI development

---

## 📄 License

MIT License — feel free to use, modify, and distribute.
