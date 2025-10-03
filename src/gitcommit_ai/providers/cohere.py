"""Cohere AI provider implementation."""
import os

import httpx

from gitcommit_ai.generator.message import CommitMessage, GitDiff
from gitcommit_ai.providers.base import AIProvider


class CohereProvider(AIProvider):
    """Cohere AI provider."""

    def __init__(self, api_key: str | None = None, model: str = "command-light"):
        """Initialize Cohere provider.

        Args:
            api_key: Cohere API key (or reads from COHERE_API_KEY env).
            model: Model to use (command, command-light).
        """
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        self.model = model
        self.base_url = "https://api.cohere.ai/v1"
        self.client = httpx.AsyncClient(timeout=30.0)

    def validate_config(self) -> list[str]:
        """Validate Cohere configuration."""
        errors = []
        if not self.api_key:
            errors.append("Cohere API key not found. Set COHERE_API_KEY environment variable.")
        return errors

    async def generate_commit_message(self, diff: GitDiff) -> CommitMessage:
        """Generate commit message using Cohere."""
        validation_errors = self.validate_config()
        if validation_errors:
            raise RuntimeError(f"Cohere validation failed: {'; '.join(validation_errors)}")

        prompt = self._build_prompt(diff)

        url = f"{self.base_url}/generate"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": 100,
            "temperature": 0.3,
            "stop_sequences": ["\n\n"],
        }

        try:
            response = await self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Extract message from Cohere response
            message_text = data["generations"][0]["text"].strip()
            return self._parse_message(message_text)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise RuntimeError("Invalid Cohere API key")
            elif e.response.status_code == 429:
                raise RuntimeError("Cohere API rate limit exceeded")
            else:
                raise RuntimeError(f"Cohere API error: {e.response.status_code}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Cohere network error: {e}")

    def _build_prompt(self, diff: GitDiff) -> str:
        """Build prompt from git diff."""
        diff_summary = f"{diff.total_additions} additions, {diff.total_deletions} deletions"
        files = "\n".join([f"- {f.path} ({f.change_type})" for f in diff.files[:5]])

        return f"""Generate a concise git commit message in conventional commit format for these changes:

Files changed:
{files}

Changes: {diff_summary}

Format: <type>(<scope>): <description>
Types: feat, fix, docs, style, refactor, test, chore

Return ONLY the commit message, nothing else."""

    def _parse_message(self, message: str) -> CommitMessage:
        """Parse message text into CommitMessage."""
        message = message.strip()

        if ":" not in message:
            raise ValueError(f"Invalid commit message format: {message}")

        type_scope, description = message.split(":", 1)
        description = description.strip()

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
