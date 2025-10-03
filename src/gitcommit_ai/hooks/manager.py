"""Hook installation and management."""
import stat
from pathlib import Path

from gitcommit_ai.hooks.template import get_hook_template


class HookManager:
    """Manages GitCommit AI git hooks."""

    HOOK_NAME = "prepare-commit-msg"
    HOOK_MARKER = "GITCOMMIT_AI_HOOK_VERSION"

    @classmethod
    def install(cls, repo_path: Path, force: bool = False) -> None:
        """Install prepare-commit-msg hook.

        Args:
            repo_path: Path to git repository root.
            force: If True, overwrite existing hook.

        Raises:
            FileExistsError: If hook exists and force=False.
        """
        hooks_dir = repo_path / ".git" / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)

        hook_file = hooks_dir / cls.HOOK_NAME

        if hook_file.exists() and not force:
            raise FileExistsError(
                f"Hook already exists at {hook_file}. Use --force to overwrite."
            )

        # Write hook script
        template = get_hook_template()
        hook_file.write_text(template)

        # Make executable
        current_mode = hook_file.stat().st_mode
        hook_file.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    @classmethod
    def uninstall(cls, repo_path: Path, force: bool = False) -> None:
        """Remove GitCommit AI hook.

        Args:
            repo_path: Path to git repository root.
            force: If True, remove any hook (not just GitCommit AI).

        Raises:
            ValueError: If hook is not GitCommit AI hook and force=False.
        """
        hooks_dir = repo_path / ".git" / "hooks"
        hook_file = hooks_dir / cls.HOOK_NAME

        if not hook_file.exists():
            return  # Nothing to do

        # Check if it's our hook
        content = hook_file.read_text()
        is_our_hook = cls.HOOK_MARKER in content

        if not is_our_hook and not force:
            raise ValueError(
                f"Hook at {hook_file} is not a GitCommit AI hook. "
                f"Use --force to remove anyway."
            )

        hook_file.unlink()

    @classmethod
    def is_installed(cls, repo_path: Path) -> bool:
        """Check if GitCommit AI hook is installed.

        Args:
            repo_path: Path to git repository root.

        Returns:
            True if hook exists and contains GitCommit AI marker.
        """
        hooks_dir = repo_path / ".git" / "hooks"
        hook_file = hooks_dir / cls.HOOK_NAME

        if not hook_file.exists():
            return False

        content = hook_file.read_text()
        return cls.HOOK_MARKER in content

    @classmethod
    def validate_installation(cls, repo_path: Path) -> list[str]:
        """Validate hook installation.

        Args:
            repo_path: Path to git repository root.

        Returns:
            List of validation errors (empty if valid).
        """
        errors = []

        if not cls.is_installed(repo_path):
            errors.append("GitCommit AI hook not installed")
            return errors  # No point checking further

        hooks_dir = repo_path / ".git" / "hooks"
        hook_file = hooks_dir / cls.HOOK_NAME

        # Check if executable
        if not hook_file.stat().st_mode & stat.S_IXUSR:
            errors.append(f"Hook at {hook_file} is not executable")

        return errors
