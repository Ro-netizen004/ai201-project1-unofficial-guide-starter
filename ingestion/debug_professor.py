"""
Debug script — run from project root:
    python -m ingestion.debug_professor

Optional flags:
    --all       print every document (verbose)
    --save      write full output to ingestion/debug_output.json
"""

import argparse
import json
from pathlib import Path

from ingestion.loaders.json_loader import load_json
from ingestion.adapters.json_adapter_professor import ProfessorJSONAdapter

DATASET = Path("documents/dataset_rate-my-professors.json")
OUTPUT_FILE = Path("ingestion/debug_output.json")


def print_document(doc: dict, index: int) -> None:
    meta = doc["metadata"]
    print(f"\n{'=' * 60}")
    print(f"Document #{index + 1}  |  type: {meta.get('type')}")
    print(f"{'=' * 60}")
    print("TEXT:")
    print(doc["text"])
    print("\nMETADATA:")
    print(json.dumps(meta, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Debug professor JSON adapter output")
    parser.add_argument("--all", action="store_true", help="Print all documents")
    parser.add_argument("--save", action="store_true", help="Save full output to JSON file")
    args = parser.parse_args()

    print(f"Loading: {DATASET}")
    raw = load_json(str(DATASET))
    print(f"Raw professors in file: {len(raw)}")

    documents = ProfessorJSONAdapter().transform(raw)

    summaries = [d for d in documents if d["metadata"]["type"] == "professor_summary"]
    reviews = [d for d in documents if d["metadata"]["type"] == "professor_review"]

    print(f"\n--- Stats ---")
    print(f"Total documents: {len(documents)}")
    print(f"  professor_summary: {len(summaries)}")
    print(f"  professor_review:  {len(reviews)}")

    lengths = [len(d["text"]) for d in documents]
    print(f"Text length (chars): min={min(lengths)}, max={max(lengths)}, avg={sum(lengths) // len(lengths)}")

    none_count = sum(1 for d in documents for v in d["metadata"].values() if v is None)
    print(f"Metadata None values: {none_count}  (strip these before Chroma)")

    if args.all:
        for i, doc in enumerate(documents):
            print_document(doc, i)
    else:
        print("\n--- Sample: 1 summary + 2 reviews (use --all to see everything) ---")
        if summaries:
            print_document(summaries[0], 0)
        for i, doc in enumerate(reviews[:2], start=1):
            print_document(doc, i)

    if args.save:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=2)
        print(f"\nSaved full output to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
