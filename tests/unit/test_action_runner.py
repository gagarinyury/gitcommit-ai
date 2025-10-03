"""Tests for GitHub Action runner."""
from unittest.mock import MagicMock, patch

import pytest

from gitcommit_ai.action import runner


class TestActionRunner:
    """Test GitHub Action main runner."""

    @patch("gitcommit_ai.action.runner.os.getenv")
    def test_main_reads_inputs_from_environment(self, mock_getenv: MagicMock) -> None:
        """Reads action inputs from environment variables."""
        env_vars = {
            "INPUT_PROVIDER": "openai",
            "INPUT_API_KEY": "test-key",
            "INPUT_MODEL": "gpt-4o",
            "INPUT_STRICT_MODE": "false",
            "INPUT_AUTO_FIX": "false",
            "INPUT_COMMENT_PR": "true",
        }
        mock_getenv.side_effect = lambda k, default="": env_vars.get(k, default)

        with patch("gitcommit_ai.action.runner.sys.exit"):
            with patch("gitcommit_ai.action.runner.print"):
                # Just test that it reads config without crashing
                try:
                    runner.main()
                except SystemExit:
                    pass  # Expected

    @patch("gitcommit_ai.action.runner.os.getenv")
    def test_main_handles_missing_github_event(self, mock_getenv: MagicMock) -> None:
        """Exits with error when GITHUB_EVENT_PATH missing."""
        mock_getenv.return_value = ""

        with patch("gitcommit_ai.action.runner.sys.exit") as mock_exit:
            with patch("gitcommit_ai.action.runner.print"):
                runner.main()
                mock_exit.assert_called_with(1)

    @patch("gitcommit_ai.action.runner.os.getenv")
    @patch("gitcommit_ai.action.runner.GitOperations.is_git_repository")
    def test_main_validates_git_repository(
        self, mock_is_repo: MagicMock, mock_getenv: MagicMock
    ) -> None:
        """Checks if running in git repository."""
        env_vars = {
            "GITHUB_EVENT_PATH": "/tmp/event.json",
        }
        mock_getenv.side_effect = lambda k, default="": env_vars.get(k, default)
        mock_is_repo.return_value = False  # Not a git repo

        with patch("gitcommit_ai.action.runner.sys.exit") as mock_exit:
            with patch("gitcommit_ai.action.runner.print"):
                runner.main()
                mock_exit.assert_called_with(1)

    @patch("gitcommit_ai.action.runner.os.getenv")
    def test_main_supports_strict_mode_flag(self, mock_getenv: MagicMock) -> None:
        """Recognizes strict_mode input."""
        env_vars = {
            "INPUT_PROVIDER": "openai",
            "INPUT_API_KEY": "test-key",
            "INPUT_STRICT_MODE": "true",
        }
        mock_getenv.side_effect = lambda k, default="": env_vars.get(k, default)

        with patch("gitcommit_ai.action.runner.sys.exit"):
            with patch("gitcommit_ai.action.runner.print") as mock_print:
                try:
                    runner.main()
                except SystemExit:
                    pass

                # Verify strict mode was logged
                print_calls = [str(call) for call in mock_print.call_args_list]
                assert any("Strict Mode" in str(call) for call in print_calls)

    @patch("gitcommit_ai.action.runner.os.getenv")
    @patch("gitcommit_ai.action.runner.GitOperations.is_git_repository")
    @patch("builtins.open")
    def test_main_returns_zero_on_success(
        self, mock_open: MagicMock, mock_is_repo: MagicMock, mock_getenv: MagicMock
    ) -> None:
        """Returns 0 exit code on successful validation."""
        import json
        env_vars = {
            "GITHUB_EVENT_PATH": "/tmp/event.json",
        }
        mock_getenv.side_effect = lambda k, default="": env_vars.get(k, default)
        mock_is_repo.return_value = True

        # Mock event file with no PR
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = json.dumps({"action": "opened"})
        mock_open.return_value = mock_file

        exit_code = runner.main()
        assert exit_code == 0
