"""Tests for OpenAI provider."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from gitcommit_ai.generator.message import CommitMessage, FileDiff, GitDiff
from gitcommit_ai.providers.openai import OpenAIProvider


@pytest.fixture
def sample_diff() -> GitDiff:
    """Create a sample GitDiff for testing."""
    return GitDiff(
        files=[
            FileDiff(
                path="src/main.py",
                change_type="modified",
                additions=5,
                deletions=2,
                diff_content="@@ sample diff @@",
            )
        ],
        total_additions=5,
        total_deletions=2,
    )


class TestOpenAIProvider:
    """Test OpenAI commit message generation."""

    @pytest.mark.asyncio
    async def test_generate_commit_message_success(
        self, sample_diff: GitDiff
    ) -> None:
        """Generates commit message from OpenAI API response."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "feat(core): add authentication module\n\n"
                        "Implemented JWT-based authentication."
                    }
                }
            ]
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200, json=lambda: mock_response
            )

            provider = OpenAIProvider(api_key="sk-test123")
            message = await provider.generate_commit_message(sample_diff)

            assert isinstance(message, CommitMessage)
            assert message.type == "feat"
            assert message.scope == "core"
            assert "authentication" in message.description.lower()

    @pytest.mark.asyncio
    async def test_generate_commit_message_api_error(
        self, sample_diff: GitDiff
    ) -> None:
        """Raises exception when API returns error."""
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=429,  # Rate limit
                json=lambda: {"error": {"message": "Rate limit exceeded"}},
            )

            provider = OpenAIProvider(api_key="sk-test123")
            with pytest.raises(Exception, match="Rate limit"):
                await provider.generate_commit_message(sample_diff)

    @pytest.mark.asyncio
    async def test_generate_commit_message_network_error(
        self, sample_diff: GitDiff
    ) -> None:
        """Raises exception on network failure."""
        with patch(
            "httpx.AsyncClient.post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.side_effect = Exception("Connection timeout")

            provider = OpenAIProvider(api_key="sk-test123")
            with pytest.raises(Exception, match="Connection timeout"):
                await provider.generate_commit_message(sample_diff)


class TestOpenAIValidation:
    """Test OpenAI provider configuration validation."""

    def test_validate_config_with_api_key(self) -> None:
        """Validation passes when API key is provided."""
        provider = OpenAIProvider(api_key="sk-test123")
        errors = provider.validate_config()
        assert len(errors) == 0

    def test_validate_config_without_api_key(self) -> None:
        """Validation fails when API key is missing."""
        provider = OpenAIProvider(api_key=None)
        errors = provider.validate_config()
        assert len(errors) > 0
        assert any("API key" in err for err in errors)


class TestOpenAIPromptBuilding:
    """Test prompt construction for OpenAI."""

    def test_build_prompt_includes_diff_content(
        self, sample_diff: GitDiff
    ) -> None:
        """Prompt includes diff statistics and file paths."""
        provider = OpenAIProvider(api_key="sk-test123")
        prompt = provider._build_prompt(sample_diff)

        assert "src/main.py" in prompt
        assert "5" in prompt  # additions
        assert "2" in prompt  # deletions

    def test_build_prompt_follows_conventional_commits(
        self, sample_diff: GitDiff
    ) -> None:
        """Prompt instructs AI to use conventional commit format."""
        provider = OpenAIProvider(api_key="sk-test123")
        prompt = provider._build_prompt(sample_diff)

        assert "conventional commit" in prompt.lower()
        assert any(
            t in prompt.lower() for t in ["feat", "fix", "docs", "refactor"]
        )
