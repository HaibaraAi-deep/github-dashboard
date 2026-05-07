import unittest
from unittest.mock import patch

from app import app, _sanitize_svg
from src.exceptions import DashboardError


class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True
        self.ctx = app.app_context()
        self.ctx.push()
        app.jinja_env.globals["csrf_token"] = lambda: "test-csrf"

    def tearDown(self):
        self.ctx.pop()

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_generate_no_username(self):
        response = self.client.post("/generate", data={})
        self.assertEqual(response.status_code, 400)

    def test_generate_invalid_username(self):
        response = self.client.post("/generate", data={"username": "-invalid"})
        self.assertEqual(response.status_code, 400)

    @patch("app.process_all")
    @patch("app.collect_all")
    def test_generate_server_error(self, mock_collect, mock_process):
        mock_collect.side_effect = DashboardError("API failure")
        response = self.client.post(
            "/generate",
            data={"username": "octocat", "token": "fake"},
        )
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn("error", data)

    def test_sanitize_svg(self):
        malicious = '<svg><script>alert("xss")</script><rect onclick="evil()"/></svg>'
        cleaned = _sanitize_svg(malicious)
        self.assertNotIn("<script", cleaned)
        self.assertNotIn("onclick", cleaned)
        self.assertIn("<rect", cleaned)

    def test_sanitize_svg_clean(self):
        clean = '<svg><rect width="100" height="100"/></svg>'
        result = _sanitize_svg(clean)
        self.assertEqual(result, clean)


if __name__ == "__main__":
    unittest.main()
