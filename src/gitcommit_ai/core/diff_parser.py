"""Parser for git unified diff format."""
import re
from typing import Literal

from gitcommit_ai.generator.message import FileDiff, GitDiff


class DiffParser:
    """Parses git unified diff output into structured data."""

    @staticmethod
    def parse(diff_text: str) -> GitDiff:
        """Parse unified diff text into GitDiff object.

        Args:
            diff_text: Raw output from `git diff`.

        Returns:
            GitDiff object with structured file changes.
        """
        if not diff_text.strip():
            return GitDiff(files=[], total_additions=0, total_deletions=0)

        files: list[FileDiff] = []
        total_additions = 0
        total_deletions = 0

        # Split by file boundaries
        file_chunks = re.split(r"^diff --git ", diff_text, flags=re.MULTILINE)

        for chunk in file_chunks[1:]:  # Skip empty first element
            file_diff = DiffParser._parse_file_chunk(chunk)
            if file_diff:
                files.append(file_diff)
                total_additions += file_diff.additions
                total_deletions += file_diff.deletions

        return GitDiff(
            files=files,
            total_additions=total_additions,
            total_deletions=total_deletions,
        )

    @staticmethod
    def _parse_file_chunk(chunk: str) -> FileDiff | None:
        """Parse a single file's diff chunk.

        Args:
            chunk: Diff text for one file.

        Returns:
            FileDiff object or None if parsing fails.
        """
        # Extract file path (e.g., "a/src/file.py b/src/file.py")
        path_match = re.search(r"a/(.+?) b/", chunk)
        if not path_match:
            return None
        file_path = path_match.group(1)

        # Determine change type
        change_type: Literal["added", "modified", "deleted"]
        if "new file mode" in chunk:
            change_type = "added"
        elif "deleted file mode" in chunk:
            change_type = "deleted"
        else:
            change_type = "modified"

        # Count additions and deletions
        additions = DiffParser._count_additions(chunk)
        deletions = DiffParser._count_deletions(chunk)

        return FileDiff(
            path=file_path,
            change_type=change_type,
            additions=additions,
            deletions=deletions,
            diff_content=chunk,
        )

    @staticmethod
    def _count_additions(diff_content: str) -> int:
        """Count lines added (starting with +, excluding +++).

        Args:
            diff_content: Diff hunk content.

        Returns:
            Number of added lines.
        """
        lines = diff_content.split("\n")
        return sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))

    @staticmethod
    def _count_deletions(diff_content: str) -> int:
        """Count lines deleted (starting with -, excluding ---).

        Args:
            diff_content: Diff hunk content.

        Returns:
            Number of deleted lines.
        """
        lines = diff_content.split("\n")
        return sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))
