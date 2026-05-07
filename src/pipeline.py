import logging
from datetime import datetime, timezone
from typing import Any

from src.collectors.rest_collector import RESTCollector
from src.collectors.graphql_collector import GraphQLCollector
from src.processors.user_processor import UserProcessor
from src.processors.repo_processor import RepoProcessor
from src.processors.language_processor import LanguageProcessor
from src.processors.contribution_processor import ContributionProcessor
from src.config import DEFAULT_TOP_N
from src.types import UserInfo, RepoResult, LanguageResult, ContributionResult

logger = logging.getLogger(__name__)


def get_date_range(year: int | None = None) -> tuple[str, str]:
    if year:
        from_date = f"{year}-01-01T00:00:00Z"
        to_date = f"{year}-12-31T23:59:59Z"
    else:
        now = datetime.now(timezone.utc)
        from_date = f"{now.year}-01-01T00:00:00Z"
        to_date = now.strftime("%Y-%m-%dT23:59:59Z")
    return from_date, to_date


def collect_all(username: str, token: str, no_forks: bool, year: int | None = None, cache_ttl: int | None = None) -> dict[str, Any]:
    rest = RESTCollector(token=token, cache_ttl=cache_ttl)
    graphql = GraphQLCollector(token=token, cache_ttl=cache_ttl)
    logger.info(f"Fetching data for user: {username}")
    user_data = rest.get_user(username)
    repos_data = rest.get_repos(username, no_forks=no_forks)
    languages_data = rest.get_all_languages(username, no_forks=no_forks)
    from_date, to_date = get_date_range(year)
    calendar_data = graphql.get_contribution_calendar(username, from_date, to_date)
    return {
        "user": user_data,
        "repos": repos_data,
        "languages": languages_data,
        "calendar": calendar_data,
    }


def process_all(raw_data: dict[str, Any], no_forks: bool = False, top_n: int = DEFAULT_TOP_N) -> dict[str, UserInfo | RepoResult | LanguageResult | ContributionResult]:
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
        "contributions": contrib_result,
    }
