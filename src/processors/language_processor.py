import logging

from src.config import DEFAULT_TOP_N, GITHUB_COLORS
from src.types import LanguageResult

logger = logging.getLogger(__name__)


class LanguageProcessor:
    def process(self, languages_data: dict | None, top_n: int = DEFAULT_TOP_N) -> LanguageResult:
        if not languages_data:
            return {
                "languages": [],
                "total_bytes": 0,
                "top_n": top_n,
            }

        total_bytes = sum(languages_data.values())
        if total_bytes == 0:
            return {
                "languages": [],
                "total_bytes": 0,
                "top_n": top_n,
            }

        sorted_languages = sorted(languages_data.items(), key=lambda x: x[1], reverse=True)

        top_languages = sorted_languages[:top_n]
        other_bytes = sum(bytes_count for _, bytes_count in sorted_languages[top_n:])

        result = []
        for lang, bytes_count in top_languages:
            percentage = round(bytes_count / total_bytes * 100, 2)
            result.append({
                "name": lang,
                "bytes": bytes_count,
                "percentage": percentage,
                "color": GITHUB_COLORS.get(lang, "#8b949e"),
            })

        if other_bytes > 0:
            other_percentage = round(other_bytes / total_bytes * 100, 2)
            result.append({
                "name": "Other",
                "bytes": other_bytes,
                "percentage": other_percentage,
                "color": "#8b949e",
            })

        return {
            "languages": result,
            "total_bytes": total_bytes,
            "total_language_count": len(languages_data),
            "top_n": top_n,
        }
