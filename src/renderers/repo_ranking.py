import logging

import svgwrite

from src.config import GITHUB_COLORS
from src.renderers.base_renderer import BaseRenderer

logger = logging.getLogger(__name__)


class RepoRankingRenderer(BaseRenderer):
    def _create_drawing(self, repo_data: dict, top_n: int = 5):
        top_repos = repo_data.get("top_by_stars", [])[:top_n]

        if not top_repos:
            logger.warning("No repo data for ranking chart")
            return None

        card_width = 800
        bar_height = 36
        bar_gap = 8
        padding = 24
        chart_left = 140
        chart_right = card_width - 80
        card_height = padding * 2 + len(top_repos) * (bar_height + bar_gap)

        dwg = svgwrite.Drawing(
            size=(f"{card_width}px", f"{card_height}px"),
        )

        bg_color = self._get_color("card_bg")
        text_color = self._get_color("text")
        text_secondary = self._get_color("text_secondary")
        accent = self._get_color("accent")
        border_color = self._get_color("border")

        dwg.add(dwg.rect(
            insert=(0, 0),
            size=(card_width, card_height),
            rx=self.card_radius,
            fill=bg_color,
            stroke=border_color,
            stroke_width=1,
        ))

        max_stars = max(r["stars"] for r in top_repos) if top_repos else 1
        if max_stars == 0:
            max_stars = 1

        bar_width = chart_right - chart_left

        for i, repo in enumerate(reversed(top_repos)):
            y = padding + i * (bar_height + bar_gap)
            name = repo.get("name", "")
            stars = repo.get("stars", 0)
            lang = repo.get("language", "")

            dwg.add(dwg.text(
                name[:20],
                insert=(padding, y + bar_height / 2 + 4),
                fill=text_color,
                font_size="12px",
                font_family=self.font_family,
                font_weight="600",
                text_anchor="start",
            ))

            bar_fill_width = (stars / max_stars) * bar_width
            bar_color = GITHUB_COLORS.get(lang, accent)

            dwg.add(dwg.rect(
                insert=(chart_left, y + 4),
                size=(bar_fill_width, bar_height - 8),
                rx=4,
                fill=bar_color,
                fill_opacity=0.85,
            ))

            if lang and bar_fill_width > 40:
                dwg.add(dwg.text(
                    lang,
                    insert=(chart_left + 10, y + bar_height / 2 + 3),
                    fill="white",
                    font_size="10px",
                    font_family=self.font_family,
                    font_weight="bold",
                ))

            dwg.add(dwg.text(
                f"★ {stars}",
                insert=(chart_right + 8, y + bar_height / 2 + 4),
                fill=text_secondary,
                font_size="11px",
                font_family=self.font_family,
            ))

        return dwg

    def render(self, repo_data: dict, top_n: int = 5) -> str | None:
        dwg = self._create_drawing(repo_data, top_n)
        if not dwg:
            return None

        filepath = self._get_filepath("repo-ranking.svg")
        dwg.filename = str(filepath)
        dwg.save()
        logger.info(f"Repo ranking chart saved to {filepath}")
        return str(filepath)

    def _render_to_string(self, repo_data: dict, top_n: int = 5) -> str:
        dwg = self._create_drawing(repo_data, top_n)
        if not dwg:
            return ""
        return dwg.tostring()
