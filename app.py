import logging
import os
from pathlib import Path
from datetime import datetime, timezone

from flask import Flask, render_template, request, jsonify, session

from src.config import THEMES, DEFAULT_TOP_N, DEFAULT_NO_FORKS
from src.collectors.rest_collector import RESTCollector
from src.collectors.graphql_collector import GraphQLCollector
from src.processors.user_processor import UserProcessor
from src.processors.repo_processor import RepoProcessor
from src.processors.language_processor import LanguageProcessor
from src.processors.contribution_processor import ContributionProcessor
from src.renderers.base_renderer import BaseRenderer
from src.renderers.heatmap import HeatmapRenderer
from src.renderers.language_chart import LanguageChartRenderer
from src.renderers.activity_chart import ActivityChartRenderer
from src.renderers.repo_ranking import RepoRankingRenderer
from src.renderers.profile_card import ProfileCardRenderer

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "github-dashboard-dev-secret-key")

BASE_DIR = Path(__file__).resolve().parent


def _get_date_range(year=None):
    if year:
        from_date = f"{year}-01-01T00:00:00Z"
        to_date = f"{year}-12-31T23:59:59Z"
    else:
        now = datetime.now(timezone.utc)
        from_date = f"{now.year}-01-01T00:00:00Z"
        to_date = now.strftime("%Y-%m-%dT23:59:59Z")
    return from_date, to_date


def _collect_all(username, token, no_forks, year=None):
    rest = RESTCollector(token=token)
    graphql = GraphQLCollector(token=token)

    user_data = rest.get_user(username)
    repos_data = rest.get_repos(username)
    languages_data = rest.get_all_languages(username, no_forks=no_forks)

    from_date, to_date = _get_date_range(year)
    calendar_data = graphql.get_contribution_calendar(username, from_date, to_date)

    return {
        "user": user_data,
        "repos": repos_data,
        "languages": languages_data,
        "calendar": calendar_data
    }


def _process_all(raw_data, no_forks, top_n):
    user_proc = UserProcessor()
    repo_proc = RepoProcessor()
    lang_proc = LanguageProcessor()
    contrib_proc = ContributionProcessor()

    user_result = user_proc.process(raw_data["user"])
    repo_result = repo_proc.process(raw_data["repos"], no_forks=no_forks, top_n=top_n)
    lang_result = lang_proc.process(raw_data["languages"], top_n=top_n)
    contrib_result = contrib_proc.process(raw_data["calendar"])

    user_result["total_stars"] = repo_result["total_stars"]

    return {
        "user": user_result,
        "repos": repo_result,
        "languages": lang_result,
        "contributions": contrib_result
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    try:
        username = request.form.get("username")
        token = request.form.get("token", "")
        no_forks = request.form.get("no_forks", False)
        theme = request.form.get("theme", "dark")
        year = request.form.get("year", None)
        if year:
            year = int(year)

        if not username:
            return jsonify({"error": "请输入 GitHub 用户名"}), 400

        raw_data = _collect_all(username, token, no_forks, year)
        processed = _process_all(raw_data, no_forks, DEFAULT_TOP_N)

        heatmap_render = HeatmapRenderer(theme=theme)
        languages_render = LanguageChartRenderer(theme=theme)
        activity_render = ActivityChartRenderer(theme=theme)
        repo_render = RepoRankingRenderer(theme=theme)
        profile_render = ProfileCardRenderer(theme=theme)

        svg_result = {
            "heatmap": heatmap_render._render_to_string(processed["contributions"], year),
            "languages": languages_render._render_to_string(processed["languages"]),
            "activity": activity_render._render_to_string(processed["contributions"]),
            "repo": repo_render._render_to_string(processed["repos"]),
            "profile": profile_render._render_to_string(processed["user"], contribution_data=processed["contributions"])
        }

        return jsonify(svg_result)
    except Exception as e:
        logging.exception("Error generating dashboard")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
