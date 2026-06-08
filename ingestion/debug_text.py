"""
Debug script — run from project root:
    python -m ingestion.debug_text documents/reddit_cop3514.txt

Optional flags:
    --save      write output to ingestion/debug_text_output.json
"""

import argparse
import json
import sys
from pathlib import Path

from ingestion.loaders.text_loader import load_text
from ingestion.adapters.text_adapter import TextAdapter

OUTPUT_FILE = Path("ingestion/debug_text_output.json")


def print_document(doc: dict) -> None:
    meta = doc["metadata"]
    print(f"\n{'=' * 60}")
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

    parser = argparse.ArgumentParser(description="Debug text/Reddit loader + adapter")
    parser.add_argument("file", help="Path to .txt file in documents/")
    parser.add_argument("--save", action="store_true", help="Save output to JSON file")
    args = parser.parse_args()

    file_path = Path(args.file)
    print(f"Loading: {file_path}")

    text = load_text(str(file_path))
    print(f"Raw text length: {len(text)} chars")

    documents = TextAdapter().transform({"file_path": str(file_path), "text": text})

    print(f"\n--- Stats ---")
    print(f"Total documents: {len(documents)}")

    none_count = sum(1 for d in documents for v in d["metadata"].values() if v is None)
    print(f"Metadata None values: {none_count}")

    for doc in documents:
        print_document(doc)

    if args.save:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=2)
        print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
