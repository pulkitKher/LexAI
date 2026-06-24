from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.analyze import router

app = FastAPI(
    title="LexAI",
    description="AI-powered Legal & Financial Document Analyzer for Indians",
    version="1.0.0"
)

# CORS — allows frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to LexAI",
        "docs": "/docs",
        "health": "/api/v1/health"
    }