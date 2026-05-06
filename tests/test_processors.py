import json
import os
import unittest

from src.processors.user_processor import UserProcessor
from src.processors.repo_processor import RepoProcessor
from src.processors.language_processor import LanguageProcessor
from src.processors.contribution_processor import ContributionProcessor

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURES_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


class TestUserProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = UserProcessor()

    def test_process_normal(self):
        data = load_fixture("user.json")
        result = self.processor.process(data)

        self.assertEqual(result["login"], "testuser")
        self.assertEqual(result["name"], "Test User")
        self.assertEqual(result["bio"], "A test user for development")
        self.assertEqual(result["public_repos"], 25)
        self.assertEqual(result["followers"], 100)
        self.assertGreater(result["account_age_days"], 0)

    def test_process_empty(self):
        result = self.processor.process({})
        self.assertEqual(result["login"], "")
        self.assertEqual(result["public_repos"], 0)

    def test_process_none(self):
        result = self.processor.process(None)
        self.assertEqual(result, {})

    def test_process_null_fields(self):
        data = {"login": "user", "name": None, "bio": None}
        result = self.processor.process(data)
        self.assertEqual(result["name"], "user")
        self.assertEqual(result["bio"], "")


class TestRepoProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = RepoProcessor()

    def test_process_normal(self):
        data = load_fixture("repos.json")
        result = self.processor.process(data)

        self.assertEqual(result["total_repos"], 3)
        self.assertEqual(result["total_stars"], 235)
        self.assertEqual(result["total_forks"], 46)

    def test_process_no_forks(self):
        data = load_fixture("repos.json")
        result = self.processor.process(data, no_forks=True)

        self.assertEqual(result["total_repos"], 2)
        self.assertEqual(result["total_stars"], 230)

    def test_process_top_by_stars(self):
        data = load_fixture("repos.json")
        result = self.processor.process(data, top_n=2)

        self.assertEqual(len(result["top_by_stars"]), 2)
        self.assertEqual(result["top_by_stars"][0]["name"], "awesome-project")
        self.assertEqual(result["top_by_stars"][0]["stars"], 150)

    def test_process_empty(self):
        result = self.processor.process([])
        self.assertEqual(result["total_repos"], 0)

    def test_process_none(self):
        result = self.processor.process(None)
        self.assertEqual(result["total_repos"], 0)


class TestLanguageProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = LanguageProcessor()

    def test_process_normal(self):
        data = {"Python": 50000, "JavaScript": 30000, "TypeScript": 20000}
        result = self.processor.process(data, top_n=2)

        self.assertEqual(len(result["languages"]), 3)
        self.assertEqual(result["languages"][0]["name"], "Python")
        self.assertAlmostEqual(result["languages"][0]["percentage"], 50.0)
        self.assertIn("Other", [l["name"] for l in result["languages"]])

    def test_process_single_language(self):
        data = {"Python": 10000}
        result = self.processor.process(data)

        self.assertEqual(len(result["languages"]), 1)
        self.assertEqual(result["languages"][0]["percentage"], 100.0)

    def test_process_empty(self):
        result = self.processor.process({})
        self.assertEqual(result["languages"], [])

    def test_process_none(self):
        result = self.processor.process(None)
        self.assertEqual(result["languages"], [])


class TestContributionProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = ContributionProcessor()

    def test_process_normal(self):
        data = load_fixture("contributions.json")
        result = self.processor.process(data)

        self.assertEqual(result["total_contributions"], 1234)
        self.assertIn("streak", result)
        self.assertIn("averages", result)
        self.assertIn("weekday_stats", result)

    def test_process_empty(self):
        result = self.processor.process({})
        self.assertEqual(result["total_contributions"], 0)

    def test_process_none(self):
        result = self.processor.process(None)
        self.assertEqual(result["total_contributions"], 0)

    def test_streak_calculation(self):
        data = load_fixture("contributions.json")
        result = self.processor.process(data)

        self.assertIn("current", result["streak"])
        self.assertIn("longest", result["streak"])
        self.assertGreaterEqual(result["streak"]["longest"], 0)

    def test_averages_calculation(self):
        data = load_fixture("contributions.json")
        result = self.processor.process(data)

        self.assertIn("daily", result["averages"])
        self.assertIn("weekly", result["averages"])
        self.assertIn("monthly", result["averages"])
        self.assertGreater(result["averages"]["daily"], 0)


if __name__ == "__main__":
    unittest.main()
