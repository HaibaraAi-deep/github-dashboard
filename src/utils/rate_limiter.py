import logging
import time

import requests

from src.config import GITHUB_API_BASE

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, token=None, threshold=100):
        self.token = token
        self.threshold = threshold
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            })

    def check_and_wait(self):
        try:
            response = self.session.get(f"{GITHUB_API_BASE}/rate_limit")
            response.raise_for_status()
            data = response.json()

            core = data.get("resources", {}).get("core", {})
            remaining = core.get("remaining", 0)
            reset_at = core.get("reset", 0)

            if remaining < self.threshold:
                wait_seconds = max(reset_at - time.time() + 10, 0)
                logger.warning(
                    f"API quota low ({remaining} remaining), "
                    f"waiting {wait_seconds:.0f} seconds..."
                )
                if wait_seconds > 0:
                    time.sleep(wait_seconds)
            else:
                logger.debug(f"API quota: {remaining} remaining")

            return remaining
        except requests.RequestException as e:
            logger.warning(f"Rate limit check failed: {e}")
            return -1

    def get_remaining(self):
        try:
            response = self.session.get(f"{GITHUB_API_BASE}/rate_limit")
            response.raise_for_status()
            data = response.json()
            return data.get("resources", {}).get("core", {}).get("remaining", 0)
        except requests.RequestException:
            return -1
