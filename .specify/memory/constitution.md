<!--
Sync Impact Report:
Version: 1.0.0 (initial constitution)
Ratification Date: 2025-10-02
Modified Principles: N/A (initial version)
Templates Status: ✅ All templates aligned
-->

# GitCommit AI Constitution

## Core Principles

### I. Library-First Architecture
Every feature must start as a standalone Python library with clear interfaces. Libraries must be:
- Self-contained and independently testable
- Documented with docstrings and type hints
- Reusable outside the CLI context

**Rationale**: Separation of concerns enables testing, reuse, and clear boundaries.

### II. CLI Interface Mandate
All functionality MUST be accessible via CLI commands following these rules:
- Text-based input/output (stdin/args → stdout, errors → stderr)
- Support both JSON and human-readable output formats
- Exit codes: 0 = success, non-zero = failure with descriptive message

**Rationale**: CLI ensures automation, scriptability, and debuggability.

### III. Test-First Development (NON-NEGOTIABLE)
TDD is mandatory for all code:
1. Write tests describing desired behavior
2. User reviews and approves test cases
3. Tests MUST fail initially (red)
4. Implement code to pass tests (green)
5. Refactor while maintaining green tests

**Rationale**: Tests define contracts, prevent regressions, and guide design.

### IV. Integration Testing Priority
Focus integration tests on:
- AI provider API interactions (OpenAI, Anthropic)
- Git command execution and parsing
- End-to-end CLI workflow scenarios

**Rationale**: Unit tests catch logic errors; integration tests catch real-world failures.

### V. Simplicity and YAGNI
- Start with minimal viable implementation
- No frameworks unless absolutely required
- Plain Python stdlib preferred over external dependencies
- One feature at a time

**Rationale**: Complexity is the enemy of maintainability and AI-assisted development.

## Technology Constraints

### Language & Runtime
- Python 3.11+ (leveraging modern type hints)
- Standard library preferred; justified deps only
- No web frameworks for CLI tools

### AI Integration
- Support OpenAI and Anthropic APIs initially
- Provider abstraction for future extensibility
- API keys via environment variables (never hardcoded)

### Git Integration
- Use subprocess for git commands (avoid gitpython dependency initially)
- Parse git output with robust error handling
- Support git hooks for auto-commit-message generation

## Development Workflow

### Code Quality Gates
1. All tests passing (pytest)
2. Type checks passing (mypy)
3. Linter passing (ruff)
4. Manual smoke test on real repository

### Review Process
- Constitution compliance verified on every PR
- Breaking changes require constitution amendment
- Security review for API key handling

## Governance

This constitution is the ultimate authority for development decisions. Any violation requires:
1. Documented justification
2. Approval from project maintainer
3. Constitution amendment if permanent exception

Amendments follow semantic versioning:
- MAJOR: Principle removal or incompatible change
- MINOR: New principle or section added
- PATCH: Clarification or typo fix

**Version**: 1.0.0 | **Ratified**: 2025-10-02 | **Last Amended**: 2025-10-02
