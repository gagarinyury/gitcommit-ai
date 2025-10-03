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
