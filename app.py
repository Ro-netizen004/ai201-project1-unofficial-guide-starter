"""Gradio UI for The Unofficial Guide RAG system."""

import gradio as gr

from generation import ask
from retrieval import build_index, EMBEDDING_MODEL, DEFAULT_TOP_K

EXAMPLE_QUESTIONS = [
    "How hard is COP 3514 according to students?",
    "What do students say about Rangachar Kasturi?",
    "What are some of the easiest CS electives at USF?",
    "What is the workload like for COP 2510?",
    "What do students think about the USF CS program overall?",
]


def startup() -> str:
    """Build the vector index on first launch if needed."""
    collection = build_index()
    return f"Index ready — {collection.count()} chunks embedded with {EMBEDDING_MODEL}."


def respond(question: str) -> tuple[str, str, str]:
    try:
        answer, sources = ask(question, top_k=DEFAULT_TOP_K)
        status = "Answer generated from retrieved sources."
        return answer, sources, status
    except ValueError as exc:
        return str(exc), "", "Missing API key."
    except Exception as exc:
        return f"Something went wrong: {exc}", "", "Error."


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="The Unofficial Guide") as demo:
        gr.Markdown(
            """
            # The Unofficial Guide
            ### USF Computer Science Survival Guide

            Ask questions about courses, professors, degree planning, and student experiences.
            Answers are grounded in Rate My Professors reviews, Reddit threads, the official
            degree plan, and student study guides.
            """
        )

        status = gr.Textbox(
            label="Status",
            value=startup(),
            interactive=False,
        )

        question = gr.Textbox(
            label="Your question",
            placeholder="e.g. How hard is COP 3514?",
            lines=2,
        )

        gr.Examples(examples=EXAMPLE_QUESTIONS, inputs=question)

        ask_btn = gr.Button("Ask", variant="primary")

        answer = gr.Markdown(label="Answer")
        sources = gr.Markdown(label="Retrieved sources")

        ask_btn.click(
            fn=respond,
            inputs=question,
            outputs=[answer, sources, status],
        )
        question.submit(
            fn=respond,
            inputs=question,
            outputs=[answer, sources, status],
        )

    return demo


if __name__ == "__main__":
    build_ui().launch()
