from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.analyze import router as analyze_router
from routes.chat import router as chat_router
from routes.report import router as report_router

app = FastAPI(
    title="LexAI",
    description="AI-powered Legal & Financial Document Analyzer for Indians",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phase 1 — Document analysis
app.include_router(analyze_router, prefix="/api/v1")

# Phase 2 — RAG Chat
app.include_router(chat_router, prefix="/api/v2")

# Phase 3 — PDF Report
app.include_router(report_router, prefix="/api/v3")

@app.get("/")
async def root():
    return {
        "message": "Welcome to LexAI",
        "docs": "/docs",
        "v1_analyze": "/api/v1/analyze",
        "v2_upload": "/api/v2/upload-and-analyze",
        "v2_chat": "/api/v2/chat",
        "v3_report": "/api/v3/generate-report"
    }