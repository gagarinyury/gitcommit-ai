"""Git operations for extracting diffs and creating commits."""
import subprocess

from gitcommit_ai.core.diff_parser import DiffParser
from gitcommit_ai.generator.message import GitDiff


class GitError(Exception):
    """Raised when git operations fail."""

    pass


class GitOperations:
    """Git command wrapper for commit message generation."""

    @staticmethod
    def is_git_repository() -> bool:
        """Check if current directory is inside a git repository.

        Returns:
            True if in a git repository, False otherwise.
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    @staticmethod
    def has_staged_changes() -> bool:
        """Check if there are any staged changes in the repository.

        Returns:
            True if there are staged changes, False otherwise.
        """
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-status"],
            capture_output=True,
            text=True,
            check=True,
        )
        return bool(result.stdout.strip())

    @staticmethod
    def get_staged_diff() -> GitDiff:
        """Extract the staged diff from the repository.

        Returns:
            GitDiff object containing all staged changes.

        Raises:
            GitError: If git command fails.
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--unified=3"],
                capture_output=True,
                text=True,
                check=True,
            )
            return DiffParser.parse(result.stdout)
        except subprocess.CalledProcessError as e:
            raise GitError(e.stderr or "Failed to get staged diff") from e

    @staticmethod
    def create_commit(message: str) -> None:
        """Create a git commit with the given message.

        Args:
            message: Commit message to use.

        Raises:
            GitError: If commit creation fails.
        """
        try:
            subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise GitError(e.stderr or "Failed to create commit") from e
