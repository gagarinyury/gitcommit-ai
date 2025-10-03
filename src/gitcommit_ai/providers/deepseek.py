"""DeepSeek provider for commit message generation."""
import os
import re

import httpx

from gitcommit_ai.generator.message import CommitMessage, GitDiff
from gitcommit_ai.providers.base import AIProvider


class DeepSeekProvider(AIProvider):
    """DeepSeek API provider for generating commit messages.

    DeepSeek uses OpenAI-compatible API format, making it a drop-in replacement.
    Pricing: $0.27/1M input tokens (18x cheaper than GPT-4o).
    """

    def __init__(self, api_key: str | None = None, model: str = "deepseek-chat") -> None:
        """Initialize DeepSeek provider.

        Args:
            api_key: DeepSeek API key (or from DEEPSEEK_API_KEY env var).
            model: Model name (deepseek-chat or deepseek-coder).

        Raises:
            ValueError: If API key is not provided.
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY is required. Get one at https://platform.deepseek.com"
            )

        self.model = model
        self.api_url = "https://api.deepseek.com/v1/chat/completions"

    async def generate_commit_message(self, diff: GitDiff) -> CommitMessage:
        """Generate commit message using DeepSeek API.

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
                raise Exception(f"DeepSeek API error: {error_msg}")

            data = response.json()
            message_text = data["choices"][0]["message"]["content"]
            return self._parse_message(message_text)

    def validate_config(self) -> list[str]:
        """Validate DeepSeek configuration.

        Returns:
            List of error messages (empty if valid).
        """
        errors: list[str] = []
        if not self.api_key:
            errors.append("DeepSeek API key is required")
        return errors

    def _build_prompt(self, diff: GitDiff) -> str:
        """Build prompt using external template with actual diff content.

        Args:
            diff: GitDiff object.

        Returns:
            Rendered prompt string with variables substituted.
        """
        from gitcommit_ai.prompts.loader import PromptLoader

        # Build diff content with actual code changes (limit to prevent token overflow)
        diff_details = []
        for f in diff.files[:5]:  # Limit to 5 files to avoid token limits
            diff_details.append(f"File: {f.path} ({f.change_type}, +{f.additions} -{f.deletions})")
            # Include first 20 lines of diff content for context
            diff_lines = f.diff_content.split('\n')[:20]
            if diff_lines:
                diff_details.append("```diff")
                diff_details.append('\n'.join(diff_lines))
                if len(f.diff_content.split('\n')) > 20:
                    diff_details.append("... (truncated)")
                diff_details.append("```")

        diff_content = "\n\n".join(diff_details)

        # Load template and render with variables
        loader = PromptLoader()
        template = loader.load("deepseek")

        return loader.render(
            template,
            diff_content=diff_content,
            total_additions=diff.total_additions,
            total_deletions=diff.total_deletions,
            file_count=len(diff.files)
        )

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
