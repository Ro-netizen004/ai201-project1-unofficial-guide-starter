"""Grounded answer generation with Groq."""

import os
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from groq import Groq

from retrieval import DEFAULT_TOP_K, retrieve

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are The Unofficial Guide — a helpful assistant for USF Computer Science students.

Rules:
1. Answer ONLY using the context documents provided below.
2. If the context does not contain enough information to answer, say clearly that you do not have enough information in the provided sources.
3. Do not use outside knowledge, guess, or invent facts.
4. When possible, cite where information comes from (professor name, course code, thread title, degree plan page, etc.).
5. Be concise and practical — write like you're advising a fellow student."""


def _get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_key_here":
        raise ValueError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return Groq(api_key=api_key)


def format_source_label(metadata: Dict) -> str:
    """Turn chunk metadata into a short human-readable source label."""
    doc_type = metadata.get("type", "document")

    if doc_type == "professor_review":
        parts = ["Professor review"]
        if metadata.get("name"):
            parts.append(metadata["name"])
        if metadata.get("course"):
            parts.append(f"({metadata['course']})")
        return " — ".join(parts)

    if doc_type == "professor_summary":
        name = metadata.get("name", "Unknown professor")
        rating = metadata.get("rating")
        if rating is not None:
            return f"Professor summary — {name} (rating {rating})"
        return f"Professor summary — {name}"

    if doc_type == "degree_plan":
        page = metadata.get("page")
        return f"USF CS degree plan — page {page}" if page else "USF CS degree plan"

    if doc_type == "reddit_thread":
        title = metadata.get("title", "Thread")
        source = metadata.get("source", "web")
        return f"{source.title()} — {title}"

    return doc_type.replace("_", " ").title()


def format_context(hits: List[Dict]) -> str:
    """Format retrieved chunks as numbered context for the LLM."""
    blocks = []
    for index, hit in enumerate(hits, start=1):
        label = format_source_label(hit["metadata"])
        blocks.append(f"[Document {index} — {label}]\n{hit['text']}")
    return "\n\n---\n\n".join(blocks)


def format_sources_panel(hits: List[Dict]) -> str:
    """Format retrieved chunks for display in the UI."""
    if not hits:
        return "_No sources retrieved._"

    lines = []
    for index, hit in enumerate(hits, start=1):
        label = format_source_label(hit["metadata"])
        distance = hit.get("distance")
        score = (
            f" (distance: {distance:.3f})"
            if distance is not None
            else " (neighbor chunk)"
        )
        meta = hit["metadata"]
        extras = []

        if meta.get("url"):
            extras.append(f"[Link]({meta['url']})")
        if meta.get("chunk_total", 1) > 1:
            extras.append(
                f"chunk {meta.get('chunk_index', 0) + 1}/{meta['chunk_total']}"
            )

        extra_text = f" {' · '.join(extras)}" if extras else ""
        preview = hit["text"][:400].strip()
        if len(hit["text"]) > 400:
            preview += "..."

        lines.append(
            f"**{index}. {label}**{score}{extra_text}\n\n{preview}"
        )

    return "\n\n---\n\n".join(lines)


def generate_answer(question: str, hits: List[Dict]) -> str:
    """Generate a grounded answer from retrieved context."""
    if not hits:
        return (
            "I couldn't find any relevant documents for that question. "
            "Try rephrasing or asking about USF CS courses, professors, or degree planning."
        )

    context = format_context(hits)
    user_message = f"""Context documents:

{context}

Question: {question}"""

    client = _get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def ask(
    question: str,
    top_k: int = DEFAULT_TOP_K,
) -> Tuple[str, str]:
    """
    Retrieve relevant chunks and generate a grounded answer.

    Returns (answer, sources_markdown).
    """
    question = question.strip()
    if not question:
        return "Please enter a question.", ""

    hits = retrieve(question, top_k=top_k)
    answer = generate_answer(question, hits)
    sources = format_sources_panel(hits)
    return answer, sources
