"""Tests for DeepSeek provider."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from gitcommit_ai.generator.message import CommitMessage, FileDiff, GitDiff
from gitcommit_ai.providers.deepseek import DeepSeekProvider


@pytest.fixture
def sample_diff() -> GitDiff:
    """Create a sample GitDiff for testing."""
    return GitDiff(
        files=[
            FileDiff(
                path="src/auth.py",
                change_type="modified",
                additions=15,
                deletions=3,
                diff_content="@@ sample diff @@",
            )
        ],
        total_additions=15,
        total_deletions=3,
    )


class TestDeepSeekProvider:
    """Test DeepSeek commit message generation."""

    @pytest.mark.asyncio
    async def test_init_with_api_key(self) -> None:
        """T114: Initializes with provided API key."""
        provider = DeepSeekProvider(api_key="sk-test123")
        assert provider.api_key == "sk-test123"
        assert provider.model == "deepseek-chat"

    @pytest.mark.asyncio
    async def test_init_with_custom_model(self) -> None:
        """T114: Initializes with custom model."""
        provider = DeepSeekProvider(api_key="sk-test123", model="deepseek-coder")
        assert provider.model == "deepseek-coder"

    @pytest.mark.asyncio
    async def test_init_without_api_key_raises_error(self, monkeypatch) -> None:
        """T119: Missing API key raises ValueError."""
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        with pytest.raises(ValueError, match="DEEPSEEK_API_KEY"):
            DeepSeekProvider(api_key=None)

    @pytest.mark.asyncio
    async def test_generate_commit_message_success(
        self, sample_diff: GitDiff
    ) -> None:
        """T115: Generates commit message from DeepSeek API response."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "feat(auth): implement JWT token refresh\n\n"
                        "Automated token refresh maintains user sessions."
                    }
                }
            ]
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200, json=lambda: mock_response
            )

            provider = DeepSeekProvider(api_key="sk-test123")
            message = await provider.generate_commit_message(sample_diff)

            assert isinstance(message, CommitMessage)
            assert message.type == "feat"
            assert message.scope == "auth"
            assert "token refresh" in message.description.lower()

    @pytest.mark.asyncio
    async def test_api_error_401_unauthorized(self, sample_diff: GitDiff) -> None:
        """T116: Handles 401 Unauthorized error."""
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=401,
                json=lambda: {"error": {"message": "Invalid API key"}},
            )

            provider = DeepSeekProvider(api_key="sk-invalid")
            with pytest.raises(Exception, match="Invalid API key"):
                await provider.generate_commit_message(sample_diff)

    @pytest.mark.asyncio
    async def test_api_error_429_rate_limit(self, sample_diff: GitDiff) -> None:
        """T116: Handles 429 Rate Limit error."""
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=429,
                json=lambda: {"error": {"message": "Rate limit exceeded"}},
            )

            provider = DeepSeekProvider(api_key="sk-test123")
            with pytest.raises(Exception, match="Rate limit"):
                await provider.generate_commit_message(sample_diff)

    @pytest.mark.asyncio
    async def test_api_error_500_server_error(self, sample_diff: GitDiff) -> None:
        """T116: Handles 500 Server Error."""
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=500,
                json=lambda: {"error": {"message": "Internal server error"}},
            )

            provider = DeepSeekProvider(api_key="sk-test123")
            with pytest.raises(Exception, match="Internal server error"):
                await provider.generate_commit_message(sample_diff)

    @pytest.mark.asyncio
    async def test_response_parsing_openai_format(self, sample_diff: GitDiff) -> None:
        """T117: Parses OpenAI-compatible response format."""
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "fix(parser): resolve null pointer in date parsing"
                    }
                }
            ]
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200, json=lambda: mock_response
            )

            provider = DeepSeekProvider(api_key="sk-test123")
            message = await provider.generate_commit_message(sample_diff)

            assert message.type == "fix"
            assert message.scope == "parser"
            assert "null pointer" in message.description

    @pytest.mark.asyncio
    async def test_model_selection_deepseek_chat(self, sample_diff: GitDiff) -> None:
        """T118: Uses deepseek-chat model."""
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {
                    "choices": [{"message": {"content": "feat: add feature"}}]
                },
            )

            provider = DeepSeekProvider(api_key="sk-test123", model="deepseek-chat")
            await provider.generate_commit_message(sample_diff)

            # Verify model in request payload
            call_args = mock_post.call_args
            assert call_args.kwargs["json"]["model"] == "deepseek-chat"

    @pytest.mark.asyncio
    async def test_model_selection_deepseek_coder(self, sample_diff: GitDiff) -> None:
        """T118: Uses deepseek-coder model."""
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: {
                    "choices": [{"message": {"content": "feat: add feature"}}]
                },
            )

            provider = DeepSeekProvider(api_key="sk-test123", model="deepseek-coder")
            await provider.generate_commit_message(sample_diff)

            # Verify model in request payload
            call_args = mock_post.call_args
            assert call_args.kwargs["json"]["model"] == "deepseek-coder"


class TestDeepSeekValidation:
    """Test DeepSeek provider configuration validation."""

    def test_validate_config_with_api_key(self) -> None:
        """Validation passes when API key is provided."""
        provider = DeepSeekProvider(api_key="sk-test123")
        errors = provider.validate_config()
        assert len(errors) == 0

    def test_validate_config_without_api_key(self, monkeypatch) -> None:
        """Validation fails when API key is missing."""
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        with pytest.raises(ValueError, match="DEEPSEEK_API_KEY"):
            DeepSeekProvider(api_key=None)


class TestDeepSeekPromptBuilding:
    """Test prompt construction for DeepSeek."""

    def test_build_prompt_includes_diff_content(self, sample_diff: GitDiff) -> None:
        """Prompt includes diff statistics and file paths."""
        provider = DeepSeekProvider(api_key="sk-test123")
        prompt = provider._build_prompt(sample_diff)

        assert "src/auth.py" in prompt
        assert "15" in prompt  # additions
        assert "3" in prompt  # deletions

    def test_build_prompt_follows_conventional_commits(
        self, sample_diff: GitDiff
    ) -> None:
        """Prompt instructs AI to use conventional commit format."""
        provider = DeepSeekProvider(api_key="sk-test123")
        prompt = provider._build_prompt(sample_diff)

        assert "conventional commit" in prompt.lower()
        assert any(
            t in prompt.lower() for t in ["feat", "fix", "docs", "refactor"]
        )

    def test_build_prompt_includes_actual_diff_content(
        self, sample_diff: GitDiff
    ) -> None:
        """Prompt includes actual diff content, not just file names."""
        provider = DeepSeekProvider(api_key="sk-test123")
        prompt = provider._build_prompt(sample_diff)

        # Should include diff markers
        assert "```diff" in prompt
        # Should include actual code changes from diff_content
        # The sample_diff fixture has diff_content with actual changes
        assert any(marker in prompt for marker in ["+", "-", "@@"])
        # Should explain to analyze actual code changes
        assert "ACTUAL" in prompt or "actual" in prompt
