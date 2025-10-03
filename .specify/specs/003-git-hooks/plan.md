# Implementation Plan: Git Hooks Integration

**Branch**: `003-git-hooks` | **Date**: 2025-10-02 | **Spec**: [003-git-hooks.md](../003-git-hooks.md)

## Summary
Add automated commit message generation via git prepare-commit-msg hook. Users run `install-hooks` once, then every `git commit` auto-generates AI messages. Implements proper hook lifecycle (install/uninstall/debug), error handling, and respects git conventions (merge/amend skip).

## Technical Context
**Language/Version**: Python 3.11+ (hook script: bash)
**Primary Dependencies**: Standard library only (subprocess, pathlib, shutil)
**Storage**: `.git/hooks/prepare-commit-msg` (shell script), `~/.gitcommit-ai/hooks.log` (errors)
**Testing**: pytest with temp git repos, hook execution tests
**Target Platform**: Linux/macOS (bash hooks)
**Project Type**: Single (extends CLI with hook commands)
**Performance Goals**: <3s hook execution (caching diff/config)
**Constraints**: Hooks must never fail commit (exit 0 always), limited PATH in hook env
**Scale/Scope**: Per-repository installation, global config support

## Constitution Check

### ✅ Library-First Architecture
- `src/gitcommit_ai/hooks/manager.py` - hook installation logic
- `src/gitcommit_ai/hooks/template.py` - hook script template
- Independently testable with temp directories

### ✅ CLI Interface Mandate
- `gitcommit-ai install-hooks [--force]`
- `gitcommit-ai uninstall-hooks [--force]`
- `gitcommit-ai debug-hooks` (troubleshooting)
- Exit codes: 6=hooks error

### ✅ Test-First Development
- Tests for hook installation/uninstallation
- Tests for hook execution in temp repos
- Tests for edge cases (merge commits, missing config)

### ✅ Integration Testing Priority
- Real git repo fixtures with hooks
- Hook execution via subprocess
- Config file interaction

### ✅ Simplicity & YAGNI
- No hook framework (direct shell script)
- No complex config (reuse existing Config)
- No daemon/watcher (hooks are git-native)

**Complexity Tracking**: None. Minimal feature using git's native hook system.

## Project Structure

### Documentation
```
.specify/specs/003-git-hooks/
├── plan.md
├── research.md          # Git hooks spec, prepare-commit-msg details
├── hook-template.sh     # Actual hook script template
└── tasks.md
```

### Source Code
```
src/gitcommit_ai/
├── hooks/
│   ├── __init__.py
│   ├── manager.py           # [NEW] HookManager class
│   └── template.py          # [NEW] Hook script template
└── cli/
    └── main.py              # [MODIFY] Add install-hooks, uninstall-hooks commands

tests/
├── unit/
│   └── test_hooks.py        # [NEW] Hook manager tests
└── integration/
    └── test_hooks_e2e.py    # [NEW] Real git repo + hook execution
```

## Phase 0: Research

**Output**: `research.md` documenting:

1. **Git Hook Specification**
   - Hook types: `prepare-commit-msg` runs before editor opens
   - Arguments: `$1` = message file path, `$2` = source (message/template/merge/squash/commit), `$3` = commit SHA
   - Exit behavior: `exit 0` continues, non-zero aborts

2. **Hook Best Practices**
   - Always exit 0 (never block commits)
   - Write errors as comments in message file
   - Use absolute paths (PATH limited)
   - Fast execution or background process

3. **Example Hook Script**
```bash
#!/usr/bin/env bash
# prepare-commit-msg hook for GitCommit AI

COMMIT_MSG_FILE=$1
COMMIT_SOURCE=$2

# Skip for merge/squash/amend
if [ "$COMMIT_SOURCE" = "merge" ] || [ "$COMMIT_SOURCE" = "squash" ]; then
    exit 0
fi

# Generate AI message
gitcommit-ai generate --json 2>/dev/null | jq -r '.message' > "$COMMIT_MSG_FILE"

exit 0
```

