"""Anthropic provider for commit message generation."""
import re

import httpx

from gitcommit_ai.generator.message import CommitMessage, GitDiff
from gitcommit_ai.providers.base import AIProvider


class AnthropicProvider(AIProvider):
    """Anthropic API provider for generating commit messages."""

    def __init__(self, api_key: str | None) -> None:
        """Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key.
        """
        self.api_key = api_key
        self.model = "claude-3-haiku-20240307"
        self.api_url = "https://api.anthropic.com/v1/messages"

    async def generate_commit_message(self, diff: GitDiff) -> CommitMessage:
        """Generate commit message using Anthropic API.

        Args:
            diff: GitDiff object with staged changes.

        Returns:
            CommitMessage in conventional commit format.

        Raises:
            Exception: If API call fails.
        """
        prompt = self._build_prompt(diff)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers={
                    "x-api-key": self.api_key or "",
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "max_tokens": 200,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=30.0,
            )

            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "Unknown error")
                raise Exception(f"Anthropic API error: {error_msg}")

            data = response.json()
            message_text = data["content"][0]["text"]
            return self._parse_message(message_text)

    def validate_config(self) -> list[str]:
        """Validate Anthropic configuration.

        Returns:
            List of error messages (empty if valid).
        """
        errors: list[str] = []
        if not self.api_key:
            errors.append("Anthropic API key is required")
        return errors

    def _build_prompt(self, diff: GitDiff) -> str:
        """Build prompt for Anthropic API.

        Args:
            diff: GitDiff object.

        Returns:
            Prompt string.
        """
        file_list = "\n".join(
            f"- {f.path} (+{f.additions} -{f.deletions})" for f in diff.files
        )

        return f"""Generate a conventional commit message for these git changes:

Files changed:
{file_list}

Total: +{diff.total_additions} -{diff.total_deletions}

Use conventional commit format: type(scope): description

Valid types: feat, fix, docs, style, refactor, test, chore
Keep description concise (under 50 characters).
Optionally add a body paragraph (2-3 sentences) if changes need explanation.

Output only the commit message, nothing else.
"""

    def _parse_message(self, text: str) -> CommitMessage:
        """Parse AI response into CommitMessage.

        Args:
            text: AI-generated message text.

        Returns:
            CommitMessage object.
        """
        lines = text.strip().split("\n")
        first_line = lines[0].strip()

        # Parse first line: type(scope): description
        match = re.match(r"^(\w+)(?:\(([^)]+)\))?: (.+)$", first_line)
        if not match:
            # Fallback if format doesn't match
            return CommitMessage(
                type="chore",
                scope=None,
                description=first_line[:50],
                body=None,
                breaking_changes=[],
            )

        commit_type, scope, description = match.groups()

        # Body is everything after first blank line
        body = None
        if len(lines) > 2 and lines[1] == "":
            body = "\n".join(lines[2:]).strip()

        return CommitMessage(
            type=commit_type,
            scope=scope,
            description=description,
            body=body,
            breaking_changes=[],
        )
