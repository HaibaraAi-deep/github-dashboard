import math

import logging

import svgwrite

from src.renderers.base_renderer import BaseRenderer

logger = logging.getLogger(__name__)


class LanguageChartRenderer(BaseRenderer):
    def _create_drawing(self, language_data: dict):
        languages = language_data.get("languages", [])
        total_language_count = language_data.get("total_language_count", 0)

        if not languages:
            logger.warning("No language data for chart")
            return None

        card_width = 800
        chart_height = 300
        legend_height = max(len(languages) * 22 + 30, 100)
        card_height = chart_height + legend_height + 40

        dwg = svgwrite.Drawing(
            size=(f"{card_width}px", f"{card_height}px"),
        )

        bg_color = self._get_color("card_bg")
        text_color = self._get_color("text")
        text_secondary = self._get_color("text_secondary")
        border_color = self._get_color("border")

        dwg.add(dwg.rect(
            insert=(0, 0),
            size=(card_width, card_height),
            rx=self.card_radius,
            fill=bg_color,
            stroke=border_color,
            stroke_width=1,
        ))

        cx = 200
        cy = chart_height // 2 + 20
        outer_r = 110
        inner_r = 66

        total_pct = sum(lang["percentage"] for lang in languages)
        start_angle = -90

        for lang in languages:
            pct = lang["percentage"]
            if total_pct > 0:
                sweep = (pct / total_pct) * 360
            else:
                sweep = 0

            if sweep < 0.5:
                start_angle += sweep
                continue

            end_angle = start_angle + sweep

            x1_outer = cx + outer_r * math.cos(math.radians(start_angle))
            y1_outer = cy + outer_r * math.sin(math.radians(start_angle))
            x2_outer = cx + outer_r * math.cos(math.radians(end_angle))
            y2_outer = cy + outer_r * math.sin(math.radians(end_angle))
            x1_inner = cx + inner_r * math.cos(math.radians(end_angle))
            y1_inner = cy + inner_r * math.sin(math.radians(end_angle))
            x2_inner = cx + inner_r * math.cos(math.radians(start_angle))
            y2_inner = cy + inner_r * math.sin(math.radians(start_angle))

            large_arc = 1 if sweep > 180 else 0

            path_d = (
                f"M {x1_outer},{y1_outer} "
                f"A {outer_r},{outer_r} 0 {large_arc},1 {x2_outer},{y2_outer} "
                f"L {x1_inner},{y1_inner} "
                f"A {inner_r},{inner_r} 0 {large_arc},0 {x2_inner},{y2_inner} "
                f"Z"
            )

            dwg.add(dwg.path(
                d=path_d,
                fill=lang["color"],
                stroke=bg_color,
                stroke_width=2,
            ))

            if pct >= 5:
                mid_angle = math.radians(start_angle + sweep / 2)
                label_r = (outer_r + inner_r) / 2
                lx = cx + label_r * math.cos(mid_angle)
                ly = cy + label_r * math.sin(mid_angle)
                dwg.add(dwg.text(
                    f"{pct:.0f}%",
                    insert=(lx, ly),
                    fill="white",
                    font_size="10px",
                    font_family=self.font_family,
                    font_weight="bold",
                    text_anchor="middle",
                    dominant_baseline="central",
                ))

            start_angle = end_angle

        dwg.add(dwg.text(
            str(total_language_count),
            insert=(cx, cy - 8),
            fill=text_color,
            font_size="22px",
            font_family=self.font_family,
            font_weight="bold",
            text_anchor="middle",
        ))
        dwg.add(dwg.text(
            "Languages",
            insert=(cx, cy + 14),
            fill=text_secondary,
            font_size="11px",
            font_family=self.font_family,
            text_anchor="middle",
        ))

        legend_x = 370
        legend_y = 30

        dwg.add(dwg.text(
            "Languages",
            insert=(legend_x, legend_y),
            fill=text_color,
            font_size="13px",
            font_family=self.font_family,
            font_weight="bold",
        ))

        for i, lang in enumerate(languages):
            ly = legend_y + 22 + i * 22

            dwg.add(dwg.rect(
                insert=(legend_x, ly - 8),
                size=(12, 12),
                rx=2,
                fill=lang["color"],
            ))

            name = lang["name"]
            if len(name) > 18:
                name = name[:16] + ".."

            dwg.add(dwg.text(
                f"{name}  {lang['percentage']}%",
                insert=(legend_x + 18, ly + 2),
                fill=text_secondary,
                font_size="12px",
                font_family=self.font_family,
            ))

        return dwg

    def render(self, language_data: dict) -> str | None:
        dwg = self._create_drawing(language_data)
        if not dwg:
            return None

        filepath = self._get_filepath("languages.svg")
        dwg.filename = str(filepath)
        dwg.save()
        logger.info(f"Language chart saved to {filepath}")
        return str(filepath)

    def _render_to_string(self, language_data: dict) -> str:
        dwg = self._create_drawing(language_data)
        if not dwg:
            return ""
        return dwg.tostring()
