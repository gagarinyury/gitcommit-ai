"""Main GitHub Action runner."""
import os
import sys

from gitcommit_ai.core.git import GitOperations


def main() -> int:
    """Run the GitHub Action.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    print("=" * 60)
    print("GitCommit AI - Commit Message Validation")
    print("=" * 60)
    print()

    # Get action inputs from environment
    provider = os.getenv("INPUT_PROVIDER", "openai")
    api_key = os.getenv("INPUT_API_KEY", "")
    model = os.getenv("INPUT_MODEL", "")
    strict_mode = os.getenv("INPUT_STRICT_MODE", "false").lower() == "true"
    auto_fix = os.getenv("INPUT_AUTO_FIX", "false").lower() == "true"
    comment_pr = os.getenv("INPUT_COMMENT_PR", "true").lower() == "true"

    print("Configuration:")
    print(f"  Provider:     {provider}")
    print(f"  Model:        {model or '(default)'}")
    print(f"  Strict Mode:  {strict_mode}")
    print(f"  Auto-Fix:     {auto_fix}")
    print(f"  Comment PR:   {comment_pr}")
    print()

    # Check if in git repository
    if not GitOperations.is_git_repository():
        print("ERROR: Not a git repository")
        sys.exit(1)

    # Get PR commits
    github_event_path = os.getenv("GITHUB_EVENT_PATH")
    if not github_event_path:
        print("ERROR: Not running in GitHub Actions environment")
        sys.exit(1)

    try:
        import json
        with open(github_event_path) as f:
            event = json.load(f)

        # Extract PR commits (simplified)
        pr_number = event.get("pull_request", {}).get("number")
        if not pr_number:
            print("WARNING: Not a pull request event, skipping validation")
            return 0

        print(f"Analyzing PR #{pr_number}")
        print()

        # Get commits from PR (would use GitHub API in real implementation)
        commits = _get_pr_commits(pr_number)

        if not commits:
            print("No commits found in PR")
            return 0

        print(f"Found {len(commits)} commit(s)")
        print()

        # Validate each commit
        valid_count = 0
        invalid_count = 0
        suggestions = []

        for i, commit in enumerate(commits, 1):
            sha = commit.get("sha", "unknown")[:7]
            message = commit.get("message", "")

            print(f"[{i}/{len(commits)}] Validating {sha}: {message[:50]}...")

            is_valid = _validate_commit_message(message)

            if is_valid:
                print("  ✓ Valid")
                valid_count += 1
            else:
                print("  ✗ Invalid")
                invalid_count += 1

                # Generate AI suggestion (simplified)
                suggestion = _generate_suggestion(message, provider, api_key, model)
                if suggestion:
                    suggestions.append({
                        "sha": sha,
                        "original": message,
                        "suggestion": suggestion
                    })
                    print(f"  💡 Suggestion: {suggestion}")

            print()

        # Summary
        print("=" * 60)
        print("Summary:")
        print(f"  Total:   {len(commits)}")
        print(f"  Valid:   {valid_count}")
        print(f"  Invalid: {invalid_count}")
        print("=" * 60)

        # Set outputs
        _set_output("total_commits", str(len(commits)))
        _set_output("valid_commits", str(valid_count))
        _set_output("invalid_commits", str(invalid_count))

        # Fail in strict mode if any invalid
        if strict_mode and invalid_count > 0:
            print()
            print("FAILED: Invalid commits found (strict mode enabled)")
            return 1

        return 0

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


def _get_pr_commits(pr_number: int) -> list[dict]:
    """Get commits from PR (mock implementation).

    Args:
        pr_number: PR number.

    Returns:
        List of commit dictionaries.
    """
    # In real implementation, would use GitHub API
    # For now, return mock data
    return [
        {"sha": "abc1234", "message": "add feature"},
        {"sha": "def5678", "message": "feat: implement user authentication"},
    ]


def _validate_commit_message(message: str) -> bool:
    """Validate if commit message follows conventions.

    Args:
        message: Commit message.

    Returns:
        True if valid, False otherwise.
    """
    # Simple validation: check for conventional commit format
    conventional_types = ["feat", "fix", "docs", "style", "refactor", "test", "chore"]

    if ":" not in message:
        return False

    type_part = message.split(":")[0].strip()

    # Check if type is valid (with optional scope)
    if "(" in type_part:
        type_part = type_part.split("(")[0]

    return type_part in conventional_types


def _generate_suggestion(
    message: str,
    provider: str,
    api_key: str,
    model: str
) -> str | None:
    """Generate AI suggestion for commit message.

    Args:
        message: Original commit message.
        provider: AI provider.
        api_key: API key.
        model: Model to use.

    Returns:
        Suggested commit message or None.
    """
    # Simplified: just return a conventional format suggestion
    # Real implementation would use GitCommit AI providers
    return f"feat: {message}"


def _set_output(name: str, value: str) -> None:
    """Set GitHub Actions output.

    Args:
        name: Output name.
        value: Output value.
    """
    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"{name}={value}\n")


if __name__ == "__main__":
    sys.exit(main())
