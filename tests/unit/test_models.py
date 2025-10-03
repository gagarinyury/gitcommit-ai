"""Tests for data models (GitDiff, CommitMessage)."""
import pytest

from gitcommit_ai.generator.message import CommitMessage, FileDiff, GitDiff


class TestFileDiff:
    """Test FileDiff dataclass."""

    def test_file_diff_creation(self) -> None:
        """FileDiff can be created with all fields."""
        diff = FileDiff(
            path="src/main.py",
            change_type="modified",
            additions=10,
            deletions=5,
            diff_content="@@ -1,5 +1,10 @@\n+new line",
        )
        assert diff.path == "src/main.py"
        assert diff.change_type == "modified"
        assert diff.additions == 10
        assert diff.deletions == 5

    def test_file_diff_added(self) -> None:
        """FileDiff correctly represents added file."""
        diff = FileDiff(
            path="src/new_file.py",
            change_type="added",
            additions=20,
            deletions=0,
            diff_content="@@ -0,0 +1,20 @@",
        )
        assert diff.change_type == "added"
        assert diff.deletions == 0

    def test_file_diff_deleted(self) -> None:
        """FileDiff correctly represents deleted file."""
        diff = FileDiff(
            path="src/old_file.py",
            change_type="deleted",
            additions=0,
            deletions=15,
            diff_content="@@ -1,15 +0,0 @@",
        )
        assert diff.change_type == "deleted"
        assert diff.additions == 0


class TestGitDiff:
    """Test GitDiff dataclass."""

    def test_git_diff_creation(self) -> None:
        """GitDiff can be created with list of FileDiff objects."""
        file_diffs = [
            FileDiff("src/a.py", "modified", 5, 2, "diff content"),
            FileDiff("src/b.py", "added", 10, 0, "diff content"),
        ]
        git_diff = GitDiff(
            files=file_diffs, total_additions=15, total_deletions=2
        )
        assert len(git_diff.files) == 2
        assert git_diff.total_additions == 15
        assert git_diff.total_deletions == 2

    def test_git_diff_empty(self) -> None:
        """GitDiff can represent empty changeset."""
        git_diff = GitDiff(files=[], total_additions=0, total_deletions=0)
        assert len(git_diff.files) == 0
        assert git_diff.total_additions == 0


class TestCommitMessage:
    """Test CommitMessage dataclass and formatting."""

    def test_commit_message_creation(self) -> None:
        """CommitMessage can be created with all fields."""
        msg = CommitMessage(
            type="feat",
            scope="auth",
            description="add JWT authentication",
            body="Implemented token-based auth using JWT.",
            breaking_changes=[],
        )
        assert msg.type == "feat"
        assert msg.scope == "auth"
        assert msg.description == "add JWT authentication"

    def test_commit_message_format_basic(self) -> None:
        """CommitMessage formats to conventional commit string."""
        msg = CommitMessage(
            type="fix",
            scope=None,
            description="resolve memory leak",
            body=None,
            breaking_changes=[],
        )
        formatted = msg.format()
        assert formatted == "fix: resolve memory leak"

    def test_commit_message_format_with_scope(self) -> None:
        """CommitMessage formats with scope correctly."""
        msg = CommitMessage(
            type="feat",
            scope="api",
            description="add user endpoints",
            body=None,
            breaking_changes=[],
        )
        formatted = msg.format()
        assert formatted == "feat(api): add user endpoints"

    def test_commit_message_format_with_body(self) -> None:
        """CommitMessage formats with body paragraph."""
        msg = CommitMessage(
            type="refactor",
            scope="core",
            description="simplify error handling",
            body="Consolidated error handling logic into single module.",
            breaking_changes=[],
        )
        formatted = msg.format()
        assert "refactor(core): simplify error handling" in formatted
        assert "Consolidated error handling logic" in formatted

    def test_commit_message_format_with_breaking_changes(self) -> None:
        """CommitMessage formats breaking changes section."""
        msg = CommitMessage(
            type="feat",
            scope="api",
            description="update response format",
            body="Changed API response structure.",
            breaking_changes=["Response now returns JSON object instead of array"],
        )
        formatted = msg.format()
        assert "BREAKING CHANGE:" in formatted
        assert "Response now returns JSON object" in formatted

    def test_commit_message_types(self) -> None:
        """CommitMessage supports all conventional commit types."""
        types = ["feat", "fix", "docs", "style", "refactor", "test", "chore"]
        for commit_type in types:
            msg = CommitMessage(
                type=commit_type,
                scope=None,
                description="test description",
                body=None,
                breaking_changes=[],
            )
            assert msg.type == commit_type
            assert commit_type in msg.format()
