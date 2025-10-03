# Tasks: Multiple Commit Message Suggestions

**Input**: plan.md from `.specify/specs/008-multiple-suggestions/`
**Prerequisites**: plan.md ✅

---

## MVP Scope (Simplified)

Focus on **core multi-generation + simple picker**. No arrow keys, no regenerate, no fancy UI.

---

## Phase 1: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE IMPLEMENTATION

**CRITICAL: All tests MUST be written and MUST FAIL before implementation begins**

### Multi-Generator Tests
- [ ] **T001** Test `generate_multiple()` generates N suggestions
- [ ] **T002** Test suggestions have different temperatures
- [ ] **T003** Test all suggestions are unique (no duplicates)
- [ ] **T004** Test same provider used for all suggestions
- [ ] **T005** Test temperature range 0.3-0.7
- [ ] **T006** Test count parameter validation (1-10)

### Picker Tests
- [ ] **T007** Test `pick()` returns selected suggestion
- [ ] **T008** Test `pick()` handles invalid input gracefully
- [ ] **T009** Test `pick()` supports number selection (1-N)
- [ ] **T010** Test `pick()` returns None on Ctrl+C/cancel

### CLI Integration Tests
- [ ] **T011** Test `--count 3` flag generates 3 suggestions
- [ ] **T012** Test `--count` with `--json` outputs JSON array
- [ ] **T013** Test picker integration in CLI flow

---

## Phase 2: Core Implementation (ONLY after tests are failing)

### Multi-Generator
- [ ] **T014** Implement `MultiSuggestionGenerator` class
  - Calculate temperature range: linspace(0.3, 0.7, count)
  - Call provider.generate() with different temperatures
  - Validate uniqueness

- [ ] **T015** Implement uniqueness validation
  - Normalize messages for comparison
  - Retry on duplicates (max 2 retries)

### Picker
- [ ] **T016** Implement `InteractivePicker` class
  - Print numbered list of suggestions
  - Read user input (number)
  - Return selected CommitMessage

- [ ] **T017** Handle invalid input
  - Validate number range
  - Re-prompt on invalid input

### CLI Integration
- [ ] **T018** Add `--count` flag to `generate` command in main.py

- [ ] **T019** Integrate multi-generator in `run_generate()`
  - If --count > 1: use MultiSuggestionGenerator
  - If --json: output array, skip picker
  - Else: use InteractivePicker

- [ ] **T020** Update JSON output format for multiple suggestions

---

## Phase 3: Polish

- [ ] **T021** Add docstrings (Google style)
- [ ] **T022** Run mypy and fix type issues
- [ ] **T023** Run ruff and fix linting
- [ ] **T024** Manual smoke test with real AI provider

---

## Dependency Graph

```
Setup: (no setup needed, use existing structure)
         ↓
Tests:  T001-T006 (multi_generator)
        T007-T010 (picker)
        T011-T013 (CLI integration)
         ↓
Impl:   T014-T015 (multi_generator) → T016-T017 (picker) → T018-T020 (CLI)
         ↓
Polish: T021-T024
```

---

## Validation Checklist

- [x] All contracts from plan.md have corresponding tests
- [x] TDD sequence enforced (tests before implementation)
- [x] File paths specified
- [x] Simplified MVP scope
- [ ] Constitution compliance verified (pending)

---

## Notes

- **MVP**: Simple numbered picker (no arrow keys)
- **No regenerate**: Future enhancement
- **Temperature strategy**: Linear interpolation 0.3-0.7
- **Uniqueness**: Normalize + compare, retry on dup
