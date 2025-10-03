"""Prompt template loader for AI providers."""
from pathlib import Path


class PromptLoader:
    """Loads and renders prompt templates from files.

    Templates can be overridden by placing custom versions in
    ~/.gitcommit-ai/prompts/ directory.
    """

    def __init__(self, user_prompts_dir: Path | None = None) -> None:
        """Initialize PromptLoader.

        Args:
            user_prompts_dir: Optional custom user prompts directory.
                            Defaults to ~/.gitcommit-ai/prompts/
        """
        # Default templates bundled with package
        self.default_dir = Path(__file__).parent / "templates"

        # User overrides directory
        if user_prompts_dir:
            self.user_dir = user_prompts_dir
        else:
            self.user_dir = Path.home() / ".gitcommit-ai" / "prompts"

        # Cache for loaded templates
        self._cache: dict[str, str] = {}

    def load(self, provider: str) -> str:
        """Load template for provider.

        Args:
            provider: Provider name (e.g., 'openai', 'deepseek').

        Returns:
            Template content as string.

        Raises:
            FileNotFoundError: If template doesn't exist.
        """
        # Check cache first
        if provider in self._cache:
            return self._cache[provider]

        # Try user override first
        user_template = self.user_dir / f"{provider}.txt"
        if user_template.exists():
            content = user_template.read_text(encoding="utf-8")
            self._cache[provider] = content
            return content

        # Fall back to default template
        default_template = self.default_dir / f"{provider}.txt"
        if not default_template.exists():
            raise FileNotFoundError(
                f"Template not found for provider '{provider}'. "
                f"Expected at: {default_template}"
            )

        content = default_template.read_text(encoding="utf-8")
        self._cache[provider] = content
        return content

    def render(self, template: str, **variables: str | int) -> str:
        """Render template with variable substitution.

        Args:
            template: Template string with {var} placeholders.
            **variables: Variables to substitute into template.

        Returns:
            Rendered template string.

        Raises:
            KeyError: If template references undefined variable.
        """
        return template.format(**variables)
