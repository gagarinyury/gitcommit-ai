"""Tests for configuration loading and validation."""
import os
from unittest.mock import patch

import pytest

from gitcommit_ai.core.config import Config, ConfigError


class TestConfigLoading:
    """Test configuration loading from environment variables."""

    def test_load_with_openai_key(self) -> None:
        """Config loads successfully with OPENAI_API_KEY set."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123"}):
            config = Config.load()
            assert config.openai_api_key == "sk-test123"
            assert config.default_provider == "openai"

    def test_load_with_anthropic_key(self) -> None:
        """Config loads successfully with ANTHROPIC_API_KEY set."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test456"}):
            config = Config.load()
            assert config.anthropic_api_key == "sk-ant-test456"

    def test_load_with_both_keys(self) -> None:
        """Config loads both keys when both are set."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "sk-test123",
                "ANTHROPIC_API_KEY": "sk-ant-test456",
            },
        ):
            config = Config.load()
            assert config.openai_api_key == "sk-test123"
            assert config.anthropic_api_key == "sk-ant-test456"

    def test_load_with_no_keys(self) -> None:
        """Config loads but has no API keys (validation catches this later)."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config.load()
            assert config.openai_api_key is None
            assert config.anthropic_api_key is None


class TestConfigValidation:
    """Test configuration validation logic."""

    def test_validate_success_with_openai(self) -> None:
        """Validation passes when OpenAI key is set."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123"}):
            config = Config.load()
            errors = config.validate()
            assert len(errors) == 0

    def test_validate_success_with_anthropic(self) -> None:
        """Validation passes when Anthropic key is set."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test456"}):
            config = Config.load()
            errors = config.validate()
            assert len(errors) == 0

    def test_validate_always_passes(self) -> None:
        """Validation always passes - providers validate their own requirements."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config.load()
            errors = config.validate()
            assert len(errors) == 0  # No validation errors


class TestConfigDefaults:
    """Test default configuration values."""

    def test_default_provider_is_openai(self) -> None:
        """Default provider is OpenAI when both keys are set."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "sk-test123",
                "ANTHROPIC_API_KEY": "sk-ant-test456",
            },
        ):
            config = Config.load()
            assert config.default_provider == "openai"

    def test_verbose_defaults_to_false(self) -> None:
        """Verbose mode defaults to False."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123"}):
            config = Config.load()
            assert config.verbose is False

    def test_default_provider_is_ollama_when_no_keys(self) -> None:
        """Default provider is Ollama when no API keys are set."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config.load()
            assert config.default_provider == "ollama"

    def test_default_provider_is_anthropic_when_only_anthropic_key(self) -> None:
        """Default provider is Anthropic when only Anthropic key is set."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test"}, clear=True):
            config = Config.load()
            assert config.default_provider == "anthropic"


class TestConfigError:
    """Test ConfigError exception."""

    def test_config_error_message(self) -> None:
        """ConfigError stores error message correctly."""
        error = ConfigError("Missing API key")
        assert str(error) == "Missing API key"
