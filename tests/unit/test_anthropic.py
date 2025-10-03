"""Tests for Anthropic provider."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from gitcommit_ai.generator.message import CommitMessage, FileDiff, GitDiff
from gitcommit_ai.providers.anthropic import AnthropicProvider


@pytest.fixture
def sample_diff() -> GitDiff:
    """Create a sample GitDiff for testing."""
    return GitDiff(
        files=[
            FileDiff(
                path="src/api.py",
                change_type="added",
                additions=15,
                deletions=0,
                diff_content="@@ sample diff @@",
            )
        ],
        total_additions=15,
        total_deletions=0,
    )


class TestAnthropicProvider:
    """Test Anthropic commit message generation."""

    @pytest.mark.asyncio
    async def test_generate_commit_message_success(
        self, sample_diff: GitDiff
    ) -> None:
        """Generates commit message from Anthropic API response."""
        mock_response = {
            "content": [
                {
                    "text": "feat(api): add REST endpoints\n\n"
                    "Created new API routes for user management."
                }
            ]
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200, json=lambda: mock_response
            )

            provider = AnthropicProvider(api_key="sk-ant-test456")
            message = await provider.generate_commit_message(sample_diff)

            assert isinstance(message, CommitMessage)
            assert message.type == "feat"
            assert message.scope == "api"
            assert "endpoints" in message.description.lower()

    @pytest.mark.asyncio
    async def test_generate_commit_message_api_error(
        self, sample_diff: GitDiff
    ) -> None:
        """Raises exception when API returns error."""
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=500,
                json=lambda: {"error": {"message": "Internal server error"}},
            )

            provider = AnthropicProvider(api_key="sk-ant-test456")
            with pytest.raises(Exception, match="server error"):
                await provider.generate_commit_message(sample_diff)

    @pytest.mark.asyncio
    async def test_generate_commit_message_network_error(
        self, sample_diff: GitDiff
    ) -> None:
        """Raises exception on network failure."""
        with patch(
            "httpx.AsyncClient.post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.side_effect = Exception("Network unreachable")

            provider = AnthropicProvider(api_key="sk-ant-test456")
            with pytest.raises(Exception, match="Network unreachable"):
                await provider.generate_commit_message(sample_diff)


class TestAnthropicValidation:
    """Test Anthropic provider configuration validation."""

    def test_validate_config_with_api_key(self) -> None:
        """Validation passes when API key is provided."""
        provider = AnthropicProvider(api_key="sk-ant-test456")
        errors = provider.validate_config()
        assert len(errors) == 0

    def test_validate_config_without_api_key(self) -> None:
        """Validation fails when API key is missing."""
        provider = AnthropicProvider(api_key=None)
        errors = provider.validate_config()
        assert len(errors) > 0
        assert any("API key" in err for err in errors)


class TestAnthropicPromptBuilding:
    """Test prompt construction for Anthropic."""

    def test_build_prompt_includes_diff_content(
        self, sample_diff: GitDiff
    ) -> None:
        """Prompt includes diff statistics and file paths."""
        provider = AnthropicProvider(api_key="sk-ant-test456")
        prompt = provider._build_prompt(sample_diff)

        assert "src/api.py" in prompt
        assert "15" in prompt  # additions

    def test_build_prompt_follows_conventional_commits(
        self, sample_diff: GitDiff
    ) -> None:
        """Prompt instructs AI to use conventional commit format."""
        provider = AnthropicProvider(api_key="sk-ant-test456")
        prompt = provider._build_prompt(sample_diff)

        assert "conventional commit" in prompt.lower()
        assert any(
            t in prompt.lower() for t in ["feat", "fix", "docs", "refactor"]
        )
