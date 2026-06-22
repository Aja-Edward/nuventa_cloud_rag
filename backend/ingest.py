import os
from dotenv import load_dotenv
from db import get_connection
from pdf_loader import load_pdf
from chunker import chunk_text
from embeddings import get_embedding

load_dotenv()


def setup_db():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    except Exception:
        conn.rollback()  # extension already exists or no permission — safe to ignore
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id          SERIAL PRIMARY KEY,
            source      TEXT,
            chunk_index INTEGER,
            content     TEXT,
            embedding   vector(1536)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database ready")


def store_chunks(source, chunks, embeddings):
    conn = get_connection()
    cur = conn.cursor()

    # Delete existing chunks for this source before re-inserting
    cur.execute("DELETE FROM documents WHERE source = %s", (source,))

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        cur.execute(
            "INSERT INTO documents (source, chunk_index, content, embedding) VALUES (%s, %s, %s, %s)",
            (source, i, chunk, embedding),
        )
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Stored {len(chunks)} chunks from '{source}'")


def ingest(pdf_path):
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return

    print(f"\n📄 Loading PDF: {pdf_path}")
    text = load_pdf(pdf_path)
    print(f"   Characters loaded: {len(text)}")

    print("\n✂️  Chunking text...")
    chunks = chunk_text(text)
    print(f"   Total chunks: {len(chunks)}")

    print("\n🔢 Generating embeddings...")
    embeddings = []
    for i, chunk in enumerate(chunks):
        vector = get_embedding(chunk)
        embeddings.append(vector)
        print(f"   Chunk {i + 1}/{len(chunks)} embedded", end="\r")
    print()

    print("\n💾 Storing in database...")
    store_chunks(source=pdf_path, chunks=chunks, embeddings=embeddings)

    print("\n🎉 Ingestion complete!")


if __name__ == "__main__":
    setup_db()
    ingest("everythingschool.pdf")
