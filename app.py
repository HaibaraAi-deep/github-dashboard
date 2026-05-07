import logging
import os
import re
from pathlib import Path

from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from src.config import DEFAULT_TOP_N, FLASK_SECRET_KEY, FLASK_DEBUG, GITHUB_USERNAME_PATTERN
from src.pipeline import collect_all, process_all
from src.renderers.heatmap import HeatmapRenderer
from src.renderers.language_chart import LanguageChartRenderer
from src.renderers.activity_chart import ActivityChartRenderer
from src.renderers.repo_ranking import RepoRankingRenderer
from src.renderers.profile_card import ProfileCardRenderer
from src.exceptions import DashboardError, ValidationError

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY or os.urandom(24)

BASE_DIR = Path(__file__).resolve().parent

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
)

SVG_SCRIPT_PATTERN = re.compile(r"<script[^>]*>.*?</script>", re.DOTALL | re.IGNORECASE)
SVG_EVENT_PATTERN = re.compile(r'\s+on\w+\s*=', re.IGNORECASE)


def _sanitize_svg(svg_string: str) -> str:
    cleaned = SVG_SCRIPT_PATTERN.sub("", svg_string)
    cleaned = SVG_EVENT_PATTERN.sub("", cleaned)
    return cleaned


def _validate_username(username: str) -> str:
    username = username.strip()
    if not username:
        raise ValidationError("请输入 GitHub 用户名")
    if not GITHUB_USERNAME_PATTERN.match(username):
        raise ValidationError("用户名格式无效")
    return username


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
@limiter.limit("10 per minute")
def generate():
    try:
        username = _validate_username(request.form.get("username", ""))
        token = request.form.get("token", "")
        no_forks = request.form.get("no_forks", False)
        theme = request.form.get("theme", "dark")
        year = request.form.get("year", None)
        if year:
            year = int(year)

        raw_data = collect_all(username, token, no_forks, year)
        processed = process_all(raw_data, no_forks, DEFAULT_TOP_N)

        heatmap_render = HeatmapRenderer(theme=theme)
        languages_render = LanguageChartRenderer(theme=theme)
        activity_render = ActivityChartRenderer(theme=theme)
        repo_render = RepoRankingRenderer(theme=theme)
        profile_render = ProfileCardRenderer(theme=theme)

        svg_result = {
            "heatmap": _sanitize_svg(heatmap_render._render_to_string(processed["contributions"], year)),
            "languages": _sanitize_svg(languages_render._render_to_string(processed["languages"])),
            "activity": _sanitize_svg(activity_render._render_to_string(processed["contributions"])),
            "repo": _sanitize_svg(repo_render._render_to_string(processed["repos"])),
            "profile": _sanitize_svg(profile_render._render_to_string(processed["user"], contribution_data=processed["contributions"])),
        }

        return jsonify(svg_result)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except DashboardError as e:
        logging.error(f"Dashboard error: {e}")
        return jsonify({"error": "数据获取失败，请稍后重试"}), 500
    except Exception:
        logging.exception("Unexpected error generating dashboard")
        return jsonify({"error": "服务内部错误，请稍后重试"}), 500


if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG, host="0.0.0.0", port=5000)
