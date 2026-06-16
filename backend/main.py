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
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

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
    "https://nuventa-cloud-rag.vercel.app/"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
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


class IngestRequest(BaseModel):
    pdf_path: str


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
def ingest_pdf(req: IngestRequest):
    """Trigger ingestion of a PDF into the database."""
    import os
    from ingest import setup_db, ingest as run_ingest

    if not os.path.exists(req.pdf_path):
        raise HTTPException(
            status_code=404, detail=f"File not found: {req.pdf_path}")
    try:
        setup_db()
        run_ingest(req.pdf_path)
        return {"status": "ingested", "pdf_path": req.pdf_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
