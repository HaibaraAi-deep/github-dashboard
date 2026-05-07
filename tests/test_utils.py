import os
import subprocess
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

from src.collectors.base import BaseCollector
from src.exceptions import ValidationError
from src.utils.cache import Cache
from src.utils.git_helper import GitHelper
from src.utils.rate_limiter import RateLimiter


class TestCache(unittest.TestCase):
    def setUp(self):
        self.cache_dir = tempfile.mkdtemp()
        self.cache = Cache(cache_dir=self.cache_dir, ttl=3600)

    def tearDown(self):
        for f in os.listdir(self.cache_dir):
            os.remove(os.path.join(self.cache_dir, f))
        os.rmdir(self.cache_dir)

    def test_get_set(self):
        self.cache.set("test_key", {"name": "value"})
        result = self.cache.get("test_key")
        self.assertEqual(result, {"name": "value"})

    def test_get_expired(self):
        expired_cache = Cache(cache_dir=self.cache_dir, ttl=0)
        expired_cache.set("expired_key", "data")
        time.sleep(0.1)
        result = expired_cache.get("expired_key")
        self.assertIsNone(result)

    def test_get_nonexistent(self):
        result = self.cache.get("does_not_exist")
        self.assertIsNone(result)

    def test_clear(self):
        self.cache.set("key1", "val1")
        self.cache.set("key2", "val2")
        self.cache.set("key3", "val3")
        self.cache.clear()
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
        self.assertIsNone(self.cache.get("key3"))

    def test_remove(self):
        self.cache.set("removable", "data")
        self.assertIsNotNone(self.cache.get("removable"))
        self.cache.remove("removable")
        self.assertIsNone(self.cache.get("removable"))

    def test_len(self):
        self.cache.set("a", 1)
        self.cache.set("b", 2)
        self.cache.set("c", 3)
        self.assertEqual(len(self.cache), 3)

    def test_max_entries(self):
        with patch("src.utils.cache.MAX_CACHE_ENTRIES", 3):
            cache = Cache(cache_dir=self.cache_dir, ttl=3600)
            cache.set("key1", "val1")
            time.sleep(0.05)
            cache.set("key2", "val2")
            time.sleep(0.05)
            cache.set("key3", "val3")
            time.sleep(0.05)
            cache.set("key4", "val4")
            self.assertIsNone(cache.get("key1"))
            self.assertIsNotNone(cache.get("key4"))


class TestRateLimiter(unittest.TestCase):
    def test_init_with_token(self):
        limiter = RateLimiter(token="ghp_test123")
        self.assertIn("Authorization", limiter.session.headers)
        self.assertEqual(limiter.session.headers["Authorization"], "token ghp_test123")

    def test_init_without_token(self):
        limiter = RateLimiter(token=None)
        self.assertNotIn("Authorization", limiter.session.headers)

    def test_get_remaining_error(self):
        limiter = RateLimiter(token=None)
        with patch.object(limiter.session, "get", side_effect=Exception("network error")):
            from requests import RequestException
            with patch.object(limiter.session, "get", side_effect=RequestException("fail")):
                result = limiter.get_remaining()
                self.assertEqual(result, -1)


class TestGitHelper(unittest.TestCase):
    def test_run_git_success(self):
        helper = GitHelper(repo_dir="/tmp")
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "  output text  "
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result):
            success, stdout, stderr = helper._run_git("status")
            self.assertTrue(success)
            self.assertEqual(stdout, "output text")
            self.assertEqual(stderr, "")

    def test_run_git_failure(self):
        helper = GitHelper(repo_dir="/tmp")
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error message"
        with patch("subprocess.run", return_value=mock_result):
            success, stdout, stderr = helper._run_git("push")
            self.assertFalse(success)
            self.assertEqual(stdout, "")
            self.assertEqual(stderr, "error message")

    def test_run_git_timeout(self):
        helper = GitHelper(repo_dir="/tmp")
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="git", timeout=60)):
            success, stdout, stderr = helper._run_git("fetch")
            self.assertFalse(success)
            self.assertEqual(stdout, "")
            self.assertEqual(stderr, "Timeout")

    def test_sanitize_commit_message(self):
        helper = GitHelper(repo_dir="/tmp")
        malicious = 'update config `rm -rf /` $(whoami)'
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            helper.commit_and_push(malicious)
            call_args = [c.args[0] for c in mock_run.call_args_list]
            commit_call = None
            for args in call_args:
                if "commit" in args and "-m" in args:
                    commit_call = args
                    break
            if commit_call:
                msg_idx = commit_call.index("-m") + 1
                sanitized_msg = commit_call[msg_idx]
                self.assertNotIn("`", sanitized_msg)
                self.assertNotIn("$(", sanitized_msg)


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.collector = BaseCollector(token="fake_token")

    def test_validate_username_valid(self):
        valid_names = ["octocat", "user-name", "User123"]
        for name in valid_names:
            result = self.collector._validate_username(name)
            self.assertEqual(result, name)

    def test_validate_username_invalid(self):
        invalid_names = ["", "a" * 40, "-start", "has spaces", "special!char"]
        for name in invalid_names:
            with self.assertRaises(ValidationError, msg=f"Expected ValidationError for: {name!r}"):
                self.collector._validate_username(name)


if __name__ == "__main__":
    unittest.main()
