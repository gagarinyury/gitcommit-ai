"""E2E tests with real AI providers.

Run with: pytest tests/e2e -m e2e -v

These tests make real API calls and require valid API keys in .env file.
Tests are automatically skipped if API keys are not configured.
"""
import os

import pytest

from gitcommit_ai.generator.message import FileDiff, GitDiff
from gitcommit_ai.providers.anthropic import AnthropicProvider
from gitcommit_ai.providers.cohere import CohereProvider
from gitcommit_ai.providers.gemini import GeminiProvider
from gitcommit_ai.providers.mistral import MistralProvider
from gitcommit_ai.providers.ollama import OllamaProvider
from gitcommit_ai.providers.openai import OpenAIProvider

# Sample git diff for testing
SAMPLE_DIFF = GitDiff(
    files=[
        FileDiff(
            path="src/api/auth.py",
            change_type="modified",
            additions=15,
            deletions=5,
            diff_content="@@ -10,5 +10,15 @@ def login(user, password):\n+    return authenticate(user)"
        ),
        FileDiff(
            path="tests/test_auth.py",
            change_type="added",
            additions=20,
            deletions=0,
            diff_content="def test_login():\n+    assert login('user', 'pass')"
        )
    ],
    total_additions=35,
    total_deletions=5
)


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set in .env"
)
class TestOpenAIE2E:
    """E2E tests for OpenAI provider with real API."""

    @pytest.mark.asyncio
    async def test_generate_real_commit_message(self):
        """Generate real commit message using OpenAI API."""
        api_key = os.getenv("OPENAI_API_KEY")
        provider = OpenAIProvider(api_key=api_key)

        # Validate config
        errors = provider.validate_config()
        assert len(errors) == 0, f"Config errors: {errors}"

        # Generate message
        message = await provider.generate_commit_message(SAMPLE_DIFF)

        # Verify message structure
        assert message.type is not None
        assert message.type in ["feat", "fix", "docs", "style", "refactor", "test", "chore"]
        assert message.description is not None
        assert len(message.description) > 10
        assert len(message.description) < 100

        # Verify conventional commit format
        formatted = message.format()
        assert ":" in formatted
        assert formatted.startswith(message.type)

        print(f"\n✅ Generated: {formatted}")

    @pytest.mark.asyncio
    async def test_generate_with_different_model(self):
        """Test with gpt-4o-mini model."""
        api_key = os.getenv("OPENAI_API_KEY")
        provider = OpenAIProvider(api_key=api_key)

        message = await provider.generate_commit_message(SAMPLE_DIFF)

        assert message.type in ["feat", "fix", "docs", "style", "refactor", "test", "chore"]
        assert len(message.description) > 5

        print(f"\n✅ GPT-4o-mini generated: {message.format()}")


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set in .env"
)
class TestAnthropicE2E:
    """E2E tests for Anthropic Claude provider with real API."""

    @pytest.mark.asyncio
    async def test_generate_real_commit_message(self):
        """Generate real commit message using Anthropic API."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        provider = AnthropicProvider(api_key=api_key)

        errors = provider.validate_config()
        assert len(errors) == 0

        message = await provider.generate_commit_message(SAMPLE_DIFF)

        assert message.type in ["feat", "fix", "docs", "style", "refactor", "test", "chore"]
        assert len(message.description) > 10

        print(f"\n✅ Claude generated: {message.format()}")


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"),
    reason="GEMINI_API_KEY or GOOGLE_API_KEY not set in .env"
)
class TestGeminiE2E:
    """E2E tests for Google Gemini provider with real API."""

    @pytest.mark.asyncio
    async def test_generate_real_commit_message(self):
        """Generate real commit message using Gemini API."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        provider = GeminiProvider(api_key=api_key)

        errors = provider.validate_config()
        assert len(errors) == 0

        message = await provider.generate_commit_message(SAMPLE_DIFF)

        assert message.type in ["feat", "fix", "docs", "style", "refactor", "test", "chore"]
        assert len(message.description) > 10

        print(f"\n✅ Gemini generated: {message.format()}")


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.skipif(
    not os.getenv("MISTRAL_API_KEY"),
    reason="MISTRAL_API_KEY not set in .env"
)
class TestMistralE2E:
    """E2E tests for Mistral AI provider with real API."""

    @pytest.mark.asyncio
    async def test_generate_real_commit_message(self):
        """Generate real commit message using Mistral API."""
        api_key = os.getenv("MISTRAL_API_KEY")
        provider = MistralProvider(api_key=api_key)

        errors = provider.validate_config()
        assert len(errors) == 0

        message = await provider.generate_commit_message(SAMPLE_DIFF)

        assert message.type in ["feat", "fix", "docs", "style", "refactor", "test", "chore"]
        assert len(message.description) > 10

        print(f"\n✅ Mistral generated: {message.format()}")


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.skipif(
    not os.getenv("COHERE_API_KEY"),
    reason="COHERE_API_KEY not set in .env"
)
class TestCohereE2E:
    """E2E tests for Cohere provider with real API."""

    @pytest.mark.asyncio
    async def test_generate_real_commit_message(self):
        """Generate real commit message using Cohere API."""
        api_key = os.getenv("COHERE_API_KEY")
        provider = CohereProvider(api_key=api_key)

        errors = provider.validate_config()
        assert len(errors) == 0

        message = await provider.generate_commit_message(SAMPLE_DIFF)

        assert message.type in ["feat", "fix", "docs", "style", "refactor", "test", "chore"]
        assert len(message.description) > 10

        print(f"\n✅ Cohere generated: {message.format()}")


@pytest.mark.e2e
@pytest.mark.slow
class TestOllamaE2E:
    """E2E tests for Ollama provider (local, no API key needed)."""

    @pytest.mark.asyncio
    async def test_ollama_installed(self):
        """Check if Ollama is installed."""
        import subprocess

        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                pytest.skip("Ollama not installed. Install with: brew install ollama")
        except FileNotFoundError:
            pytest.skip("Ollama not installed. Install with: brew install ollama")

    @pytest.mark.asyncio
    async def test_generate_real_commit_message(self):
        """Generate real commit message using Ollama (local)."""
        # First check if ollama is available
        import subprocess
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                pytest.skip("Ollama not running")

            # Check if any model is available
            if "qwen" not in result.stdout.lower() and "llama" not in result.stdout.lower() and "mistral" not in result.stdout.lower():
                pytest.skip("No Ollama models installed. Run: ollama pull qwen2.5")
        except FileNotFoundError:
            pytest.skip("Ollama not installed")

        provider = OllamaProvider()

        errors = provider.validate_config()
        assert len(errors) == 0

        message = await provider.generate_commit_message(SAMPLE_DIFF)

        assert message.type in ["feat", "fix", "docs", "style", "refactor", "test", "chore"]
        assert len(message.description) > 10

        print(f"\n✅ Ollama generated: {message.format()}")
