"""Provider registry for managing AI providers."""
import os
import subprocess
from dataclasses import dataclass


@dataclass
class ProviderInfo:
    """Information about an AI provider."""
    name: str
    configured: bool
    models: list[str]
    description: str


class ProviderRegistry:
    """Registry for all available AI providers."""

    @staticmethod
    def list_providers() -> list[ProviderInfo]:
        """Get list of all available providers with configuration status.

        Returns:
            List of ProviderInfo objects.
        """
        providers = [
            ProviderInfo(
                name="openai",
                configured=bool(os.getenv("OPENAI_API_KEY")),
                models=["gpt-4o", "gpt-4o-mini"],
                description="OpenAI GPT models"
            ),
            ProviderInfo(
                name="anthropic",
                configured=bool(os.getenv("ANTHROPIC_API_KEY")),
                models=["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
                description="Anthropic Claude models"
            ),
            ProviderInfo(
                name="gemini",
                configured=bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")),
                models=["gemini-2.0-flash-001", "gemini-2.5-flash", "gemini-2.5-pro"],
                description="Google Gemini models"
            ),
            ProviderInfo(
                name="mistral",
                configured=bool(os.getenv("MISTRAL_API_KEY")),
                models=["mistral-tiny", "mistral-small", "mistral-medium"],
                description="Mistral AI models"
            ),
            ProviderInfo(
                name="cohere",
                configured=bool(os.getenv("COHERE_API_KEY")),
                models=["command", "command-light"],
                description="Cohere Command models"
            ),
            ProviderInfo(
                name="deepseek",
                configured=bool(os.getenv("DEEPSEEK_API_KEY")),
                models=["deepseek-chat", "deepseek-coder"],
                description="DeepSeek models (cheapest: $0.27/1M tokens)"
            ),
            ProviderInfo(
                name="ollama",
                configured=ProviderRegistry._check_ollama(),
                models=["qwen2.5:7b", "qwen2.5:3b", "llama3.2", "codellama"],
                description="Ollama (local AI models)"
            ),
        ]
        return providers

    @staticmethod
    def _check_ollama() -> bool:
        """Check if Ollama is installed and running."""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    @staticmethod
    def get_provider_names() -> list[str]:
        """Get list of all provider names.

        Returns:
            List of provider names (lowercase).
        """
        return [p.name for p in ProviderRegistry.list_providers()]

    @staticmethod
    def get_configured_providers() -> list[str]:
        """Get list of configured provider names.

        Returns:
            List of configured provider names.
        """
        return [p.name for p in ProviderRegistry.list_providers() if p.configured]
