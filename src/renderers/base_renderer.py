import io
import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from src.config import OUTPUT_DIR, THEMES, DEFAULT_THEME

logger = logging.getLogger(__name__)


class BaseRenderer:
    def __init__(self, output_dir: str | None = None, theme: str = DEFAULT_THEME) -> None:
        self.output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.theme_name = theme
        self.theme = THEMES.get(theme, THEMES[DEFAULT_THEME])

    def _get_color(self, key: str) -> str:
        return self.theme.get(key, "")

    @property
    def font_family(self) -> str:
        return "-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif"

    @property
    def card_radius(self) -> int:
        return 12

    @property
    def width(self) -> int:
        return 800

    def _get_filepath(self, filename: str) -> Path:
        return self.output_dir / filename

    def _render_matplotlib_to_string(self, fig) -> str:
        try:
            buf = io.BytesIO()
            fig.savefig(buf, format="svg", bbox_inches="tight", transparent=True, dpi=150, pad_inches=0.1)
            return buf.getvalue().decode("utf-8")
        finally:
            plt.close(fig)

    def _save_matplotlib_to_file(self, fig, filename: str) -> str:
        try:
            filepath = self._get_filepath(filename)
            fig.savefig(str(filepath), format="svg", bbox_inches="tight", transparent=True, dpi=150, pad_inches=0.1)
            return str(filepath)
        finally:
            plt.close(fig)
