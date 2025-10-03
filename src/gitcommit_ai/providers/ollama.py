"""Ollama local AI provider implementation."""
import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncIterator

import httpx

from gitcommit_ai.generator.message import CommitMessage, GitDiff
from gitcommit_ai.providers.base import AIProvider


@dataclass
class OllamaConfig:
    """Configuration for Ollama provider."""

    host: str = "http://localhost:11434"
    default_model: str = "qwen2.5"
    timeout_seconds: int = 60
    stream: bool = True

    @classmethod
    def from_env(cls) -> "OllamaConfig":
        """Create config from environment variables."""
        return cls(
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            default_model=os.getenv("OLLAMA_DEFAULT_MODEL", "qwen2.5"),
            timeout_seconds=int(os.getenv("OLLAMA_TIMEOUT", "60")),
        )


@dataclass
class ModelInfo:
    """Ollama model metadata."""

    name: str
    size: str
    modified: str

    @classmethod
    def from_list_row(cls, row: str) -> "ModelInfo":
        """Parse a row from 'ollama list' output."""
        parts = row.split()
        if len(parts) < 4:
            raise ValueError(f"Invalid ollama list row: {row}")
        return cls(
            name=parts[0],
            size=f"{parts[2]} {parts[3]}",
            modified=" ".join(parts[4:]),
        )


class OllamaProvider(AIProvider):
    """Ollama local LLM provider."""

    def __init__(self, config: OllamaConfig | None = None, model: str | None = None):
        """Initialize Ollama provider.

        Args:
            config: OllamaConfig instance (defaults to environment-based config).
            model: Override default model.
        """
        self.config = config or OllamaConfig.from_env()
        self.model = model or self.config.default_model
        self.client = httpx.AsyncClient(timeout=self.config.timeout_seconds)

    @staticmethod
    def is_installed() -> bool:
        """Check if Ollama CLI is installed.

        Returns:
            True if 'ollama' command exists, False otherwise.
        """
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
    def list_models() -> list[ModelInfo]:
        """Get available Ollama models.

        Returns:
            List of ModelInfo objects.

        Raises:
            RuntimeError: If 'ollama list' command fails.
        """
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                check=True,
            )
            lines = result.stdout.strip().split("\n")
            # Skip header line
            if len(lines) <= 1:
                return []
            return [ModelInfo.from_list_row(line) for line in lines[1:]]
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to list Ollama models: {e}")
        except FileNotFoundError:
            raise RuntimeError("Ollama not installed")

    async def check_service_running(self) -> bool:
        """Check if Ollama service is running.

        Returns:
            True if service responds, False otherwise.
        """
        try:
            response = await self.client.get(f"{self.config.host}/api/tags")
            return response.status_code == 200
        except (httpx.ConnectError, httpx.TimeoutException):
            return False

    def validate_config(self) -> list[str]:
        """Validate Ollama configuration.

        Returns:
            List of validation errors (empty if valid).
        """
        errors = []

        if not self.is_installed():
            errors.append(
                "Ollama not installed. Install from: https://ollama.ai"
            )
            return errors  # No point checking further

        # Check if model exists
        try:
            models = self.list_models()
            model_names = [m.name for m in models]
            if self.model not in model_names and not any(
                m.startswith(self.model) for m in model_names
            ):
                errors.append(
                    f"Model '{self.model}' not found. Run: ollama pull {self.model}"
                )
        except RuntimeError as e:
            errors.append(str(e))

        return errors

    async def _stream_response(self, prompt: str) -> AsyncIterator[str]:
        """Stream response from Ollama API.

        Args:
            prompt: The prompt to send.

        Yields:
            Response chunks as they arrive.
        """
        url = f"{self.config.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": self.config.stream,
            "options": {
                "temperature": 0.3,    # Focused output (vs default ~0.8)
                "top_p": 0.9,          # Quality sampling
                "top_k": 40,           # Vocabulary control
                "num_predict": 256,    # Allow body generation (vs default 128)
            }
        }

        async with self.client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue  # Skip malformed lines

    async def generate_commit_message(self, diff: GitDiff) -> CommitMessage:
        """Generate commit message using Ollama.

        Args:
            diff: GitDiff object with staged changes.

        Returns:
            CommitMessage in conventional commit format.

        Raises:
            RuntimeError: If Ollama is not available or request fails.
        """
        # Validate before generating
        validation_errors = self.validate_config()
        if validation_errors:
            raise RuntimeError(f"Ollama validation failed: {'; '.join(validation_errors)}")

        # Check service
        if not await self.check_service_running():
            raise RuntimeError(
                f"Cannot connect to Ollama at {self.config.host}. "
                f"Is the service running? Try: ollama serve"
            )

        # Build prompt
        prompt = self._build_prompt(diff)

        # Stream and accumulate response
        full_response = ""
        async for chunk in self._stream_response(prompt):
            full_response += chunk

        # Parse response into CommitMessage
        return self._parse_response(full_response.strip())

    def _build_prompt(self, diff: GitDiff) -> str:
        """Build prompt using external template.

        Args:
            diff: GitDiff object.

        Returns:
            Rendered prompt string with variables substituted.
        """
        from gitcommit_ai.prompts.loader import PromptLoader

        # Build file list with stats (limit to 10 files)
        file_list = "\n".join([
            f"- {f.path} ({f.change_type}, +{f.additions} -{f.deletions})"
            for f in diff.files[:10]
        ])

        # Load template and render
        loader = PromptLoader()
        template = loader.load("ollama")

        return loader.render(
            template,
            file_list=file_list,
            total_additions=diff.total_additions,
            total_deletions=diff.total_deletions
        )

    def _parse_response(self, response: str) -> CommitMessage:
        """Parse Ollama response into CommitMessage.

        Args:
            response: Raw response string from Ollama.

        Returns:
            CommitMessage object.

        Raises:
            ValueError: If response format is invalid.
        """
        # Clean response
        message = response.strip()

        # Extract type and scope
        if ":" not in message:
            raise ValueError(f"Invalid commit message format: {message}")

        type_scope, description = message.split(":", 1)
        description = description.strip()

        # Parse type and optional scope
        if "(" in type_scope and ")" in type_scope:
            type_part = type_scope.split("(")[0].strip()
            scope = type_scope.split("(")[1].split(")")[0].strip()
        else:
            type_part = type_scope.strip()
            scope = None

        return CommitMessage(
            type=type_part,
            scope=scope,
            description=description,
            body=None,
            breaking_changes=[],
        )
