"""
Debug script — run from project root:
    python -m ingestion.debug_pdf

Optional flags:
    --all       print every document (verbose)
    --save      write full output to ingestion/debug_pdf_output.json
"""

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from ingestion.loaders.pdf_loader import PDFLoader
from ingestion.adapters.pdf_adapter import PDFAdapter

PDF_FILE = Path("documents/usf_cs_plan.pdf")
OUTPUT_FILE = Path("ingestion/debug_pdf_output.json")


def print_document(doc: dict, index: int) -> None:
    meta = doc["metadata"]
    print(f"\n{'=' * 60}")
    print(f"Document #{index + 1}  |  type: {meta.get('type')}  |  page: {meta.get('page')}")
    print(f"{'=' * 60}")
    print("TEXT:")
    print(doc["text"])
    print("\nMETADATA:")
    print(json.dumps(meta, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Debug PDF loader + adapter output")
    parser.add_argument("--all", action="store_true", help="Print all documents")
    parser.add_argument("--save", action="store_true", help="Save full output to JSON file")
    args = parser.parse_args()

    print(f"Loading: {PDF_FILE}")
    loader = PDFLoader()
    pages = loader.load_pages(str(PDF_FILE))
    print(f"Pages with text: {len(pages)}")

    raw_data = {"file_path": str(PDF_FILE), "pages": pages}
    documents = PDFAdapter().transform(raw_data)

    print(f"\n--- Stats ---")
    print(f"Total documents: {len(documents)}")

    lengths = [len(d["text"]) for d in documents]
    print(f"Text length (chars): min={min(lengths)}, max={max(lengths)}, avg={sum(lengths) // len(lengths)}")

    none_count = sum(1 for d in documents for v in d["metadata"].values() if v is None)
    print(f"Metadata None values: {none_count}")

    if args.all:
        for i, doc in enumerate(documents):
            print_document(doc, i)
    else:
        print("\n--- Sample: first 2 pages (use --all to see everything) ---")
        for i, doc in enumerate(documents[:2]):
            print_document(doc, i)

    if args.save:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(documents, f, indent=2)
        print(f"\nSaved full output to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
