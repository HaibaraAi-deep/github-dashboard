import logging
import subprocess

logger = logging.getLogger(__name__)


class GitHelper:
    def __init__(self, repo_dir=None):
        self.repo_dir = repo_dir

    def _run_git(self, *args):
        cmd = ["git"] + list(args)
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            logger.error(f"Git command timed out: {' '.join(cmd)}")
            return False, "", "Timeout"
        except FileNotFoundError:
            logger.error("Git is not installed or not in PATH")
            return False, "", "Git not found"

    def has_changes(self, paths=None):
        if paths:
            self._run_git("add", *paths)
        success, stdout, _ = self._run_git("diff", "--staged", "--quiet")
        return not success

    def commit_and_push(self, message, paths=None):
        if paths:
            self._run_git("add", *paths)
        else:
            self._run_git("add", "-A")

        if not self.has_changes():
            logger.info("No changes to commit")
            return False

        success, _, stderr = self._run_git("commit", "-m", message)
        if not success:
            logger.error(f"Git commit failed: {stderr}")
            return False

        success, _, stderr = self._run_git("push")
        if not success:
            logger.error(f"Git push failed: {stderr}")
            return False

        logger.info(f"Successfully committed and pushed: {message}")
        return True

    def configure_user(self, name="github-actions[bot]", email="github-actions[bot]@users.noreply.github.com"):
        self._run_git("config", "user.name", name)
        self._run_git("config", "user.email", email)
