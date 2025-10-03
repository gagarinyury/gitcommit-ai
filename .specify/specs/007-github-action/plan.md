# Implementation Plan: GitHub Action for CI/CD

**Branch**: `007-github-action` | **Date**: 2025-10-02 | **Spec**: [007-github-action.md](../007-github-action.md)

## Summary
Build a GitHub Action that validates commit messages in PRs using AI. Supports validation, suggestions, and auto-fix modes with multiple AI providers.

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: httpx (async HTTP), existing gitcommit_ai libraries
**Storage**: GitHub Actions environment variables, no persistence
**Testing**: pytest with mocking for GitHub Actions environment
**Target Platform**: GitHub Actions (Ubuntu Linux)
**Project Type**: GitHub Action (composite action with Python)
**Performance Goals**: <2 minutes for PRs with <20 commits
**Constraints**: GitHub Actions rate limits (1000 API calls/hour), no secrets in fork PRs
**Scale/Scope**: Single PR validation per run

## Constitution Check

### ✅ Library-First Architecture
- `action/validator.py` — CommitValidator library (standalone)
- `action/scorer.py` — CommitScorer library (standalone)
- `action/runner.py` — Main entrypoint (orchestrator)
- All libraries independently testable

### ✅ CLI Interface Mandate
- Action runs as Python script in GitHub Actions
- Outputs to stdout (GitHub Actions logs)
- Sets GitHub Actions outputs via environment file
- Exit codes: 0=success, 1=validation failure (strict mode)

### ✅ Test-First Development
- Tests written BEFORE implementation
- All tests MUST fail initially (RED)
- Implementation makes tests pass (GREEN)
- Refactor while maintaining GREEN

### ✅ Integration Testing Priority
- Test with mock GitHub Actions environment
- Test AI provider integration
- Test commit validation logic
- End-to-end action workflow test

### ✅ Simplicity & YAGNI
- Reuse existing gitcommit_ai providers
- No new dependencies (use stdlib + httpx)
- Minimal GitHub Actions complexity

## Project Structure

### Documentation
```
.specify/specs/007-github-action/
├── plan.md              # This file
├── tasks.md             # Task breakdown (next step)
└── contracts/           # API contracts
    ├── validator.md     # CommitValidator interface
    └── scorer.md        # CommitScorer interface
```

### Source Code
```
src/gitcommit_ai/action/
├── __init__.py
├── runner.py            # Main GitHub Action entrypoint
├── validator.py         # CommitValidator (validates conventional commits)
├── scorer.py            # CommitScorer (scores quality 0-100)
└── github_api.py        # GitHub API helpers (PR comments)

tests/unit/
└── test_action_runner.py   # Update existing tests
└── test_validator.py        # New: validator tests
└── test_scorer.py           # New: scorer tests

tests/integration/
└── test_action_e2e.py       # New: full action workflow test
```

### GitHub Action Files
```
action.yml               # GitHub Action metadata
```

## Phase 0: Research

**Key Findings:**
1. **GitHub Actions Environment:**
   - Inputs via `INPUT_*` env vars
   - Outputs via `GITHUB_OUTPUT` file
   - PR info in `GITHUB_EVENT_PATH` JSON

2. **Commit Validation:**
   - Conventional commits regex: `^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?!?: .+$`
   - Scoring based on: type presence, scope, description length, clarity

3. **GitHub API:**
   - POST `/repos/{owner}/{repo}/issues/{pr_number}/comments` for PR comments
   - Requires `GITHUB_TOKEN` from secrets

## Phase 1: Design

### Data Models

**CommitValidationResult:**
```python
@dataclass
class CommitValidationResult:
    sha: str
    message: str
    is_valid: bool
    score: int  # 0-100
    issues: list[str]  # Validation issues
    suggestion: Optional[str]  # AI-generated suggestion
```

**ActionConfig:**
```python
@dataclass
class ActionConfig:
    provider: str
    model: Optional[str]
    mode: Literal["validate", "suggest", "auto-fix"]
    strict_mode: bool
    min_score: int
    gitmoji: bool
```

### Contracts

**validator.md:**
```python
class CommitValidator:
    def validate_conventional(message: str) -> tuple[bool, list[str]]
    def score_quality(message: str) -> int
```

**scorer.md:**
```python
class CommitScorer:
    def score(message: str) -> int  # 0-100
    def get_issues(message: str) -> list[str]
```

## Phase 2: Task Generation Plan

Tasks will be broken down into:
1. **Setup** (T001-T003): Action structure, config loading
2. **Tests Layer** (T004-T012): Write ALL tests (RED phase)
3. **Implementation Layer** (T013-T020): Implement to pass tests (GREEN)
4. **Integration** (T021-T024): GitHub Actions integration, action.yml
5. **Polish** (T025-T027): Documentation, smoke test

## Progress Tracking

- [x] Initial Constitution Check (passed)
- [x] Phase 0: Research
- [x] Phase 1: Design
- [x] Phase 2: Task generation plan
- [ ] Tasks.md creation (next: /tasks)
- [ ] Implementation (next: follow tasks.md)

## Unresolved Questions

None. All requirements clear from spec.
