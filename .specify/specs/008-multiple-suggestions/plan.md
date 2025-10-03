# Implementation Plan: Multiple Commit Message Suggestions

**Branch**: `008-multiple-suggestions` | **Date**: 2025-10-02 | **Spec**: [008-multiple-suggestions.md](../008-multiple-suggestions.md)

## Summary
Extend `gitcommit-ai generate` to support `--count N` flag for generating multiple commit message suggestions with interactive picker for selection.

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: httpx (existing), no new deps for MVP
**Storage**: In-memory (suggestions), statistics DB (selection tracking)
**Testing**: pytest with mocking for AI providers
**Target Platform**: CLI (macOS, Linux, Windows)
**Project Type**: CLI enhancement
**Performance Goals**: <3 seconds for 3 suggestions (parallel generation)
**Constraints**: Terminal must support interactive input (fallback to JSON for CI/CD)
**Scale/Scope**: 1-10 suggestions per generation

## Constitution Check

### ✅ Library-First Architecture
- `generator/multi_generator.py` — MultiSuggestionGenerator library (standalone)
- `cli/picker.py` — InteractivePicker library (standalone, reusable)
- `cli/main.py` — CLI integration (uses libraries)
- All libraries independently testable

### ✅ CLI Interface Mandate
- `gitcommit-ai generate --count 3` — CLI command ✅
- Supports `--json` for programmatic access ✅
- Exit codes: 0=success, 1=failure ✅
- Text-based I/O ✅

### ✅ Test-First Development
- Tests written BEFORE implementation
- RED → GREEN → Refactor cycle
- 100% TDD compliance

### ✅ Integration Testing Priority
- Mock AI provider temperature variations
- Test interactive picker in non-TTY mode
- End-to-end CLI flow test

### ✅ Simplicity & YAGNI
- Reuse existing generator/providers
- No fancy UI libraries (plain terminal I/O)
- MVP: no arrow keys (just number selection)
- MVP: no regenerate (future)
- MVP: no syntax highlighting (future)

## Project Structure

### Documentation
```
.specify/specs/008-multiple-suggestions/
├── plan.md              # This file
├── tasks.md             # Task breakdown (next)
└── contracts/
    └── multi_generator.md  # MultiSuggestionGenerator interface
```

### Source Code
```
src/gitcommit_ai/generator/
├── multi_generator.py   # NEW: MultiSuggestionGenerator

src/gitcommit_ai/cli/
├── picker.py            # NEW: InteractivePicker (simple, numbered)
└── main.py              # UPDATED: add --count flag

tests/unit/
├── test_multi_generator.py  # NEW
└── test_picker.py            # NEW

tests/integration/
└── test_multi_suggestions_e2e.py  # NEW
```

## Phase 0: Research

**Key Findings:**
1. **Temperature parameter:**
   - OpenAI: supports `temperature` 0.0-2.0
   - Anthropic: supports `temperature` 0.0-1.0
   - Ollama: supports `temperature` 0.0-1.0
   - Use range: 0.3 (focused) to 0.7 (creative)

2. **Uniqueness validation:**
   - Compare normalized messages (lowercase, strip whitespace)
   - Retry if duplicates found (max 2 retries per suggestion)

3. **Interactive picker (MVP):**
   - No arrow keys (complexity)
   - Simple: print numbered list, input() for selection
   - Check `sys.stdout.isatty()` for TTY detection

## Phase 1: Design

### Data Models

**SuggestionSet:**
```python
@dataclass
class SuggestionSet:
    suggestions: list[CommitMessage]
    provider: str
    temperatures: list[float]
    generation_time_ms: int
```

### Contracts

**multi_generator.md:**
```python
class MultiSuggestionGenerator:
    async def generate_multiple(
        count: int,
        provider: str,
        api_key: str,
        temp_range: tuple[float, float] = (0.3, 0.7)
    ) -> SuggestionSet
```

**picker.md:**
```python
class InteractivePicker:
    def pick(suggestions: list[CommitMessage]) -> Optional[CommitMessage]
    # Returns None if cancelled, selected message otherwise
```

## Phase 2: Task Generation Plan

Tasks breakdown:
1. **Setup** (T001-T002): Multi-generator module, picker module
2. **Tests** (T003-T012): All tests FIRST (RED)
3. **Implementation** (T013-T020): Code to pass tests (GREEN)
4. **CLI Integration** (T021-T023): --count flag, picker integration
5. **Polish** (T024-T026): Docstrings, linting

## Progress Tracking

- [x] Constitution Check (passed)
- [x] Phase 0: Research
- [x] Phase 1: Design
- [x] Phase 2: Task plan
- [ ] Tasks.md creation
- [ ] Implementation

## Unresolved Questions

None. MVP scope simplified (no arrow keys, no regenerate).
