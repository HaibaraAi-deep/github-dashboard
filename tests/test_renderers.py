import json
import os
import tempfile
import unittest

from src.renderers.heatmap import HeatmapRenderer
from src.renderers.language_chart import LanguageChartRenderer
from src.renderers.activity_chart import ActivityChartRenderer
from src.renderers.repo_ranking import RepoRankingRenderer
from src.renderers.profile_card import ProfileCardRenderer

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name):
    with open(os.path.join(FIXTURES_DIR, name), "r", encoding="utf-8") as f:
        return json.load(f)


class TestHeatmapRenderer(unittest.TestCase):
    def setUp(self):
        self.output_dir = tempfile.mkdtemp()
        self.renderer = HeatmapRenderer(output_dir=self.output_dir, theme="dark")

    def test_render_normal(self):
        data = load_fixture("contributions.json")
        filepath = self.renderer.render(data, year=2025)

        self.assertIsNotNone(filepath)
        self.assertTrue(os.path.exists(filepath))

    def test_render_empty(self):
        filepath = self.renderer.render({})
        self.assertIsNone(filepath)


class TestLanguageChartRenderer(unittest.TestCase):
    def setUp(self):
        self.output_dir = tempfile.mkdtemp()
        self.renderer = LanguageChartRenderer(output_dir=self.output_dir, theme="dark")

    def test_render_normal(self):
        data = {
            "languages": [
                {"name": "Python", "bytes": 50000, "percentage": 50.0, "color": "#3572A5"},
                {"name": "JavaScript", "bytes": 30000, "percentage": 30.0, "color": "#f1e05a"},
                {"name": "Other", "bytes": 20000, "percentage": 20.0, "color": "#8b949e"},
            ],
            "total_bytes": 100000,
            "total_language_count": 5,
        }
        filepath = self.renderer.render(data)

        self.assertIsNotNone(filepath)
        self.assertTrue(os.path.exists(filepath))

    def test_render_empty(self):
        filepath = self.renderer.render({"languages": []})
        self.assertIsNone(filepath)


class TestActivityChartRenderer(unittest.TestCase):
    def setUp(self):
        self.output_dir = tempfile.mkdtemp()
        self.renderer = ActivityChartRenderer(output_dir=self.output_dir, theme="dark")

    def test_render_normal(self):
        data = {
            "weekly_trend": [
                {"date": "2025-01-06", "count": 10},
                {"date": "2025-01-13", "count": 25},
                {"date": "2025-01-20", "count": 15},
            ]
        }
        filepath = self.renderer.render(data)

        self.assertIsNotNone(filepath)
        self.assertTrue(os.path.exists(filepath))

    def test_render_empty(self):
        filepath = self.renderer.render({"weekly_trend": []})
        self.assertIsNone(filepath)


class TestRepoRankingRenderer(unittest.TestCase):
    def setUp(self):
        self.output_dir = tempfile.mkdtemp()
        self.renderer = RepoRankingRenderer(output_dir=self.output_dir, theme="dark")

    def test_render_normal(self):
        data = {
            "top_by_stars": [
                {"name": "awesome-project", "stars": 150, "language": "Python", "forks": 30, "description": "", "full_name": "", "updated_at": "", "html_url": ""},
                {"name": "web-app", "stars": 80, "language": "TypeScript", "forks": 15, "description": "", "full_name": "", "updated_at": "", "html_url": ""},
            ]
        }
        filepath = self.renderer.render(data, top_n=5)

        self.assertIsNotNone(filepath)
        self.assertTrue(os.path.exists(filepath))

    def test_render_empty(self):
        filepath = self.renderer.render({"top_by_stars": []})
        self.assertIsNone(filepath)


class TestProfileCardRenderer(unittest.TestCase):
    def setUp(self):
        self.output_dir = tempfile.mkdtemp()
        self.renderer = ProfileCardRenderer(output_dir=self.output_dir, theme="dark")

    def test_render_normal(self):
        user_data = {
            "login": "testuser",
            "name": "Test User",
            "bio": "A test user",
            "avatar_url": "https://avatars.githubusercontent.com/u/12345?v=4",
            "public_repos": 25,
            "followers": 100,
            "following": 50,
            "total_stars": 235,
            "account_age_years": 7.0,
        }
        filepath = self.renderer.render(user_data)

        self.assertIsNotNone(filepath)
        self.assertTrue(os.path.exists(filepath))

    def test_render_empty(self):
        filepath = self.renderer.render(None)
        self.assertIsNone(filepath)


if __name__ == "__main__":
    unittest.main()
