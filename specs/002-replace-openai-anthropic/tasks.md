# Tasks: Add OpenRouter Provider, Remove Mistral/Cohere

**Input**: Design documents from `/specs/002-replace-openai-anthropic/`
**Prerequisites**: plan.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

## Execution Summary

**Feature**: Add OpenRouter as unified provider for 100+ AI models, remove Mistral/Cohere direct providers

**Key Decisions** (from research.md):
- OpenRouter uses OpenAI-compatible API (reuse existing patterns)
- Keep all providers except Mistral/Cohere (zero breaking changes)
- No automatic fallback (show error + manual provider suggestions)
- TDD mandatory: All tests before implementation

**Scope**:
- **Add**: OpenRouter provider, prompt template, unit/integration tests
- **Remove**: Mistral provider, Cohere provider, related tests
- **Update**: Provider registry, CLI help, config, documentation
- **Maintain**: 273 existing tests must pass (backward compatibility)

**Estimated Effort**: ~35 tasks, 4-6 hours with TDD discipline

---

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Paths relative to repository root

---

## Phase 3.1: Setup & Environment

- [ ] **T001** Verify branch `002-replace-openai-anthropic` is active and clean
  ```bash
  git checkout 002-replace-openai-anthropic
  git status  # Should be clean
  ```

- [ ] **T002** Run existing test suite to establish baseline (273 tests should pass)
  ```bash
  pytest tests/ -v
  # Expected: 273 passed, 2 skipped (Mistral, Cohere)
  ```

- [ ] **T003** Verify constitution compliance checklist complete
  - Review `specs/002-replace-openai-anthropic/plan.md` Constitution Check section
  - Confirm all gates show ✅ PASS

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL**: These tests MUST be written and MUST FAIL before ANY implementation.
Run `pytest tests/unit/test_openrouter.py -v` after each test task - it MUST show RED (failures).

### Contract Tests (from contracts/openrouter-api.yaml)

