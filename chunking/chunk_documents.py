"""Split ingested documents into embedder-sized chunks."""

from typing import Dict, List

# all-MiniLM-L6-v2 max ~256 tokens — keep whole docs under ~800 chars
MAX_WHOLE_CHARS = 800
CHUNK_SIZE = 500
OVERLAP = 75


def _split_long_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Split long text with overlap, preferring breaks at newlines."""
    chunks: List[str] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        if end < text_len:
            break_at = text.rfind("\n", start, end)
            if break_at > start + chunk_size // 2:
                end = break_at

        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)

        if end >= text_len:
            break

        next_start = end - overlap
        start = next_start if next_start > start else end

    return chunks


def chunk_documents(documents: List[Dict]) -> List[Dict]:
    """
    Convert standardized documents into chunks ready for embedding.

    Short documents (reviews, PDF pages) pass through as one chunk.
    Longer documents are split into ~500 character chunks with 75 char overlap.
    """
    chunks: List[Dict] = []

    for doc in documents:
        text = doc["text"].strip()
        if not text:
            continue

        base_meta = dict(doc["metadata"])

        if len(text) <= MAX_WHOLE_CHARS:
            chunks.append({
                "text": text,
                "metadata": {
                    **base_meta,
                    "chunk_index": 0,
                    "chunk_total": 1,
                },
            })
            continue

        parts = _split_long_text(text, CHUNK_SIZE, OVERLAP)
        for index, piece in enumerate(parts):
            chunks.append({
                "text": piece,
                "metadata": {
                    **base_meta,
                    "chunk_index": index,
                    "chunk_total": len(parts),
                },
            })

    return chunks
