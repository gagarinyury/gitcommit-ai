"""Tests for commit message generator orchestration."""
from unittest.mock import AsyncMock, patch

import pytest

from gitcommit_ai.generator.generator import CommitMessageGenerator
from gitcommit_ai.generator.message import CommitMessage, FileDiff, GitDiff


@pytest.fixture
def sample_diff() -> GitDiff:
    """Create a sample GitDiff for testing."""
    return GitDiff(
        files=[
            FileDiff(
                path="src/test.py",
                change_type="modified",
                additions=3,
                deletions=1,
                diff_content="@@ diff @@",
            )
        ],
        total_additions=3,
        total_deletions=1,
    )


class TestCommitMessageGenerator:
    """Test commit message generation orchestration."""

    @pytest.mark.asyncio
    async def test_generate_uses_openai_provider(
        self, sample_diff: GitDiff
    ) -> None:
        """Generator uses OpenAI provider when configured."""
        mock_message = CommitMessage(
            type="feat",
            scope="test",
            description="add tests",
            body=None,
            breaking_changes=[],
        )

        with patch(
            "gitcommit_ai.core.git.GitOperations.get_staged_diff"
        ) as mock_git:
            mock_git.return_value = sample_diff

            with patch(
                "gitcommit_ai.providers.openai.OpenAIProvider.generate_commit_message",
                new_callable=AsyncMock,
            ) as mock_provider:
                mock_provider.return_value = mock_message

                generator = CommitMessageGenerator(
                    provider="openai", api_key="sk-test123"
                )
                message = await generator.generate()

                assert message == mock_message
                mock_provider.assert_called_once_with(sample_diff)

    @pytest.mark.asyncio
    async def test_generate_uses_anthropic_provider(
        self, sample_diff: GitDiff
    ) -> None:
        """Generator uses Anthropic provider when configured."""
        mock_message = CommitMessage(
            type="fix",
            scope=None,
            description="resolve bug",
            body=None,
            breaking_changes=[],
        )

        with patch(
            "gitcommit_ai.core.git.GitOperations.get_staged_diff"
        ) as mock_git:
            mock_git.return_value = sample_diff

            with patch(
                "gitcommit_ai.providers.anthropic.AnthropicProvider.generate_commit_message",
                new_callable=AsyncMock,
            ) as mock_provider:
                mock_provider.return_value = mock_message

                generator = CommitMessageGenerator(
                    provider="anthropic", api_key="sk-ant-test456"
                )
                message = await generator.generate()

                assert message == mock_message

    @pytest.mark.asyncio
    async def test_generate_raises_on_invalid_provider(self) -> None:
        """Generator raises error for unknown provider."""
        with pytest.raises(ValueError, match="Unknown provider"):
            CommitMessageGenerator(provider="unknown", api_key="test")  # type: ignore

    @pytest.mark.asyncio
    async def test_generate_extracts_git_diff(self) -> None:
        """Generator calls GitOperations to get staged diff."""
        with patch(
            "gitcommit_ai.core.git.GitOperations.get_staged_diff"
        ) as mock_git:
            mock_git.return_value = GitDiff(
                files=[], total_additions=0, total_deletions=0
            )

            with patch(
                "gitcommit_ai.providers.openai.OpenAIProvider.generate_commit_message",
                new_callable=AsyncMock,
            ) as mock_provider:
                mock_provider.return_value = CommitMessage(
                    type="chore",
                    scope=None,
                    description="empty",
                    body=None,
                    breaking_changes=[],
                )

                generator = CommitMessageGenerator(
                    provider="openai", api_key="sk-test"
                )
                await generator.generate()

                mock_git.assert_called_once()
