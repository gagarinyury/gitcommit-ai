"""Tests for Git Hooks Manager."""
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestHookTemplate:
    """T075: Test hook template generation."""

    def test_hook_template_contains_gitcommit_ai_marker(self):
        """Test template has GitCommit AI marker comment."""
        from gitcommit_ai.hooks.template import get_hook_template

        template = get_hook_template()
        assert "# GitCommit AI" in template
        assert "GITCOMMIT_AI_HOOK_VERSION" in template

    def test_hook_template_is_valid_bash(self):
        """Test template starts with shebang."""
        from gitcommit_ai.hooks.template import get_hook_template

        template = get_hook_template()
        assert template.startswith("#!/usr/bin/env bash")

    def test_hook_template_handles_commit_source_arg(self):
        """Test template checks $2 (commit source)."""
        from gitcommit_ai.hooks.template import get_hook_template

        template = get_hook_template()
        assert "COMMIT_SOURCE=$2" in template
        assert "merge" in template  # Should skip merge commits

    def test_hook_template_macos_compatible(self):
        """Test template doesn't use GNU timeout (not available on macOS)."""
        from gitcommit_ai.hooks.template import get_hook_template

        template = get_hook_template()
        # Should NOT use 'timeout' command (GNU coreutils, not on macOS)
        assert "timeout 10s" not in template
        # Should use background execution with kill for timeout
        assert "kill" in template or "GENERATE_PID" in template


class TestHookManagerInstall:
    """T076: Test HookManager.install()."""

    def test_install_creates_hook_file(self):
        """Test install creates .git/hooks/prepare-commit-msg."""
        from gitcommit_ai.hooks.manager import HookManager

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            hooks_dir = repo_path / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            HookManager.install(repo_path)

            hook_file = hooks_dir / "prepare-commit-msg"
            assert hook_file.exists()

    def test_install_makes_hook_executable(self):
        """Test install sets executable bit on hook."""
        from gitcommit_ai.hooks.manager import HookManager

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            hooks_dir = repo_path / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            HookManager.install(repo_path)

            hook_file = hooks_dir / "prepare-commit-msg"
            assert hook_file.stat().st_mode & 0o111  # Executable bit

    def test_install_creates_hooks_dir_if_missing(self):
        """Test install creates .git/hooks/ if it doesn't exist."""
        from gitcommit_ai.hooks.manager import HookManager

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            git_dir = repo_path / ".git"
            git_dir.mkdir()
            # Don't create hooks dir

            HookManager.install(repo_path)

            hooks_dir = git_dir / "hooks"
            assert hooks_dir.exists()

    def test_install_raises_if_hook_exists_without_force(self):
        """Test install raises error if hook exists and force=False."""
        from gitcommit_ai.hooks.manager import HookManager

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            hooks_dir = repo_path / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)
            hook_file = hooks_dir / "prepare-commit-msg"
            hook_file.write_text("# Existing hook")

            with pytest.raises(FileExistsError, match="already exists"):
                HookManager.install(repo_path, force=False)

    def test_install_overwrites_with_force_flag(self):
        """Test install overwrites existing hook when force=True."""
        from gitcommit_ai.hooks.manager import HookManager

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            hooks_dir = repo_path / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)
            hook_file = hooks_dir / "prepare-commit-msg"
            hook_file.write_text("# Old hook")

            HookManager.install(repo_path, force=True)

            content = hook_file.read_text()
            assert "GitCommit AI" in content
            assert "# Old hook" not in content


class TestHookManagerUninstall:
    """T077: Test HookManager.uninstall()."""

    def test_uninstall_removes_gitcommit_ai_hook(self):
        """Test uninstall removes hook file."""
        from gitcommit_ai.hooks.manager import HookManager

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            hooks_dir = repo_path / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)
            hook_file = hooks_dir / "prepare-commit-msg"
            hook_file.write_text("# GITCOMMIT_AI_HOOK_VERSION=1.0.0")

            HookManager.uninstall(repo_path)

            assert not hook_file.exists()

    def test_uninstall_does_nothing_if_no_hook(self):
        """Test uninstall succeeds silently if no hook exists."""
        from gitcommit_ai.hooks.manager import HookManager

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            hooks_dir = repo_path / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            # Should not raise
            HookManager.uninstall(repo_path)

    def test_uninstall_raises_if_not_gitcommit_hook_without_force(self):
        """Test uninstall refuses to remove non-GitCommit hook without force."""
        from gitcommit_ai.hooks.manager import HookManager

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            hooks_dir = repo_path / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)
            hook_file = hooks_dir / "prepare-commit-msg"
            hook_file.write_text("# Some other hook")

            with pytest.raises(ValueError, match="not a GitCommit AI hook"):
                HookManager.uninstall(repo_path, force=False)

    def test_uninstall_removes_any_hook_with_force(self):
        """Test uninstall removes any hook when force=True."""
        from gitcommit_ai.hooks.manager import HookManager

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            hooks_dir = repo_path / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)
            hook_file = hooks_dir / "prepare-commit-msg"
            hook_file.write_text("# Other hook")

            HookManager.uninstall(repo_path, force=True)

            assert not hook_file.exists()


class TestHookManagerDetection:
    """T078: Test HookManager.is_installed()."""

    def test_is_installed_returns_true_when_hook_exists(self):
        """Test is_installed returns True for GitCommit AI hook."""
        from gitcommit_ai.hooks.manager import HookManager

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            hooks_dir = repo_path / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)
            hook_file = hooks_dir / "prepare-commit-msg"
            hook_file.write_text("# GITCOMMIT_AI_HOOK_VERSION=1.0.0")

            assert HookManager.is_installed(repo_path) is True

    def test_is_installed_returns_false_when_no_hook(self):
        """Test is_installed returns False when hook missing."""
        from gitcommit_ai.hooks.manager import HookManager

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            hooks_dir = repo_path / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            assert HookManager.is_installed(repo_path) is False

    def test_is_installed_returns_false_for_non_gitcommit_hook(self):
        """Test is_installed returns False for other hooks."""
        from gitcommit_ai.hooks.manager import HookManager

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            hooks_dir = repo_path / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)
            hook_file = hooks_dir / "prepare-commit-msg"
            hook_file.write_text("#!/bin/bash\necho 'other hook'")

            assert HookManager.is_installed(repo_path) is False

    def test_validate_installation_returns_no_errors_for_valid_hook(self):
        """Test validate_installation returns [] for healthy hook."""
        from gitcommit_ai.hooks.manager import HookManager

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            HookManager.install(repo_path)

            errors = HookManager.validate_installation(repo_path)
            assert errors == []

    def test_validate_installation_detects_missing_hook(self):
        """Test validate_installation detects missing hook."""
        from gitcommit_ai.hooks.manager import HookManager

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            hooks_dir = repo_path / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)

            errors = HookManager.validate_installation(repo_path)
            assert "not installed" in errors[0]

    def test_validate_installation_detects_non_executable_hook(self):
        """Test validate_installation detects non-executable hook."""
        from gitcommit_ai.hooks.manager import HookManager

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            hooks_dir = repo_path / ".git" / "hooks"
            hooks_dir.mkdir(parents=True)
            hook_file = hooks_dir / "prepare-commit-msg"
            hook_file.write_text("# GITCOMMIT_AI_HOOK_VERSION=1.0.0")
            hook_file.chmod(0o644)  # Not executable

            errors = HookManager.validate_installation(repo_path)
            assert any("not executable" in e for e in errors)
