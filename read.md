source venv/Scripts/activate
uvicorn main:app --reload --port 8000

echo "# LexAI" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/pulkitKher/LexAI.git
git push -u origin main

docker build -t lexai-backend .
docker run -p 8000:8000 --env-file .env lexai-backend

Part 1: Why This Folder Structure? 🏗️
This is called Separation of Concerns — one of the most important software engineering principles. Every folder has ONE job.
backend/
├── main.py          → Entry point (just starts the app)
├── models/          → Data structures only
├── services/        → Business logic only  
├── routes/          → API endpoints only
Think of it like a restaurant:
FolderRestaurant EquivalentJobmain.pyRestaurant entranceWelcomes everyone, directs to right placeroutes/WaitersTakes order from customer, passes to kitchenservices/Kitchen / ChefsDoes the actual cooking (real work)models/Menu / Recipe bookDefines what dishes look like

Part 2: Each File Explained Like a Story 📖

models/schemas.py — The Blueprint
Why it exists:
Before building anything, you need to define what your data looks like. Like before building a house, you need a blueprint.
pythonclass RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
This says — risk can ONLY be one of these 3 values. If Gemini returns "very high" by mistake, Pydantic rejects it automatically.
pythonclass Clause(BaseModel):
    clause_type: str
    original_text: str
    plain_explanation: str
    risk_level: RiskLevel
    recommendation: str
This is the shape of ONE clause. Every clause in every document must have exactly these 5 fields.
Interview answer:

"I used Pydantic models to enforce strict data validation. This ensures that even if the AI returns malformed JSON, the API never sends bad data to the frontend."


services/extractor.py — The Document Reader
Why it exists:
Documents in real life come in 3 forms. We need to handle all 3:
Form 1: Digital PDF (typed on computer)
        → pdfplumber reads it directly ✅

Form 2: Digital PDF but complex layout
        → PyMuPDF (fitz) as backup ✅

Form 3: Scanned document (photographed paper)
        → EasyOCR converts image to text ✅
Why 3 methods and not 1?
Because in India, most legal documents are physically signed and scanned. A rental agreement written by hand, stamped, and scanned as JPG — pdfplumber would return empty string. EasyOCR saves us.
The waterfall logic:
pythontry pdfplumber → got 100+ chars? return it
try PyMuPDF → got 100+ chars? return it  
fallback to EasyOCR → always works
Interview answer:

"I built a three-layer text extraction pipeline because Indian legal documents exist in many formats — digital PDFs, scanned copies, and phone photographs. The system tries the fastest method first and falls back to OCR only when needed, optimizing for both speed and accuracy."


services/analyzer.py — The Gemini Brain
Why it exists:
This is the core GenAI integration. Three important things happen here:
1. Prompt Engineering:
pythondef build_prompt(text: str) -> str:
We don't just dump text to Gemini. We tell it:

WHO it is (LexAI, Indian legal expert)
WHAT to return (strict JSON format)
HOW to think (India-specific laws)
WHAT to avoid (legal jargon)

The quality of your AI output is 80% determined by your prompt. Bad prompt = bad output.
2. Truncation:
pythonif len(extracted_text) > 30000:
    extracted_text = extracted_text[:30000]
