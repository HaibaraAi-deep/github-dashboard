import logging
import time

import requests

from src.config import GITHUB_API_BASE, GITHUB_TOKEN
from src.utils.cache import Cache
from src.utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class BaseCollector:
    def __init__(self, token=None, cache_ttl=None):
        self.token = token or GITHUB_TOKEN
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "GitHub-Personal-Dashboard/1.0",
            "Accept": "application/vnd.github.v3+json",
        })
        if self.token:
            self.session.headers.update({
                "Authorization": f"token {self.token}",
            })

        self.cache = Cache(ttl=cache_ttl)
        self.rate_limiter = RateLimiter(token=self.token)
        self.max_retries = 3
        self.retry_delay = 1

    def _request_with_retry(self, url, params=None, method="GET"):
        delay = self.retry_delay
        for attempt in range(self.max_retries):
            try:
                if method == "GET":
                    response = self.session.get(url, params=params, timeout=30)
                else:
                    response = self.session.post(url, json=params, timeout=30)

                if response.status_code == 200:
                    return response.json()

                if response.status_code == 202:
                    logger.info(
                        f"Data computing, retrying in {delay}s... "
                        f"({attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(delay)
                    delay *= 2
                    continue

                if response.status_code == 403:
                    remaining = self.rate_limiter.get_remaining()
                    if remaining <= 0:
                        logger.warning("Rate limit exceeded, waiting...")
                        self.rate_limiter.check_and_wait()
                        continue
                    response.raise_for_status()

                if response.status_code >= 500:
                    logger.warning(
                        f"Server error {response.status_code}, retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    delay *= 2
                    continue

                response.raise_for_status()

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout, retrying... ({attempt + 1}/{self.max_retries})")
                time.sleep(delay)
                delay *= 2
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error, retrying... ({attempt + 1}/{self.max_retries})")
                time.sleep(delay)
                delay *= 2

        raise Exception(f"Request failed after {self.max_retries} retries: {url}")

    def _fetch_with_cache(self, cache_key, url, params=None):
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        data = self._request_with_retry(url, params=params)
        self.cache.set(cache_key, data)
        return data
