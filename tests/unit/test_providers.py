"""Tests for AI provider abstraction."""
from abc import ABC

import pytest

from gitcommit_ai.providers.base import AIProvider


class TestAIProviderAbstract:
    """Test AIProvider abstract base class."""

    def test_cannot_instantiate_abstract_provider(self) -> None:
        """Cannot directly instantiate AIProvider (abstract class)."""
        with pytest.raises(TypeError, match="abstract"):
            AIProvider()  # type: ignore

    def test_provider_is_abstract_base_class(self) -> None:
        """AIProvider is an ABC."""
        assert issubclass(AIProvider, ABC)

    def test_provider_has_required_methods(self) -> None:
        """AIProvider defines required abstract methods."""
        # Check that abstract methods exist
        abstract_methods = AIProvider.__abstractmethods__
        assert "generate_commit_message" in abstract_methods
        assert "validate_config" in abstract_methods


class ConcreteProvider(AIProvider):
    """Concrete implementation for testing."""

    async def generate_commit_message(self, diff):  # type: ignore
        """Dummy implementation."""
        from gitcommit_ai.generator.message import CommitMessage

        return CommitMessage(
            type="test",
            scope=None,
            description="test message",
            body=None,
            breaking_changes=[],
        )

    def validate_config(self) -> list[str]:
        """Dummy implementation."""
        return []


class TestConcreteProvider:
    """Test that concrete implementations work correctly."""

    @pytest.mark.asyncio
    async def test_can_instantiate_concrete_provider(self) -> None:
        """Can instantiate a concrete AIProvider implementation."""
        provider = ConcreteProvider()
        assert isinstance(provider, AIProvider)

    @pytest.mark.asyncio
    async def test_concrete_provider_can_generate_message(self) -> None:
        """Concrete provider can generate commit messages."""
        from gitcommit_ai.generator.message import GitDiff

        provider = ConcreteProvider()
        diff = GitDiff(files=[], total_additions=0, total_deletions=0)
        message = await provider.generate_commit_message(diff)
        assert message.type == "test"
