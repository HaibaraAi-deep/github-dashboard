import logging

from src.config import DEFAULT_TOP_N
from src.types import RepoResult

logger = logging.getLogger(__name__)


class RepoProcessor:
    def process(self, repos_data: list | None, no_forks: bool = False, top_n: int = DEFAULT_TOP_N) -> RepoResult:
        if not repos_data:
            return {
                "total_repos": 0,
                "total_stars": 0,
                "total_forks": 0,
                "repos_by_language": {},
                "top_by_stars": [],
                "top_by_forks": [],
                "all_repos": [],
            }

        repos = repos_data
        if no_forks:
            repos = [r for r in repos if not r.get("fork", False)]

        total_stars = sum(r.get("stargazers_count", 0) for r in repos)
        total_forks = sum(r.get("forks_count", 0) for r in repos)

        repos_by_language = {}
        for repo in repos:
            lang = repo.get("language") or "Other"
            repos_by_language[lang] = repos_by_language.get(lang, 0) + 1

        sorted_by_stars = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)
        sorted_by_forks = sorted(repos, key=lambda r: r.get("forks_count", 0), reverse=True)

        def _format_repo(repo: dict) -> dict:
            return {
                "name": repo.get("name", ""),
                "full_name": repo.get("full_name", ""),
                "description": repo.get("description", "") or "",
                "language": repo.get("language") or "",
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "updated_at": repo.get("updated_at", ""),
                "html_url": repo.get("html_url", ""),
            }

        return {
            "total_repos": len(repos),
            "total_stars": total_stars,
            "total_forks": total_forks,
            "repos_by_language": repos_by_language,
            "top_by_stars": [_format_repo(r) for r in sorted_by_stars[:top_n]],
            "top_by_forks": [_format_repo(r) for r in sorted_by_forks[:top_n]],
            "all_repos": [_format_repo(r) for r in repos],
        }
