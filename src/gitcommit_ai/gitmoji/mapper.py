"""Gitmoji emoji mapping for conventional commit types."""
from gitcommit_ai.generator.message import CommitMessage

# Standard gitmoji mappings
GITMOJI_MAP = {
    "feat": "✨",  # sparkles - new feature
    "fix": "🐛",  # bug - bug fix
    "docs": "📝",  # memo - documentation
    "style": "🎨",  # art - style/formatting
    "refactor": "♻️",  # recycle - refactoring
    "test": "✅",  # check - tests
    "chore": "🔧",  # wrench - chores
    "perf": "🚀",  # rocket - performance
    "security": "🔒",  # lock - security
}

BREAKING_EMOJI = "💥"  # boom - breaking changes


class GitmojiMapper:
    """Maps conventional commit types to gitmoji emojis."""

    @staticmethod
    def get_emoji(commit_type: str) -> str | None:
        """Get emoji for a commit type.

        Args:
            commit_type: Conventional commit type (feat, fix, etc.)

        Returns:
            Emoji string or None if type not found.
        """
        return GITMOJI_MAP.get(commit_type)

    @staticmethod
    def format_message(message: CommitMessage, use_gitmoji: bool = False) -> str:
        """Format commit message with optional gitmoji prefix.

        Args:
            message: CommitMessage object.
            use_gitmoji: If True, prepend emoji to message.

        Returns:
            Formatted commit message string.
        """
        if not use_gitmoji:
            return message.format()

        # Check for breaking changes first
        if message.breaking_changes:
            emoji_prefix = BREAKING_EMOJI
        else:
            emoji = GitmojiMapper.get_emoji(message.type)
            if not emoji:
                # No emoji for this type, return plain format
                return message.format()
            emoji_prefix = emoji

        return f"{emoji_prefix} {message.format()}"
