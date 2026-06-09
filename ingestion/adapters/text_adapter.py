from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple

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

        sections = self._split_body(body)
        flat_sections: List[Tuple[str, str]] = []
        for label, section_text in sections:
            flat_sections.extend(self._split_long_section(label, section_text))

        if len(flat_sections) == 1:
            label, section_text = flat_sections[0]
            return [
                self.build_document(
                    self._build_text(title, section_text, source),
                    self._build_metadata(
                        file_path, title, url, source, label, 0, 1
                    ),
                )
            ]

        documents = []
        for index, (label, section_text) in enumerate(flat_sections):
            documents.append(
                self.build_document(
                    self._build_text(title, section_text, source),
                    self._build_metadata(
                        file_path, title, url, source, label, index, len(flat_sections)
                    ),
                )
            )
        return documents

    def _build_metadata(
        self,
        file_path: str,
        title: str,
        url: Optional[str],
        source: str,
        section: str,
        section_index: int,
        section_total: int,
    ) -> Dict:
        return {
            "type": "reddit_thread" if source == "reddit" else "text_document",
            "source": source,
            "file": file_path,
            "title": title,
            "url": url,
            "section": section,
            "sectionIndex": section_index,
            "sectionTotal": section_total,
        }

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

    def _split_body(self, body: str) -> List[Tuple[str, str]]:
        """
        Split Reddit-style threads into POST / COMMENT sections.
        Files without those markers stay as one section.
        """
        sections: List[Tuple[str, str]] = []
        current_label = "body"
        current_lines: List[str] = []

        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith(("POST", "COMMENT", "Course Major Topics")):
                if current_lines:
                    text = "\n".join(current_lines).strip()
                    if text:
                        sections.append((current_label, text))
                current_label = stripped.split(":", 1)[0].strip()
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines:
            text = "\n".join(current_lines).strip()
            if text:
                sections.append((current_label, text))

        return sections if sections else [("body", body)]

    def _split_long_section(
        self, label: str, text: str, max_chars: int = 750
    ) -> List[Tuple[str, str]]:
        """Keep sections small enough to pass through chunking as one unit."""
        topic_parts = re.split(r"(?<=\.)\s+(?=As for )", text)
        if len(topic_parts) > 1:
            sections = []
            for index, part in enumerate(topic_parts, start=1):
                part = part.strip()
                if not part:
                    continue
                part_label = f"{label} (part {index})"
                sections.extend(self._split_long_section(part_label, part, max_chars))
            return sections

        if len(text) <= max_chars:
            return [(label, text)]

        parts: List[Tuple[str, str]] = []
        paragraphs = text.split("\n\n")
        current: List[str] = []
        current_len = 0
        part_num = 1

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            extra = len(paragraph) + (2 if current else 0)
            if current and current_len + extra > max_chars:
                parts.append((f"{label} (part {part_num})", "\n\n".join(current)))
                part_num += 1
                current = [paragraph]
                current_len = len(paragraph)
            else:
                current.append(paragraph)
                current_len += extra

        if current:
            part_label = label if part_num == 1 else f"{label} (part {part_num})"
            parts.append((part_label, "\n\n".join(current)))

        return parts

    def _build_text(self, title: str, body: str, source: str) -> str:
        prefix = {
            "reddit": "Reddit Thread",
            "github": "Study Guide",
        }.get(source, "Document")
        return f"{prefix}: {title}\n\n{body}"
