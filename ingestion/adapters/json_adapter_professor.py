from typing import List, Dict, Any, Optional
from ingestion.adapters.base_adapter import BaseAdapter


class ProfessorJSONAdapter(BaseAdapter):

    def transform(self, raw_data: Any) -> List[Dict]:
        """
        Converts professor JSON data into standardized documents.
        Expected input: list of professor dicts

        Emits one summary document per professor plus one document per review.
        """
        documents = []

        for prof in raw_data:
            documents.append(
                self.build_document(
                    self._build_summary_text(prof),
                    self._build_summary_metadata(prof),
                )
            )

            for review_index, review in enumerate(prof.get("reviews") or []):
                documents.append(
                    self.build_document(
                        self._build_review_text(prof, review),
                        self._build_review_metadata(prof, review, review_index),
                    )
                )

        return documents

    def _build_summary_text(self, prof: Dict) -> str:
        """Professor-level overview for aggregate rating/difficulty questions."""
        lines = []
        self._append_line(lines, "Professor", prof.get("professorName"))
        self._append_line(lines, "Department", prof.get("department"))
        self._append_line(lines, "School", prof.get("schoolName"))
        self._append_line(lines, "Overall Rating", prof.get("overallQualityRating"))
        self._append_line(lines, "Difficulty", prof.get("levelOfDifficulty"))
        self._append_line(lines, "Would Take Again", prof.get("wouldTakeAgainPercentage"))
        self._append_line(lines, "Number of Ratings", prof.get("numberOfRatings"))
        self._append_line(lines, "Description", prof.get("description"))

        distribution = prof.get("ratingDistribution") or []
        if distribution:
            breakdown = ", ".join(
                f"{entry.get('label')}: {entry.get('count')}"
                for entry in distribution
            )
            self._append_line(lines, "Rating Breakdown", breakdown)

        return "\n".join(lines)

    def _build_review_text(self, prof: Dict, review: Dict) -> str:
        """Single student review — the main source for experience-based questions."""
        lines = []
        self._append_line(lines, "Professor", prof.get("professorName"))
        self._append_line(lines, "Course", review.get("course"))
        self._append_line(lines, "Review Date", review.get("date"))
        self._append_line(lines, "Quality Rating", review.get("qualityRating"))
        self._append_line(lines, "Difficulty Rating", review.get("difficultyRating"))
        self._append_line(lines, "Would Take Again", review.get("wouldTakeAgain"))
        self._append_line(lines, "Grade Received", review.get("grade"))
        self._append_line(lines, "Attendance", review.get("attendance"))
        self._append_line(lines, "Textbook Required", review.get("textbook"))
        self._append_line(lines, "Tags", self._format_tags(review.get("tags")))
        self._append_line(lines, "Student Review", review.get("comment"))

        return "\n".join(lines)

    def _append_line(self, lines: List[str], label: str, value: Any) -> None:
        if value is not None:
            lines.append(f"{label}: {value}")

    def _build_summary_metadata(self, prof: Dict) -> Dict:
        return {
            "type": "professor_summary",
            "source": "rate_my_professors",
            "professorId": prof.get("professorId"),
            "name": prof.get("professorName"),
            "department": prof.get("department"),
            "school": prof.get("schoolName"),
            "rating": self._safe_float(prof.get("overallQualityRating")),
            "difficulty": self._safe_float(prof.get("levelOfDifficulty")),
            "wouldTakeAgain": prof.get("wouldTakeAgainPercentage"),
            "numRatings": prof.get("numberOfRatings"),
        }

    def _build_review_metadata(
        self, prof: Dict, review: Dict, review_index: int
    ) -> Dict:
        return {
            "type": "professor_review",
            "source": "rate_my_professors",
            "professorId": prof.get("professorId"),
            "name": prof.get("professorName"),
            "department": prof.get("department"),
            "course": review.get("course"),
            "reviewDate": review.get("date"),
            "qualityRating": self._safe_float(review.get("qualityRating")),
            "difficultyRating": self._safe_float(review.get("difficultyRating")),
            "wouldTakeAgain": review.get("wouldTakeAgain"),
            "grade": review.get("grade"),
            "tags": self._format_tags(review.get("tags")),
            "reviewIndex": review_index,
        }

    def _format_tags(self, tags: Any) -> Optional[str]:
        if not tags:
            return None
        if isinstance(tags, list):
            return ", ".join(str(tag) for tag in tags)
        return str(tags)

    def _safe_float(self, value):
        """Converts strings like "4.2" safely into float."""
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
