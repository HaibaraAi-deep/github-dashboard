import logging
import io
from datetime import datetime

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from src.renderers.base_renderer import BaseRenderer

logger = logging.getLogger(__name__)


class ActivityChartRenderer(BaseRenderer):
    def _create_figure(self, contribution_data):
        weekly_trend = contribution_data.get("weekly_trend", [])

        if not weekly_trend:
            logger.warning("No activity data for chart")
            return None

        dates = []
        counts = []
        for item in weekly_trend:
            date_str = item.get("date", "")
            if date_str:
                try:
                    dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
                    counts.append(item.get("count", 0))
                except ValueError:
                    continue

        if not dates:
            logger.warning("No valid dates in activity data")
            return None

        fig, ax = plt.subplots(figsize=(8, 4))

        accent = self._get_color("accent")
        text_color = self._get_color("text")
        text_secondary = self._get_color("text_secondary")

        ax.fill_between(dates, counts, alpha=0.3, color=accent)
        ax.plot(dates, counts, color=accent, linewidth=1.5)

        if counts:
            max_count = max(counts)
            max_idx = counts.index(max_count)
            ax.annotate(
                f"{max_count}",
                xy=(dates[max_idx], max_count),
                xytext=(0, 10),
                textcoords="offset points",
                ha="center",
                fontsize=9,
                fontweight="bold",
                color=text_color,
                arrowprops=dict(arrowstyle="->", color=text_secondary, lw=0.8),
            )

        ax.set_xlabel("Date", fontsize=10, color=text_secondary)
        ax.set_ylabel("Contributions", fontsize=10, color=text_secondary)
        ax.tick_params(colors=text_secondary, labelsize=8)

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        fig.autofmt_xdate(rotation=45, ha="right")

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.set_facecolor("none")
        fig.patch.set_alpha(0)
        ax.grid(axis="y", alpha=0.2, color=text_secondary)

        return fig

    def render(self, contribution_data):
        fig = self._create_figure(contribution_data)
        if not fig:
            return None

        filepath = self._get_filepath("activity.svg")
        fig.savefig(
            str(filepath),
            format="svg",
            bbox_inches="tight",
            transparent=True,
            dpi=150,
            pad_inches=0.1,
        )
        plt.close(fig)

        logger.info(f"Activity chart saved to {filepath}")
        return str(filepath)

    def _render_to_string(self, contribution_data):
        fig = self._create_figure(contribution_data)
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
