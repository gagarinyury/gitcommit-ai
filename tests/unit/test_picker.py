"""Tests for InteractivePicker."""
from unittest.mock import MagicMock, patch

import pytest

from gitcommit_ai.cli.picker import InteractivePicker
from gitcommit_ai.generator.message import CommitMessage


class TestInteractivePicker:
    """Test suite for interactive picker."""

    def test_pick_returns_selected_suggestion(self) -> None:
        """Returns the selected commit message."""
        suggestions = [
            CommitMessage("feat", None, "option 1", None, None, None),
            CommitMessage("fix", None, "option 2", None, None, None),
            CommitMessage("docs", None, "option 3", None, None, None),
        ]

        picker = InteractivePicker()

        with patch("builtins.input", return_value="2"):
            selected = picker.pick(suggestions)

        assert selected == suggestions[1]  # Index 1 = option 2

    def test_pick_handles_invalid_input(self) -> None:
        """Re-prompts on invalid input."""
        suggestions = [
            CommitMessage("feat", None, "option 1", None, None, None),
            CommitMessage("fix", None, "option 2", None, None, None),
        ]

        picker = InteractivePicker()

        # First invalid, then valid
        with patch("builtins.input", side_effect=["invalid", "1"]):
            selected = picker.pick(suggestions)

        assert selected == suggestions[0]

    def test_pick_supports_number_selection(self) -> None:
        """Supports selecting by number (1-N)."""
        suggestions = [
            CommitMessage("feat", None, "first", None, None, None),
            CommitMessage("fix", None, "second", None, None, None),
            CommitMessage("docs", None, "third", None, None, None),
        ]

        picker = InteractivePicker()

        # Select option 3
        with patch("builtins.input", return_value="3"):
            selected = picker.pick(suggestions)

        assert selected == suggestions[2]

    def test_pick_returns_none_on_cancel(self) -> None:
        """Returns None when user cancels (Ctrl+C)."""
        suggestions = [
            CommitMessage("feat", None, "test", None, None, None),
        ]

        picker = InteractivePicker()

        with patch("builtins.input", side_effect=KeyboardInterrupt):
            selected = picker.pick(suggestions)

        assert selected is None
