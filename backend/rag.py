import os
from dotenv import load_dotenv
from openai import OpenAI
from backend.db import get_connection
from backend.embeddings import get_embedding

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def retrieve_chunks(query: str, top_k: int = 5) -> list[dict]:
    """Embed the query and find the most similar chunks in the DB."""
    query_vector = get_embedding(query)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT content, source, chunk_index,
               1 - (embedding <=> %s::vector) AS similarity
        FROM documents
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (query_vector, query_vector, top_k),
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "content": row[0],
            "source": row[1],
            "chunk_index": row[2],
            "similarity": round(row[3], 4),
        }
        for row in rows
    ]


def generate_answer(question: str, chunks: list[dict]) -> str:
    """Send retrieved context + question to GPT and return the answer."""
    context = "\n\n---\n\n".join(chunk["content"] for chunk in chunks)

    system_prompt = """You are a helpful assistant that answers questions based strictly on the provided context.
If the answer is not found in the context, say "I don't have enough information to answer that."
Do not make up information."""

    user_prompt = f"""Context:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()


def ask(question: str, top_k: int = 5) -> str:
    """Full RAG pipeline: retrieve relevant chunks then generate an answer."""
    print(f"\n🔍 Question: {question}")

    print("   Retrieving relevant chunks...")
    chunks = retrieve_chunks(question, top_k=top_k)

    print(
        f"   Found {len(chunks)} chunks (top similarity: {chunks[0]['similarity']})")

    print("   Generating answer...\n")
    answer = generate_answer(question, chunks)

    return answer


if __name__ == "__main__":
    # Try a few sample questions — change these to suit your PDF
    questions = [
        "What is this document about?",
        "What are the main topics covered?",
    ]

    for question in questions:
        answer = ask(question)
        print(f"💬 Answer: {answer}")
        print("\n" + "=" * 60 + "\n")
