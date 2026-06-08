from pathlib import Path
from typing import Any, Dict, List

from ingestion.adapters.base_adapter import BaseAdapter


class PDFAdapter(BaseAdapter):

    def transform(self, raw_data: Any) -> List[Dict]:
        """
        Convert extracted PDF pages into standardized documents.
        Expected input:
        {
            "file_path": str,
            "pages": [{"page": int, "text": str}, ...]
        }
        """
        file_path = raw_data["file_path"]
        pages = raw_data["pages"]
        source_id = Path(file_path).stem

        documents = []
        for page in pages:
            page_num = page["page"]
            documents.append(
                self.build_document(
                    self._build_page_text(source_id, page_num, page["text"]),
                    {
                        "type": "degree_plan",
                        "source": source_id,
                        "file": file_path,
                        "page": page_num,
                    },
                )
            )

        return documents

    def _build_page_text(self, source_id: str, page_num: int, text: str) -> str:
        return f"USF CS Degree Plan ({source_id}) — Page {page_num}\n\n{text.strip()}"
