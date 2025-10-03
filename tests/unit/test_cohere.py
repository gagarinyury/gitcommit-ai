"""Tests for Cohere provider."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from gitcommit_ai.generator.message import CommitMessage, FileDiff, GitDiff
from gitcommit_ai.providers.cohere import CohereProvider


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


class TestCohereProvider:
    """Test Cohere commit message generation."""

    @pytest.mark.asyncio
    async def test_generate_commit_message_success(
        self, sample_diff: GitDiff
    ) -> None:
        """Generates commit message from Cohere API response."""
        mock_response = {
            "generations": [
                {
                    "text": "feat(core): add authentication module"
                }
            ]
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: mock_response,
                raise_for_status=lambda: None
            )

            provider = CohereProvider(api_key="test-key-123")
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
        import httpx

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock(status_code=429)
            mock_post.return_value = mock_response
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Rate limit", request=MagicMock(), response=mock_response
            )

            provider = CohereProvider(api_key="test-key-123")
            with pytest.raises(RuntimeError, match="rate limit"):
                await provider.generate_commit_message(sample_diff)

    @pytest.mark.asyncio
    async def test_generate_commit_message_network_error(
        self, sample_diff: GitDiff
    ) -> None:
        """Raises exception on network failure."""
        import httpx

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.RequestError("Connection timeout")

            provider = CohereProvider(api_key="test-key-123")
            with pytest.raises(RuntimeError, match="network error"):
                await provider.generate_commit_message(sample_diff)


class TestCohereValidation:
    """Test Cohere provider configuration validation."""

    def test_validate_config_with_api_key(self) -> None:
        """Validation passes when API key is provided."""
        provider = CohereProvider(api_key="test-key-123")
        errors = provider.validate_config()
        assert len(errors) == 0

    def test_validate_config_without_api_key(self) -> None:
        """Validation fails when API key is missing."""
        provider = CohereProvider(api_key=None)
        errors = provider.validate_config()
        assert len(errors) > 0
        assert any("API key" in err for err in errors)


class TestCoherePromptBuilding:
    """Test prompt construction for Cohere."""

    def test_build_prompt_includes_diff_content(
        self, sample_diff: GitDiff
    ) -> None:
        """Prompt includes diff statistics and file paths."""
        provider = CohereProvider(api_key="test-key-123")
        prompt = provider._build_prompt(sample_diff)

        assert "src/main.py" in prompt
        assert "5" in prompt  # additions
        assert "2" in prompt  # deletions

    def test_build_prompt_follows_conventional_commits(
        self, sample_diff: GitDiff
    ) -> None:
        """Prompt instructs AI to use conventional commit format."""
        provider = CohereProvider(api_key="test-key-123")
        prompt = provider._build_prompt(sample_diff)

        assert "conventional commit" in prompt.lower()
        assert any(
            t in prompt.lower() for t in ["feat", "fix", "docs", "refactor"]
        )
