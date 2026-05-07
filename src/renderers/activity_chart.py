import logging

import svgwrite

from src.renderers.base_renderer import BaseRenderer

logger = logging.getLogger(__name__)


class ActivityChartRenderer(BaseRenderer):
    def _create_drawing(self, contribution_data: dict):
        weekly_trend = contribution_data.get("weekly_trend", [])

        if not weekly_trend:
            logger.warning("No activity data for chart")
            return None

        valid_items = []
        for item in weekly_trend:
            date_str = item.get("date", "")
            count = item.get("count", 0)
            if date_str:
                valid_items.append((date_str, count))

        if not valid_items:
            logger.warning("No valid dates in activity data")
            return None

        card_width = 800
        chart_left = 50
        chart_right = card_width - 30
        chart_top = 30
        chart_bottom = 220
        card_height = 260

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

        max_count = max(c for _, c in valid_items) if valid_items else 1
        if max_count == 0:
            max_count = 1

        chart_width = chart_right - chart_left
        chart_height_px = chart_bottom - chart_top

        for i in range(5):
            y = chart_bottom - (i / 4) * chart_height_px
            val = int((i / 4) * max_count)
            dwg.add(dwg.line(
                start=(chart_left, y),
                end=(chart_right, y),
                stroke=text_secondary,
                stroke_opacity=0.15,
                stroke_width=1,
            ))
            dwg.add(dwg.text(
                str(val),
                insert=(chart_left - 8, y + 4),
                fill=text_secondary,
                font_size="9px",
                font_family=self.font_family,
                text_anchor="end",
            ))

        n = len(valid_items)
        points = []
        for idx, (date_str, count) in enumerate(valid_items):
            x = chart_left + (idx / max(n - 1, 1)) * chart_width
            y = chart_bottom - (count / max_count) * chart_height_px
            points.append((x, y))

        if len(points) >= 2:
            area_path = f"M {points[0][0]},{chart_bottom} "
            for px, py in points:
                area_path += f"L {px},{py} "
            area_path += f"L {points[-1][0]},{chart_bottom} Z"

            dwg.add(dwg.path(
                d=area_path,
                fill=accent,
                fill_opacity=0.2,
            ))

            line_path = f"M {points[0][0]},{points[0][1]} "
            for px, py in points[1:]:
                line_path += f"L {px},{py} "

            dwg.add(dwg.path(
                d=line_path,
                fill="none",
                stroke=accent,
                stroke_width=2,
            ))

        if points:
            max_idx = max(range(len(valid_items)), key=lambda i: valid_items[i][1])
            mx, my = points[max_idx]

            dwg.add(dwg.circle(
                center=(mx, my),
                r=4,
                fill=accent,
            ))

            dwg.add(dwg.text(
                str(valid_items[max_idx][1]),
                insert=(mx, my - 12),
                fill=text_color,
                font_size="10px",
                font_family=self.font_family,
                font_weight="bold",
                text_anchor="middle",
            ))

        label_count = min(n, 8)
        step = max(n // label_count, 1)
        for idx in range(0, n, step):
            x = chart_left + (idx / max(n - 1, 1)) * chart_width
            date_str = valid_items[idx][0]
            label = date_str[5:]
            dwg.add(dwg.text(
                label,
                insert=(x, chart_bottom + 16),
                fill=text_secondary,
                font_size="9px",
                font_family=self.font_family,
                text_anchor="middle",
                transform=f"rotate(-30, {x}, {chart_bottom + 16})",
            ))

        return dwg

    def render(self, contribution_data: dict) -> str | None:
        dwg = self._create_drawing(contribution_data)
        if not dwg:
            return None

        filepath = self._get_filepath("activity.svg")
        dwg.filename = str(filepath)
        dwg.save()
        logger.info(f"Activity chart saved to {filepath}")
        return str(filepath)

    def _render_to_string(self, contribution_data: dict) -> str:
        dwg = self._create_drawing(contribution_data)
        if not dwg:
            return ""
        return dwg.tostring()