Free tier Gemini has token limits. We cut documents at 30,000 characters to avoid quota errors.
3. Response Parsing:
pythondef parse_gemini_response(raw_text: str) -> AnalysisResponse:
Gemini sometimes wraps JSON in markdown fences like ```json. We strip that before parsing, making the code robust.
Interview answer:

"The analyzer uses prompt engineering to instruct Gemini to act as an Indian legal expert and return strictly structured JSON. I handle edge cases like markdown-wrapped responses and truncate large documents to stay within free tier limits."


services/rag.py — The Memory System
Why it exists:
Gemini has no memory between requests. If you upload a 50-page document and ask 10 questions, you can't send 50 pages every time — it's slow and hits rate limits.
RAG solves this:
Step 1: CHUNKING
50-page document → split into 500-char chunks with 50-char overlap
Why overlap? So context isn't lost at chunk boundaries

Step 2: STORING
Each chunk stored in ChromaDB with an embedding (vector representation)
ChromaDB converts text → numbers that capture semantic meaning

Step 3: RETRIEVAL
User asks: "What happens if I break lease?"
ChromaDB finds top 4 chunks most semantically similar to this question
NOT keyword search — it understands MEANING

Step 4: ANSWERING
Only those 4 chunks sent to Gemini → fast, cheap, accurate
Why ChromaDB specifically?

Runs locally — no cloud, no cost, no data privacy issues
Persistent — data survives server restarts
Fast — millisecond retrieval even for large documents

Interview answer:

"I implemented RAG using ChromaDB as the vector store. Documents are chunked with overlapping windows to preserve context, embedded locally, and retrieved semantically at query time. This means users can ask unlimited questions about a document without resending it to the LLM every time — reducing latency and API costs significantly."


services/report.py — The PDF Generator
Why it exists:
JSON responses are great for developers but useless for regular users. A tenant needs something they can print and show their lawyer. ReportLab builds professional PDFs programmatically.
Key design decisions:

Color coding (red/orange/green) for instant visual risk assessment
Original text + explanation + recommendation per clause
Disclaimer at bottom for legal protection
A4 size — standard Indian document format


routes/ — The Waiters
Why separate from services?
Routes handle HTTP concerns:

File validation (is this actually a PDF?)
File size check (is it under 10MB?)
UUID generation (unique filename to avoid conflicts)
Cleanup (delete temp file after processing)
Error handling (return proper HTTP status codes)

Services handle business logic:

Extract text
Analyze with Gemini
Store in ChromaDB
Generate report

If you mix them: routes become 300 lines, untestable, unmaintainable.
If you separate them: each file has one job, easy to debug, easy to test.

main.py — The Entry Point
Three things only:

Create FastAPI app
Add CORS middleware (so React frontend can call the API)
Register all routers with version prefixes

Version prefixes (/api/v1, /api/v2, /api/v3) mean you can release new versions without breaking old clients — standard industry practice.

Part 3: Where Do These Legal Documents Exist in Real Life? 🏛️
This is important for your placement interviews — shows product thinking.
Documents LexAI Can Analyze:
Rental / Housing:

Rent agreements (most common in India)
Lease deeds
Society NOC letters
Property sale agreements

Employment:

Offer letters (notice period traps, bond clauses)
Employment contracts
NDA agreements (non-disclosure)
Freelance contracts

Financial:

Loan agreements (personal, home, education)
Credit card terms
Insurance policy documents
Mutual fund KIM documents

Consumer:

E-commerce return policies
App terms and conditions
Warranty documents
Builder-buyer agreements

Education:

College fee refund policies
Scholarship bonds
Hostel agreements


The Real Problem LexAI Solves:
Scenario 1: Ramesh from Jaipur signs a rental agreement without reading it. Clause 17 says if he overstays by even 1 day, he pays double rent. He didn't know. LexAI would have flagged this as HIGH RISK.
Scenario 2: Priya gets an offer letter with a 2-year bond clause buried in page 6. She joins, then gets a better offer after 8 months. She has to pay ₹2 lakhs to leave. LexAI would have highlighted this.
Scenario 3: A student takes an education loan. The agreement has a clause that the guarantor (his father) becomes liable even if the student dies. LexAI would flag this as HIGH RISK.
These aren't hypothetical — they happen every day in India.

Why This Problem Is Massive in India:

1.4 billion people, most don't have legal literacy
Average lawyer consultation costs ₹2,000–5,000 per hour
Most people sign documents without reading them
Indian courts have 45 million pending cases — mostly contract disputes
LexAI addresses all of this for free


One Paragraph to Impress Any Interviewer:

"LexAI addresses a fundamental access-to-justice problem in India. Most Indians sign legal documents — rental agreements, offer letters, loan papers — without understanding what they're agreeing to, simply because legal consultation is expensive and legal language is incomprehensible. LexAI uses a RAG-based GenAI pipeline with Gemini 2.5 Flash to extract clauses, classify risk levels, provide plain-English explanations, and generate downloadable reports. The system handles both digital and scanned documents through a three-layer OCR pipeline. Built with FastAPI, ChromaDB, and ReportLab, it's a complete production-grade system — not a tutorial project."


Take your time to absorb this. Make notes. Then tell me when you're ready to build the React frontend — the final big piece! 🚀