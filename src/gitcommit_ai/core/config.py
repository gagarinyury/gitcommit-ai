"""Configuration management for GitCommit AI."""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from current directory or parent directories
load_dotenv()


class ConfigError(Exception):
    """Raised when configuration is invalid."""

    pass


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    openai_api_key: str | None
    anthropic_api_key: str | None
    deepseek_api_key: str | None
    default_provider: str
    verbose: bool

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment variables.

        Returns:
            Config instance with values from environment.
        """
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")

        # Priority: 1) OpenAI, 2) Anthropic, 3) DeepSeek, 4) Ollama (always available)
        if openai_key:
            default_provider = "openai"
        elif anthropic_key:
            default_provider = "anthropic"
        elif deepseek_key:
            default_provider = "deepseek"
        else:
            # Default to Ollama (no API key needed, works offline)
            default_provider = "ollama"

        return cls(
            openai_api_key=openai_key,
            anthropic_api_key=anthropic_key,
            deepseek_api_key=deepseek_key,
            default_provider=default_provider,
            verbose=False,
        )

    def validate(self) -> list[str]:
        """Validate configuration and return list of error messages.

        Returns:
            List of validation errors (empty if valid).
        """
        # No validation needed here - each provider will validate its own requirements
        return []
