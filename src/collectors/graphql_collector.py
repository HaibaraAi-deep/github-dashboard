import logging
import time

import requests

from src.collectors.base import BaseCollector
from src.config import GITHUB_GRAPHQL_URL

logger = logging.getLogger(__name__)

QUERY_CONTRIBUTION_CALENDAR = """
query($username: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $username) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            date
            color
            weekday
          }
        }
      }
    }
  }
}
"""

QUERY_CONTRIBUTION_YEARS = """
query($username: String!) {
  user(login: $username) {
    contributionsCollection {
      contributionYears
    }
  }
}
"""

QUERY_RATE_LIMIT = """
query {
  rateLimit {
    remaining
    resetAt
  }
}
"""


class GraphQLCollector(BaseCollector):
    def _graphql_request(self, query, variables=None):
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        cache_key = f"gql_{hash(query)}_{hash(str(variables))}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        delay = self.retry_delay
        for attempt in range(self.max_retries):
            try:
                response = self.session.post(
                    GITHUB_GRAPHQL_URL,
                    json=payload,
                    timeout=30,
                )

                if response.status_code == 200:
                    data = response.json()
                    if "errors" in data:
                        error_msgs = [e.get("message", "Unknown error") for e in data["errors"]]
                        logger.error(f"GraphQL errors: {error_msgs}")
                        raise Exception(f"GraphQL query failed: {error_msgs}")
                    self.cache.set(cache_key, data["data"])
                    return data["data"]

                if response.status_code == 403:
                    logger.warning("GraphQL rate limit exceeded, waiting...")
                    self.rate_limiter.check_and_wait()
                    continue

                if response.status_code >= 500:
                    logger.warning(
                        f"GraphQL server error {response.status_code}, "
                        f"retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    delay *= 2
                    continue

                response.raise_for_status()

            except requests.exceptions.Timeout:
                logger.warning(f"GraphQL timeout, retrying... ({attempt + 1}/{self.max_retries})")
                time.sleep(delay)
                delay *= 2
            except requests.exceptions.ConnectionError:
                logger.warning(f"GraphQL connection error, retrying...")
                time.sleep(delay)
                delay *= 2

        raise Exception(f"GraphQL request failed after {self.max_retries} retries")

    def get_contribution_calendar(self, username, from_date, to_date):
        variables = {
            "username": username,
            "from": from_date,
            "to": to_date,
        }
        data = self._graphql_request(QUERY_CONTRIBUTION_CALENDAR, variables)
        return data.get("user", {}).get("contributionsCollection", {}).get("contributionCalendar", {})

    def get_contribution_years(self, username):
        variables = {"username": username}
        data = self._graphql_request(QUERY_CONTRIBUTION_YEARS, variables)
        return data.get("user", {}).get("contributionsCollection", {}).get("contributionYears", [])

    def get_rate_limit(self):
        data = self._graphql_request(QUERY_RATE_LIMIT)
        return data.get("rateLimit", {})

