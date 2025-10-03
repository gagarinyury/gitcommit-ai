"""Multi-suggestion generator for commit messages."""
from collections.abc import Awaitable, Callable

from gitcommit_ai.generator.message import CommitMessage


class MultiSuggestionGenerator:
    """Generates multiple commit message suggestions with varying temperatures."""

    async def generate_multiple(
        self,
        count: int,
        generate_fn: Callable[[float], Awaitable[CommitMessage]]
    ) -> list[CommitMessage]:
        """Generate multiple suggestions with different temperatures.

        Args:
            count: Number of suggestions to generate (1-10).
            generate_fn: Async function that takes temperature and returns CommitMessage.

        Returns:
            List of CommitMessage suggestions.

        Raises:
            ValueError: If count is not in range 1-10.
        """
        if count < 1 or count > 10:
            raise ValueError("count must be between 1 and 10")

        # Calculate temperature range using linear interpolation
        if count == 1:
            temperatures = [0.5]  # Middle value
        else:
            step = (0.7 - 0.3) / (count - 1)
            temperatures = [0.3 + i * step for i in range(count)]

        # Generate suggestions
        suggestions = []
        for temp in temperatures:
            message = await generate_fn(temp)
            suggestions.append(message)

        return suggestions
