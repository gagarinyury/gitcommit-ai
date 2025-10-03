"""Tests for OpenRouter provider."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from gitcommit_ai.generator.message import CommitMessage, FileDiff, GitDiff
from gitcommit_ai.providers.openrouter import OpenRouterProvider


@pytest.fixture
def sample_diff() -> GitDiff:
    """Create a sample GitDiff for testing."""
    return GitDiff(
        files=[
            FileDiff(
                path="src/api/auth.py",
                change_type="added",
                additions=42,
                deletions=0,
                diff_content="@@ +42 lines of auth implementation @@",
            )
        ],
        total_additions=42,
        total_deletions=0,
    )


class TestOpenRouterProvider:
    """Test OpenRouter provider initialization and basic functionality."""

    def test_openrouter_provider_init(self) -> None:
        """OpenRouterProvider initializes with API key and model.

        This test verifies T007 requirement:
        - API key loaded from constructor
        - Model format validated on init
        - Base URL defaults to https://openrouter.ai/api/v1
        """
        provider = OpenRouterProvider(
            api_key="sk-or-v1-test123",
            model="openai/gpt-4o-mini"
        )

        assert provider.api_key == "sk-or-v1-test123"
        assert provider.model == "openai/gpt-4o-mini"
        assert provider.base_url == "https://openrouter.ai/api/v1"
        assert provider.timeout == 60

    def test_model_name_validation(self) -> None:
        """Model name format validation with regex pattern.

        This test verifies T008 requirement:
        - Valid format: vendor/model-name (lowercase, numbers, hyphens, dots)
        - Invalid: missing vendor, wrong case, empty parts
        - Regex: ^[a-z0-9-]+/[a-z0-9-\.]+$
        """
        # Valid model formats
        valid_models = [
            "openai/gpt-4o",
            "anthropic/claude-3-5-sonnet",
            "google/gemini-2.0-flash-exp",
            "mistral/mistral-tiny",
            "cohere/command-light",
        ]

        for model in valid_models:
            provider = OpenRouterProvider(api_key="sk-test", model=model)
            assert provider._validate_model_format(model) is True

        # Invalid model formats
        invalid_models = [
            "gpt-4o",  # Missing vendor
            "openai/",  # Missing model
            "/gpt-4o",  # Missing vendor prefix
            "OpenAI/GPT-4O",  # Wrong case
            "openai gpt-4o",  # Space instead of slash
            "",  # Empty
        ]

        for model in invalid_models:
            with pytest.raises(ValueError, match="Invalid model format"):
                OpenRouterProvider(api_key="sk-test", model=model)

    def test_validate_config(self) -> None:
        """validate_config() returns errors for invalid configuration.

        This test verifies T009 requirement:
        - Returns error if API key missing or empty
        - Returns error if model format invalid
        - Returns empty list if config valid
        """
        # Valid config
        provider = OpenRouterProvider(
            api_key="sk-or-v1-valid",
            model="openai/gpt-4o-mini"
        )
        errors = provider.validate_config()
        assert errors == []

        # Missing API key
        provider_no_key = OpenRouterProvider(api_key="", model="openai/gpt-4o")
        errors = provider_no_key.validate_config()
        assert len(errors) > 0
        assert any("API key" in error for error in errors)

        # Invalid model format (should raise on init, but test validate_config)
        with pytest.raises(ValueError):
            OpenRouterProvider(api_key="sk-test", model="invalid-format")


class TestOpenRouterRequestFormat:
    """Test OpenRouter API request format (contract tests from T004)."""

    @pytest.mark.asyncio
    async def test_openrouter_request_format(self, sample_diff: GitDiff) -> None:
        """OpenRouter request has correct structure and headers.

        This test verifies T004 requirement (contract test):
        - Request has model, messages, temperature, max_tokens
        - Model format matches vendor/model-name pattern
        - Authorization header includes Bearer token
        - Messages array has system + user roles
        """
        mock_response = {
            "id": "gen-test123",
            "model": "openai/gpt-4o-mini",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "feat(api): add JWT authentication endpoint"
                },
                "finish_reason": "stop"
            }]
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: mock_response
            )

            provider = OpenRouterProvider(
                api_key="sk-or-v1-test",
                model="openai/gpt-4o-mini"
            )
            await provider.generate_commit_message(sample_diff)

            # Verify request was made
            assert mock_post.called
            call_kwargs = mock_post.call_args.kwargs

            # Verify URL
            assert "openrouter.ai/api/v1/chat/completions" in str(call_kwargs.get("url", ""))

            # Verify headers
            headers = call_kwargs.get("headers", {})
            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer sk-or-v1-test"

            # Verify request payload
            json_data = call_kwargs.get("json", {})
            assert json_data["model"] == "openai/gpt-4o-mini"
            assert "messages" in json_data
            assert len(json_data["messages"]) >= 2
            assert json_data["messages"][0]["role"] == "system"
            assert json_data["messages"][1]["role"] == "user"
            assert "temperature" in json_data
            assert "max_tokens" in json_data


class TestOpenRouterResponseParsing:
    """Test OpenRouter API response parsing (contract tests from T005)."""

    @pytest.mark.asyncio
    async def test_openrouter_response_parsing(self, sample_diff: GitDiff) -> None:
        """OpenRouter response correctly parsed into CommitMessage.

        This test verifies T005 requirement:
        - Extracts choices[0].message.content correctly
        - Parses into CommitMessage (type, scope, description, body)
        - Handles conventional commit format
        """
        mock_response = {
            "id": "gen-abc123",
            "model": "anthropic/claude-3-haiku",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "feat(auth): implement JWT-based authentication\n\n"
                              "Adds secure token-based authentication with refresh tokens."
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 25,
                "total_tokens": 175
            }
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: mock_response
            )

            provider = OpenRouterProvider(
                api_key="sk-or-v1-test",
                model="anthropic/claude-3-haiku"
            )
            message = await provider.generate_commit_message(sample_diff)

            # Verify CommitMessage structure
            assert isinstance(message, CommitMessage)
            assert message.type == "feat"
            assert message.scope == "auth"
            assert "jwt" in message.description.lower() or "authentication" in message.description.lower()
            assert message.body is not None
            assert "refresh tokens" in message.body.lower()


class TestOpenRouterErrorHandling:
    """Test OpenRouter error responses (contract tests from T006)."""

    @pytest.mark.asyncio
    async def test_openrouter_invalid_api_key(self, sample_diff: GitDiff) -> None:
        """Returns helpful error for 401 Unauthorized.

        This test verifies T006 requirement:
        - 401 error includes link to https://openrouter.ai/keys
        - Error message is user-friendly
        """
        mock_error_response = {
            "error": {
                "message": "Invalid API key",
                "type": "invalid_request_error",
                "code": "invalid_api_key"
            }
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=401,
                json=lambda: mock_error_response
            )

            provider = OpenRouterProvider(
                api_key="sk-or-v1-invalid",
                model="openai/gpt-4o-mini"
            )

            with pytest.raises(Exception) as exc_info:
                await provider.generate_commit_message(sample_diff)

            error_message = str(exc_info.value)
            assert "401" in error_message or "Invalid" in error_message or "Unauthorized" in error_message
            assert "openrouter.ai/keys" in error_message.lower()

    @pytest.mark.asyncio
    async def test_openrouter_rate_limit(self, sample_diff: GitDiff) -> None:
        """Returns helpful error for 429 Rate Limit.

        This test verifies T006 requirement:
        - 429 error includes rate limit message
        - No automatic retry (per design decision)
        """
        mock_error_response = {
            "error": {
                "message": "Rate limit exceeded. Try again in 60 seconds.",
                "type": "rate_limit_error",
                "code": "rate_limit_exceeded"
            }
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=429,
                json=lambda: mock_error_response
            )

            provider = OpenRouterProvider(
                api_key="sk-or-v1-test",
                model="openai/gpt-4o-mini"
            )

            with pytest.raises(Exception) as exc_info:
                await provider.generate_commit_message(sample_diff)

            error_message = str(exc_info.value)
            assert "429" in error_message or "rate limit" in error_message.lower()

    @pytest.mark.asyncio
    async def test_openrouter_service_unavailable(self, sample_diff: GitDiff) -> None:
        """Returns helpful error for 503 Service Unavailable.

        This test verifies T006 requirement:
        - 503 error suggests fallback providers
        - Error includes manual provider suggestions (openai, anthropic, ollama, deepseek)
        """
        mock_error_response = {
            "error": {
                "message": "Service temporarily unavailable",
                "type": "server_error",
                "code": "service_unavailable"
            }
        }

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = MagicMock(
                status_code=503,
                json=lambda: mock_error_response
            )

            provider = OpenRouterProvider(
                api_key="sk-or-v1-test",
                model="openai/gpt-4o-mini"
            )

            with pytest.raises(Exception) as exc_info:
                await provider.generate_commit_message(sample_diff)

            error_message = str(exc_info.value)
            assert "503" in error_message or "unavailable" in error_message.lower()
            # Should suggest fallback providers (per clarification session)
            assert any(provider in error_message.lower() for provider in ["openai", "anthropic", "ollama", "deepseek"])
