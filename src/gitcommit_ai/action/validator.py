"""Commit message validator."""
import re
from typing import Tuple


class CommitValidator:
    """Validates commit messages against conventional commits format."""

    CONVENTIONAL_COMMIT_PATTERN = re.compile(
        r'^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?!?: .+'
    )

    VALID_TYPES = {'feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore'}

    def validate_conventional(self, message: str) -> Tuple[bool, list[str]]:
        """Validate if message follows conventional commits format.

        Args:
            message: Commit message to validate.

        Returns:
            Tuple of (is_valid, list_of_issues).
        """
        issues = []

        if not message or message.strip() == "":
            return (False, ["Empty commit message"])

        # Check if matches conventional format
        if not self.CONVENTIONAL_COMMIT_PATTERN.match(message):
            # Identify specific issues
            if not any(message.startswith(t) for t in self.VALID_TYPES):
                # Check if it's invalid type or missing type
                first_word = message.split(':')[0].split('(')[0]
                if first_word in self.VALID_TYPES:
                    pass  # Valid type, other issue
                elif ':' not in message:
                    issues.append("Missing commit type (feat, fix, docs, etc.)")
                else:
                    issues.append(f"Invalid commit type '{first_word}' (use: feat, fix, docs, style, refactor, test, chore)")

            if ':' in message and message.split(':')[1].strip() == "":
                issues.append("Missing description after colon")

            if not issues:
                issues.append("Does not follow conventional commits format")

            return (False, issues)

        # Valid conventional commit
        return (True, [])
