"""OpenRouter provider for commit message generation.

OpenRouter provides unified access to 100+ AI models (OpenAI, Anthropic, Google,
Mistral, Cohere, and more) through a single API key and OpenAI-compatible interface.

Website: https://openrouter.ai
API Docs: https://openrouter.ai/docs
"""
import re

import httpx

from gitcommit_ai.generator.message import CommitMessage, GitDiff
from gitcommit_ai.providers.base import AIProvider


class OpenRouterProvider(AIProvider):
    """OpenRouter API provider for generating commit messages.

    OpenRouter uses OpenAI-compatible API format, allowing easy integration
    with minimal code changes from OpenAI provider.

    Model format: vendor/model-name (e.g., openai/gpt-4o, anthropic/claude-3-haiku)
    """

    # Regex pattern for model name validation: vendor/model-name
    MODEL_PATTERN = re.compile(r"^[a-z0-9-]+/[a-z0-9-\.]+$")

    def __init__(self, api_key: str, model: str) -> None:
        """Initialize OpenRouter provider.

        Args:
            api_key: OpenRouter API key (format: sk-or-v1-...).
            model: Model in format "vendor/model-name" (e.g., "openai/gpt-4o-mini").

        Raises:
            ValueError: If model format is invalid.
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.timeout = 60

        # Validate model format on initialization
        if not self._validate_model_format(model):
            raise ValueError(
                f"Invalid model format '{model}'. "
                f"Must be 'vendor/model-name' (e.g., 'openai/gpt-4o')"
            )

    def _validate_model_format(self, model: str) -> bool:
        """Validate model name format.

        Args:
            model: Model name to validate.

        Returns:
            True if valid, False otherwise.

        Valid format: vendor/model-name (lowercase, numbers, hyphens, dots)
        Examples: openai/gpt-4o, anthropic/claude-3-haiku, google/gemini-2.0-flash
        """
        return bool(self.MODEL_PATTERN.match(model))

    async def generate_commit_message(self, diff: GitDiff) -> CommitMessage:
        """Generate commit message using OpenRouter API.

        Args:
            diff: GitDiff object with staged changes.

        Returns:
            CommitMessage in conventional commit format.

        Raises:
            Exception: If API call fails, with helpful error messages:
                - 401: Invalid API key (includes link to https://openrouter.ai/keys)
                - 429: Rate limit exceeded
                - 503: Service unavailable (suggests fallback providers)
        """
        prompt = self._build_prompt(diff)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/gagarinyury/gitcommit-ai",
                    "X-Title": "GitCommit AI",
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
                    "max_tokens": 500,
                },
                timeout=self.timeout,
            )

            # Handle error responses with helpful messages
            if response.status_code != 200:
                await self._handle_error_response(response)

            data = response.json()
            message_text = data["choices"][0]["message"]["content"]
            return self._parse_message(message_text)

    async def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses with helpful, user-friendly messages.

        Args:
            response: HTTP response object.

        Raises:
            Exception: With context-specific error message.
        """
        status_code = response.status_code

        try:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", "Unknown error")
        except Exception:
            error_msg = response.text or "Unknown error"

        if status_code == 401:
            raise Exception(
                f"OpenRouter API error (401 Unauthorized): {error_msg}\n\n"
                f"Get your API key at: https://openrouter.ai/keys\n"
                f"Then: export OPENROUTER_API_KEY=\"sk-or-v1-...\""
            )
        elif status_code == 429:
            raise Exception(
                f"OpenRouter API error (429 Rate Limit): {error_msg}\n\n"
                f"Rate limit exceeded. Try again later."
            )
        elif status_code == 503:
            raise Exception(
                f"OpenRouter API error (503 Service Unavailable): {error_msg}\n\n"
                f"Try alternative providers:\n"
                f"  --provider openai        (if OPENAI_API_KEY configured)\n"
                f"  --provider anthropic     (if ANTHROPIC_API_KEY configured)\n"
                f"  --provider deepseek      (if DEEPSEEK_API_KEY configured)\n"
                f"  --provider ollama        (local, free - no key needed)"
            )
        else:
            raise Exception(f"OpenRouter API error ({status_code}): {error_msg}")

    def validate_config(self) -> list[str]:
        """Validate OpenRouter configuration.

        Returns:
            List of error messages (empty if valid).
        """
        errors: list[str] = []

        if not self.api_key or len(self.api_key) < 10:
            errors.append(
                "OpenRouter API key is required. "
                "Get yours at: https://openrouter.ai/keys"
            )

        if not self._validate_model_format(self.model):
            errors.append(
                f"Invalid model format '{self.model}'. "
                f"Use 'vendor/model-name' format (e.g., 'openai/gpt-4o')"
            )

        return errors

    def _build_prompt(self, diff: GitDiff) -> str:
        """Build prompt using external template.

        Args:
            diff: GitDiff object.

        Returns:
            Rendered prompt string.
        """
        from gitcommit_ai.prompts.loader import PromptLoader

        file_list = "\n".join(
            f"- {f.path} (+{f.additions} -{f.deletions})" for f in diff.files
        )

        loader = PromptLoader()
        template = loader.load("openrouter")

        return loader.render(
            template,
            file_list=file_list,
            total_additions=diff.total_additions,
            total_deletions=diff.total_deletions
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
