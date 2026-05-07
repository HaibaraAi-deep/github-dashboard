import logging

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from src.renderers.base_renderer import BaseRenderer

logger = logging.getLogger(__name__)


class LanguageChartRenderer(BaseRenderer):
    def _create_figure(self, language_data: dict):
        languages = language_data.get("languages", [])
        total_language_count = language_data.get("total_language_count", 0)

        if not languages:
            logger.warning("No language data for chart")
            return None

        fig, ax = plt.subplots(figsize=(8, 5))

        sizes = [lang["percentage"] for lang in languages]
        colors = [lang["color"] for lang in languages]

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=None,
            colors=colors,
            autopct=lambda pct: f"{pct:.1f}%" if pct >= 3 else "",
            startangle=90,
            pctdistance=0.82,
            wedgeprops=dict(width=0.4, edgecolor=self._get_color("card_bg"), linewidth=2),
        )

        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_color("white")
            autotext.set_fontweight("bold")

        center_text = f"{total_language_count}\nLanguages"
        ax.text(0, 0, center_text, ha="center", va="center",
                fontsize=14, fontweight="bold", color=self._get_color("text"))

        legend_labels = [f"{lang['name']} ({lang['percentage']}%)" for lang in languages]
        ax.legend(
            wedges, legend_labels,
            title="Languages",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=9,
            title_fontsize=10,
        )

        fig.patch.set_alpha(0)
        ax.set_facecolor("none")

        return fig

    def render(self, language_data: dict) -> str | None:
        fig = self._create_figure(language_data)
        if not fig:
            return None

        filepath = self._save_matplotlib_to_file(fig, "languages.svg")
        logger.info(f"Language chart saved to {filepath}")
        return filepath

    def _render_to_string(self, language_data: dict) -> str:
        fig = self._create_figure(language_data)
        if not fig:
            return ""

        return self._render_matplotlib_to_string(fig)
