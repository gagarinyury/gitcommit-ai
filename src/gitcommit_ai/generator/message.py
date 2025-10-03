"""Data models for git diffs and commit messages."""
from dataclasses import dataclass
from typing import Literal


@dataclass
class FileDiff:
    """Represents changes to a single file."""

    path: str
    change_type: Literal["added", "modified", "deleted"]
    additions: int
    deletions: int
    diff_content: str


@dataclass
class GitDiff:
    """Represents the complete staged diff."""

    files: list[FileDiff]
    total_additions: int
    total_deletions: int


@dataclass
class CommitMessage:
    """Structured commit message following conventional commits format."""

    type: str  # feat, fix, docs, style, refactor, test, chore
    scope: str | None
    description: str
    body: str | None
    breaking_changes: list[str]
    emoji: str | None = None  # Optional gitmoji emoji

    def format(self) -> str:
        """Format commit message as conventional commit string.

        Returns:
            Formatted commit message string.
        """
        # First line: type(scope): description
        if self.scope:
            first_line = f"{self.type}({self.scope}): {self.description}"
        else:
            first_line = f"{self.type}: {self.description}"

        parts = [first_line]

        # Body paragraph (if present)
        if self.body:
            parts.append("")  # Blank line
            parts.append(self.body)

        # Breaking changes section (if present)
        if self.breaking_changes:
            parts.append("")  # Blank line
            parts.append("BREAKING CHANGE:")
            for change in self.breaking_changes:
                parts.append(f"- {change}")

        return "\n".join(parts)
