from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseAdapter(ABC):

    @abstractmethod
    def transform(self, raw_data: Any) -> List[Dict]:
        """
        Convert raw input into standardized documents.
        Must return a list of:
        {
            "text": str,
            "metadata": dict
        }
        """
        pass

    def build_document(self, text: str, metadata: Dict) -> Dict:
        """
        Shared helper to enforce consistent output format.
        Strips None values from metadata (required for ChromaDB).
        """
        return {
            "text": text,
            "metadata": {k: v for k, v in metadata.items() if v is not None},
        }
