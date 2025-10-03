"""Tests for Mistral AI provider."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from gitcommit_ai.generator.message import CommitMessage, FileDiff, GitDiff
from gitcommit_ai.providers.mistral import MistralProvider


@pytest.fixture
def sample_diff() -> GitDiff:
    """Create a sample GitDiff for testing."""
    return GitDiff(
        files=[
            FileDiff(
                path="tests/test_api.py",
                change_type="added",
                additions=25,
                deletions=0,
                diff_content="@@ new test file @@",
            )
        ],
        total_additions=25,
        total_deletions=0,
    )


class TestMistralProvider:
    """Test Mistral commit message generation."""

    @pytest.mark.asyncio
    async def test_generate_commit_message_success(
        self, sample_diff: GitDiff
    ) -> None:
        """Generates commit message from Mistral API response."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "test: add API integration tests"
                    }
                }
            ]
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: mock_response,
                raise_for_status=lambda: None
            )

            provider = MistralProvider(api_key="test-mistral-key")
            message = await provider.generate_commit_message(sample_diff)

            assert isinstance(message, CommitMessage)
            assert message.type == "test"
            assert "test" in message.description.lower() or "api" in message.description.lower()

    @pytest.mark.asyncio
    async def test_generate_commit_message_api_error(
        self, sample_diff: GitDiff
    ) -> None:
        """Raises exception when API returns error."""
        import httpx

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock(status_code=401)
            mock_post.return_value = mock_response
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Unauthorized", request=MagicMock(), response=mock_response
            )

            provider = MistralProvider(api_key="invalid-key")
            with pytest.raises(RuntimeError, match="API key"):
                await provider.generate_commit_message(sample_diff)

    @pytest.mark.asyncio
    async def test_generate_commit_message_network_error(
        self, sample_diff: GitDiff
    ) -> None:
        """Raises exception on network failure."""
        import httpx

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.RequestError("Connection failed")

            provider = MistralProvider(api_key="test-key")
            with pytest.raises(RuntimeError, match="network error"):
                await provider.generate_commit_message(sample_diff)


class TestMistralValidation:
    """Test Mistral provider configuration validation."""

    def test_validate_config_with_api_key(self) -> None:
        """Validation passes when API key is provided."""
        provider = MistralProvider(api_key="test-mistral-key")
        errors = provider.validate_config()
        assert len(errors) == 0

    def test_validate_config_without_api_key(self) -> None:
        """Validation fails when API key is missing."""
        provider = MistralProvider(api_key=None)
        errors = provider.validate_config()
        assert len(errors) > 0
        assert any("API key" in err for err in errors)


class TestMistralPromptBuilding:
    """Test prompt construction for Mistral."""

    def test_build_prompt_includes_diff_content(
        self, sample_diff: GitDiff
    ) -> None:
        """Prompt includes diff statistics and file paths."""
        provider = MistralProvider(api_key="test-key")
        prompt = provider._build_prompt(sample_diff)

        assert "tests/test_api.py" in prompt
        assert "25" in prompt  # additions

    def test_build_prompt_follows_conventional_commits(
        self, sample_diff: GitDiff
    ) -> None:
        """Prompt instructs AI to use conventional commit format."""
        provider = MistralProvider(api_key="test-key")
        prompt = provider._build_prompt(sample_diff)

        assert "conventional commit" in prompt.lower()
        assert any(
            t in prompt.lower() for t in ["feat", "fix", "docs", "test"]
        )