- [ ] **T004** [P] Write failing contract test for OpenRouter API request format
  - **File**: `tests/unit/test_openrouter.py`
  - **Test**: `test_openrouter_request_format()`
  - **Assert**: Request has correct structure (model, messages, temperature, max_tokens)
  - **Assert**: Model format matches `vendor/model-name` pattern
  - **Assert**: Authorization header includes Bearer token
  - **Expected**: ❌ FAIL (OpenRouterProvider doesn't exist yet)

- [ ] **T005** [P] Write failing contract test for OpenRouter API response parsing
  - **File**: `tests/unit/test_openrouter.py`
  - **Test**: `test_openrouter_response_parsing()`
  - **Assert**: Extracts `choices[0].message.content` correctly
  - **Assert**: Parses into CommitMessage (type, scope, description, body)
  - **Expected**: ❌ FAIL (parsing logic doesn't exist yet)

- [ ] **T006** [P] Write failing contract test for OpenRouter error responses
  - **File**: `tests/unit/test_openrouter.py`
  - **Tests**:
    - `test_openrouter_invalid_api_key()` (401)
    - `test_openrouter_rate_limit()` (429)
    - `test_openrouter_service_unavailable()` (503)
  - **Assert**: Error messages include fallback provider suggestions
  - **Expected**: ❌ FAIL (error handling doesn't exist yet)

### Unit Tests (from data-model.md)

- [ ] **T007** [P] Write failing test for OpenRouterProvider initialization
  - **File**: `tests/unit/test_openrouter.py`
  - **Test**: `test_openrouter_provider_init()`
  - **Assert**: API key loaded from OPENROUTER_API_KEY env var
  - **Assert**: Model format validated on init
  - **Assert**: Base URL defaults to https://openrouter.ai/api/v1
  - **Expected**: ❌ FAIL (OpenRouterProvider class doesn't exist)

- [ ] **T008** [P] Write failing test for model name validation
  - **File**: `tests/unit/test_openrouter.py`
  - **Test**: `test_model_name_validation()`
  - **Assert**: `openai/gpt-4o` is valid ✅
  - **Assert**: `gpt-4o` is invalid (missing vendor) ❌
  - **Assert**: `OpenAI/GPT-4O` is invalid (wrong case) ❌
  - **Assert**: Regex pattern: `^[a-z0-9-]+/[a-z0-9-\.]+$`
  - **Expected**: ❌ FAIL (validation logic doesn't exist)

- [ ] **T009** [P] Write failing test for OpenRouterProvider.validate_config()
  - **File**: `tests/unit/test_openrouter.py`
  - **Test**: `test_validate_config()`
  - **Assert**: Returns error if OPENROUTER_API_KEY missing
  - **Assert**: Returns error if model format invalid
  - **Assert**: Returns empty list if config valid
  - **Expected**: ❌ FAIL (validate_config() doesn't exist)

### Integration Tests (from quickstart.md scenarios)

- [ ] **T010** [P] Write failing E2E test for OpenRouter commit generation
  - **File**: `tests/e2e/test_real_providers.py`
  - **Class**: `TestOpenRouterE2E`
  - **Test**: `test_generate_real_commit_message()`
  - **Setup**: Skip if `OPENROUTER_API_KEY` not set
  - **Action**: Generate commit for sample diff using `openai/gpt-4o-mini`
  - **Assert**: Returns valid CommitMessage in conventional format
  - **Expected**: ❌ FAIL (OpenRouter provider not in registry)

- [ ] **T011** [P] Write failing E2E test for multiple model support
  - **File**: `tests/e2e/test_real_providers.py`
  - **Tests**:
    - `test_openrouter_claude()` - `anthropic/claude-3-haiku`
    - `test_openrouter_mistral()` - `mistral/mistral-tiny`
  - **Assert**: Different models return valid commit messages
  - **Expected**: ❌ FAIL (OpenRouter not implemented)

- [ ] **T012** [P] Write failing integration test for CLI error messages
  - **File**: `tests/integration/test_cli_e2e.py`
  - **Test**: `test_openrouter_error_fallback_suggestions()`
  - **Action**: Mock OpenRouter 503 error
  - **Assert**: Error message suggests `--provider openai`, `--provider ollama`, etc.
  - **Expected**: ❌ FAIL (error handling not implemented)

- [ ] **T013** [P] Write failing integration test for `providers` command
  - **File**: `tests/integration/test_cli_e2e.py`
  - **Test**: `test_cli_providers_list_includes_openrouter()`
  - **Action**: Run `gitcommit-ai providers`
  - **Assert**: Output includes "openrouter" with status and popular models
  - **Expected**: ❌ FAIL (OpenRouter not in registry)

### Regression Tests for Provider Removal

- [ ] **T014** [P] Write failing test for Mistral provider removal
  - **File**: `tests/unit/test_registry.py`
  - **Test**: `test_mistral_not_in_registry()`
  - **Assert**: `get_provider_names()` does NOT include "mistral"
  - **Expected**: ❌ FAIL (Mistral still in registry)

- [ ] **T015** [P] Write failing test for Cohere provider removal
  - **File**: `tests/unit/test_registry.py`
  - **Test**: `test_cohere_not_in_registry()`
  - **Assert**: `get_provider_names()` does NOT include "cohere"
  - **Expected**: ❌ FAIL (Cohere still in registry)

---

## Phase 3.3: Core Implementation (ONLY after tests are RED)

**GATE CHECK**: Before proceeding, verify ALL tests in Phase 3.2 are written and FAILING.
```bash
pytest tests/unit/test_openrouter.py -v  # Should show RED failures
pytest tests/e2e/test_real_providers.py::TestOpenRouterE2E -v  # Should fail
```

### OpenRouter Provider Implementation

- [ ] **T016** Create OpenRouterProvider class in `src/gitcommit_ai/providers/openrouter.py`
  - **Inherit from**: `AIProvider` (from `base.py`)
  - **Attributes**:
    ```python
    api_key: str
    model: str
    base_url: str = "https://openrouter.ai/api/v1"
    timeout: int = 60
    ```
  - **Methods**: `__init__`, `validate_config`, `generate_commit_message` (async)
  - **Expected**: T007 (init test) turns GREEN ✅

- [ ] **T017** Implement model name validation logic in OpenRouterProvider
  - **File**: `src/gitcommit_ai/providers/openrouter.py`
  - **Method**: `_validate_model_format(model: str) -> bool`
  - **Regex**: `^[a-z0-9-]+/[a-z0-9-\.]+$`
  - **Call from**: `__init__()` and `validate_config()`
  - **Expected**: T008 (validation test) turns GREEN ✅

- [ ] **T018** Implement OpenRouterProvider.validate_config()
  - **File**: `src/gitcommit_ai/providers/openrouter.py`
  - **Check**: API key exists (non-empty)
  - **Check**: Model format valid (call `_validate_model_format`)
  - **Return**: List of error messages (empty if valid)
  - **Expected**: T009 (config test) turns GREEN ✅

- [ ] **T019** Implement API request formatting for OpenRouter
  - **File**: `src/gitcommit_ai/providers/openrouter.py`
  - **Method**: `_build_request_payload(prompt: str) -> dict`
  - **Structure** (OpenAI-compatible):
    ```python
    {
        "model": self.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    ```
  - **Headers**: `Authorization: Bearer {api_key}`
  - **Expected**: T004 (request format test) turns GREEN ✅

- [ ] **T020** Implement response parsing for OpenRouter
  - **File**: `src/gitcommit_ai/providers/openrouter.py`
  - **Method**: `_parse_response(response_json: dict) -> CommitMessage`
  - **Extract**: `response_json["choices"][0]["message"]["content"]`
  - **Parse**: Conventional commit format (reuse existing parser from `generator/message.py`)
  - **Expected**: T005 (response parsing test) turns GREEN ✅

- [ ] **T021** Implement error handling for OpenRouter
  - **File**: `src/gitcommit_ai/providers/openrouter.py`
  - **Method**: `generate_commit_message(diff: GitDiff) -> CommitMessage`
  - **Handle**: 401 (invalid key) → "Get key at https://openrouter.ai/keys"
  - **Handle**: 429 (rate limit) → "Rate limit exceeded"
  - **Handle**: 503 (unavailable) → "Try --provider openai, --provider ollama..."
  - **Expected**: T006 (error handling test) turns GREEN ✅

- [ ] **T022** Create OpenRouter prompt template in `src/gitcommit_ai/prompts/openrouter.md`
  - **Base on**: `prompts/deepseek.md` (most recent, well-tested)
  - **Content**: Conventional commits format, conciseness, clarity
  - **No provider-specific instructions** (OpenRouter handles routing)
  - **Load in**: `OpenRouterProvider._build_request_payload()`

### Provider Registry Updates

- [ ] **T023** Add OpenRouter to provider registry
  - **File**: `src/gitcommit_ai/providers/registry.py`
  - **Add to**: `PROVIDERS` dict
  - **Entry**:
    ```python
    "openrouter": {
        "name": "openrouter",
        "display_name": "OpenRouter",
        "models": [
            "openai/gpt-4o", "anthropic/claude-3-5-sonnet",
            "google/gemini-2.0-flash-exp", "mistral/mistral-large"
        ],
        "requires_api_key": True,
        "api_key_env": "OPENROUTER_API_KEY",
        "website": "https://openrouter.ai"
    }
    ```
  - **Expected**: T013 (providers command test) turns GREEN ✅

- [ ] **T024** Remove Mistral from provider registry
  - **File**: `src/gitcommit_ai/providers/registry.py`
  - **Remove**: `"mistral"` entry from `PROVIDERS` dict
  - **Expected**: T014 (Mistral removal test) turns GREEN ✅

- [ ] **T025** Remove Cohere from provider registry
  - **File**: `src/gitcommit_ai/providers/registry.py`
  - **Remove**: `"cohere"` entry from `PROVIDERS` dict
  - **Expected**: T015 (Cohere removal test) turns GREEN ✅

### Configuration Updates

- [ ] **T026** Add OPENROUTER_API_KEY to config.py
  - **File**: `src/gitcommit_ai/core/config.py`
  - **Add**: `openrouter_api_key = os.getenv("OPENROUTER_API_KEY")`
  - **No default provider change** (Ollama remains default)

### CLI Updates

- [ ] **T027** Update CLI help text for OpenRouter
  - **File**: `src/gitcommit_ai/cli/main.py`
  - **Update**: `--provider` help string
  - **Add**: "openrouter (100+ models via unified API)"
  - **Remove**: "mistral" and "cohere" from examples

---

## Phase 3.4: Provider Removal (after OpenRouter tests GREEN)

**GATE CHECK**: Verify OpenRouter tests (T004-T013) are all GREEN before removing old providers.

- [ ] **T028** [P] Delete Mistral provider implementation
  - **Delete file**: `src/gitcommit_ai/providers/mistral.py`
  - **Expected**: No import errors (already removed from registry in T024)

- [ ] **T029** [P] Delete Cohere provider implementation
  - **Delete file**: `src/gitcommit_ai/providers/cohere.py`
  - **Expected**: No import errors (already removed from registry in T025)

- [ ] **T030** [P] Delete Mistral tests
  - **Delete file**: `tests/unit/test_mistral.py`
  - **Expected**: Test count decreases

- [ ] **T031** [P] Delete Cohere tests
  - **Delete file**: `tests/unit/test_cohere.py`
  - **Expected**: Test count decreases

- [ ] **T032** Update provider registry imports
  - **File**: `src/gitcommit_ai/providers/__init__.py`
  - **Remove**: `from .mistral import MistralProvider`
  - **Remove**: `from .cohere import CohereProvider`
  - **Add**: `from .openrouter import OpenRouterProvider`

---

## Phase 3.5: Documentation & Migration

- [ ] **T033** Update README.md with OpenRouter section
  - **File**: `README.md`
  - **Add**: OpenRouter setup instructions (after Ollama section)
  - **Update**: Provider comparison table
  - **Mark**: Mistral/Cohere as "via OpenRouter"
  - **Example**:
    ```markdown
    **Option 5: OpenRouter** (100+ models, one API key)
    ```bash
    export OPENROUTER_API_KEY="sk-or-v1-..."
    gitcommit-ai generate --provider openrouter --model openai/gpt-4o
    ```

- [ ] **T034** Update .env.example with OpenRouter
  - **File**: `.env.example`
  - **Add**:
    ```bash
    # OpenRouter (recommended for access to 100+ models)
    OPENROUTER_API_KEY=sk-or-v1-...
    ```
  - **Comment**: Mistral/Cohere accessible via OpenRouter

- [ ] **T035** Create migration guide section in README
  - **File**: `README.md`
  - **Section**: "## Migration from Mistral/Cohere"
  - **Content**:
    - Before/after examples
    - Model name mapping (e.g., `mistral-tiny` → `mistral/mistral-tiny`)
    - Link to OpenRouter model list

---

## Phase 3.6: Validation & Polish

- [ ] **T036** Run full test suite (all 273+ existing tests must pass)
  ```bash
  pytest tests/ -v --tb=short
  # Expected: 273+ passed (new OpenRouter tests added, Mistral/Cohere removed)
  ```

- [ ] **T037** Manual smoke test - OpenRouter with multiple models
  ```bash
  export OPENROUTER_API_KEY="your-key"
  git add .
  gitcommit-ai generate --provider openrouter --model openai/gpt-4o-mini
  gitcommit-ai generate --provider openrouter --model anthropic/claude-3-haiku
  # Expected: Valid commit messages generated
  ```

- [ ] **T038** Manual smoke test - fallback providers still work
  ```bash
  gitcommit-ai generate --provider openai
  gitcommit-ai generate --provider anthropic
  gitcommit-ai generate --provider ollama
  # Expected: All work as before (backward compatibility)
  ```

- [ ] **T039** Manual smoke test - error handling
  ```bash
  export OPENROUTER_API_KEY="invalid"
  gitcommit-ai generate --provider openrouter --model openai/gpt-4o-mini
  # Expected: Clear error + link to https://openrouter.ai/keys

  gitcommit-ai generate --provider openrouter --model invalid-format
  # Expected: Model format error + popular model suggestions
  ```

- [ ] **T040** Manual smoke test - provider list command
  ```bash
  gitcommit-ai providers
  # Expected: OpenRouter listed, Mistral/Cohere NOT listed
  ```

- [ ] **T041** Run linter and type checker
  ```bash
  ruff check src/ tests/
  mypy src/
  # Expected: No errors
  ```

- [ ] **T042** Update CHANGELOG.md
  - **File**: `CHANGELOG.md` (create if missing)
  - **Add**:
    ```markdown
    ## [0.2.0] - 2025-10-03
    ### Added
    - OpenRouter provider for unified access to 100+ AI models
    - Support for Mistral and Cohere models via OpenRouter

    ### Removed
    - Direct Mistral provider (use OpenRouter instead)
    - Direct Cohere provider (use OpenRouter instead)

    ### Migration
    - Mistral users: Use `--provider openrouter --model mistral/mistral-*`
    - Cohere users: Use `--provider openrouter --model cohere/command*`
    ```

---

## Dependencies

**Critical Paths** (must be sequential):
1. Setup (T001-T003) → Tests (T004-T015) → Implementation (T016-T027)
2. OpenRouter tests GREEN (T004-T013) → Removal (T028-T032)
3. Implementation complete → Documentation (T033-T035)
4. Everything complete → Validation (T036-T042)

**Parallel Opportunities**:
- T004-T006 (contract tests) can run in parallel [P]
- T007-T009 (unit tests) can run in parallel [P]
- T010-T013 (integration tests) can run in parallel [P]
- T014-T015 (removal tests) can run in parallel [P]
- T028-T031 (file deletions) can run in parallel [P]

---

## Parallel Execution Example

**Launch all contract tests together** (Phase 3.2):
```bash
# Test T004-T006 in parallel
pytest tests/unit/test_openrouter.py::test_openrouter_request_format -v &
pytest tests/unit/test_openrouter.py::test_openrouter_response_parsing -v &
pytest tests/unit/test_openrouter.py::test_openrouter_invalid_api_key -v &
wait
# All should fail (RED) - good!
```

**Launch all integration tests together** (Phase 3.2):
```bash
# Test T010-T013 in parallel
pytest tests/e2e/test_real_providers.py::TestOpenRouterE2E -v &
pytest tests/integration/test_cli_e2e.py::test_openrouter_error_fallback_suggestions -v &
pytest tests/integration/test_cli_e2e.py::test_cli_providers_list_includes_openrouter -v &
wait
```

**Delete provider files in parallel** (Phase 3.4):
```bash
# Execute T028-T031 together
rm src/gitcommit_ai/providers/mistral.py &
rm src/gitcommit_ai/providers/cohere.py &
rm tests/unit/test_mistral.py &
rm tests/unit/test_cohere.py &
wait
```

---

## Validation Checklist

**Before marking complete**, verify:
- [x] All contracts (openrouter-api.yaml) have corresponding tests (T004-T006)
- [x] All entities from data-model.md have tasks (OpenRouterProvider in T016-T021)
- [x] All tests come before implementation (Phase 3.2 before 3.3)
- [x] Parallel tasks [P] are truly independent (different files)
- [x] Each task specifies exact file path
- [x] No [P] task modifies same file as another [P] task
- [x] TDD enforced: Tests must fail before implementation
- [x] 273 existing tests maintained (backward compatibility)
- [x] Constitution compliance verified (plan.md Constitution Check)

---

## Notes

- **TDD is mandatory**: Write tests, see them fail, implement, see them pass
- **Commit after each GREEN**: Small, atomic commits (e.g., "test: add OpenRouter request format test", "feat: implement OpenRouter provider")
- **No shortcuts**: Don't skip tests or implement before tests are written
- **Backward compatibility**: All existing providers (OpenAI, Anthropic, Gemini, DeepSeek, Ollama) must remain functional
- **Error messages**: Must be helpful (include links, suggestions, alternatives)

---

## Estimated Timeline

**Total**: 42 tasks, ~4-6 hours with TDD discipline

- **Phase 3.1** (Setup): 15 min
- **Phase 3.2** (Tests): 2 hours (15 test tasks, ~8 min each)
- **Phase 3.3** (Implementation): 1.5 hours (12 tasks, ~7 min each)
- **Phase 3.4** (Removal): 15 min (5 tasks, parallel)
- **Phase 3.5** (Documentation): 30 min (3 tasks)
- **Phase 3.6** (Validation): 30 min (7 tasks)

**Ready for execution!** 🚀
