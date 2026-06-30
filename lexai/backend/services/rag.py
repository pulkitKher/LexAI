import chromadb
import os
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ChromaDB client — stores data locally in backend/chroma_db/
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Gemini model for chat
chat_model = genai.GenerativeModel("gemini-2.5-flash-lite") 


def chunk_text(text: str) -> list[str]:
    """Split document into overlapping chunks for better retrieval"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    return splitter.split_text(text)


def store_document(session_id: str, text: str) -> int:
    """Chunk document and store in ChromaDB under session_id"""

    # Delete old collection if exists (fresh session)
    try:
        chroma_client.delete_collection(name=session_id)
    except Exception:
        pass

    collection = chroma_client.create_collection(name=session_id)
    chunks = chunk_text(text)

    # Store each chunk with a unique ID
    collection.add(
        documents=chunks,
        ids=[f"{session_id}_{i}" for i in range(len(chunks))]
    )

    return len(chunks)


def retrieve_relevant_chunks(session_id: str, question: str, top_k: int = 4) -> list[str]:
    """Find most relevant chunks for the question"""
    try:
        collection = chroma_client.get_collection(name=session_id)
        results = collection.query(
            query_texts=[question],
            n_results=min(top_k, collection.count())
        )
        return results["documents"][0] if results["documents"] else []
    except Exception as e:
        raise ValueError(f"Session not found. Please upload document first. Error: {e}")


def answer_question(session_id: str, question: str) -> str:
    """RAG pipeline — retrieve chunks then answer with Gemini"""

    chunks = retrieve_relevant_chunks(session_id, question)

    if not chunks:
        return "I could not find relevant information in the document to answer your question."

    context = "\n\n---\n\n".join(chunks)

    prompt = f"""You are LexAI, an expert Indian legal and financial document assistant.

Answer the user's question based ONLY on the document excerpts provided below.
If the answer is not in the document, say "This information is not found in the uploaded document."
Keep your answer clear, simple, and helpful for a common Indian person.
If relevant, mention applicable Indian laws or rights.

Document Excerpts:
{context}

User Question: {question}

Answer:"""

    try:
        response = chat_model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise ValueError(f"Gemini error: {str(e)}")


def delete_session(session_id: str) -> bool:
    """Clean up session data from ChromaDB"""
    try:
        chroma_client.delete_collection(name=session_id)
        return True
    except Exception:
        return False