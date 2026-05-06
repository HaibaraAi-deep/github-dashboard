import logging

from src.collectors.base import BaseCollector
from src.config import GITHUB_API_BASE

logger = logging.getLogger(__name__)


class RESTCollector(BaseCollector):
    def get_user(self, username):
        url = f"{GITHUB_API_BASE}/users/{username}"
        cache_key = f"user_{username}"
        return self._fetch_with_cache(cache_key, url)

    def get_repos(self, username, sort="updated", per_page=100, no_forks=False):
        all_repos = []
        page = 1
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

    def get_repo_languages(self, owner, repo):
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/languages"
        cache_key = f"languages_{owner}_{repo}"
        return self._fetch_with_cache(cache_key, url)

    def get_commit_activity(self, owner, repo):
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/stats/commit_activity"
        cache_key = f"commit_activity_{owner}_{repo}"
        return self._fetch_with_cache(cache_key, url)

    def get_all_languages(self, username, no_forks=False):
        repos = self.get_repos(username, no_forks=no_forks)
        all_languages = {}
        for repo in repos:
            if repo.get("fork") and no_forks:
                continue
            lang_url = repo.get("languages_url")
            if not lang_url:
                owner = repo["owner"]["login"]
                name = repo["name"]
                langs = self.get_repo_languages(owner, name)
            else:
                cache_key = f"languages_{username}_{repo['name']}"
                langs = self._fetch_with_cache(cache_key, lang_url)

            for lang, bytes_count in langs.items():
                all_languages[lang] = all_languages.get(lang, 0) + bytes_count

        return all_languages

    def get_all_commit_activity(self, username, no_forks=False):
        repos = self.get_repos(username, no_forks=no_forks)
        all_activity = []
        for repo in repos:
            if repo.get("fork") and no_forks:
                continue
            owner = repo["owner"]["login"]
            name = repo["name"]
            try:
                activity = self.get_commit_activity(owner, name)
                if activity and isinstance(activity, list):
                    all_activity.append({
                        "repo": name,
                        "activity": activity,
                    })
            except Exception as e:
                logger.warning(f"Failed to get commit activity for {name}: {e}")
        return all_activity
