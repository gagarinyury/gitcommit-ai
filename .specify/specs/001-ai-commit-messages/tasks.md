# Tasks: AI-Powered Git Commit Message Generator

**Input**: Design documents from `.specify/specs/001-ai-commit-messages/`
**Prerequisites**: plan.md ✅

---

## Phase 3.1: Setup

- [ ] **T001** Create project structure: `src/gitcommit_ai/{core,providers,generator,cli}/`, `tests/{unit,integration,fixtures}/`
- [ ] **T002** Initialize Python project with `pyproject.toml` (deps: httpx, pytest, pytest-asyncio, ruff, mypy)
- [ ] **T003** [P] Configure linting (`ruff.toml`), type checking (`mypy.ini`), pytest config
- [ ] **T004** [P] Create `.gitignore` (Python defaults: `__pycache__/`, `*.pyc`, `.pytest_cache/`, `venv/`)
- [ ] **T005** [P] Add test fixtures: `tests/fixtures/sample_diffs/` with 3-5 realistic git diffs

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: All tests MUST be written and MUST FAIL before implementation begins**

### Layer 0: Configuration & Data Models
- [ ] **T006** [P] Test config loading in `tests/unit/test_config.py` (env vars, defaults, validation)
- [ ] **T007** [P] Test GitDiff/CommitMessage dataclasses in `tests/unit/test_models.py` (serialization, validation)

### Layer 1: Git Operations
- [ ] **T008** [P] Test `is_git_repository()` in `tests/unit/test_git.py` (✅ in repo, ❌ outside repo)
- [ ] **T009** [P] Test `has_staged_changes()` in `tests/unit/test_git.py` (empty, non-empty staging)
- [ ] **T010** [P] Test `get_staged_diff()` in `tests/unit/test_git.py` (parse diff output, handle errors)
- [ ] **T011** [P] Test diff parser in `tests/unit/test_diff_parser.py` (additions/deletions, file types)

### Layer 2: AI Providers
- [ ] **T012** [P] Test OpenAI provider in `tests/unit/test_openai.py` (mock HTTP, parse response, handle errors)
- [ ] **T013** [P] Test Anthropic provider in `tests/unit/test_anthropic.py` (mock HTTP, parse response, handle errors)
- [ ] **T014** [P] Test AIProvider validation in `tests/unit/test_providers.py` (missing API keys)

### Layer 3: Message Generator
- [ ] **T015** Test generator orchestration in `tests/unit/test_generator.py` (git → AI → message flow)
- [ ] **T016** [P] Test conventional commit formatting in `tests/unit/test_message.py` (type extraction, scope detection)

### Layer 4: CLI
- [ ] **T017** [P] Test CLI arg parsing in `tests/unit/test_cli.py` (flags: --json, --provider, --verbose)
- [ ] **T018** [P] Test CLI output formatting in `tests/unit/test_cli.py` (human-readable vs JSON)

### Integration Tests
- [ ] **T019** [P] Test git integration in `tests/integration/test_git_integration.py` (real temp repo, actual git commands)
- [ ] **T020** [P] Test API integration in `tests/integration/test_api_integration.py` (recorded HTTP responses with VCR.py)
- [ ] **T021** Test end-to-end CLI in `tests/integration/test_cli_e2e.py` (temp repo + mock API → commit message)

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Layer 0: Configuration & Data Models
- [ ] **T022** [P] Implement config module in `src/gitcommit_ai/core/config.py` (load env vars, validate)
- [ ] **T023** [P] Implement data models in `src/gitcommit_ai/generator/message.py` (GitDiff, CommitMessage dataclasses)

### Layer 1: Git Operations
- [ ] **T024** Implement git operations in `src/gitcommit_ai/core/git.py` (subprocess wrappers: diff, status, commit)
- [ ] **T025** Implement diff parser in `src/gitcommit_ai/core/diff_parser.py` (parse unified diff format)

### Layer 2: AI Providers
- [ ] **T026** [P] Implement base provider in `src/gitcommit_ai/providers/base.py` (AIProvider ABC)
- [ ] **T027** [P] Implement OpenAI provider in `src/gitcommit_ai/providers/openai.py` (httpx async client, API call)
- [ ] **T028** [P] Implement Anthropic provider in `src/gitcommit_ai/providers/anthropic.py` (httpx async client, API call)

