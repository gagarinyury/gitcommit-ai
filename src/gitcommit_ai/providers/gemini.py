"""Google Gemini AI provider implementation."""
import os
from typing import Any

import httpx

from gitcommit_ai.generator.message import CommitMessage, GitDiff
from gitcommit_ai.providers.base import AIProvider


class GeminiProvider(AIProvider):
    """Google Gemini AI provider for commit message generation."""

    def __init__(self, api_key: str | None = None, model: str = "gemini-2.0-flash-001"):
        """Initialize Gemini provider.

        Args:
            api_key: Google API key (or reads from GEMINI_API_KEY/GOOGLE_API_KEY env).
            model: Gemini model to use (default: gemini-2.0-flash-001).
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com"
        self.client = httpx.AsyncClient(timeout=30.0)

    def validate_config(self) -> list[str]:
        """Validate Gemini configuration.

        Returns:
            List of validation errors (empty if valid).
        """
        errors = []
        if not self.api_key:
            errors.append(
                "Google API key not found. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable."
            )
        return errors

    async def generate_commit_message(self, diff: GitDiff) -> CommitMessage:
        """Generate commit message using Google Gemini.

        Args:
            diff: GitDiff object with staged changes.

        Returns:
            CommitMessage in conventional commit format.

        Raises:
            RuntimeError: If API call fails.
        """
        # Validate config
        validation_errors = self.validate_config()
        if validation_errors:
            raise RuntimeError(f"Gemini validation failed: {'; '.join(validation_errors)}")

        # Build prompt
        prompt = self._build_prompt(diff)

        # Call Gemini API
        url = f"{self.base_url}/v1/models/{self.model}:generateContent"
        headers = {"x-goog-api-key": self.api_key}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 100,
            }
        }

        try:
            response = await self.client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Parse Gemini response
            message_text = self._extract_message(data)
            return self._parse_message(message_text)

        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 403):
                raise RuntimeError("Invalid Gemini API key")
            elif e.response.status_code == 429:
                raise RuntimeError("Gemini API rate limit exceeded")
            else:
                raise RuntimeError(f"Gemini API error: {e.response.status_code}")
        except httpx.RequestError as e:
            raise RuntimeError(f"Gemini network error: {e}")

    def _build_prompt(self, diff: GitDiff) -> str:
        """Build prompt for Gemini from git diff.

        Args:
            diff: GitDiff object.

        Returns:
            Formatted prompt string.
        """
        diff_summary = f"{diff.total_additions} additions, {diff.total_deletions} deletions"
        files = "\n".join([f"- {f.path} ({f.change_type})" for f in diff.files[:5]])

        prompt = f"""Generate a concise git commit message in conventional commit format for these changes:

Files changed:
{files}

Changes: {diff_summary}

Format: <type>(<scope>): <description>
Types: feat, fix, docs, style, refactor, test, chore

Return ONLY the commit message, nothing else."""
        return prompt

    def _extract_message(self, data: dict[str, Any]) -> str:
        """Extract message text from Gemini API response.

        Args:
            data: JSON response from Gemini API.

        Returns:
            Generated message text.

        Raises:
            ValueError: If response format is invalid.
        """
        try:
            candidates = data["candidates"]
            if not candidates:
                raise ValueError("No candidates in Gemini response")

            content = candidates[0]["content"]
            parts = content["parts"]
            if not parts:
                raise ValueError("No parts in Gemini response")

            text = parts[0]["text"]
            return text.strip()

        except (KeyError, IndexError) as e:
            raise ValueError(f"Invalid Gemini response format: {e}")

    def _parse_message(self, message: str) -> CommitMessage:
        """Parse message text into CommitMessage.

        Args:
            message: Raw message string from Gemini.

        Returns:
            CommitMessage object.

        Raises:
            ValueError: If message format is invalid.
        """
        # Clean message
        message = message.strip()

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
