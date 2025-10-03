"""Tests for git operations."""
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from gitcommit_ai.core.git import GitError, GitOperations
from gitcommit_ai.generator.message import FileDiff, GitDiff


class TestIsGitRepository:
    """Test git repository detection."""

    def test_is_git_repository_when_in_repo(self) -> None:
        """Returns True when in a git repository."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = GitOperations.is_git_repository()
            assert result is True
            mock_run.assert_called_once()

    def test_is_not_git_repository_when_outside_repo(self) -> None:
        """Returns False when not in a git repository."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=128)
            result = GitOperations.is_git_repository()
            assert result is False


class TestHasStagedChanges:
    """Test staged changes detection."""

    def test_has_staged_changes_when_files_staged(self) -> None:
        """Returns True when there are staged changes."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="M  src/file.py\nA  src/new.py\n"
            )
            result = GitOperations.has_staged_changes()
            assert result is True

    def test_has_no_staged_changes_when_empty(self) -> None:
        """Returns False when no files are staged."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            result = GitOperations.has_staged_changes()
            assert result is False


class TestGetStagedDiff:
    """Test staged diff extraction."""

    def test_get_staged_diff_success(self) -> None:
        """Extracts diff from staged changes."""
        diff_output = """diff --git a/src/main.py b/src/main.py
index 123..456 100644
--- a/src/main.py
+++ b/src/main.py
@@ -1,3 +1,4 @@
+import os
 def main():
     pass
"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout=diff_output
            )
            diff = GitOperations.get_staged_diff()
            assert isinstance(diff, GitDiff)
            assert len(diff.files) > 0

    def test_get_staged_diff_empty_when_nothing_staged(self) -> None:
        """Returns empty GitDiff when nothing is staged."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            diff = GitOperations.get_staged_diff()
            assert isinstance(diff, GitDiff)
            assert len(diff.files) == 0
            assert diff.total_additions == 0
            assert diff.total_deletions == 0

    def test_get_staged_diff_raises_on_git_error(self) -> None:
        """Raises GitError when git command fails."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "git", stderr="fatal: not a git repository"
            )
            with pytest.raises(GitError, match="not a git repository"):
                GitOperations.get_staged_diff()


class TestCreateCommit:
    """Test commit creation."""

    def test_create_commit_success(self) -> None:
        """Creates commit with given message."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            GitOperations.create_commit("feat: add new feature")
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "git" in call_args
            assert "commit" in call_args
            assert "-m" in call_args

    def test_create_commit_raises_on_error(self) -> None:
        """Raises GitError when commit fails."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, "git", stderr="nothing to commit"
            )
            with pytest.raises(GitError, match="nothing to commit"):
                GitOperations.create_commit("feat: test")


class TestGitError:
    """Test GitError exception."""

    def test_git_error_message(self) -> None:
        """GitError stores error message correctly."""
        error = GitError("Repository not found")
        assert str(error) == "Repository not found"
