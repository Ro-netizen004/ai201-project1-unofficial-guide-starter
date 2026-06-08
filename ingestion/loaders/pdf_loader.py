import pdfplumber
from typing import Dict, List


class PDFLoader:

    def load_pages(self, file_path: str) -> List[Dict]:
        """
        Extract text page by page.
        Returns: [{"page": 1, "text": "..."}, ...]
        """
        pages = []

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    pages.append({"page": page_num, "text": page_text})

        return pages

    def load(self, file_path: str) -> str:
        """Extracts all page text as a single string."""
        return "\n\n".join(p["text"] for p in self.load_pages(file_path))
