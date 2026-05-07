import logging
import sys
from pathlib import Path
from typing import Any

import click

from src.config import (
    GITHUB_TOKEN,
    GITHUB_USERNAME,
    OUTPUT_DIR,
    DEFAULT_TOP_N,
    DEFAULT_THEME,
    DEFAULT_NO_FORKS,
    CACHE_TTL,
)
from src.pipeline import collect_all, process_all, get_date_range
from src.collectors.rest_collector import RESTCollector
from src.collectors.graphql_collector import GraphQLCollector
from src.processors.repo_processor import RepoProcessor
from src.processors.language_processor import LanguageProcessor
from src.processors.contribution_processor import ContributionProcessor
from src.renderers.heatmap import HeatmapRenderer
from src.renderers.language_chart import LanguageChartRenderer
from src.renderers.activity_chart import ActivityChartRenderer
from src.renderers.repo_ranking import RepoRankingRenderer
from src.renderers.profile_card import ProfileCardRenderer
from src.utils.git_helper import GitHelper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _render_all(processed_data: dict[str, Any], output_dir: str, theme: str, top_n: int) -> dict[str, str | None]:
    results: dict[str, str | None] = {}

    heatmap = HeatmapRenderer(output_dir=output_dir, theme=theme)
    results["heatmap"] = heatmap.render(
        processed_data["contributions"],
        year=None,
    )

    lang_chart = LanguageChartRenderer(output_dir=output_dir, theme=theme)
    results["languages"] = lang_chart.render(processed_data["languages"])

    activity_chart = ActivityChartRenderer(output_dir=output_dir, theme=theme)
    results["activity"] = activity_chart.render(processed_data["contributions"])

    repo_ranking = RepoRankingRenderer(output_dir=output_dir, theme=theme)
    results["repo_ranking"] = repo_ranking.render(processed_data["repos"], top_n=top_n)

    profile_card = ProfileCardRenderer(output_dir=output_dir, theme=theme)
    results["profile_card"] = profile_card.render(
        processed_data["user"],
        contribution_data=processed_data["contributions"],
    )

    return results


@click.group()
@click.option("--username", "-u", default=GITHUB_USERNAME, help="GitHub username")
@click.option("--token", "-t", default=GITHUB_TOKEN, help="GitHub Personal Access Token")
@click.option("--output", "-o", default=str(OUTPUT_DIR), help="Output directory")
@click.option("--year", "-y", default=None, type=int, help="Year for contribution data")
@click.option("--top-n", "-n", default=DEFAULT_TOP_N, type=int, help="Top N items to display")
@click.option("--no-forks", is_flag=True, default=DEFAULT_NO_FORKS, help="Exclude forked repositories")
@click.option("--theme", default=DEFAULT_THEME, type=click.Choice(["dark", "light"]), help="Color theme")
@click.option("--cache-ttl", default=CACHE_TTL, type=int, help="Cache TTL in seconds")
@click.option("--dry-run", is_flag=True, default=False, help="Only fetch data, don't generate charts")
@click.option("--push", is_flag=True, default=False, help="Auto commit and push generated files")
@click.option("--verbose", "-v", is_flag=True, default=False, help="Enable verbose logging")
@click.pass_context
def cli(ctx: click.Context, username: str, token: str, output: str, year: int | None, top_n: int, no_forks: bool, theme: str, cache_ttl: int, dry_run: bool, push: bool, verbose: bool) -> None:
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    ctx.ensure_object(dict)
    ctx.obj.update({
        "username": username,
        "token": token,
        "output": output,
        "year": year,
        "top_n": top_n,
        "no_forks": no_forks,
        "theme": theme,
        "cache_ttl": cache_ttl,
        "dry_run": dry_run,
        "push": push,
    })


@cli.command()
@click.pass_context
def all(ctx: click.Context) -> None:
    obj = ctx.obj
    username = obj["username"]

    if not username:
        click.echo("Error: GitHub username is required. Use --username or set GITHUB_USERNAME in .env")
        sys.exit(1)

    raw_data = collect_all(
        username, obj["token"], obj["no_forks"],
        year=obj["year"], cache_ttl=obj["cache_ttl"],
    )

    processed = process_all(raw_data, obj["no_forks"], obj["top_n"])

    if obj["dry_run"]:
        click.echo("Dry run mode - data fetched successfully, skipping chart generation")
        click.echo(f"User: {processed['user'].get('name', 'N/A')}")
        click.echo(f"Public repos: {processed['user'].get('public_repos', 0)}")
        click.echo(f"Total stars: {processed['repos'].get('total_stars', 0)}")
        click.echo(f"Total contributions: {processed['contributions'].get('total_contributions', 0)}")
        return

    results = _render_all(processed, obj["output"], obj["theme"], obj["top_n"])

    for name, filepath in results.items():
        if filepath:
            click.echo(f"Generated: {filepath}")
        else:
            click.echo(f"Skipped: {name} (no data)")

    if obj["push"]:
        git = GitHelper(repo_dir=Path(obj["output"]).parent)
        git.configure_user()
        if git.commit_and_push("🔄 Update dashboard", paths=["output/"]):
            click.echo("Changes committed and pushed")
        else:
            click.echo("No changes to push")


