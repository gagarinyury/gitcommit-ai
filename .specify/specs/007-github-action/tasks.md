# Tasks: GitHub Action for CI/CD

**Input**: plan.md from `.specify/specs/007-github-action/`
**Prerequisites**: plan.md ✅

---

## MVP Scope (Simplified)

Focus on **core validation** for MVP. Auto-fix and PR comments are future enhancements.

---

## Phase 1: Setup

- [ ] **T001** Create `src/gitcommit_ai/action/validator.py` skeleton
- [ ] **T002** Create `src/gitcommit_ai/action/scorer.py` skeleton
- [ ] **T003** Update `src/gitcommit_ai/action/runner.py` skeleton

---

## Phase 2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE PHASE 3

**CRITICAL: All tests MUST be written and MUST FAIL before implementation begins**

### Validator Tests
- [ ] **T004** Test `CommitValidator.validate_conventional()` for valid commits
- [ ] **T005** Test `CommitValidator.validate_conventional()` for invalid commits
- [ ] **T006** Test `CommitValidator.validate_conventional()` edge cases (empty, malformed)

### Scorer Tests
- [ ] **T007** Test `CommitScorer.score()` for high-quality commits (80-100)
- [ ] **T008** Test `CommitScorer.score()` for medium-quality commits (50-79)
- [ ] **T009** Test `CommitScorer.score()` for low-quality commits (0-49)
- [ ] **T010** Test `CommitScorer.get_issues()` identifies problems

### Runner Tests (update existing)
- [ ] **T011** Test `runner.main()` validates git repository
- [ ] **T012** Test `runner.main()` handles missing API key
- [ ] **T013** Test `runner.main()` returns 0 on success
- [ ] **T014** Test `runner.main()` reads GitHub Actions env vars
- [ ] **T015** Test `runner.main()` sets GitHub Actions outputs

---

## Phase 3: Core Implementation (ONLY after tests are failing)

### Validator Implementation
- [ ] **T016** Implement `CommitValidator.validate_conventional()`
  - Regex: `^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?!?: .+$`
  - Return tuple: (is_valid, issues)

### Scorer Implementation
- [ ] **T017** Implement `CommitScorer.score()`
  - Check type presence (+40 points)
  - Check scope presence (+20 points)
  - Check description length 10-80 chars (+30 points)
  - Check no generic words like "fix stuff" (+10 points)

- [ ] **T018** Implement `CommitScorer.get_issues()`
  - Return list of validation issues

### Runner Implementation
- [ ] **T019** Implement `runner.main()`
  - Read `GITHUB_EVENT_PATH` for PR commits
  - Validate each commit
  - Score each commit
  - Output summary to stdout

- [ ] **T020** Implement GitHub Actions outputs
  - Write to `GITHUB_OUTPUT` file
  - Set: `total_commits`, `valid_commits`, `invalid_commits`

---

## Phase 4: Integration

- [ ] **T021** Create `action.yml` GitHub Action metadata
  ```yaml
  name: 'GitCommit AI Validator'
  description: 'Validate commit messages with AI'
  inputs:
    provider:
      description: 'AI provider'
      default: 'openai'
    strict-mode:
      description: 'Fail on invalid commits'
      default: 'false'
  outputs:
    total_commits:
      description: 'Total commits analyzed'
  runs:
    using: 'composite'
    steps:
      - run: python -m gitcommit_ai.action.runner
  ```

- [ ] **T022** Test action.yml with act (local GitHub Actions runner)

---

## Phase 5: Polish

- [ ] **T023** Add docstrings to all public functions (Google style)
- [ ] **T024** Run mypy and fix type issues
- [ ] **T025** Run ruff and fix linting
- [ ] **T026** Update action_runner tests to pass
- [ ] **T027** Manual smoke test in real GitHub Actions

---

## Dependency Graph

```
Setup: T001 → T002 → T003
         ↓
Tests:  T004,T005,T006 (validator)
        T007,T008,T009,T010 (scorer)
        T011,T012,T013,T014,T015 (runner)
         ↓
Impl:   T016 (validator) → T017,T018 (scorer) → T019,T020 (runner)
         ↓
Integration: T021 → T022
         ↓
Polish: T023,T024,T025 → T026 → T027
```

---

## Validation Checklist

- [x] All contracts from plan.md have corresponding tests
- [x] TDD sequence enforced (tests before implementation)
- [x] File paths specified in task descriptions
- [x] Simplified scope for MVP (no auto-fix, no PR comments initially)
- [ ] Constitution compliance verified (pending implementation review)

---

## Notes

- **MVP Focus**: Core validation + scoring only
- **Future**: PR comments, auto-fix, GitHub API integration
- **Testing**: Mock GitHub Actions environment variables
- **Exit Codes**: 0=success, 1=failure (strict mode only)
