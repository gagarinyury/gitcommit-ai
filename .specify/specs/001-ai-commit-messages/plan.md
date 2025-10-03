# Implementation Plan: AI-Powered Git Commit Message Generator

**Branch**: `001-ai-commit-messages` | **Date**: 2025-10-02 | **Spec**: [001-ai-commit-messages.md](../001-ai-commit-messages.md)

## Summary
Build a Python CLI tool that analyzes git staged changes and generates conventional commit messages using OpenAI or Anthropic APIs. Primary focus: library-first architecture with clean separation between git operations, AI provider abstraction, and CLI interface.

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: Standard library only (subprocess, json, os, pathlib); AI clients: `httpx` (async HTTP)
**Storage**: N/A (reads git state, no persistence)
**Testing**: pytest with pytest-asyncio for async code
**Target Platform**: Linux/macOS (git required)
**Project Type**: Single (standalone CLI tool)
**Performance Goals**: <3s for typical diffs (<500 lines), <10s for large diffs
**Constraints**: API rate limits respected, graceful degradation on failures
**Scale/Scope**: Single repository per invocation, local tool (no server component)

## Constitution Check

### ✅ Library-First Architecture
- Core modules: `git_operations`, `ai_providers`, `message_generator`
- Each library independently testable with clear interfaces
- CLI layer thin wrapper around libraries

### ✅ CLI Interface Mandate
- `gitcommit-ai generate [--json] [--provider=openai|anthropic] [--verbose]`
- Human-readable default output, JSON via flag
- Exit codes: 0=success, 1=git error, 2=API error, 3=config error

### ✅ Test-First Development
- Tests written before implementation for all core functions
- Integration tests for git and API interactions (mocked initially)
- Acceptance criteria from spec mapped to test cases

### ✅ Integration Testing Priority
- Git operations: subprocess mocking, real git repo test fixtures
- AI providers: HTTP mocking with recorded responses
- End-to-end: temporary git repo + mock API

### ✅ Simplicity & YAGNI
- No ORM, no web framework, no heavy dependencies
- Direct subprocess calls to git (no GitPython)
- Simple httpx for API calls (no langchain/SDKs initially)

**Complexity Tracking**: None. Minimal dependency approach adheres to constitution.

## Project Structure

### Documentation (this feature)
```
.specify/specs/001-ai-commit-messages/
├── plan.md              # This file
├── research.md          # Phase 0: git diff parsing, AI prompt strategies
├── data-model.md        # Phase 1: internal data structures
├── quickstart.md        # Phase 1: setup and usage guide
├── contracts/           # Phase 1: API interfaces
│   ├── git-operations.md
│   ├── ai-provider.md
│   └── cli-interface.md
└── tasks.md             # Phase 2: created by /tasks command
```

### Source Code (repository root)
```
src/gitcommit_ai/
├── core/
│   ├── __init__.py
│   ├── git.py               # Git diff extraction, staging checks
│   ├── diff_parser.py       # Parse diff into structured format
│   └── config.py            # Configuration loading (env vars)
├── providers/
│   ├── __init__.py
│   ├── base.py              # AIProvider abstract interface
│   ├── openai.py            # OpenAI implementation
│   └── anthropic.py         # Anthropic implementation
├── generator/
│   ├── __init__.py
│   ├── message.py           # CommitMessage data class
│   └── generator.py         # Orchestrates git → AI → message
└── cli/
    ├── __init__.py
    └── main.py              # CLI entry point (argparse)

tests/
├── unit/
│   ├── test_git.py
│   ├── test_diff_parser.py
│   ├── test_openai.py
│   ├── test_anthropic.py
│   └── test_generator.py
├── integration/
│   ├── test_git_integration.py
│   ├── test_api_integration.py
│   └── test_cli_e2e.py
└── fixtures/
    ├── sample_diffs/
    └── mock_responses/

pyproject.toml               # Project metadata, deps, entry points
README.md                    # User-facing documentation
.gitignore
```

## Phase 0: Research

**Output**: `research.md` documenting:

1. **Git Diff Extraction**
   - Command: `git diff --cached --unified=3`
   - Parsing strategies for diff format
   - Edge cases: binary files, large diffs, merge conflicts

