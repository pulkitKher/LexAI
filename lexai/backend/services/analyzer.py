import google.generativeai as genai
import json
import os
import re
from dotenv import load_dotenv
from models.schemas import AnalysisResponse, Clause, RiskLevel

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


def analyze_document(extracted_text: str) -> AnalysisResponse:
    """Send extracted text to Gemini and get structured clause analysis"""

    if not extracted_text or len(extracted_text.strip()) < 50:
        raise ValueError("Document text too short or empty to analyze.")

    # Truncate if too long (Gemini has limits on free tier)
    if len(extracted_text) > 30000:
        extracted_text = extracted_text[:30000] + "\n...[document truncated]..."

    prompt = build_prompt(extracted_text)

    try:
        response = model.generate_content(prompt)
        raw_text = response.text
        return parse_gemini_response(raw_text)

    except Exception as e:
        raise ValueError(f"Gemini API error: {str(e)}")


def build_prompt(text: str) -> str:
    return f"""
You are LexAI, an expert Indian legal and financial document analyst.

Analyze the following document and respond ONLY with a valid JSON object.
No explanation, no markdown, no code blocks. Just raw JSON.

Document Text:
\"\"\"
{text}
\"\"\"

Respond with exactly this JSON structure:
{{
  "document_type": "Type of document (e.g. Rental Agreement, Employment Contract, Loan Agreement, etc.)",
  "summary": "2-3 sentence plain English summary of what this document is about",
  "total_clauses_found": <number>,
  "high_risk_count": <number>,
  "medium_risk_count": <number>,
  "low_risk_count": <number>,
  "clauses": [
    {{
      "clause_type": "Name of clause (e.g. Termination Clause, Penalty Clause)",
      "original_text": "Exact relevant excerpt from the document (max 200 chars)",
      "plain_explanation": "Explain this clause in simple English that a student can understand",
      "risk_level": "high" or "medium" or "low",
      "recommendation": "What should the user do or watch out for regarding this clause"
    }}
  ]
}}

Rules:
- Identify ALL important clauses (minimum 5, maximum 15)
- Risk levels: high = could cause financial loss or legal trouble, medium = needs attention, low = standard/safe
- Focus on clauses that affect the common Indian person (students, tenants, employees, borrowers)
- plain_explanation must be in simple English, no legal jargon
- If document is in Hindi or mixed language, still respond in English
- Be specific to Indian law context (IPC, Consumer Protection Act, Rent Control Act, etc.) where relevant
"""


def parse_gemini_response(raw_text: str) -> AnalysisResponse:
    """Parse Gemini's JSON response into our schema"""

    # Clean up response — remove markdown fences if present
    cleaned = raw_text.strip()
    cleaned = re.sub(r'^```json\s*', '', cleaned)
    cleaned = re.sub(r'^```\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Gemini response as JSON: {e}\nRaw: {raw_text[:500]}")

    # Build Clause objects
    clauses = []
    for c in data.get("clauses", []):
        try:
            clause = Clause(
                clause_type=c["clause_type"],
                original_text=c["original_text"],
                plain_explanation=c["plain_explanation"],
                risk_level=RiskLevel(c["risk_level"].lower()),
                recommendation=c["recommendation"]
            )
            clauses.append(clause)
        except Exception as e:
            print(f"Skipping malformed clause: {e}")
            continue

    return AnalysisResponse(
        document_type=data.get("document_type", "Unknown"),
        summary=data.get("summary", ""),
        total_clauses_found=data.get("total_clauses_found", len(clauses)),
        high_risk_count=data.get("high_risk_count", 0),
        medium_risk_count=data.get("medium_risk_count", 0),
        low_risk_count=data.get("low_risk_count", 0),
        clauses=clauses
    )