@cli.command()
@click.pass_context
def heatmap(ctx: click.Context) -> None:
    obj = ctx.obj
    username = obj["username"]

    if not username:
        click.echo("Error: GitHub username is required.")
        sys.exit(1)

    graphql = GraphQLCollector(token=obj["token"], cache_ttl=obj["cache_ttl"])
    from_date, to_date = get_date_range(obj["year"])
    calendar_data = graphql.get_contribution_calendar(username, from_date, to_date)

    contrib_proc = ContributionProcessor()
    processed = contrib_proc.process(calendar_data)

    renderer = HeatmapRenderer(output_dir=obj["output"], theme=obj["theme"])
    filepath = renderer.render(processed, year=obj["year"])
    if filepath:
        click.echo(f"Generated: {filepath}")


@cli.command()
@click.pass_context
def languages(ctx: click.Context) -> None:
    obj = ctx.obj
    username = obj["username"]

    if not username:
        click.echo("Error: GitHub username is required.")
        sys.exit(1)

    rest = RESTCollector(token=obj["token"], cache_ttl=obj["cache_ttl"])
    languages_data = rest.get_all_languages(username, no_forks=obj["no_forks"])

    lang_proc = LanguageProcessor()
    processed = lang_proc.process(languages_data, top_n=obj["top_n"])

    renderer = LanguageChartRenderer(output_dir=obj["output"], theme=obj["theme"])
    filepath = renderer.render(processed)
    if filepath:
        click.echo(f"Generated: {filepath}")


@cli.command()
@click.pass_context
def activity(ctx: click.Context) -> None:
    obj = ctx.obj
    username = obj["username"]

    if not username:
        click.echo("Error: GitHub username is required.")
        sys.exit(1)

    graphql = GraphQLCollector(token=obj["token"], cache_ttl=obj["cache_ttl"])
    from_date, to_date = get_date_range(obj["year"])
    calendar_data = graphql.get_contribution_calendar(username, from_date, to_date)

    contrib_proc = ContributionProcessor()
    processed = contrib_proc.process(calendar_data)

    renderer = ActivityChartRenderer(output_dir=obj["output"], theme=obj["theme"])
    filepath = renderer.render(processed)
    if filepath:
        click.echo(f"Generated: {filepath}")


@cli.command(name="repos")
@click.pass_context
def repos(ctx: click.Context) -> None:
    obj = ctx.obj
    username = obj["username"]

    if not username:
        click.echo("Error: GitHub username is required.")
        sys.exit(1)

    rest = RESTCollector(token=obj["token"], cache_ttl=obj["cache_ttl"])
    repos_data = rest.get_repos(username, no_forks=obj["no_forks"])

    repo_proc = RepoProcessor()
    processed = repo_proc.process(repos_data, no_forks=obj["no_forks"], top_n=obj["top_n"])

    renderer = RepoRankingRenderer(output_dir=obj["output"], theme=obj["theme"])
    filepath = renderer.render(processed, top_n=5)
    if filepath:
        click.echo(f"Generated: {filepath}")


@cli.command()
@click.pass_context
def profile(ctx: click.Context) -> None:
    obj = ctx.obj
    username = obj["username"]

    if not username:
        click.echo("Error: GitHub username is required.")
        sys.exit(1)

    raw_data = collect_all(
        username, obj["token"], obj["no_forks"],
        year=obj["year"], cache_ttl=obj["cache_ttl"],
    )
    processed = process_all(raw_data, obj["no_forks"], obj["top_n"])

    renderer = ProfileCardRenderer(output_dir=obj["output"], theme=obj["theme"])
    filepath = renderer.render(processed["user"], contribution_data=processed["contributions"])
    if filepath:
        click.echo(f"Generated: {filepath}")


if __name__ == "__main__":
    cli()
