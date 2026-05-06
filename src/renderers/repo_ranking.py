import logging
import io

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from src.config import GITHUB_COLORS
from src.renderers.base_renderer import BaseRenderer

logger = logging.getLogger(__name__)


class RepoRankingRenderer(BaseRenderer):
    def _create_figure(self, repo_data, top_n=5):
        top_repos = repo_data.get("top_by_stars", [])[:top_n]

        if not top_repos:
            logger.warning("No repo data for ranking chart")
            return None

        fig, ax = plt.subplots(figsize=(8, len(top_repos) * 0.8 + 1))

        text_color = self._get_color("text")
        text_secondary = self._get_color("text_secondary")
        accent = self._get_color("accent")

        names = [r["name"] for r in reversed(top_repos)]
        stars = [r["stars"] for r in reversed(top_repos)]
        languages = [r.get("language", "") for r in reversed(top_repos)]

        bar_colors = [GITHUB_COLORS.get(lang, accent) for lang in languages]

        bars = ax.barh(names, stars, color=bar_colors, height=0.6, edgecolor="none")

        for bar, star_count in zip(bars, stars):
            width = bar.get_width()
            ax.text(
                width + max(stars) * 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"★ {star_count}",
                va="center",
                fontsize=9,
                color=text_color,
            )

        for i, lang in enumerate(languages):
            if lang:
                ax.text(
                    max(stars) * 0.02,
                    i,
                    lang,
                    va="center",
                    fontsize=8,
                    color="white",
                    fontweight="bold",
                )

        ax.set_xlabel("Stars", fontsize=10, color=text_secondary)
        ax.tick_params(colors=text_secondary, labelsize=9)

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.set_facecolor("none")
        fig.patch.set_alpha(0)
        ax.grid(axis="x", alpha=0.2, color=text_secondary)

        return fig

    def render(self, repo_data, top_n=5):
        fig = self._create_figure(repo_data, top_n)
        if not fig:
            return None

        filepath = self._get_filepath("repo-ranking.svg")
        fig.savefig(
            str(filepath),
            format="svg",
            bbox_inches="tight",
            transparent=True,
            dpi=150,
            pad_inches=0.1,
        )
        plt.close(fig)

        logger.info(f"Repo ranking chart saved to {filepath}")
        return str(filepath)

    def _render_to_string(self, repo_data, top_n=5):
        fig = self._create_figure(repo_data, top_n)
        if not fig:
            return ""

        svg_buffer = io.BytesIO()
        fig.savefig(
            svg_buffer,
            format="svg",
            bbox_inches="tight",
            transparent=True,
            dpi=150,
            pad_inches=0.1,
        )
        plt.close(fig)

        return svg_buffer.getvalue().decode("utf-8")
