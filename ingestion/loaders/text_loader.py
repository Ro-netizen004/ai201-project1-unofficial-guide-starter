from pathlib import Path


def load_text(file_path: str) -> str:
    """Read a plain-text file (e.g. copied Reddit thread)."""
    path = Path(file_path)
    text = path.read_text(encoding="utf-8-sig")
    return text