4. **Hook Detection Strategy**
   - Check if `.git/hooks/prepare-commit-msg` exists
   - Parse for GitCommit AI marker comment
   - Backup existing hooks before overwrite

## Phase 1: Design

**Outputs**: `data-model.md`, `hook-template.sh`

### Hook Template (`hook-template.sh`)
```bash
#!/usr/bin/env bash
# GitCommit AI - Auto-generated commit messages
# GITCOMMIT_AI_HOOK_VERSION=1.0.0

COMMIT_MSG_FILE=$1
COMMIT_SOURCE=$2
COMMIT_SHA=$3

# Skip for special commit types
if [ -n "$COMMIT_SOURCE" ]; then
    exit 0
fi

# Find gitcommit-ai executable
GITCOMMIT_AI=$(command -v gitcommit-ai 2>/dev/null)
if [ -z "$GITCOMMIT_AI" ]; then
    echo "# GitCommit AI not found in PATH" >> "$COMMIT_MSG_FILE"
    exit 0
fi

# Generate message (timeout after 10s)
TEMP_MSG=$(mktemp)
timeout 10s "$GITCOMMIT_AI" generate --json 2>/dev/null > "$TEMP_MSG" || {
    echo "# GitCommit AI generation failed" >> "$COMMIT_MSG_FILE"
    rm -f "$TEMP_MSG"
    exit 0
}

# Extract message from JSON
python3 -c "import json, sys; print(json.load(sys.stdin)['message'])" < "$TEMP_MSG" > "$COMMIT_MSG_FILE" 2>/dev/null || {
    echo "# GitCommit AI: Error parsing response" >> "$COMMIT_MSG_FILE"
}

rm -f "$TEMP_MSG"
exit 0
```

### Hook Manager API (`manager.py`)
```python
class HookManager:
    def install(repo_path: Path, force: bool = False) -> None:
        """Install prepare-commit-msg hook"""

    def uninstall(repo_path: Path, force: bool = False) -> None:
        """Remove GitCommit AI hook"""

    def is_installed(repo_path: Path) -> bool:
        """Check if hook is installed"""

    def validate_installation(repo_path: Path) -> list[str]:
        """Check hook health (executable, correct version)"""
```

## Phase 2: Task Generation Plan

Tasks will cover:
1. **Layer 1**: Hook template creation (shell script)
2. **Layer 2**: HookManager implementation (install/uninstall logic)
3. **Layer 3**: CLI integration (new commands)
4. **Layer 4**: Integration tests (temp repos + hook execution)

## Progress Tracking

- [x] Initial Constitution Check (passed)
- [ ] Phase 0: Research
- [ ] Phase 1: Design
- [ ] Post-Design Constitution Check
- [ ] Phase 2: Task generation (/tasks)
- [ ] Phase 3-4: Implementation

## Dependencies

**Required from Feature 001:**
- CLI infrastructure (`src/gitcommit_ai/cli/main.py`)
- Config system (`src/gitcommit_ai/core/config.py`)
- Generate command (used by hook)

**Required from Feature 002:**
- Ollama support (if user configured)

## Unresolved Questions

1. **Hook performance**: If generation takes >5s, show progress?
   - **Recommendation**: No progress in hook (non-interactive). Timeout after 10s.

2. **Multiple hooks**: Preserve existing prepare-commit-msg?
   - **Recommendation**: MVP = overwrite (backup to `.bak`). V2 = chain hooks.

3. **Windows support**: Git Bash compatibility?
   - **Recommendation**: Out of scope for MVP (focus Linux/macOS).

4. **Hook config storage**: Per-repo `.git/gitcommit-ai-config`?
   - **Recommendation**: Reuse global `~/.gitcommit-ai/config`. Per-repo in V2.
