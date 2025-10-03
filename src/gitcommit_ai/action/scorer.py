"""Commit message quality scorer."""
import re


class CommitScorer:
    """Scores commit message quality from 0-100."""

    VALID_TYPES = {'feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore'}
    GENERIC_WORDS = {'stuff', 'things', 'work', 'update', 'change', 'misc'}

    def score(self, message: str) -> int:
        """Score commit message quality 0-100.

        Args:
            message: Commit message to score.

        Returns:
            Score from 0 (worst) to 100 (best).
        """
        score = 0

        # Check for type (+40 points)
        # Accept both "feat:" and "feat " formats
        has_type = any(
            message.startswith(t + ':') or message.startswith(t + '(') or message.startswith(t + ' ')
            for t in self.VALID_TYPES
        )
        if has_type:
            score += 40

        # Check for scope (+20 points)
        has_scope = '(' in message and ')' in message
        if has_scope:
            score += 20

        # Extract description
        if ':' in message:
            description = message.split(':', 1)[1].strip()
        else:
            description = message

        # Check description length (+30 points if 10-80 chars)
        desc_len = len(description)
        if 10 <= desc_len <= 80:
            score += 30
        elif 5 <= desc_len < 10:
            score += 15  # Partial points
        elif desc_len > 80:
            score += 20  # Partial points

        # Check for generic words (penalty for generic, bonus for good)
        if any(word in description.lower() for word in self.GENERIC_WORDS):
            score -= 20  # Penalty
        elif has_type:
            score += 10  # Bonus for non-generic with type

        return max(0, min(100, score))  # Clamp to 0-100

    def get_issues(self, message: str) -> list[str]:
        """Get list of quality issues.

        Args:
            message: Commit message to analyze.

        Returns:
            List of issue descriptions.
        """
        issues = []

        # Check for type
        if not any(message.startswith(t) for t in self.VALID_TYPES):
            issues.append("Missing conventional commit type")

        # Extract description
        if ':' in message:
            description = message.split(':', 1)[1].strip()
        else:
            description = message

        # Check for generic words
        found_generic = [word for word in self.GENERIC_WORDS if word in description.lower()]
        if found_generic:
            issues.append(f"Contains generic words: {', '.join(found_generic)}")

        # Check description length
        if len(description) < 10:
            issues.append("Description too short (should be at least 10 characters)")
        elif len(description) > 80:
            issues.append("Description too long (should be under 80 characters)")

        return issues
