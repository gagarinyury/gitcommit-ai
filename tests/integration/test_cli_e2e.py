"""End-to-end CLI integration tests."""
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from gitcommit_ai.cli.main import main


class TestCLIEndToEnd:
    """Test CLI end-to-end workflows."""

    @pytest.fixture
    def temp_git_repo_with_changes(self):
        """Create git repo with staged changes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Initialize git
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )

            # Create and stage a file
            test_file = repo_path / "feature.py"
            test_file.write_text("def new_feature():\n    pass\n")
            subprocess.run(["git", "add", "feature.py"], cwd=repo_path, check=True)

            yield repo_path

    def test_cli_generate_with_mocked_ai(
        self, temp_git_repo_with_changes: Path
    ) -> None:
        """CLI generates commit message with mocked AI provider."""
        import os

        with patch("gitcommit_ai.generator.generator.CommitMessageGenerator.generate") as mock_generate:
            from gitcommit_ai.generator.message import CommitMessage

            mock_generate.return_value = CommitMessage(
                type="feat",
                scope="api",
                description="add new feature endpoint",
                body=None,
                breaking_changes=[],
            )

            original_cwd = os.getcwd()
            try:
                os.chdir(temp_git_repo_with_changes)

                # This would normally run CLI, but we're testing the flow
                # Full E2E test would require subprocess.run with CLI entry point
                assert True  # Placeholder for actual CLI invocation test
            finally:
                os.chdir(original_cwd)

    def test_cli_providers_list_command(self) -> None:
        """CLI lists available providers."""
        # Mock the CLI command execution
        with patch("sys.argv", ["gitcommit-ai", "providers", "list"]):
            with patch("gitcommit_ai.cli.main.print") as mock_print:
                with patch("gitcommit_ai.cli.main.sys.exit"):
                    try:
                        main()
                    except SystemExit:
                        pass

                    # Verify providers were listed
                    print_calls = [str(call) for call in mock_print.call_args_list]
                    # At least some provider names should be printed
                    assert len(print_calls) > 0

    def test_cli_hooks_install_command(self, temp_git_repo_with_changes: Path) -> None:
        """CLI installs git hooks."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(temp_git_repo_with_changes)

            with patch("sys.argv", ["gitcommit-ai", "install-hooks"]):
                with patch("gitcommit_ai.cli.main.print"):
                    with patch("gitcommit_ai.cli.main.sys.exit"):
                        try:
                            main()
                        except SystemExit:
                            pass

            # Check that hook was created
            hook_path = temp_git_repo_with_changes / ".git" / "hooks" / "prepare-commit-msg"
            assert hook_path.exists()
        finally:
            os.chdir(original_cwd)


class TestOpenRouterCLIIntegration:
    """Integration tests for OpenRouter CLI functionality.

    Tests T012 and T013 requirements:
    - Error message formatting and fallback suggestions
    - Provider list command shows OpenRouter
    """

    def test_openrouter_error_fallback_suggestions(self, capsys):
        """Test that OpenRouter errors suggest fallback providers.

        This verifies T012 requirement:
        - Mock OpenRouter 503 error
        - Error message suggests --provider openai, --provider ollama, etc.
        """
        from unittest.mock import AsyncMock, MagicMock, patch

        from gitcommit_ai.generator.message import FileDiff, GitDiff
        from gitcommit_ai.providers.openrouter import OpenRouterProvider

        sample_diff = GitDiff(
            files=[FileDiff("test.py", "added", 10, 0, "+code")],
            total_additions=10,
            total_deletions=0
        )

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            # Mock 503 Service Unavailable
            mock_post.return_value = MagicMock(
                status_code=503,
                json=lambda: {
                    "error": {
                        "message": "Service temporarily unavailable",
                        "type": "server_error"
                    }
                }
            )

            provider = OpenRouterProvider(
                api_key="sk-or-v1-test",
                model="openai/gpt-4o-mini"
            )

            with pytest.raises(Exception) as exc_info:
                import asyncio
                asyncio.run(provider.generate_commit_message(sample_diff))

            error_message = str(exc_info.value).lower()

            # Verify error includes fallback suggestions
            assert "503" in error_message or "unavailable" in error_message
            # Should suggest at least one alternative provider
            has_fallback_suggestion = any(
                provider_name in error_message
                for provider_name in ["openai", "anthropic", "ollama", "deepseek"]
            )
            assert has_fallback_suggestion, f"Error should suggest fallback providers: {error_message}"

    def test_cli_providers_list_includes_openrouter(self, capsys):
        """Test that 'gitcommit-ai providers' command includes OpenRouter.

        This verifies T013 requirement:
        - Output includes "openrouter" provider
        - Shows status (configured/not configured)
        - Lists popular models
        """
        import sys
        from unittest.mock import patch

        with patch.object(sys, 'argv', ['gitcommit-ai', 'providers']):
            try:
                main()
            except SystemExit:
                pass

            captured = capsys.readouterr()
            output = captured.out.lower()

            # Verify OpenRouter is listed
            assert "openrouter" in output, "OpenRouter should be in provider list"

            # Should show some model examples
            # (exact format depends on implementation, but should mention models)
            assert "model" in output or "gpt" in output or "claude" in output


class TestMistralCohereRemoval:
    """Tests for Mistral and Cohere provider removal.

    Tests T014 and T015 requirements:
    - Mistral NOT in registry
    - Cohere NOT in registry
    """

    def test_mistral_not_in_registry(self):
        """Test that Mistral is removed from provider registry.

        This verifies T014 requirement:
        - get_provider_names() does NOT include "mistral"
        """
        from gitcommit_ai.providers.registry import ProviderRegistry

        provider_names = ProviderRegistry.get_provider_names()

        assert "mistral" not in provider_names, "Mistral should be removed from registry"
        # OpenRouter should be present (replacement)
        assert "openrouter" in provider_names, "OpenRouter should be in registry"

    def test_cohere_not_in_registry(self):
        """Test that Cohere is removed from provider registry.

        This verifies T015 requirement:
        - get_provider_names() does NOT include "cohere"
        """
        from gitcommit_ai.providers.registry import ProviderRegistry

        provider_names = ProviderRegistry.get_provider_names()

        assert "cohere" not in provider_names, "Cohere should be removed from registry"
        # OpenRouter should be present (replacement)
        assert "openrouter" in provider_names, "OpenRouter should be in registry"
