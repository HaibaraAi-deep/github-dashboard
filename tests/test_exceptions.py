import unittest

from src.exceptions import APIError, DashboardError, RateLimitError, RenderError, ValidationError


class TestDashboardError(unittest.TestCase):
    def test_dashboard_error(self):
        err = DashboardError("something went wrong")
        self.assertEqual(err.message, "something went wrong")
        self.assertEqual(str(err), "something went wrong")

    def test_dashboard_error_default(self):
        err = DashboardError()
        self.assertEqual(err.message, "An error occurred in the GitHub Dashboard")


class TestAPIError(unittest.TestCase):
    def test_api_error(self):
        err = APIError("request failed", status_code=404, url="https://api.github.com/users/x")
        self.assertEqual(err.message, "request failed")
        self.assertEqual(err.status_code, 404)
        self.assertEqual(err.url, "https://api.github.com/users/x")
        self.assertEqual(str(err), "request failed | status_code=404 | url=https://api.github.com/users/x")

    def test_api_error_minimal(self):
        err = APIError("request failed")
        self.assertEqual(err.message, "request failed")
        self.assertIsNone(err.status_code)
        self.assertIsNone(err.url)
        self.assertEqual(str(err), "request failed")


class TestRateLimitError(unittest.TestCase):
    def test_rate_limit_error(self):
        err = RateLimitError("rate limited", reset_at=1700000000)
        self.assertEqual(err.message, "rate limited")
        self.assertEqual(err.reset_at, 1700000000)
        self.assertEqual(str(err), "rate limited | reset_at=1700000000")

    def test_rate_limit_error_no_reset(self):
        err = RateLimitError("rate limited")
        self.assertEqual(str(err), "rate limited")


class TestValidationError(unittest.TestCase):
    def test_validation_error(self):
        err = ValidationError("bad input")
        self.assertEqual(err.message, "bad input")
        self.assertEqual(str(err), "bad input")


class TestRenderError(unittest.TestCase):
    def test_render_error(self):
        err = RenderError("svg failed")
        self.assertEqual(err.message, "svg failed")
        self.assertEqual(str(err), "svg failed")


class TestInheritance(unittest.TestCase):
    def test_inheritance(self):
        self.assertTrue(issubclass(APIError, DashboardError))
        self.assertTrue(issubclass(RateLimitError, DashboardError))
        self.assertTrue(issubclass(ValidationError, DashboardError))
        self.assertTrue(issubclass(RenderError, DashboardError))

    def test_catch_as_base(self):
        with self.assertRaises(DashboardError):
            raise APIError("api fail")

        with self.assertRaises(DashboardError):
            raise RateLimitError("rate fail")

        with self.assertRaises(DashboardError):
            raise ValidationError("valid fail")

        with self.assertRaises(DashboardError):
            raise RenderError("render fail")


if __name__ == "__main__":
    unittest.main()
