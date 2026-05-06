import logging
from datetime import datetime

import svgwrite

from src.renderers.base_renderer import BaseRenderer

logger = logging.getLogger(__name__)


class HeatmapRenderer(BaseRenderer):
    def _create_drawing(self, contribution_data, year=None):
        weeks = contribution_data.get("weeks", [])
        total = contribution_data.get("totalContributions", 0)

        if not weeks:
            logger.warning("No contribution data for heatmap")
            return None

        cell_size = 12
        cell_gap = 2
        cell_step = cell_size + cell_gap
        left_margin = 40
        top_margin = 30
        bottom_margin = 20
        right_margin = 20

        num_weeks = len(weeks)
        svg_width = left_margin + num_weeks * cell_step + right_margin
        svg_height = top_margin + 7 * cell_step + bottom_margin

        dwg = svgwrite.Drawing(
            size=(f"{svg_width}px", f"{svg_height}px"),
        )

        bg_color = self._get_color("card_bg")
        text_color = self._get_color("text")
        text_secondary = self._get_color("text_secondary")
        heatmap_levels = self._get_color("heatmap_levels")

        dwg.add(dwg.rect(
            insert=(0, 0),
            size=(svg_width, svg_height),
            rx=self.card_radius,
            fill=bg_color,
        ))

        year_label = str(year) if year else ""
        if weeks and weeks[0].get("contributionDays"):
            first_date = weeks[0]["contributionDays"][0].get("date", "")
            if first_date:
                year_label = first_date[:4]

        title_text = f"{year_label}: {total} contributions" if year_label else f"{total} contributions"
        dwg.add(dwg.text(
            title_text,
            insert=(left_margin, top_margin - 10),
            fill=text_color,
            font_size="14px",
            font_family=self.font_family,
            font_weight="bold",
        ))

        weekday_labels = ["", "Mon", "", "Wed", "", "Fri", ""]
        for i, label in enumerate(weekday_labels):
            if label:
                dwg.add(dwg.text(
                    label,
                    insert=(left_margin - 5, top_margin + i * cell_step + cell_size),
                    fill=text_secondary,
                    font_size="10px",
                    font_family=self.font_family,
                    text_anchor="end",
                    dominant_baseline="central",
                ))

        month_positions = {}
        for week_idx, week in enumerate(weeks):
            days = week.get("contributionDays", [])
            for day in days:
                count = day.get("contributionCount", 0)
                weekday = day.get("weekday", 0)
                date_str = day.get("date", "")

                if count == 0:
                    level = 0
                elif count <= 4:
                    level = 1
                elif count <= 9:
                    level = 2
                elif count <= 19:
                    level = 3
                else:
                    level = 4

                x = left_margin + week_idx * cell_step
                y = top_margin + weekday * cell_step

                dwg.add(dwg.rect(
                    insert=(x, y),
                    size=(cell_size, cell_size),
                    rx=2, ry=2,
                    fill=heatmap_levels[level],
                ))

                if date_str:
                    month = date_str[:7]
                    if month not in month_positions:
                        month_positions[month] = x

        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        sorted_months = sorted(month_positions.keys())
        prev_month_label = ""
        for month_key in sorted_months:
            month_num = int(month_key.split("-")[1]) - 1
            month_label = month_names[month_num]
            if month_label != prev_month_label:
                dwg.add(dwg.text(
                    month_label,
                    insert=(month_positions[month_key], top_margin - 2),
                    fill=text_secondary,
                    font_size="10px",
                    font_family=self.font_family,
                ))
                prev_month_label = month_label

        return dwg

    def render(self, contribution_data, year=None):
        dwg = self._create_drawing(contribution_data, year)
        if not dwg:
            return None

        filepath = self._get_filepath("heatmap.svg")
        dwg.filename = str(filepath)
        dwg.save()
        logger.info(f"Heatmap saved to {filepath}")
        return str(filepath)

    def _render_to_string(self, contribution_data, year=None):
        dwg = self._create_drawing(contribution_data, year)
        if not dwg:
            return ""
        return dwg.tostring()
