"""Tests for PromptLoader - external prompt template system."""
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from gitcommit_ai.prompts.loader import PromptLoader


class TestPromptLoaderBasics:
    """Test basic PromptLoader functionality."""

    def test_loads_default_template_from_package(self) -> None:
        """T201: Loads default template from package templates/ directory."""
        loader = PromptLoader()
        template = loader.load("deepseek")

        # Should load successfully
        assert template is not None
        assert len(template) > 0
        assert isinstance(template, str)

    def test_raises_error_on_missing_template(self) -> None:
        """T201: Raises error when template doesn't exist."""
        loader = PromptLoader()

        with pytest.raises(FileNotFoundError, match="nonexistent"):
            loader.load("nonexistent")

    def test_loads_all_provider_templates(self) -> None:
        """T201: All 7 providers have templates."""
        loader = PromptLoader()
        providers = ["openai", "anthropic", "deepseek", "ollama", "gemini", "mistral", "cohere"]

        for provider in providers:
            template = loader.load(provider)
            assert template is not None
            assert len(template) > 0


class TestPromptLoaderUserOverrides:
    """Test user override system."""

    def test_loads_user_override_when_exists(self) -> None:
        """T201: Prefers user override from ~/.gitcommit-ai/prompts/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "prompts"
            user_dir.mkdir()
            user_template = user_dir / "deepseek.txt"
            user_template.write_text("CUSTOM USER PROMPT")

            loader = PromptLoader(user_prompts_dir=user_dir)
            template = loader.load("deepseek")

            assert template == "CUSTOM USER PROMPT"

    def test_falls_back_to_default_when_no_override(self) -> None:
        """T201: Uses default when user override doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "prompts"
            user_dir.mkdir()

            loader = PromptLoader(user_prompts_dir=user_dir)
            template = loader.load("deepseek")

            # Should load default, not error
            assert template is not None
            assert "CUSTOM" not in template  # Not the user one


class TestPromptLoaderRendering:
    """Test template rendering with variables."""

    def test_renders_template_with_variables(self) -> None:
        """T201: Substitutes {var} placeholders correctly."""
        loader = PromptLoader()
        template = "Hello {name}, you have {count} messages"

        result = loader.render(template, name="Alice", count=5)

        assert result == "Hello Alice, you have 5 messages"

    def test_renders_multiline_template(self) -> None:
        """T201: Handles multiline templates."""
        loader = PromptLoader()
        template = """CHANGES:
{diff_content}

STATS:
Total: {total_additions} additions"""

        result = loader.render(
            template,
            diff_content="+ added line\n- removed line",
            total_additions=10
        )

        assert "+ added line" in result
        assert "10 additions" in result

    def test_renders_missing_variable_as_empty(self) -> None:
        """T201: Missing variables render as empty string or raise error."""
        loader = PromptLoader()
        template = "Hello {name}, {missing}"

        # Either raises KeyError or renders as empty - pick one
        with pytest.raises(KeyError, match="missing"):
            loader.render(template, name="Alice")


class TestPromptLoaderCaching:
    """Test template caching for performance."""

    def test_caches_loaded_templates(self) -> None:
        """T201: Doesn't reload template on subsequent calls."""
        loader = PromptLoader()

        # Load twice
        template1 = loader.load("deepseek")
        template2 = loader.load("deepseek")

        # Should be same object (cached)
        assert template1 is template2

    def test_cache_is_per_provider(self) -> None:
        """T201: Different providers have separate cache entries."""
        loader = PromptLoader()

        deepseek = loader.load("deepseek")
        ollama = loader.load("ollama")

        assert deepseek != ollama
        assert deepseek is not ollama


class TestPromptLoaderErrorHandling:
    """Test error handling and edge cases."""

    def test_handles_malformed_template(self) -> None:
        """T201: Handles templates with syntax errors gracefully."""
        loader = PromptLoader()
        template = "Hello {name"  # Missing closing brace

        # Should either validate on load or fail on render
        # Let's say it fails on render
        with pytest.raises((KeyError, ValueError)):
            loader.render(template, name="Alice")

    def test_handles_empty_template(self) -> None:
        """T201: Handles empty template file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user_dir = Path(tmpdir) / "prompts"
            user_dir.mkdir()
            empty_template = user_dir / "test.txt"
            empty_template.write_text("")

            loader = PromptLoader(user_prompts_dir=user_dir)
            template = loader.load("test")

            assert template == ""
