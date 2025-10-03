"""Commit message generator orchestration."""
from typing import Literal

from gitcommit_ai.core.git import GitOperations
from gitcommit_ai.generator.message import CommitMessage
from gitcommit_ai.providers.anthropic import AnthropicProvider
from gitcommit_ai.providers.base import AIProvider
from gitcommit_ai.providers.deepseek import DeepSeekProvider
from gitcommit_ai.providers.openai import OpenAIProvider


class CommitMessageGenerator:
    """Orchestrates git diff extraction and AI message generation."""

    def __init__(
        self, provider: Literal["openai", "anthropic", "deepseek"], api_key: str
    ) -> None:
        """Initialize generator with AI provider.

        Args:
            provider: AI provider name ("openai", "anthropic", or "deepseek").
            api_key: API key for the provider.

        Raises:
            ValueError: If provider is unknown.
        """
        self.provider: AIProvider

        if provider == "openai":
            self.provider = OpenAIProvider(api_key=api_key)
        elif provider == "anthropic":
            self.provider = AnthropicProvider(api_key=api_key)
        elif provider == "deepseek":
            self.provider = DeepSeekProvider(api_key=api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def generate(self) -> CommitMessage:
        """Generate commit message for staged changes.

        Returns:
            CommitMessage object.

        Raises:
            GitError: If git operations fail.
            Exception: If AI provider fails.
        """
        # Extract staged diff
        diff = GitOperations.get_staged_diff()

        # Generate message using AI
        message = await self.provider.generate_commit_message(diff)

        return message
