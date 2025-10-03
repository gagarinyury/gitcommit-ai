# Tasks: Ollama Support (Local AI Models)

**Input**: Design documents from `.specify/specs/002-ollama-support/`
**Prerequisites**: plan.md ✅, Feature 001 (AIProvider base) ✅

---

## Phase 3.1: Setup

- [ ] **T041** Update `pyproject.toml` dependencies (no new deps, ollama uses httpx)
- [ ] **T042** [P] Create test fixtures: `tests/fixtures/ollama_responses/` with sample streaming JSON
- [ ] **T043** [P] Add Ollama test helper: `tests/helpers/ollama_mock.py` (mock server factory)

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: All tests MUST be written and MUST FAIL before implementation begins**

### Layer 0: Configuration & Data Models
- [ ] **T044** [P] Test OllamaConfig in `tests/unit/test_ollama_config.py` (OLLAMA_HOST env var, defaults)
- [ ] **T045** [P] Test ModelInfo dataclass in `tests/unit/test_ollama_models.py` (parse ollama list output)

### Layer 1: Ollama Detection
- [ ] **T046** [P] Test `is_installed()` in `tests/unit/test_ollama_detection.py` (✅ installed, ❌ not found)
- [ ] **T047** [P] Test `list_models()` in `tests/unit/test_ollama_detection.py` (parse table, empty list)
- [ ] **T048** [P] Test `check_service_running()` in `tests/unit/test_ollama_detection.py` (connection check)

### Layer 2: Streaming Response Parser
- [ ] **T049** Test streaming parser in `tests/unit/test_ollama_parser.py` (accumulate lines, handle `done`)
- [ ] **T050** [P] Test malformed response handling in `tests/unit/test_ollama_parser.py` (invalid JSON, missing fields)

### Layer 3: Ollama Provider
- [ ] **T051** Test OllamaProvider init in `tests/unit/test_ollama_provider.py` (config validation)
- [ ] **T052** Test `generate_commit_message()` in `tests/unit/test_ollama_provider.py` (mock HTTP stream)
- [ ] **T053** [P] Test timeout handling in `tests/unit/test_ollama_provider.py` (60s timeout)
- [ ] **T054** [P] Test error scenarios in `tests/unit/test_ollama_provider.py` (404 model, connection refused)

### Layer 4: CLI Integration
- [ ] **T055** Test CLI arg parsing in `tests/unit/test_cli_ollama.py` (--provider ollama --model llama3.2)
- [ ] **T056** [P] Test provider factory in `tests/unit/test_cli_ollama.py` (creates OllamaProvider when --provider=ollama)

### Integration Tests
- [ ] **T057** Test Ollama integration in `tests/integration/test_ollama_integration.py` (mocked HTTP server)
- [ ] **T058** Test end-to-end CLI in `tests/integration/test_ollama_e2e.py` (temp repo + mock Ollama → commit)

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Layer 0: Configuration & Data Models
- [ ] **T059** [P] Implement OllamaConfig in `src/gitcommit_ai/providers/ollama.py` (dataclass with defaults)
- [ ] **T060** [P] Implement ModelInfo in `src/gitcommit_ai/providers/ollama.py` (parse ollama list row)
- [ ] **T061** Update Config in `src/gitcommit_ai/core/config.py` (add ollama_host, ollama_default_model)

### Layer 1: Ollama Detection
- [ ] **T062** Implement detection utilities in `src/gitcommit_ai/providers/ollama.py`:
  - `is_installed() -> bool` (subprocess: ollama --version)
  - `list_models() -> list[ModelInfo]` (subprocess: ollama list, parse table)
  - `check_service_running(host: str) -> bool` (httpx: GET /api/tags)

### Layer 2: Streaming Response Parser
- [ ] **T063** Implement `OllamaStreamParser` in `src/gitcommit_ai/providers/ollama.py`:
  - `parse_line(line: str) -> dict` (json.loads with error handling)
  - `accumulate_response(data: dict)` (append `response` field)
  - `is_done(data: dict) -> bool` (check `done` field)

### Layer 3: Ollama Provider
- [ ] **T064** Implement OllamaProvider in `src/gitcommit_ai/providers/ollama.py`:
  - `__init__(config: OllamaConfig)`
  - `validate_config() -> list[str]` (check Ollama installed, service running)
