import logging
from pathlib import Path

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
