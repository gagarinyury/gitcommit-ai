"""OpenAI provider for commit message generation."""
import re

import httpx

from gitcommit_ai.generator.message import CommitMessage, GitDiff
from gitcommit_ai.providers.base import AIProvider


class OpenAIProvider(AIProvider):
    """OpenAI API provider for generating commit messages."""

    def __init__(self, api_key: str | None) -> None:
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key.
        """
        self.api_key = api_key
        self.model = "gpt-4o-mini"
        self.api_url = "https://api.openai.com/v1/chat/completions"

    async def generate_commit_message(self, diff: GitDiff) -> CommitMessage:
        """Generate commit message using OpenAI API.

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
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a commit message generator. Generate concise conventional commit messages.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 200,
                },
                timeout=30.0,
            )

            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "Unknown error")
                raise Exception(f"OpenAI API error: {error_msg}")

            data = response.json()
            message_text = data["choices"][0]["message"]["content"]
            return self._parse_message(message_text)

    def validate_config(self) -> list[str]:
        """Validate OpenAI configuration.

        Returns:
            List of error messages (empty if valid).
        """
        errors: list[str] = []
        if not self.api_key:
            errors.append("OpenAI API key is required")
        return errors

    def _build_prompt(self, diff: GitDiff) -> str:
        """Build prompt for OpenAI API.

        Args:
            diff: GitDiff object.

        Returns:
            Prompt string.
        """
        file_list = "\n".join(
            f"- {f.path} (+{f.additions} -{f.deletions})" for f in diff.files
        )

        return f"""Generate a conventional commit message for these changes:

Files changed:
{file_list}

Total: +{diff.total_additions} -{diff.total_deletions}

Format: type(scope): description

Types: feat, fix, docs, style, refactor, test, chore
Keep description under 50 characters.
Add body paragraph if needed (2-3 sentences max).
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
