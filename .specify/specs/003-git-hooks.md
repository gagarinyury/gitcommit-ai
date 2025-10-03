# Feature Specification: Git Hooks Integration

**Feature Branch**: `003-git-hooks`
**Created**: 2025-10-02
**Status**: Draft
**Priority**: High (automation = killer feature)

## User Scenarios & Testing

### Primary User Story
A developer installs GitCommit AI hooks once. After that, whenever they run `git commit` (without `-m`), the system automatically generates an AI commit message, opens it in their editor for review/edit, and commits if approved.

### Acceptance Scenarios

1. **Given** hooks installed, **When** user runs `git commit`, **Then** AI generates message → editor opens → user can edit/save/abort

2. **Given** hooks installed, **When** user runs `git commit -m "manual"`, **Then** hooks are bypassed (manual message used)

3. **Given** hooks not installed, **When** user runs `gitcommit-ai install-hooks`, **Then** system creates `.git/hooks/prepare-commit-msg` file

4. **Given** hooks already exist, **When** user runs install-hooks, **Then** system asks: "Overwrite existing hook? (y/n)"

5. **Given** hooks installed, **When** user runs `gitcommit-ai uninstall-hooks`, **Then** system removes hook file

### Edge Cases
- What if `.git/hooks/` doesn't exist? → Create directory
- What if other hooks exist? → Preserve them, add ours
- What if API key missing during hook? → Show error, open editor with empty message
- What if commit is merge/rebase? → Skip AI generation, use default message
- Monorepo with multiple git repos? → Install per-repo

## Requirements

### Functional Requirements

**Installation**
- **FR-040**: System MUST provide `install-hooks` command
- **FR-041**: System MUST create `.git/hooks/prepare-commit-msg` file
- **FR-042**: System MUST make hook file executable (chmod +x)
- **FR-043**: System MUST detect existing hooks and ask before overwriting
- **FR-044**: System MUST support `--force` flag to skip confirmation

**Hook Behavior**
- **FR-045**: Hook MUST run before commit message editor opens
- **FR-046**: Hook MUST generate AI message and write to $1 (commit message file)
- **FR-047**: Hook MUST respect commit source ($2): skip for merge/squash/amend
- **FR-048**: Hook MUST handle API failures gracefully (fall back to empty message)
- **FR-049**: Hook MUST be fast (<5s) or show "Generating..." message

**Uninstallation**
- **FR-050**: System MUST provide `uninstall-hooks` command
- **FR-051**: System MUST remove only GitCommit AI hook (preserve others)
- **FR-052**: System MUST confirm before removal unless `--force` used

**Configuration**
- **FR-053**: Hook MUST respect user's configured provider (from ~/.gitcommit-ai)
- **FR-054**: Hook MUST respect `--no-verify` flag (skip hooks entirely)
- **FR-055**: System MUST allow per-repo hook config (override global)

**Error Handling**
- **FR-056**: Hook MUST NOT fail commit on error (write error to message file as comment)
- **FR-057**: Hook MUST log errors to ~/.gitcommit-ai/hooks.log
- **FR-058**: System MUST provide troubleshooting command: `gitcommit-ai debug-hooks`

### Key Entities

- **HookManager**: Installs/uninstalls/validates hooks
- **HookScript**: Template for prepare-commit-msg hook
- **HookConfig**: Per-repo hook settings (provider, model, enabled)

---

## Technical Constraints

- Git hooks are shell scripts (bash/sh)
- Hook receives args: $1=commit-msg-file, $2=commit-source, $3=commit-sha
- Exit code 0 = continue, non-zero = abort commit
- Hooks run in git repository root
- PATH may be limited (use absolute paths)

---

## Hook Script Template

```bash
#!/bin/sh
# GitCommit AI - prepare-commit-msg hook

COMMIT_MSG_FILE=$1
COMMIT_SOURCE=$2

# Skip for merge/squash/amend
if [ -n "$COMMIT_SOURCE" ]; then
    exit 0
fi

# Skip if message already provided (-m flag)
if [ -s "$COMMIT_MSG_FILE" ]; then
    exit 0
fi

# Generate AI message
gitcommit-ai generate --hook-mode > "$COMMIT_MSG_FILE" 2>> ~/.gitcommit-ai/hooks.log

# Always exit 0 (don't block commit on failure)
exit 0
```

---

## Out of Scope (for MVP)

- Support for other hooks (post-commit, pre-push)
- GUI hook installer
- Hook analytics (track usage)
- Team-wide hook distribution (.githooks/)
- Windows support (Git Bash only)

---

## Success Criteria

- ✅ One-command install: `gitcommit-ai install-hooks`
- ✅ Automatic message generation on `git commit`
- ✅ User can still edit/abort in editor
- ✅ Errors don't block commits
- ✅ Works with existing git workflows
