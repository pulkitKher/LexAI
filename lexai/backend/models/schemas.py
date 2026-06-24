from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Clause(BaseModel):
    clause_type: str
    original_text: str
    plain_explanation: str
    risk_level: RiskLevel
    recommendation: str

class AnalysisResponse(BaseModel):
    document_type: str
    summary: str
    total_clauses_found: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    clauses: List[Clause]
    disclaimer: str = "LexAI is an AI-powered document assistant for informational purposes only. It does not constitute legal advice. Please consult a qualified lawyer for legal decisions."

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None