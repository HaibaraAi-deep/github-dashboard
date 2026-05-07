import json
import os
import unittest
from datetime import datetime, timezone

from src.pipeline import get_date_range, process_all


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURES_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


class TestGetDateRange(unittest.TestCase):
    def test_get_date_range_with_year(self):
        from_date, to_date = get_date_range(year=2025)
        self.assertEqual(from_date, "2025-01-01T00:00:00Z")
        self.assertEqual(to_date, "2025-12-31T23:59:59Z")

    def test_get_date_range_without_year(self):
        from_date, to_date = get_date_range(year=None)
        current_year = str(datetime.now(timezone.utc).year)
        self.assertTrue(from_date.startswith(current_year))
        self.assertTrue(to_date.startswith(current_year))
        self.assertTrue(from_date.endswith("T00:00:00Z"))
        self.assertTrue(to_date.endswith("T23:59:59Z"))


class TestProcessAll(unittest.TestCase):
    def test_process_all(self):
        user_data = load_fixture("user.json")
        repos_data = load_fixture("repos.json")
        contributions_data = load_fixture("contributions.json")
        raw_data = {
            "user": user_data,
            "repos": repos_data,
            "languages": {"Python": 50000, "JavaScript": 30000},
            "calendar": contributions_data,
        }
        result = process_all(raw_data)
        self.assertIn("user", result)
        self.assertIn("repos", result)
        self.assertIn("languages", result)
        self.assertIn("contributions", result)
        self.assertEqual(result["user"]["login"], "testuser")
        self.assertIn("total_stars", result["user"])
        self.assertGreater(result["repos"]["total_repos"], 0)
        self.assertGreater(len(result["languages"]["languages"]), 0)
        self.assertGreater(result["contributions"]["total_contributions"], 0)


if __name__ == "__main__":
    unittest.main()