- [ ] **T065** Implement `generate_commit_message()` in OllamaProvider:
  - Build prompt from GitDiff
  - POST to /api/generate with streaming
  - Parse streamed response
  - Convert to CommitMessage
- [ ] **T066** [P] Implement error handling in OllamaProvider (timeouts, connection errors, 404 model)

### Layer 4: CLI Integration
- [ ] **T067** Update CLI in `src/gitcommit_ai/cli/main.py`:
  - Add "ollama" to --provider choices
  - Add --model flag (optional, provider-specific)
  - Update provider factory to create OllamaProvider
- [ ] **T068** [P] Add progress indicator in CLI (print "Generating..." for Ollama)

---

## Phase 3.4: Polish & Documentation

- [ ] **T069** [P] Add docstrings to OllamaProvider (Google style)
- [ ] **T070** [P] Update README.md (add Ollama setup instructions)
- [ ] **T071** Create Ollama quickstart: `.specify/specs/002-ollama-support/quickstart.md`
- [ ] **T072** [P] Add edge case tests: custom OLLAMA_HOST, slow models, partial responses
- [ ] **T073** Manual smoke test: install Ollama, run `ollama pull llama3.2`, test CLI
- [ ] **T074** [P] Update help text (`gitcommit-ai --help` shows Ollama usage)

---

## Dependency Graph

```
Setup: T041 → T042,T043 (parallel)
           ↓
Tests Layer 0: T044,T045 (parallel)
           ↓
Tests Layer 1: T046,T047,T048 (parallel)
           ↓
Tests Layer 2: T049,T050 (T049 → T050)
           ↓
Tests Layer 3: T051 → T052 → T053,T054 (parallel)
           ↓
Tests Layer 4: T055,T056 (parallel)
           ↓
Integration: T057,T058 (parallel)
           ↓
Impl Layer 0: T059,T060 (parallel) → T061
           ↓
Impl Layer 1: T062 (single file, sequential methods)
           ↓
Impl Layer 2: T063 (single class)
           ↓
Impl Layer 3: T064 → T065 → T066
           ↓
Impl Layer 4: T067 → T068
           ↓
Polish: T069,T070,T071,T072,T074 (parallel) → T073
```

---

## Parallel Execution Examples

**After T043 (setup complete):**
```bash
# Parallel test writing (different test files)
Agent1: T044 (test_ollama_config.py)
Agent2: T045 (test_ollama_models.py)
```

**After T048 (detection tests done):**
```bash
# Parallel test writing
Agent1: T049 (test_ollama_parser.py - streaming)
Agent2: T050 (test_ollama_parser.py - errors)
```

**After T058 (all tests written & failing):**
```bash
# Parallel implementation (data models)
Agent1: T059 (OllamaConfig)
Agent2: T060 (ModelInfo)
```

**Polish phase:**
```bash
# Parallel documentation
Agent1: T069 (docstrings)
Agent2: T070 (README updates)
Agent3: T071 (quickstart guide)
Agent4: T072 (edge case tests)
Agent5: T074 (help text)
```

---

## Validation Checklist

- [x] All requirements from spec (FR-021 to FR-039) have test coverage
- [x] TDD sequence enforced (tests T044-T058 before impl T059-T068)
- [x] Parallel tasks marked with [P]
- [x] File paths specified in task descriptions
- [x] Integration tests cover mocked Ollama server
- [ ] Constitution compliance verified (pending implementation review)
- [x] Dependencies on Feature 001 identified (AIProvider base, GitDiff, CommitMessage)

---

## Exit Codes

Ollama-specific exit codes (extend existing codes from Feature 001):
- **4**: Ollama not installed
- **5**: Ollama model not found
- **2**: Ollama connection error (existing code, reused)

---

## Notes

- **No new dependencies**: Ollama provider uses httpx (already in deps)
- **Offline-first**: All tests use mocked responses, no network required
- **Streaming**: Tests verify line-by-line JSON parsing, not blocking response
- **Model agnostic**: Code supports any Ollama model, tests use llama3.2 as example
- **Manual test (T073)** requires:
  1. Install Ollama: https://ollama.ai
  2. Pull model: `ollama pull llama3.2`
  3. Run: `gitcommit-ai generate --provider ollama`