### Layer 3: Message Generator
- [ ] **T029** Implement generator in `src/gitcommit_ai/generator/generator.py` (orchestrate git + AI)
- [ ] **T030** Implement conventional commit logic in `src/gitcommit_ai/generator/message.py` (type/scope extraction)

### Layer 4: CLI
- [ ] **T031** Implement CLI entry point in `src/gitcommit_ai/cli/main.py` (argparse, error handling)
- [ ] **T032** Wire up CLI to generator in `src/gitcommit_ai/cli/main.py` (handle --json, --provider flags)
- [ ] **T033** Add CLI entry point to `pyproject.toml` ([project.scripts] gitcommit-ai = "gitcommit_ai.cli.main:main")

---

## Phase 3.4: Polish & Documentation

- [ ] **T034** [P] Add docstrings to all public functions (Google style)
- [ ] **T035** [P] Run mypy and fix type issues (`mypy src/`)
- [ ] **T036** [P] Run ruff and fix linting issues (`ruff check --fix src/ tests/`)
- [ ] **T037** Create README.md (installation, usage examples, API key setup)
- [ ] **T038** Create quickstart guide in `.specify/specs/001-ai-commit-messages/quickstart.md`
- [ ] **T039** [P] Add edge case tests: binary files, empty diffs, network timeouts
- [ ] **T040** Manual smoke test: run on real repository with actual API

---

## Dependency Graph

```
Setup: T001 → T002 → T003,T004,T005 (parallel)
                ↓
Tests Layer 0: T006,T007 (parallel)
                ↓
Tests Layer 1: T008,T009,T010,T011 (parallel)
                ↓
Tests Layer 2: T012,T013,T014 (parallel)
                ↓
Tests Layer 3: T015,T016 (parallel)
                ↓
Tests Layer 4: T017,T018 (parallel)
                ↓
Integration:   T019,T020 (parallel) → T021
                ↓
Impl Layer 0:  T022,T023 (parallel, after all Layer 0 tests)
                ↓
Impl Layer 1:  T024 → T025
                ↓
Impl Layer 2:  T026 → T027,T028 (parallel)
                ↓
Impl Layer 3:  T029 → T030
                ↓
Impl Layer 4:  T031 → T032 → T033
                ↓
Polish:        T034,T035,T036 (parallel) → T037,T038 → T039 → T040
```

---

## Parallel Execution Examples

**After T005 (setup complete):**
```bash
# Parallel test writing (different files, no conflicts)
Agent1: T006 (test_config.py)
Agent2: T007 (test_models.py)
Agent3: T008 (test_git.py, part 1)
```

**After T011 (Layer 1 tests done):**
```bash
# Parallel AI provider test writing
Agent1: T012 (test_openai.py)
Agent2: T013 (test_anthropic.py)
Agent3: T014 (test_providers.py)
```

**After T021 (all tests written & failing):**
```bash
# Parallel implementation (independent modules)
Agent1: T022 (config.py)
Agent2: T023 (message.py)
```

**Polish phase:**
```bash
# Parallel cleanup
Agent1: T034 (docstrings)
Agent2: T035 (mypy fixes)
Agent3: T036 (ruff fixes)
```

---

## Validation Checklist

- [x] All contracts from `plan.md` have corresponding tests (git ops, AI providers, CLI)
- [x] All data models have test coverage (GitDiff, CommitMessage)
- [x] TDD sequence enforced (tests before implementation)
- [x] Parallel tasks marked with [P]
- [x] File paths specified in task descriptions
- [x] Integration tests cover end-to-end scenarios
- [ ] Constitution compliance verified (pending implementation review)

---

## Notes

- **API credentials**: Tests use mocked responses; manual smoke test (T040) requires real API keys
- **Git fixtures**: T005 creates sample diffs for unit tests; integration tests (T019) use real git commands
- **Test isolation**: Each test module focuses on single responsibility (git, AI, CLI layers)
- **Exit codes**: Tests verify CLI returns correct codes (0=success, 1=git error, 2=API error, 3=config error)
