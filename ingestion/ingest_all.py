"""Load every document source and return standardized documents."""

from pathlib import Path
from typing import Dict, List

from ingestion.adapters.json_adapter_professor import ProfessorJSONAdapter
from ingestion.adapters.pdf_adapter import PDFAdapter
from ingestion.adapters.text_adapter import TextAdapter
from ingestion.loaders.json_loader import load_json
from ingestion.loaders.pdf_loader import PDFLoader
from ingestion.loaders.text_loader import load_text

DOCUMENTS_DIR = Path("documents")
PROFESSOR_JSON = DOCUMENTS_DIR / "dataset_rate-my-professors.json"
DEGREE_PLAN_PDF = DOCUMENTS_DIR / "usf_cs_plan.pdf"


def _text_files() -> List[Path]:
    """All collected .txt sources, excluding templates (_*.txt)."""
    return sorted(
        f for f in DOCUMENTS_DIR.glob("*.txt")
        if not f.name.startswith("_")
    )


def ingest_professors() -> List[Dict]:
    raw = load_json(str(PROFESSOR_JSON))
    return ProfessorJSONAdapter().transform(raw)


def ingest_degree_plan() -> List[Dict]:
    loader = PDFLoader()
    return PDFAdapter().transform({
        "file_path": str(DEGREE_PLAN_PDF),
        "pages": loader.load_pages(str(DEGREE_PLAN_PDF)),
    })


def ingest_text_file(file_path: Path) -> List[Dict]:
    return TextAdapter().transform({
        "file_path": str(file_path),
        "text": load_text(str(file_path)),
    })


def ingest_all() -> List[Dict]:
    """Load and transform every document source into standardized documents."""
    documents: List[Dict] = []

    documents.extend(ingest_professors())
    documents.extend(ingest_degree_plan())

    for file_path in _text_files():
        documents.extend(ingest_text_file(file_path))

    return documents
