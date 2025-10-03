"""CLI entry point for gitcommit-ai."""
import argparse
import asyncio
import json
import os
import sys

from gitcommit_ai.core.config import Config
from gitcommit_ai.core.git import GitError, GitOperations
from gitcommit_ai.generator.generator import CommitMessageGenerator
from gitcommit_ai.generator.message import CommitMessage


def _log_commit_stats(
    provider: str,
    model: str | None,
    commit_type: str | None,
    success: bool,
    response_time_ms: int | None,
    diff_lines: int | None
) -> None:
    """Log commit generation to statistics database.

    Args:
        provider: AI provider used.
        model: Model used (if known).
        commit_type: Commit type (feat, fix, etc.).
        success: Whether generation succeeded.
        response_time_ms: Response time in milliseconds.
        diff_lines: Number of diff lines.
    """
    try:
        from datetime import datetime

        from gitcommit_ai.stats.database import CommitRecord, StatsDatabase

        db = StatsDatabase()
        record = CommitRecord(
            id=None,
            timestamp=datetime.now().isoformat(),
            provider=provider,
            model=model,
            commit_type=commit_type,
            success=success,
            response_time_ms=response_time_ms,
            diff_lines=diff_lines
        )
        db.insert(record)
    except Exception:
        # Silently fail - stats should never break generation
        pass


def format_output(
    message: CommitMessage, json_format: bool = False, use_gitmoji: bool = False
) -> str:
    """Format commit message for output.

    Args:
        message: CommitMessage object.
        json_format: If True, output JSON; else human-readable.
        use_gitmoji: If True, add emoji prefix.

    Returns:
        Formatted string.
    """
    if json_format:
        data = {
            "type": message.type,
            "scope": message.scope,
            "description": message.description,
            "body": message.body,
            "breaking_changes": message.breaking_changes,
        }
        if message.emoji:
            data["emoji"] = message.emoji
        return json.dumps(data, indent=2)
    else:
        # Use GitmojiMapper for formatting
        if use_gitmoji:
            from gitcommit_ai.gitmoji.mapper import GitmojiMapper

            return GitmojiMapper.format_message(message, use_gitmoji=True)
        return message.format()


