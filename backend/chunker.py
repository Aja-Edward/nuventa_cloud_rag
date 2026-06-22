# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from backend.pdf_loader import load_pdf


# def chunk_text(text):
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=500, chunk_overlap=100
#     )

#     chunks = splitter.split_text(text)
#     return chunks


# if __name__ == "__main__":
#     pdf_path = "everythingschool.pdf"
#     text = load_pdf(pdf_path)

#     chunks = chunk_text(text)
#     print("Total chunks:", len(chunks))
#     print("\n--- SAMPLE CHUNK ---\n")

#     for i, chunk in enumerate(chunks[:5]):
#         print(f"Chunk {i + 1}:\n{chunk}\n")


"""
chunker.py — Semantic-aware text chunker with overlap.

Strategy:
  1. Split on natural paragraph/sentence boundaries first.
  2. Assemble chunks that are close to CHUNK_SIZE tokens (≈ characters / 4).
  3. Slide a OVERLAP_SIZE token window between consecutive chunks so the
     embedding model always sees enough context → higher cosine scores.

Tuning constants (adjust to taste):
  CHUNK_SIZE    ≈ 400 tokens  → sweet-spot for text-embedding-3-small
  OVERLAP_SIZE  ≈ 80  tokens  → ~20 % overlap keeps retrieval coherent
  MIN_CHUNK     ≈ 50  tokens  → discard noise fragments
"""

import re

# ── tuneable constants ──────────────────────────────────────────────────────
CHUNK_SIZE = 800   # characters  (~200 tokens)  ← halved from 1600
OVERLAP_SIZE = 160   # characters  (~40 tokens)   ← keep at ~20% of CHUNK_SIZE
MIN_CHUNK = 100   # characters  (~25 tokens)   ← halved from 200
# ───────────────────────────────────────────────────────────────────────────


def _split_sentences(text: str) -> list[str]:
    """Split on sentence-ending punctuation while keeping the delimiter."""
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def _split_paragraphs(text: str) -> list[str]:
    """Split on blank lines (paragraph boundaries)."""
    paras = re.split(r"\n{2,}", text)
    return [p.strip() for p in paras if p.strip()]


def chunk_text(text: str) -> list[str]:
    """
    Return a list of overlapping text chunks optimised for embedding quality.

    Pipeline
    --------
    text → paragraphs → sentences → assembled windows → deduplicated
    """
    # 1. Paragraph-level split
    paragraphs = _split_paragraphs(text)

    # 2. Sentence-level split within each paragraph
    sentences: list[str] = []
    for para in paragraphs:
        sents = _split_sentences(para)
        if sents:
            sentences.extend(sents)
            # Paragraph boundary marker — empty string used as a soft break
            sentences.append("")

    # 3. Assemble sentences into fixed-size windows with overlap
    chunks: list[str] = []
    current_chars: list[str] = []   # sentence buffer for current chunk
    current_len = 0

    for sent in sentences:
        sent_len = len(sent)

        # Flush if adding this sentence would exceed CHUNK_SIZE
        if current_len + sent_len > CHUNK_SIZE and current_chars:
            chunk_text_str = " ".join(s for s in current_chars if s).strip()
            if len(chunk_text_str) >= MIN_CHUNK:
                chunks.append(chunk_text_str)

            # ── overlap: keep tail of current buffer ──
            overlap_chars: list[str] = []
            overlap_len = 0
            for s in reversed(current_chars):
                if overlap_len + len(s) > OVERLAP_SIZE:
                    break
                overlap_chars.insert(0, s)
                overlap_len += len(s) + 1  # +1 for space

            current_chars = overlap_chars
            current_len = overlap_len

        current_chars.append(sent)
        current_len += sent_len + 1

    # Flush final buffer
    if current_chars:
        chunk_text_str = " ".join(s for s in current_chars if s).strip()
        if len(chunk_text_str) >= MIN_CHUNK:
            chunks.append(chunk_text_str)

    return chunks


# ── quick self-test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample = (
        "This is the first sentence. And this is the second sentence!\n\n"
        "A new paragraph starts here. It contains multiple sentences. "
        "Here is yet another one. Overlap should carry part of this.\n\n"
        "Final paragraph with a single line."
    )
    result = chunk_text(sample)
    for i, c in enumerate(result):
        print(f"[Chunk {i + 1}] ({len(c)} chars)\n{c}\n{'-' * 60}")
