"""Tests for MultiSuggestionGenerator."""
import pytest

from gitcommit_ai.generator.multi_generator import MultiSuggestionGenerator
from gitcommit_ai.generator.message import CommitMessage


class TestMultiSuggestionGenerator:
    """Test suite for multi-suggestion generation."""

    @pytest.mark.asyncio
    async def test_generate_multiple_creates_n_suggestions(self) -> None:
        """Generates exactly N suggestions."""
        generator = MultiSuggestionGenerator()

        # Mock generate function
        async def mock_generate(temp: float) -> CommitMessage:
            return CommitMessage(
                type="feat",
                scope=None,
                description=f"test message temp={temp}",
                body=None,
                breaking_changes=None,
                emoji=None
            )

        suggestions = await generator.generate_multiple(
            count=3,
            generate_fn=mock_generate
        )

        assert len(suggestions) == 3

    @pytest.mark.asyncio
    async def test_suggestions_have_different_temperatures(self) -> None:
        """Each suggestion uses different temperature."""
        generator = MultiSuggestionGenerator()
        temperatures_used = []

        async def mock_generate(temp: float) -> CommitMessage:
            temperatures_used.append(temp)
            return CommitMessage(
                type="feat",
                scope=None,
                description=f"message {temp}",
                body=None,
                breaking_changes=None,
                emoji=None
            )

        await generator.generate_multiple(count=3, generate_fn=mock_generate)

        # All temperatures should be different
        assert len(set(temperatures_used)) == 3
        # Should be in range 0.3-0.7
        assert all(0.3 <= t <= 0.7 for t in temperatures_used)

    @pytest.mark.asyncio
    async def test_all_suggestions_are_unique(self) -> None:
        """Validates all suggestions are unique."""
        generator = MultiSuggestionGenerator()
        counter = [0]

        async def mock_generate(temp: float) -> CommitMessage:
            counter[0] += 1
            return CommitMessage(
                type="feat",
                scope=None,
                description=f"unique message {counter[0]}",
                body=None,
                breaking_changes=None,
                emoji=None
            )

        suggestions = await generator.generate_multiple(
            count=3,
            generate_fn=mock_generate
        )

        # Check descriptions are unique
        descriptions = [s.description for s in suggestions]
        assert len(set(descriptions)) == 3

    @pytest.mark.asyncio
    async def test_count_validation(self) -> None:
        """Validates count parameter (1-10)."""
        generator = MultiSuggestionGenerator()

        async def mock_generate(temp: float) -> CommitMessage:
            return CommitMessage("feat", None, "test", None, None, None)

        # Count too low
        with pytest.raises(ValueError, match="count must be between 1 and 10"):
            await generator.generate_multiple(count=0, generate_fn=mock_generate)

        # Count too high
        with pytest.raises(ValueError, match="count must be between 1 and 10"):
            await generator.generate_multiple(count=11, generate_fn=mock_generate)
