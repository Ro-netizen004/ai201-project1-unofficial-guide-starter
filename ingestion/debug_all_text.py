"""
Debug all Reddit .txt files — run from project root:
    python -m ingestion.debug_all_text

Optional flags:
    --all       print full text for each file (verbose)
    --save      write combined output to ingestion/debug_all_text_output.json
"""

import argparse
import json
import sys
from pathlib import Path

from ingestion.loaders.text_loader import load_text
from ingestion.adapters.text_adapter import TextAdapter

DOCUMENTS_DIR = Path("documents")
OUTPUT_FILE = Path("ingestion/debug_all_text_output.json")


def print_document(doc: dict, file_name: str) -> None:
    meta = doc["metadata"]
    print(f"\n{'=' * 60}")
    print(f"File: {file_name}")
    print(f"type: {meta.get('type')}  |  title: {meta.get('title')}")
    print(f"{'=' * 60}")
    print("TEXT:")
    print(doc["text"][:1500])
    if len(doc["text"]) > 1500:
        print(f"\n... ({len(doc['text']) - 1500} more chars)")
    print("\nMETADATA:")
    print(json.dumps(meta, indent=2))


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Debug all Reddit text files")
    parser.add_argument("--all", action="store_true", help="Print full output per file")
    parser.add_argument("--save", action="store_true", help="Save all documents to JSON")
    args = parser.parse_args()

    txt_files = sorted(DOCUMENTS_DIR.glob("reddit_*.txt"))
    if not txt_files:
        print("No reddit_*.txt files found in documents/")
        return

    adapter = TextAdapter()
    all_documents = []

    print(f"Found {len(txt_files)} text file(s)\n")
    print(f"{'File':<35} {'Chars':>6}  {'Docs':>4}  Title")
    print("-" * 80)

    for file_path in txt_files:
        text = load_text(str(file_path))
        documents = adapter.transform({"file_path": str(file_path), "text": text})
        all_documents.extend(documents)

        title = documents[0]["metadata"].get("title", "?") if documents else "?"
        print(f"{file_path.name:<35} {len(text):>6}  {len(documents):>4}  {title[:40]}")

    lengths = [len(d["text"]) for d in all_documents]
    none_count = sum(1 for d in all_documents for v in d["metadata"].values() if v is None)

    print(f"\n--- Totals ---")
    print(f"Files: {len(txt_files)}")
    print(f"Documents: {len(all_documents)}")
    print(f"Text length (chars): min={min(lengths)}, max={max(lengths)}, avg={sum(lengths) // len(lengths)}")
    print(f"Metadata None values: {none_count}")

    if args.all:
        for file_path in txt_files:
            text = load_text(str(file_path))
            documents = adapter.transform({"file_path": str(file_path), "text": text})
            for doc in documents:
                print_document(doc, file_path.name)
    else:
        print("\nUse --all to print each file's text and metadata.")

    if args.save:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_documents, f, indent=2)
        print(f"\nSaved {len(all_documents)} documents to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
