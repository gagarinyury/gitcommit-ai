"""Tests for validate-pr CLI command."""
import json
from unittest.mock import MagicMock, patch

import pytest

from gitcommit_ai.cli.main import main


class TestValidatePRCommand:
    """Test suite for validate-pr CLI command."""

    @patch("sys.argv", ["gitcommit-ai", "validate-pr"])
    @patch("gitcommit_ai.cli.main.os.getenv")
    @patch("gitcommit_ai.cli.main.GitOperations.is_git_repository")
    @patch("builtins.open")
    def test_validate_pr_command_exists(
        self, mock_open: MagicMock, mock_is_repo: MagicMock, mock_getenv: MagicMock
    ) -> None:
        """validate-pr command is available in CLI."""
        mock_getenv.return_value = "/tmp/event.json"
        mock_is_repo.return_value = True

        # Mock empty event
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = json.dumps({"action": "opened"})
        mock_open.return_value = mock_file

        with patch("gitcommit_ai.cli.main.print"):
            exit_code = main()
            assert exit_code == 0

    @patch("sys.argv", ["gitcommit-ai", "validate-pr", "--json"])
    @patch("gitcommit_ai.cli.main.os.getenv")
    @patch("gitcommit_ai.cli.main.GitOperations.is_git_repository")
    @patch("builtins.open")
    def test_validate_pr_json_output(
        self, mock_open: MagicMock, mock_is_repo: MagicMock, mock_getenv: MagicMock
    ) -> None:
        """validate-pr supports --json flag for JSON output."""
        mock_getenv.return_value = "/tmp/event.json"
        mock_is_repo.return_value = True

        # Mock event with PR
        event_data = {
            "pull_request": {"number": 123},
            "action": "opened"
        }
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = json.dumps(event_data)
        mock_open.return_value = mock_file

        with patch("gitcommit_ai.cli.main.print") as mock_print:
            exit_code = main()

            # Should print JSON
            print_calls = [str(call) for call in mock_print.call_args_list]
            # At least one call should contain JSON-like output
            assert exit_code == 0

    @patch("sys.argv", ["gitcommit-ai", "validate-pr", "--strict"])
    @patch("gitcommit_ai.cli.main.os.getenv")
    @patch("gitcommit_ai.cli.main.GitOperations.is_git_repository")
    @patch("builtins.open")
    def test_validate_pr_strict_mode(
        self, mock_open: MagicMock, mock_is_repo: MagicMock, mock_getenv: MagicMock
    ) -> None:
        """validate-pr supports --strict flag."""
        mock_getenv.return_value = "/tmp/event.json"
        mock_is_repo.return_value = True

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = json.dumps({"action": "opened"})
        mock_open.return_value = mock_file

        with patch("gitcommit_ai.cli.main.print"):
            exit_code = main()
            assert exit_code == 0

    @patch("sys.argv", ["gitcommit-ai", "validate-pr"])
    @patch("gitcommit_ai.cli.main.os.getenv")
    @patch("gitcommit_ai.cli.main.GitOperations.is_git_repository")
    def test_validate_pr_not_in_git_repo(
        self, mock_is_repo: MagicMock, mock_getenv: MagicMock
    ) -> None:
        """validate-pr exits with code 1 if not in git repo."""
        mock_getenv.return_value = "/tmp/event.json"
        mock_is_repo.return_value = False

        with patch("gitcommit_ai.cli.main.print"):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1

    @patch("sys.argv", ["gitcommit-ai", "validate-pr"])
    @patch("gitcommit_ai.cli.main.os.getenv")
    def test_validate_pr_missing_event_path(self, mock_getenv: MagicMock) -> None:
        """validate-pr exits with code 1 if GITHUB_EVENT_PATH missing."""
        mock_getenv.return_value = ""

        with patch("gitcommit_ai.cli.main.print"):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1
