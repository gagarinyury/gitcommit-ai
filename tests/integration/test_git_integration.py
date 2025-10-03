"""Integration tests for git operations."""
import subprocess
import tempfile
from pathlib import Path

import pytest

from gitcommit_ai.core.git import GitOperations


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        yield repo_path


class TestGitIntegration:
    """Test real git operations."""

    def test_is_git_repository_in_real_repo(self, temp_git_repo: Path) -> None:
        """Detects real git repository."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            assert GitOperations.is_git_repository() is True
        finally:
            os.chdir(original_cwd)

    def test_is_git_repository_outside_repo(self) -> None:
        """Returns False outside git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                assert GitOperations.is_git_repository() is False
            finally:
                os.chdir(original_cwd)

    def test_has_staged_changes_with_staged_file(self, temp_git_repo: Path) -> None:
        """Detects staged changes."""
        import os

        # Create and stage a file
        test_file = temp_git_repo / "test.txt"
        test_file.write_text("Hello, world!")

        subprocess.run(["git", "add", "test.txt"], cwd=temp_git_repo, check=True)

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            assert GitOperations.has_staged_changes() is True
        finally:
            os.chdir(original_cwd)

    def test_get_staged_diff_returns_diff(self, temp_git_repo: Path) -> None:
        """Returns diff for staged changes."""
        import os

        # Create and stage a file
        test_file = temp_git_repo / "test.txt"
        test_file.write_text("Test content\n")

        subprocess.run(["git", "add", "test.txt"], cwd=temp_git_repo, check=True)

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            diff = GitOperations.get_staged_diff()
            assert len(diff.files) > 0
            assert diff.files[0].path == "test.txt"
            assert diff.total_additions > 0
        finally:
            os.chdir(original_cwd)

    def test_create_commit_makes_commit(self, temp_git_repo: Path) -> None:
        """Creates actual git commit."""
        import os

        # Create and stage a file
        test_file = temp_git_repo / "test.txt"
        test_file.write_text("Initial commit\n")

        subprocess.run(["git", "add", "test.txt"], cwd=temp_git_repo, check=True)

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo)
            GitOperations.create_commit("feat: add test file")

            # Verify commit was created
            result = subprocess.run(
                ["git", "log", "--oneline"],
                capture_output=True,
                text=True,
                check=True,
            )
            assert "feat: add test file" in result.stdout
        finally:
            os.chdir(original_cwd)
