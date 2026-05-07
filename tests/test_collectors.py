import json
import os
import unittest
from unittest.mock import patch

from src.collectors.base import BaseCollector
from src.collectors.rest_collector import RESTCollector
from src.collectors.graphql_collector import GraphQLCollector
from src.utils.cache import Cache

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURES_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


class TestBaseCollector(unittest.TestCase):
    def setUp(self):
        self.collector = BaseCollector(token="fake_token")

    def test_headers_set(self):
        self.assertIn("Authorization", self.collector.session.headers)
        self.assertEqual(
            self.collector.session.headers["Authorization"],
            "token fake_token",
        )

    def test_user_agent_set(self):
        self.assertIn("User-Agent", self.collector.session.headers)

    def test_cache_initialized(self):
        self.assertIsInstance(self.collector.cache, Cache)


class TestRESTCollector(unittest.TestCase):
    def setUp(self):
        self.collector = RESTCollector(token="fake_token")

    @patch.object(BaseCollector, "_request_with_retry")
    def test_get_user(self, mock_request):
        fixture = load_fixture("user.json")
        mock_request.return_value = fixture

        result = self.collector.get_user("testuser")
        self.assertEqual(result["login"], "testuser")
        self.assertEqual(result["name"], "Test User")

    @patch.object(BaseCollector, "_fetch_with_cache")
    def test_get_repos(self, mock_fetch):
        fixture = load_fixture("repos.json")
        mock_fetch.return_value = fixture

        result = self.collector.get_repos("testuser")
        self.assertEqual(len(result), 3)

    @patch.object(BaseCollector, "_fetch_with_cache")
    def test_get_repo_languages(self, mock_fetch):
        mock_fetch.return_value = {"Python": 10000, "JavaScript": 5000}
        result = self.collector.get_repo_languages("testuser", "awesome-project")
        self.assertIn("Python", result)
        self.assertIn("JavaScript", result)


class TestGraphQLCollector(unittest.TestCase):
    def setUp(self):
        self.collector = GraphQLCollector(token="fake_token")

    @patch.object(GraphQLCollector, "_graphql_request")
    def test_get_contribution_calendar(self, mock_request):
        fixture = load_fixture("contributions.json")
        mock_request.return_value = {
            "user": {
                "contributionsCollection": {
                    "contributionCalendar": fixture
                }
            }
        }

        result = self.collector.get_contribution_calendar(
            "testuser", "2025-01-01T00:00:00Z", "2025-12-31T23:59:59Z"
        )
        self.assertEqual(result["totalContributions"], 1234)

    @patch.object(GraphQLCollector, "_graphql_request")
    def test_get_contribution_years(self, mock_request):
        mock_request.return_value = {
            "user": {
                "contributionsCollection": {
                    "contributionYears": [2023, 2024, 2025]
                }
            }
        }

        result = self.collector.get_contribution_years("testuser")
        self.assertEqual(result, [2023, 2024, 2025])


if __name__ == "__main__":
    unittest.main()
