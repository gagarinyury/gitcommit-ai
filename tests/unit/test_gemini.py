"""Tests for Google Gemini provider."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from gitcommit_ai.generator.message import CommitMessage, FileDiff, GitDiff
from gitcommit_ai.providers.gemini import GeminiProvider


@pytest.fixture
def sample_diff() -> GitDiff:
    """Create a sample GitDiff for testing."""
    return GitDiff(
        files=[
            FileDiff(
                path="src/auth.py",
                change_type="modified",
                additions=10,
                deletions=3,
                diff_content="@@ authentication changes @@",
            )
        ],
        total_additions=10,
        total_deletions=3,
    )


class TestGeminiProvider:
    """Test Gemini commit message generation."""

    @pytest.mark.asyncio
    async def test_generate_commit_message_success(
        self, sample_diff: GitDiff
    ) -> None:
        """Generates commit message from Gemini API response."""
        mock_response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "feat(auth): implement JWT authentication"
                            }
                        ]
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

            provider = GeminiProvider(api_key="test-gemini-key")
            message = await provider.generate_commit_message(sample_diff)

            assert isinstance(message, CommitMessage)
            assert message.type == "feat"
            assert message.scope == "auth"
            assert "authentication" in message.description.lower()

    @pytest.mark.asyncio
    async def test_generate_commit_message_api_error(
        self, sample_diff: GitDiff
    ) -> None:
        """Raises exception when API returns error."""
        import httpx

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock(status_code=403)
            mock_post.return_value = mock_response
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Invalid API key", request=MagicMock(), response=mock_response
            )

            provider = GeminiProvider(api_key="invalid-key")
            with pytest.raises(RuntimeError, match="API key"):
                await provider.generate_commit_message(sample_diff)

    @pytest.mark.asyncio
    async def test_generate_commit_message_network_error(
        self, sample_diff: GitDiff
    ) -> None:
        """Raises exception on network failure."""
        import httpx

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.RequestError("Network unreachable")

            provider = GeminiProvider(api_key="test-key")
            with pytest.raises(RuntimeError, match="network error"):
                await provider.generate_commit_message(sample_diff)


class TestGeminiValidation:
    """Test Gemini provider configuration validation."""

    def test_validate_config_with_api_key(self) -> None:
        """Validation passes when API key is provided."""
        provider = GeminiProvider(api_key="test-gemini-key")
        errors = provider.validate_config()
        assert len(errors) == 0

    def test_validate_config_without_api_key(self) -> None:
        """Validation fails when API key is missing."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}, clear=False):
            provider = GeminiProvider(api_key=None)
            errors = provider.validate_config()
            assert len(errors) > 0
            assert any("API key" in err for err in errors)

    def test_validate_config_accepts_google_api_key_env(self) -> None:
        """Accepts GOOGLE_API_KEY environment variable."""
        with patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}):
            provider = GeminiProvider()
            errors = provider.validate_config()
            assert len(errors) == 0


class TestGeminiPromptBuilding:
    """Test prompt construction for Gemini."""

    def test_build_prompt_includes_diff_content(
        self, sample_diff: GitDiff
    ) -> None:
        """Prompt includes diff statistics and file paths."""
        provider = GeminiProvider(api_key="test-key")
        prompt = provider._build_prompt(sample_diff)

        assert "src/auth.py" in prompt
        assert "10" in prompt  # additions
        assert "3" in prompt  # deletions

    def test_build_prompt_follows_conventional_commits(
        self, sample_diff: GitDiff
    ) -> None:
        """Prompt instructs AI to use conventional commit format."""
        provider = GeminiProvider(api_key="test-key")
        prompt = provider._build_prompt(sample_diff)

        assert "conventional commit" in prompt.lower()
        assert any(
            t in prompt.lower() for t in ["feat", "fix", "docs", "refactor"]
        )
