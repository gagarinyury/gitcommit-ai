"""Abstract base class for AI providers."""
from abc import ABC, abstractmethod

from gitcommit_ai.generator.message import CommitMessage, GitDiff


class AIProvider(ABC):
    """Abstract interface for AI commit message generation providers."""

    @abstractmethod
    async def generate_commit_message(self, diff: GitDiff) -> CommitMessage:
        """Generate a commit message from a git diff.

        Args:
            diff: GitDiff object containing staged changes.

        Returns:
            CommitMessage object in conventional commit format.

        Raises:
            Exception: If API call fails or response is invalid.
        """
        pass

    @abstractmethod
    def validate_config(self) -> list[str]:
        """Validate provider configuration.

        Returns:
            List of validation error messages (empty if valid).
        """
        pass
