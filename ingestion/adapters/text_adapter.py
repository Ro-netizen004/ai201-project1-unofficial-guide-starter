from pathlib import Path
from typing import Any, Dict, List, Tuple

from ingestion.adapters.base_adapter import BaseAdapter


class TextAdapter(BaseAdapter):
    """Adapter for plain-text files such as copied Reddit threads."""

    def transform(self, raw_data: Any) -> List[Dict]:
        """
        Convert a text file into standardized document(s).
        Expected input:
        {
            "file_path": str,
            "text": str
        }

        Optional header at the top of the file (before ---):
            Title: thread title
            URL: https://www.reddit.com/...
            Source: reddit
        """
        file_path = raw_data["file_path"]
        header, body = self._parse_header(raw_data["text"])
        source_id = Path(file_path).stem

        title = header.get("title") or source_id.replace("_", " ")
        url = header.get("url")
        source = header.get("source") or "reddit"

        return [
            self.build_document(
                self._build_text(title, body),
                {
                    "type": "reddit_thread",
                    "source": source,
                    "file": file_path,
                    "title": title,
                    "url": url,
                },
            )
        ]

    def _parse_header(self, text: str) -> Tuple[Dict[str, str], str]:
        lines = text.strip().splitlines()
        header: Dict[str, str] = {}
        body_start = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            if stripped == "---":
                body_start = i + 1
                break

            if stripped.lower().startswith("title:"):
                header["title"] = stripped.split(":", 1)[1].strip()
            elif stripped.lower().startswith("url:"):
                header["url"] = stripped.split(":", 1)[1].strip()
            elif stripped.lower().startswith("source:"):
                header["source"] = stripped.split(":", 1)[1].strip()
            elif stripped:
                # No header block — treat entire file as body
                return {}, text.strip()

        body = "\n".join(lines[body_start:]).strip()
        return header, body

    def _build_text(self, title: str, body: str) -> str:
        return f"Reddit Thread: {title}\n\n{body}"