async def run_generate(args: argparse.Namespace) -> None:
    """Run the generate command.

    Args:
        args: Parsed command-line arguments.

    Raises:
        SystemExit: On errors with appropriate exit codes.
    """
    import time
    from datetime import datetime

    start_time = time.time()

    # Check if in git repository
    if not GitOperations.is_git_repository():
        print("Error: Not a git repository", file=sys.stderr)
        sys.exit(1)

    # Check for staged changes
    if not GitOperations.has_staged_changes():
        print("Error: No staged changes to commit", file=sys.stderr)
        sys.exit(1)

    # Load configuration
    config = Config.load()
    errors = config.validate()
    if errors:
        print("Configuration errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(3)

    # Determine provider
    provider = args.provider if args.provider else config.default_provider

    # Handle Ollama separately (no API key needed)
    if provider == "ollama":
        if args.verbose:
            print("Using Ollama (local AI)...", file=sys.stderr)
        try:
            from gitcommit_ai.providers.ollama import OllamaProvider

            ollama = OllamaProvider(model=args.model)
            validation_errors = ollama.validate_config()
            if validation_errors:
                # Show friendly setup message
                print("\n⚠️  Ollama not found or not configured properly\n", file=sys.stderr)
                print("🎉 Get FREE local AI in 2 steps:\n", file=sys.stderr)

                import platform
                os_type = platform.system()
                if os_type == "Darwin":
                    print("  1. Install: brew install ollama", file=sys.stderr)
                elif os_type == "Linux":
                    print("  1. Install: curl https://ollama.ai/install.sh | sh", file=sys.stderr)
                elif os_type == "Windows":
                    print("  1. Download from: https://ollama.ai", file=sys.stderr)
                else:
                    print("  1. Visit: https://ollama.ai", file=sys.stderr)

                print("  2. Download model: ollama pull qwen2.5:7b  (4.7GB, best quality)", file=sys.stderr)
                print("\n💡 Or use quick setup: gitcommit-ai setup-ollama\n", file=sys.stderr)
                print("Errors:", file=sys.stderr)
                for error in validation_errors:
                    print(f"  - {error}", file=sys.stderr)
                sys.exit(4)  # Ollama not installed

            # Determine gitmoji usage
            use_gitmoji = False
            if hasattr(args, "gitmoji") and args.gitmoji:
                use_gitmoji = True
            if hasattr(args, "no_gitmoji") and args.no_gitmoji:
                use_gitmoji = False

            diff = GitOperations.get_staged_diff()

            # Check if multiple suggestions requested
            if hasattr(args, 'count') and args.count > 1:
                from gitcommit_ai.generator.multi_generator import MultiSuggestionGenerator
                from gitcommit_ai.cli.picker import InteractivePicker

                multi_gen = MultiSuggestionGenerator()

                async def generate_fn(temp: float) -> 'CommitMessage':
                    # Ollama generates with variance each time
                    return await ollama.generate_commit_message(diff)

                suggestions = await multi_gen.generate_multiple(
                    count=args.count,
                    generate_fn=generate_fn
                )

                # JSON mode: output all suggestions
                if args.json:
                    output_data = [
                        {
                            "type": msg.type,
                            "scope": msg.scope,
                            "description": msg.description,
                            "body": msg.body,
                            "breaking_changes": msg.breaking_changes,
                        }
                        for msg in suggestions
                    ]
                    print(json.dumps(output_data, indent=2))
                    return

                # Interactive picker
                picker = InteractivePicker()
                message = picker.pick(suggestions)

                if message is None:
                    print("No message selected, commit cancelled", file=sys.stderr)
                    sys.exit(1)
            else:
                # Single message generation
                message = await ollama.generate_commit_message(diff)

            output = format_output(
                message, json_format=args.json, use_gitmoji=use_gitmoji
            )
            print(output)
            return
        except RuntimeError as e:
            print(f"Ollama error: {e}", file=sys.stderr)
            sys.exit(5)  # Ollama model error

    # Handle new providers (gemini, mistral, cohere, deepseek)
    if provider in ["gemini", "mistral", "cohere", "deepseek"]:
        if args.verbose:
            print(f"Using {provider.title()} provider...", file=sys.stderr)
        try:
            if provider == "gemini":
                from gitcommit_ai.providers.gemini import GeminiProvider
                provider_instance = GeminiProvider(model=args.model)
            elif provider == "mistral":
                from gitcommit_ai.providers.mistral import MistralProvider
                provider_instance = MistralProvider(model=args.model or "mistral-small")
            elif provider == "cohere":
                from gitcommit_ai.providers.cohere import CohereProvider
                provider_instance = CohereProvider(model=args.model or "command-light")
            elif provider == "deepseek":
                from gitcommit_ai.providers.deepseek import DeepSeekProvider
                provider_instance = DeepSeekProvider(model=args.model or "deepseek-chat")

            validation_errors = provider_instance.validate_config()
            if validation_errors:
                for error in validation_errors:
                    print(f"Error: {error}", file=sys.stderr)
                sys.exit(3)

            # Determine gitmoji usage
            use_gitmoji = False
            if hasattr(args, "gitmoji") and args.gitmoji:
                use_gitmoji = True
            if hasattr(args, "no_gitmoji") and args.no_gitmoji:
                use_gitmoji = False

            diff = GitOperations.get_staged_diff()
            message = await provider_instance.generate_commit_message(diff)
            output = format_output(message, json_format=args.json, use_gitmoji=use_gitmoji)
            print(output)
            return
        except RuntimeError as e:
            print(f"{provider.title()} error: {e}", file=sys.stderr)
            sys.exit(2)

    # Get API key for cloud providers (openai, anthropic)
    if provider == "openai":
        api_key = config.openai_api_key
    else:
        api_key = config.anthropic_api_key

    if not api_key:
        print(f"Error: No API key for {provider}", file=sys.stderr)
        sys.exit(3)

    # Determine if gitmoji should be used
    use_gitmoji = False
    if hasattr(args, "gitmoji") and args.gitmoji:
        use_gitmoji = True
    if hasattr(args, "no_gitmoji") and args.no_gitmoji:
        use_gitmoji = False

    # Generate commit message(s)
    try:
        # Check if multiple suggestions requested
        if hasattr(args, 'count') and args.count > 1:
            from gitcommit_ai.generator.multi_generator import MultiSuggestionGenerator
            from gitcommit_ai.cli.picker import InteractivePicker

            generator = CommitMessageGenerator(provider=provider, api_key=api_key)
            multi_gen = MultiSuggestionGenerator()

            async def generate_fn(temp: float) -> 'CommitMessage':
                # Temporarily modify provider temperature (simplified)
                return await generator.generate()

            suggestions = await multi_gen.generate_multiple(
                count=args.count,
                generate_fn=generate_fn
            )

            # JSON mode: output all suggestions
            if args.json:
                output_data = [
                    {
                        "type": msg.type,
                        "scope": msg.scope,
                        "description": msg.description,
                        "body": msg.body,
                        "breaking_changes": msg.breaking_changes,
                    }
                    for msg in suggestions
                ]
                print(json.dumps(output_data, indent=2))
                return

            # Interactive picker
            picker = InteractivePicker()
            message = picker.pick(suggestions)

            if message is None:
                print("No message selected, commit cancelled", file=sys.stderr)
                sys.exit(1)
        else:
            # Single message generation
            generator = CommitMessageGenerator(provider=provider, api_key=api_key)
            message = await generator.generate()

        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)

        # Log to statistics
        _log_commit_stats(
            provider=provider,
            model=None,  # OpenAI/Anthropic don't expose model in generator
            commit_type=message.type,
            success=True,
            response_time_ms=response_time_ms,
            diff_lines=GitOperations.get_staged_diff().total_additions + GitOperations.get_staged_diff().total_deletions
        )

        # Output result
        output = format_output(message, json_format=args.json, use_gitmoji=use_gitmoji)
        print(output)

    except GitError as e:
        print(f"Git error: {e}", file=sys.stderr)
        _log_commit_stats(provider=provider, model=None, commit_type=None, success=False, response_time_ms=None, diff_lines=None)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        _log_commit_stats(provider=provider, model=None, commit_type=None, success=False, response_time_ms=None, diff_lines=None)
        sys.exit(2)