2. **AI Prompt Design**
   - System prompt template for commit message generation
   - How to structure diff context (truncation strategy)
   - Conventional commit format specification

3. **API Integration Patterns**
   - OpenAI Chat Completions API (model: gpt-4o-mini)
   - Anthropic Messages API (model: claude-3-haiku)
   - Error handling: rate limits, network failures, invalid responses

4. **Conventional Commit Specification**
   - Format: `type(scope): description`
   - Types: feat, fix, docs, style, refactor, test, chore
   - Scope extraction from file paths

## Phase 1: Design

**Outputs**: `data-model.md`, `contracts/`, `quickstart.md`, `CLAUDE.md`

### Data Model (`data-model.md`)
```python
@dataclass
class GitDiff:
    files: list[FileDiff]
    total_additions: int
    total_deletions: int

@dataclass
class FileDiff:
    path: str
    change_type: Literal["added", "modified", "deleted"]
    additions: int
    deletions: int
    diff_content: str

@dataclass
class CommitMessage:
    type: str  # feat, fix, etc.
    scope: Optional[str]
    description: str
    body: Optional[str]
    breaking_changes: list[str]

    def format(self) -> str:
        """Returns conventional commit formatted string"""
```

### Contracts

**`contracts/git-operations.md`**
```python
class GitOperations:
    def is_git_repository() -> bool
    def get_staged_diff() -> GitDiff
    def has_staged_changes() -> bool
    def create_commit(message: str) -> None
```

**`contracts/ai-provider.md`**
```python
class AIProvider(ABC):
    @abstractmethod
    async def generate_commit_message(diff: GitDiff) -> CommitMessage

    @abstractmethod
    def validate_config() -> list[str]  # Returns missing config keys
```

**`contracts/cli-interface.md`**
- Command structure
- Argument specifications
- Output formats (human-readable vs JSON)
- Exit codes

### Agent Context (`CLAUDE.md`)
Runtime guidance for Claude Code:
- Project structure navigation
- Testing workflow (TDD sequence)
- How to run tests: `pytest -v`
- Linting: `ruff check src/`
- Type checking: `mypy src/`

### Quickstart (`quickstart.md`)
- Installation: `pip install -e .`
- Configuration: `export OPENAI_API_KEY=...`
- Usage examples
- Troubleshooting common errors

## Phase 2: Task Generation Plan

The `/tasks` command will create `tasks.md` by:

1. **Analyzing contracts** to identify implementable units
2. **Grouping by dependency layers**:
   - Layer 0: Data models, configuration
   - Layer 1: Git operations (no AI deps)
   - Layer 2: AI providers (no git deps)
   - Layer 3: Generator (combines git + AI)
   - Layer 4: CLI (thin wrapper)
3. **Creating test-first task pairs**:
   - Task N: Write tests for X
   - Task N+1: Implement X to pass tests
4. **Identifying integration milestones**:
   - After Layer 1: Can extract diffs
   - After Layer 2: Can call AI APIs
   - After Layer 3: Can generate messages
   - After Layer 4: Full CLI functional

Each task will include:
- Prerequisites (prior tasks)
- Acceptance criteria (test assertions)
- Files to create/modify
- Estimated complexity

## Progress Tracking

- [x] Initial Constitution Check (passed)
- [ ] Phase 0: Research (pending /plan execution)
- [ ] Phase 1: Design artifacts (pending /plan execution)
- [ ] Post-Design Constitution Check (pending)
- [ ] Phase 2: Task generation (delegated to /tasks)
- [ ] Phase 3-4: Implementation (delegated to developer)

## Unresolved Questions

1. **From FR-019**: Commit message style customization
   - **Decision needed**: Support emoji prefixes (e.g., ✨ feat)? Max description length? Tone (formal vs casual)?
   - **Recommendation**: Start without customization (use strict conventional commits), add config in v2

2. **Diff truncation strategy**:
   - **Decision needed**: For large diffs (>10k lines), truncate intelligently or sample key sections?
   - **Recommendation**: Truncate to first 500 lines + summary stats, document limitation

3. **Offline fallback**:
   - **Decision needed**: Provide fallback when API unavailable?
   - **Recommendation**: No fallback in MVP, clear error message suffices
