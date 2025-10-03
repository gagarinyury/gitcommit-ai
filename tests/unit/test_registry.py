"""Tests for provider registry."""
from unittest.mock import patch

from gitcommit_ai.providers.registry import ProviderInfo, ProviderRegistry


class TestProviderRegistry:
    """Test provider listing and configuration detection."""

    def test_list_providers_returns_all_providers(self) -> None:
        """Returns all available providers."""
        providers = ProviderRegistry.list_providers()
        assert len(providers) >= 6  # openai, anthropic, gemini, deepseek, openrouter, ollama

        provider_names = [p.name for p in providers]
        assert "openai" in provider_names
        assert "anthropic" in provider_names
        assert "ollama" in provider_names
        assert "gemini" in provider_names
        assert "deepseek" in provider_names
        assert "openrouter" in provider_names
        # mistral and cohere removed - now accessible via openrouter
        assert "mistral" not in provider_names
        assert "cohere" not in provider_names

    def test_list_providers_checks_configuration(self) -> None:
        """Detects configured providers via environment variables."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
            providers = ProviderRegistry.list_providers()
            openai = next((p for p in providers if p.name == "openai"), None)
            assert openai is not None
            assert openai.configured is True

    def test_list_providers_unconfigured_without_env(self) -> None:
        """Providers without API keys are not configured."""
        with patch.dict("os.environ", {}, clear=True):
            providers = ProviderRegistry.list_providers()
            openai = next((p for p in providers if p.name == "openai"), None)
            assert openai is not None
            assert openai.configured is False

    def test_provider_info_includes_models(self) -> None:
        """Each provider includes list of supported models."""
        providers = ProviderRegistry.list_providers()

        for provider in providers:
            assert isinstance(provider, ProviderInfo)
            assert len(provider.models) > 0
            assert isinstance(provider.description, str)

    def test_get_provider_names(self) -> None:
        """Returns list of all provider names."""
        names = ProviderRegistry.get_provider_names()
        assert isinstance(names, list)
        assert len(names) >= 6
        assert all(isinstance(name, str) for name in names)

    def test_get_configured_providers(self) -> None:
        """Returns only configured providers."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            configured = ProviderRegistry.get_configured_providers()
            assert "anthropic" in configured

    def test_get_configured_providers_empty_when_none(self) -> None:
        """Returns empty list when no providers configured."""
        with patch.dict("os.environ", {}, clear=True):
            # Mock ollama as not installed
            with patch("gitcommit_ai.providers.registry.ProviderRegistry._check_ollama", return_value=False):
                configured = ProviderRegistry.get_configured_providers()
                assert len(configured) == 0


class TestOllamaDetection:
    """Test Ollama installation detection."""

    def test_check_ollama_returns_true_when_installed(self) -> None:
        """Returns True when ollama command exists."""
        import subprocess

        mock_result = subprocess.CompletedProcess(
            args=["ollama", "--version"],
            returncode=0,
            stdout="ollama version 0.1.0"
        )

        with patch("subprocess.run", return_value=mock_result):
            assert ProviderRegistry._check_ollama() is True

    def test_check_ollama_returns_false_when_not_found(self) -> None:
        """Returns False when ollama command not found."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert ProviderRegistry._check_ollama() is False

    def test_check_ollama_returns_false_on_error(self) -> None:
        """Returns False when ollama command fails."""
        import subprocess

        mock_result = subprocess.CompletedProcess(
            args=["ollama", "--version"],
            returncode=1,
            stdout=""
        )

        with patch("subprocess.run", return_value=mock_result):
            assert ProviderRegistry._check_ollama() is False
