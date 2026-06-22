"""
main.py — FastAPI backend for the School Management RAG system.

Endpoints
---------
POST /ask          → RAG query (question → answer + sources)
GET  /health       → liveness check
GET  /stats        → chunk count in DB
POST /ingest       → (re)ingest a PDF  [optional utility endpoint]
"""

from __future__ import annotations
from openai import OpenAI
from embeddings import get_embedding
from db import get_connection

import os
import time
from typing import Optional

from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, File, FastAPI, HTTPException

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


# ── lazy imports so the app still starts even if heavy deps are loading ──────

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── app ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="School RAG API",
    description="Query the Everything School Management System documentation.",
    version="1.0.0",
)


origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://nuventa-cloud-rag.vercel.app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── request / response models ────────────────────────────────────────────────
class AskRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5
    # discard low-confidence chunks
    similarity_threshold: Optional[float] = 0.30


class SourceChunk(BaseModel):
    content: str
    source: str
    chunk_index: int
    similarity: float


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceChunk]
    elapsed_ms: int


# ── helpers ──────────────────────────────────────────────────────────────────

def retrieve_chunks(query: str, top_k: int, threshold: float) -> list[dict]:
    """Embed query and return top-k chunks above the similarity threshold."""
    query_vector = get_embedding(query)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT content, source, chunk_index,
               1 - (embedding <=> %s::vector) AS similarity
        FROM   documents
        ORDER  BY embedding <=> %s::vector
        LIMIT  %s
        """,
        (query_vector, query_vector, top_k),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "content":     row[0],
            "source":      row[1],
            "chunk_index": row[2],
            "similarity":  round(row[3], 4),
        }
        for row in rows
        if row[3] >= threshold
    ]


def generate_answer(question: str, chunks: list[dict]) -> str:
    """Send retrieved context + question to GPT and return the answer."""
    if not chunks:
        return (
            "I couldn't find relevant information in the documentation to "
            "answer your question. Please try rephrasing or ask something "
            "related to the school management system."
        )

    context = "\n\n---\n\n".join(c["content"] for c in chunks)

    system_prompt = """You are a helpful assistant for the Everything School Management System.
Answer questions based strictly on the provided documentation context.
Be concise, precise, and use bullet points when listing multiple items.
If the answer is not found in the context, say so clearly — do not make up information."""

    user_prompt = f"""Documentation context:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=800,
    )
    return response.choices[0].message.content.strip()


# ── routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stats")
def stats():
    """Return the number of stored chunks."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM documents;")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return {"total_chunks": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    """Full RAG pipeline: retrieve → generate → return."""
    if not req.question.strip():
        raise HTTPException(
            status_code=400, detail="Question must not be empty.")

    start = time.time()

    try:
        chunks = retrieve_chunks(
            req.question, req.top_k, req.similarity_threshold)
        answer = generate_answer(req.question, chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    elapsed = int((time.time() - start) * 1000)

    return AskResponse(
        question=req.question,
        answer=answer,
        sources=[SourceChunk(**c) for c in chunks],
        elapsed_ms=elapsed,
    )


@app.post("/ingest")
async def ingest_pdf(file: UploadFile = File(...)):
    """Upload PDF to Cloudinary, process it, store embeddings in Supabase."""
    tmp_path = f"/tmp/{file.filename}"

    try:
        # 1. Save upload temporarily to /tmp
        with open(tmp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Upload to Cloudinary for storage
        upload_result = cloudinary.uploader.upload(
            tmp_path,
            resource_type="raw",
            folder="rag_pdfs",
            public_id=file.filename,
        )
        cloudinary_url = upload_result.get("secure_url")
        print(f"✅ Uploaded to Cloudinary: {cloudinary_url}")

        # 3. Process the local /tmp copy (already there, no re-download needed)
        from ingest import setup_db, ingest as run_ingest
        setup_db()
        run_ingest(tmp_path)

        return {
            "status": "ingested",
            "filename": file.filename,
            "cloudinary_url": cloudinary_url,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 4. Clean up /tmp — file is safe on Cloudinary
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/debug-pdf")
async def debug_pdf(file: UploadFile = File(...)):
    import shutil
    tmp_path = f"/tmp/{file.filename}"
    with open(tmp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    from pdf_loader import load_pdf
    from chunker import chunk_text

    text = load_pdf(tmp_path)
    chunks = chunk_text(text)

    os.remove(tmp_path)

    return {
        "total_characters": len(text),
        "total_chunks": len(chunks),
        "first_500_chars": text[:500],
        "sample_chunks": chunks[:3],
    }
