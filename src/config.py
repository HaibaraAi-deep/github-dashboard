import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR: Path = Path(__file__).resolve().parent.parent

GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
GITHUB_USERNAME: str = os.getenv("GITHUB_USERNAME", "")

GITHUB_API_BASE: str = "https://api.github.com"
GITHUB_GRAPHQL_URL: str = "https://api.github.com/graphql"

OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", str(BASE_DIR / "output")))
CACHE_DIR: Path = Path(os.getenv("CACHE_DIR", str(BASE_DIR / ".cache")))
CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))
MAX_CACHE_ENTRIES: int = int(os.getenv("MAX_CACHE_ENTRIES", "1000"))

GITHUB_USERNAME_PATTERN: re.Pattern = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$")

DEFAULT_TOP_N: int = 10
DEFAULT_THEME: str = "dark"
DEFAULT_NO_FORKS: bool = False

FLASK_SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "")
FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() in ("true", "1", "yes")

GITHUB_USERNAME_PATTERN: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$")

MAX_CACHE_ENTRIES: int = int(os.getenv("MAX_CACHE_ENTRIES", "1000"))

_COLORS_PATH = Path(__file__).resolve().parent / "data" / "github_colors.json"
with open(_COLORS_PATH, "r", encoding="utf-8") as _f:
    GITHUB_COLORS: dict[str, str] = json.load(_f)

THEMES: dict[str, dict[str, str | list[str]]] = {
    "dark": {
        "background": "#0d1117",
        "text": "#c9d1d9",
        "text_secondary": "#8b949e",
        "border": "#30363d",
        "accent": "#58a6ff",
        "heatmap_levels": ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
        "card_bg": "#161b22",
    },
    "light": {
        "background": "#ffffff",
        "text": "#24292f",
        "text_secondary": "#57606a",
        "border": "#d0d7de",
        "accent": "#0969da",
        "heatmap_levels": ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
        "card_bg": "#f6f8fa",
    },
}
