import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List

from src.collectors.base import BaseCollector
from src.config import GITHUB_API_BASE

logger = logging.getLogger(__name__)


class RESTCollector(BaseCollector):
    def get_user(self, username: str) -> Dict[str, Any]:
        self._validate_username(username)
        url = f"{GITHUB_API_BASE}/users/{username}"
        cache_key = f"user_{username}"
        return self._fetch_with_cache(cache_key, url)

    def get_repos(self, username: str, sort: str = "updated", per_page: int = 100, no_forks: bool = False) -> List[Dict[str, Any]]:
        self._validate_username(username)
        all_repos: List[Dict[str, Any]] = []
        page: int = 1
        while True:
            url = f"{GITHUB_API_BASE}/users/{username}/repos"
            params = {
                "sort": sort,
                "per_page": per_page,
                "page": page,
                "type": "owner" if no_forks else "all",
            }
            cache_key = f"repos_{username}_{sort}_{per_page}_{page}_{no_forks}"
            data = self._fetch_with_cache(cache_key, url, params=params)

            if not data:
                break

            all_repos.extend(data)

            if len(data) < per_page:
                break

            page += 1

        return all_repos

    def get_repo_languages(self, owner: str, repo: str) -> Dict[str, int]:
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/languages"
        cache_key = f"languages_{owner}_{repo}"
        return self._fetch_with_cache(cache_key, url)

    def get_commit_activity(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/stats/commit_activity"
        cache_key = f"commit_activity_{owner}_{repo}"
        return self._fetch_with_cache(cache_key, url)

    def _fetch_repo_languages(self, username: str, repo: Dict[str, Any], no_forks: bool) -> Dict[str, int]:
        if repo.get("fork") and no_forks:
            return {}
        lang_url = repo.get("languages_url")
        if not lang_url:
            owner = repo["owner"]["login"]
            name = repo["name"]
            return self.get_repo_languages(owner, name)
        else:
            cache_key = f"languages_{username}_{repo['name']}"
            return self._fetch_with_cache(cache_key, lang_url)

    def get_all_languages(self, username: str, no_forks: bool = False) -> Dict[str, int]:
        self._validate_username(username)
        repos = self.get_repos(username, no_forks=no_forks)
        all_languages: Dict[str, int] = {}

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self._fetch_repo_languages, username, repo, no_forks): repo
                for repo in repos
            }
            for future in as_completed(futures):
                try:
                    langs = future.result()
                    for lang, bytes_count in langs.items():
                        all_languages[lang] = all_languages.get(lang, 0) + bytes_count
                except Exception as e:
                    repo = futures[future]
                    logger.warning(f"Failed to fetch languages for {repo.get('name', 'unknown')}: {e}")

        return all_languages

    def _fetch_repo_activity(self, repo: dict, no_forks: bool) -> dict[str, Any] | None:
        if repo.get("fork") and no_forks:
            return None
        owner = repo["owner"]["login"]
        name = repo["name"]
        try:
            activity = self.get_commit_activity(owner, name)
            if activity and isinstance(activity, list):
                return {"repo": name, "activity": activity}
        except Exception as e:
            logger.warning(f"Failed to get commit activity for {name}: {e}")
        return None

    def get_all_commit_activity(self, username: str, no_forks: bool = False) -> List[Dict[str, Any]]:
        self._validate_username(username)
        repos = self.get_repos(username, no_forks=no_forks)
        all_activity: List[Dict[str, Any]] = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self._fetch_repo_activity, repo, no_forks): repo
                for repo in repos
            }
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        all_activity.append(result)
                except Exception as e:
                    repo = futures[future]
                    logger.warning(f"Failed to fetch activity for {repo.get('name', 'unknown')}: {e}")

        return all_activity
