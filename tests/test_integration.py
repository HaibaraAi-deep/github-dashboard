import json
import os
import tempfile
import unittest
from unittest.mock import patch

from src.pipeline import process_all, get_date_range
from src.renderers.heatmap import HeatmapRenderer
from src.renderers.language_chart import LanguageChartRenderer
from src.renderers.activity_chart import ActivityChartRenderer
from src.renderers.repo_ranking import RepoRankingRenderer
from src.renderers.profile_card import ProfileCardRenderer
from src.collectors.rest_collector import RESTCollector
from src.collectors.graphql_collector import GraphQLCollector

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURES_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


class TestFullPipeline(unittest.TestCase):
    def setUp(self):
        self.output_dir = tempfile.mkdtemp()
        self.user_data = load_fixture("user.json")
        self.repos_data = load_fixture("repos.json")
        self.contributions_data = load_fixture("contributions.json")
        self.languages_data = {"Python": 50000, "JavaScript": 30000, "TypeScript": 20000}

    def test_collect_and_process(self):
        raw_data = {
            "user": self.user_data,
            "repos": self.repos_data,
            "languages": self.languages_data,
            "calendar": self.contributions_data,
        }
        result = process_all(raw_data)
        self.assertIn("user", result)
        self.assertIn("repos", result)
        self.assertIn("languages", result)
        self.assertIn("contributions", result)
        self.assertEqual(result["user"]["login"], "testuser")
        self.assertGreater(result["repos"]["total_repos"], 0)
        self.assertGreater(result["languages"]["total_bytes"], 0)
        self.assertGreater(result["contributions"]["total_contributions"], 0)

    def test_collect_and_process_empty(self):
        raw_data = {
            "user": None,
            "repos": [],
            "languages": {},
            "calendar": None,
        }
        result = process_all(raw_data)
        self.assertEqual(result["user"], {"total_stars": 0})
        self.assertEqual(result["repos"]["total_repos"], 0)
        self.assertEqual(result["languages"]["languages"], [])
        self.assertEqual(result["contributions"]["total_contributions"], 0)

    @patch.object(RESTCollector, "get_user", return_value=load_fixture("user.json") if os.path.exists(os.path.join(FIXTURES_DIR, "user.json")) else {})
    @patch.object(RESTCollector, "get_repos", return_value=load_fixture("repos.json") if os.path.exists(os.path.join(FIXTURES_DIR, "repos.json")) else [])
    @patch.object(RESTCollector, "get_all_languages", return_value={"Python": 50000})
    @patch.object(GraphQLCollector, "get_contribution_calendar", return_value=load_fixture("contributions.json") if os.path.exists(os.path.join(FIXTURES_DIR, "contributions.json")) else {})
    def test_collect_all_with_mocks(self, mock_calendar, mock_langs, mock_repos, mock_user):
        from src.pipeline import collect_all
        raw_data = collect_all("testuser", "fake_token", False, None)
        self.assertIn("user", raw_data)
        self.assertIn("repos", raw_data)
        self.assertIn("languages", raw_data)
        self.assertIn("calendar", raw_data)

    def test_render_all_charts(self):
        raw_data = {
            "user": self.user_data,
            "repos": self.repos_data,
            "languages": self.languages_data,
            "calendar": self.contributions_data,
        }
        result = process_all(raw_data)

        heatmap = HeatmapRenderer(output_dir=self.output_dir, theme="dark")
        lang_chart = LanguageChartRenderer(output_dir=self.output_dir, theme="dark")
        activity = ActivityChartRenderer(output_dir=self.output_dir, theme="dark")
        repo_rank = RepoRankingRenderer(output_dir=self.output_dir, theme="dark")
        profile = ProfileCardRenderer(output_dir=self.output_dir, theme="dark")

        heatmap_path = heatmap.render(result["contributions"], year=2025)
        lang_path = lang_chart.render(result["languages"])
        activity_path = activity.render(result["contributions"])
        repo_path = repo_rank.render(result["repos"])
        profile_path = profile.render(result["user"], contribution_data=result["contributions"])

        if heatmap_path:
            self.assertTrue(os.path.exists(heatmap_path))
        if lang_path:
            self.assertTrue(os.path.exists(lang_path))
        if activity_path:
            self.assertTrue(os.path.exists(activity_path))
        if repo_path:
            self.assertTrue(os.path.exists(repo_path))
        if profile_path:
            self.assertTrue(os.path.exists(profile_path))


class TestDateRangeIntegration(unittest.TestCase):
    def test_date_range_consistency(self):
        from_date, to_date = get_date_range(year=2024)
        self.assertEqual(from_date, "2024-01-01T00:00:00Z")
        self.assertEqual(to_date, "2024-12-31T23:59:59Z")

    def test_date_range_current_year(self):
        from_date, to_date = get_date_range()
        self.assertIn("T00:00:00Z", from_date)
        self.assertIn("T23:59:59Z", to_date)


if __name__ == "__main__":
    unittest.main()
