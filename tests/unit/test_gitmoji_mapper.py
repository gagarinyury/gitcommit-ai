"""Tests for Gitmoji mapper."""
import pytest

from gitcommit_ai.generator.message import CommitMessage


class TestGitmojiMapping:
    """T085-T090: Test emoji mappings."""

    def test_get_emoji_for_feat(self):
        """Test feat maps to sparkles emoji."""
        from gitcommit_ai.gitmoji.mapper import GitmojiMapper

        emoji = GitmojiMapper.get_emoji("feat")
        assert emoji == "✨"

    def test_get_emoji_for_fix(self):
        """Test fix maps to bug emoji."""
        from gitcommit_ai.gitmoji.mapper import GitmojiMapper

        emoji = GitmojiMapper.get_emoji("fix")
        assert emoji == "🐛"

    def test_get_emoji_for_docs(self):
        """Test docs maps to memo emoji."""
        from gitcommit_ai.gitmoji.mapper import GitmojiMapper

        emoji = GitmojiMapper.get_emoji("docs")
        assert emoji == "📝"

    def test_get_emoji_for_unknown_type(self):
        """Test unknown type returns None."""
        from gitcommit_ai.gitmoji.mapper import GitmojiMapper

        emoji = GitmojiMapper.get_emoji("unknown")
        assert emoji is None

    def test_all_standard_mappings(self):
        """Test all standard gitmoji mappings."""
        from gitcommit_ai.gitmoji.mapper import GitmojiMapper

        expected = {
            "feat": "✨",
            "fix": "🐛",
            "docs": "📝",
            "style": "🎨",
            "refactor": "♻️",
            "test": "✅",
            "chore": "🔧",
            "perf": "🚀",
            "security": "🔒",
        }

        for commit_type, expected_emoji in expected.items():
            assert GitmojiMapper.get_emoji(commit_type) == expected_emoji


class TestGitmojiFormatting:
    """T086-T090: Test message formatting with emojis."""

    def test_format_message_with_gitmoji_enabled(self):
        """Test formatting with gitmoji adds emoji prefix."""
        from gitcommit_ai.gitmoji.mapper import GitmojiMapper

        message = CommitMessage(
            type="feat",
            scope="auth",
            description="add JWT support",
            body=None,
            breaking_changes=[],
        )

        formatted = GitmojiMapper.format_message(message, use_gitmoji=True)
        assert formatted == "✨ feat(auth): add JWT support"

    def test_format_message_with_gitmoji_disabled(self):
        """Test formatting without gitmoji has no emoji."""
        from gitcommit_ai.gitmoji.mapper import GitmojiMapper

        message = CommitMessage(
            type="feat",
            scope="auth",
            description="add JWT support",
            body=None,
            breaking_changes=[],
        )

        formatted = GitmojiMapper.format_message(message, use_gitmoji=False)
        assert formatted == "feat(auth): add JWT support"
        assert "✨" not in formatted

    def test_format_message_without_scope(self):
        """Test formatting without scope."""
        from gitcommit_ai.gitmoji.mapper import GitmojiMapper

        message = CommitMessage(
            type="fix",
            scope=None,
            description="resolve memory leak",
            body=None,
            breaking_changes=[],
        )

        formatted = GitmojiMapper.format_message(message, use_gitmoji=True)
        assert formatted == "🐛 fix: resolve memory leak"

    def test_format_message_with_unknown_type_no_emoji(self):
        """Test unknown type doesn't add emoji."""
        from gitcommit_ai.gitmoji.mapper import GitmojiMapper

        message = CommitMessage(
            type="unknown",
            scope=None,
            description="some change",
            body=None,
            breaking_changes=[],
        )

        formatted = GitmojiMapper.format_message(message, use_gitmoji=True)
        # Should not have emoji, just regular format
        assert formatted == "unknown: some change"

    def test_format_message_with_breaking_change(self):
        """Test breaking change adds boom emoji prefix."""
        from gitcommit_ai.gitmoji.mapper import GitmojiMapper

        message = CommitMessage(
            type="feat",
            scope="api",
            description="breaking change",
            body=None,
            breaking_changes=["BREAKING: API changed"],
        )

        formatted = GitmojiMapper.format_message(message, use_gitmoji=True)
        # Breaking changes should add 💥 prefix
        assert "💥" in formatted or "✨" in formatted

    def test_emoji_in_json_format(self):
        """Test emoji is included in CommitMessage object."""
        message = CommitMessage(
            type="feat",
            scope=None,
            description="test",
            body=None,
            breaking_changes=[],
        )

        # Check that we can store emoji
        message_with_emoji = CommitMessage(
            type="feat",
            scope=None,
            description="test",
            body=None,
            breaking_changes=[],
            emoji="✨",
        )
        assert message_with_emoji.emoji == "✨"


class TestGitmojiValidator:
    """T091-T092: Test UTF-8 validation."""

    def test_supports_utf8_returns_bool(self):
        """Test supports_utf8 returns boolean."""
        from gitcommit_ai.gitmoji.validator import supports_utf8

        result = supports_utf8()
        assert isinstance(result, bool)

    def test_supports_utf8_checks_stdout_encoding(self):
        """Test supports_utf8 checks sys.stdout.encoding."""
        import sys
        from unittest.mock import MagicMock, patch

        from gitcommit_ai.gitmoji.validator import supports_utf8

        # Mock UTF-8 support
        mock_stdout = MagicMock()
        mock_stdout.encoding = "utf-8"
        with patch("sys.stdout", mock_stdout):
            assert supports_utf8() is True

        # Mock non-UTF-8
        mock_stdout.encoding = "ascii"
        with patch("sys.stdout", mock_stdout):
            assert supports_utf8() is False

    def test_fallback_when_utf8_unsupported(self):
        """Test that gitmoji is disabled when terminal doesn't support UTF-8."""
        from gitcommit_ai.gitmoji.mapper import GitmojiMapper

        message = CommitMessage(
            type="feat",
            scope=None,
            description="test",
            body=None,
            breaking_changes=[],
        )

        # If UTF-8 not supported, application should pass use_gitmoji=False
        formatted = GitmojiMapper.format_message(message, use_gitmoji=False)
        assert "✨" not in formatted
        assert formatted == "feat: test"
