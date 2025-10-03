# Tasks: Additional AI Providers (Gemini, Mistral, Cohere)

**Prerequisites**: plan.md ✅, Feature 001 (AIProvider base) ✅

## Phase 3.2: Tests (TDD)

### Gemini Provider
- [ ] **T085** [P] Test GeminiProvider init in `tests/unit/test_gemini.py`
- [ ] **T086** [P] Test generate_commit_message() with mocked HTTP
- [ ] **T087** [P] Test Gemini API error handling (401, 429, 500)
- [ ] **T088** [P] Test response parsing (Gemini format → CommitMessage)

### Mistral Provider
- [ ] **T089** [P] Test MistralProvider init in `tests/unit/test_mistral.py`
- [ ] **T090** [P] Test generate with mocked HTTP (OpenAI-compatible)
- [ ] **T091** [P] Test Mistral-specific errors
- [ ] **T092** [P] Test model selection (mistral-tiny, small, medium)

### Cohere Provider
- [ ] **T093** [P] Test CohereProvider init in `tests/unit/test_cohere.py`
- [ ] **T094** [P] Test generate with streaming response
- [ ] **T095** [P] Test Cohere error handling
- [ ] **T096** [P] Test Cohere format parsing

### Provider Registry
- [ ] **T097** Test ProviderRegistry.list_providers() in `tests/unit/test_registry.py`
- [ ] **T098** [P] Test provider status detection (configured vs missing key)
- [ ] **T099** [P] Test ProviderRegistry.get_provider() factory

### CLI Integration
- [ ] **T100** Test `providers list` command in `tests/unit/test_cli_providers.py`
- [ ] **T101** [P] Test CLI with --provider gemini/mistral/cohere

## Phase 3.3: Implementation

### Gemini Provider
- [ ] **T102** Implement GeminiProvider in `src/gitcommit_ai/providers/gemini.py`
- [ ] **T103** Update Config with GEMINI_API_KEY in `src/gitcommit_ai/core/config.py`

### Mistral Provider
- [ ] **T104** Implement MistralProvider in `src/gitcommit_ai/providers/mistral.py`
- [ ] **T105** Update Config with MISTRAL_API_KEY

### Cohere Provider
- [ ] **T106** Implement CohereProvider in `src/gitcommit_ai/providers/cohere.py`
- [ ] **T107** Update Config with COHERE_API_KEY

### Provider Registry
- [ ] **T108** Implement ProviderRegistry in `src/gitcommit_ai/providers/registry.py`

### CLI Integration
- [ ] **T109** Add `providers` subcommand to `src/gitcommit_ai/cli/main.py`
- [ ] **T110** Update `--provider` choices to include gemini/mistral/cohere

## Phase 3.4: Polish

- [ ] **T111** [P] Update README with all provider setup instructions
- [ ] **T112** [P] Create provider comparison table in docs
- [ ] **T113** Manual test: try all 6 providers (OpenAI, Anthropic, Gemini, Mistral, Cohere, Ollama)

**Total**: 29 tasks (T085-T113)

## Dependency Graph

```
Tests: T085-T088 (Gemini) → T089-T092 (Mistral) → T093-T096 (Cohere) → T097-T099 (Registry) → T100-T101 (CLI)
             ↓
Impl: T102-T103 → T104-T105 → T106-T107 → T108 → T109-T110
             ↓
Polish: T111, T112 (parallel) → T113
```

## Notes
- All 3 providers use httpx (no new deps)
- Gemini/Mistral/Cohere follow same pattern as OpenAI/Anthropic
- ProviderRegistry enables future extensibility (plugins?)