def run_install_hooks(args: argparse.Namespace) -> None:
    """Run the install-hooks command."""
    from pathlib import Path

    from gitcommit_ai.hooks.manager import HookManager

    repo_path = Path.cwd()

    try:
        HookManager.install(repo_path, force=args.force)
        print(f"✓ Git hooks installed successfully in {repo_path / '.git' / 'hooks'}")
    except FileExistsError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Use --force to overwrite existing hook", file=sys.stderr)
        sys.exit(6)
    except Exception as e:
        print(f"Error installing hooks: {e}", file=sys.stderr)
        sys.exit(6)


def run_uninstall_hooks(args: argparse.Namespace) -> None:
    """Run the uninstall-hooks command."""
    from pathlib import Path

    from gitcommit_ai.hooks.manager import HookManager

    repo_path = Path.cwd()

    try:
        HookManager.uninstall(repo_path, force=args.force)
        print("✓ Git hooks uninstalled successfully")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Use --force to remove anyway", file=sys.stderr)
        sys.exit(6)
    except Exception as e:
        print(f"Error uninstalling hooks: {e}", file=sys.stderr)
        sys.exit(6)


def run_debug_hooks(args: argparse.Namespace) -> None:
    """Run the debug-hooks command."""
    from pathlib import Path

    from gitcommit_ai.hooks.manager import HookManager

    repo_path = Path.cwd()

    print("GitCommit AI Hooks Debug Info")
    print("=" * 40)
    print(f"Repository: {repo_path}")
    print(f"Hooks dir: {repo_path / '.git' / 'hooks'}")
    print()

    if HookManager.is_installed(repo_path):
        print("✓ GitCommit AI hook is installed")
        errors = HookManager.validate_installation(repo_path)
        if errors:
            print("\n⚠ Validation issues:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("✓ Hook validation passed")
    else:
        print("✗ GitCommit AI hook is NOT installed")
        print("\nRun: gitcommit-ai install-hooks")


def run_providers_list(args: argparse.Namespace) -> None:
    """Run the providers command."""
    from gitcommit_ai.providers.registry import ProviderRegistry

    print("Available AI Providers:")
    print()

    providers = ProviderRegistry.list_providers()
    for provider in providers:
        status = "✓" if provider.configured else "✗"
        models_str = ", ".join(provider.models[:2])
        if len(provider.models) > 2:
            models_str += ", ..."

        print(f"  {status} {provider.name:12} {provider.description}")
        print(f"     Models: {models_str}")
        if not provider.configured and provider.name != "ollama":
            key_name = f"{provider.name.upper()}_API_KEY"
            print(f"     Config: Set {key_name} environment variable")
        print()


def run_validate_pr(args: argparse.Namespace) -> int:
    """Run the validate-pr command (GitHub Action mode).

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    import os
    from gitcommit_ai.action.runner import main as action_main

    # Set environment variables from CLI args for action runner
    if args.json:
        os.environ["OUTPUT_FORMAT"] = "json"
    if args.strict:
        os.environ["INPUT_STRICT_MODE"] = "true"
    if args.provider:
        os.environ["INPUT_PROVIDER"] = args.provider

    # Run action runner
    return action_main()


def run_setup_ollama(args: argparse.Namespace) -> int:
    """Run the setup-ollama command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    from gitcommit_ai.cli.setup import OllamaSetup

    return OllamaSetup.run()


def run_stats(args: argparse.Namespace) -> None:
    """Run the stats command."""
    from pathlib import Path

    from gitcommit_ai.stats.aggregator import StatsAggregator
    from gitcommit_ai.stats.database import StatsDatabase
    from gitcommit_ai.stats.exporter import StatsExporter

    db = StatsDatabase()
    aggregator = StatsAggregator(db)

    # Get summary
    summary = aggregator.get_summary(provider=args.provider, days=args.days)

    # Handle export
    if args.export:
        records = db.get_all()
        output_path = Path(f"gitcommit-stats.{args.export}")

        if args.export == "csv":
            StatsExporter.to_csv(records, output_path)
        else:
            StatsExporter.to_json(records, output_path)

        print(f"✓ Exported {len(records)} records to {output_path}")
        return

    # Display summary
    print("GitCommit AI Statistics")
    print("=" * 40)
    print()
    print(f"Total Commits:    {summary.total_commits}")
    print(f"Success Rate:     {summary.success_rate:.1f}%")

    if summary.avg_response_time_ms:
        print(f"Avg Response:     {summary.avg_response_time_ms:.0f}ms")

    if summary.fastest_provider:
        print(f"Fastest Provider: {summary.fastest_provider}")

    if summary.most_reliable_provider:
        print(f"Most Reliable:    {summary.most_reliable_provider}")

    print()

    if summary.provider_breakdown:
        print("Provider Breakdown:")
        for provider, count in summary.provider_breakdown.items():
            pct = (count / summary.total_commits) * 100
            print(f"  {provider:12} {count:4} ({pct:.1f}%)")
        print()

    if summary.type_breakdown:
        print("Commit Types:")
        for commit_type, count in summary.type_breakdown.items():
            pct = (count / summary.total_commits) * 100
            print(f"  {commit_type:12} {count:4} ({pct:.1f}%)")
        print()


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI-powered git commit message generator"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate commit message for staged changes"
    )
    generate_parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )
    generate_parser.add_argument(
        "--provider",
        choices=["openai", "anthropic", "ollama", "gemini", "mistral", "cohere", "deepseek"],
        help="AI provider to use (default: from config)",
    )
    generate_parser.add_argument(
        "--model",
        help="Model to use (provider-specific, e.g., llama3.2 for Ollama)",
    )
    generate_parser.add_argument(
        "--verbose", action="store_true", help="Verbose output"
    )
    generate_parser.add_argument(
        "--gitmoji", action="store_true", help="Add emoji prefix to commit message"
    )
    generate_parser.add_argument(
        "--no-gitmoji",
        action="store_true",
        help="Disable emoji prefix (even if enabled in config)",
    )
    generate_parser.add_argument(
        "--count",
        type=int,
        default=1,
        metavar="N",
        help="Generate N suggestions and pick interactively (1-10, default: 1)",
    )

    # install-hooks command
    install_parser = subparsers.add_parser(
        "install-hooks", help="Install git hooks for automatic message generation"
    )
    install_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing hook"
    )

    # uninstall-hooks command
    uninstall_parser = subparsers.add_parser(
        "uninstall-hooks", help="Remove GitCommit AI git hooks"
    )
    uninstall_parser.add_argument(
        "--force", action="store_true", help="Force removal even if not GitCommit hook"
    )

    # debug-hooks command
    subparsers.add_parser("debug-hooks", help="Debug hook installation status")

    # providers command
    subparsers.add_parser("providers", help="List available AI providers")

    # setup-ollama command
    subparsers.add_parser(
        "setup-ollama", help="Interactive Ollama setup wizard (install + download models)"
    )

    # stats command
    stats_parser = subparsers.add_parser("stats", help="Show commit statistics")
    stats_parser.add_argument(
        "--provider", help="Filter by provider"
    )
    stats_parser.add_argument(
        "--days", type=int, help="Filter by last N days"
    )
    stats_parser.add_argument(
        "--export", choices=["csv", "json"], help="Export data to file"
    )

    # validate-pr command (GitHub Action mode)
    validate_pr_parser = subparsers.add_parser(
        "validate-pr", help="Validate commits in PR (GitHub Action mode)"
    )
    validate_pr_parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )
    validate_pr_parser.add_argument(
        "--strict", action="store_true", help="Fail on invalid commits"
    )
    validate_pr_parser.add_argument(
        "--provider", help="AI provider (for suggestions)"
    )

    args = parser.parse_args()

    if args.command == "generate":
        asyncio.run(run_generate(args))
    elif args.command == "install-hooks":
        run_install_hooks(args)
    elif args.command == "uninstall-hooks":
        run_uninstall_hooks(args)
    elif args.command == "debug-hooks":
        run_debug_hooks(args)
    elif args.command == "providers":
        run_providers_list(args)
    elif args.command == "setup-ollama":
        sys.exit(run_setup_ollama(args))
    elif args.command == "stats":
        run_stats(args)
    elif args.command == "validate-pr":
        return run_validate_pr(args)


if __name__ == "__main__":
    main()
