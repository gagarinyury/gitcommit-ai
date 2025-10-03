# Research: OpenRouter Integration & Provider Removal

**Phase**: 0 (Research)
**Date**: 2025-10-03
**Feature**: Add OpenRouter Provider, Remove Mistral/Cohere

## Research Questions Resolved

### 1. OpenRouter API Compatibility

**Decision**: Use OpenAI-compatible endpoint (`https://openrouter.ai/api/v1/chat/completions`)

**Rationale**:
- OpenRouter provides OpenAI-compatible API - can reuse OpenAI provider pattern
- Same request/response format as OpenAI (messages array, role/content structure)
- Minimal code duplication - inherit common logic from existing pattern

**Alternatives Considered**:
- Build completely custom provider → **Rejected**: Unnecessary duplication
- Use OpenRouter's native SDK → **Rejected**: Adds dependency, OpenAI compat is simpler

**Implementation Notes**:
- Endpoint: `https://openrouter.ai/api/v1/chat/completions`
- Auth: `Authorization: Bearer $OPENROUTER_API_KEY`
- Model format: `vendor/model-name` (e.g., `openai/gpt-4o`, `anthropic/claude-3-5-sonnet`)
- Extra headers: `HTTP-Referer`, `X-Title` for app identification (optional but recommended)

**References**:
- https://openrouter.ai/docs#quick-start
- https://openrouter.ai/docs#models

---

### 2. Backward Compatibility Strategy

**Decision**: Keep all direct providers (OpenAI, Anthropic, Gemini, DeepSeek, Ollama), deprecate only Mistral/Cohere

**Rationale**:
- Users with existing OpenAI/Anthropic keys should continue working
- OpenRouter is new *option*, not mandatory replacement
- Removes only 2 providers that are now accessible via OpenRouter
- No breaking changes for existing users

**Migration Path**:
- Mistral users → `gitcommit-ai generate --provider openrouter --model mistral/mistral-large`
- Cohere users → `gitcommit-ai generate --provider openrouter --model cohere/command`
- Add deprecation warning in v0.2.0, remove in v0.3.0

**Alternatives Considered**:
- Remove all providers except Ollama + OpenRouter → **Rejected**: Too aggressive, breaks users
- Auto-migrate Mistral/Cohere to OpenRouter → **Rejected**: Requires user consent, API key setup

---

### 3. Error Handling for OpenRouter Failures

**Decision**: No automatic fallback - show error with manual provider suggestions

**Rationale**:
- Explicit is better than implicit (Python Zen)
- Auto-fallback confuses users about which provider was used
- Clear error message guides user to alternatives

**Error Message Template**:
```
Error: OpenRouter API unavailable (status 503)

Try alternative providers:
  --provider openai        (if OPENAI_API_KEY configured)
  --provider anthropic     (if ANTHROPIC_API_KEY configured)
  --provider deepseek      (if DEEPSEEK_API_KEY configured)
  --provider ollama        (local, free - no API key needed)
```

**Alternatives Considered**:
- Silent fallback to OpenAI if key exists → **Rejected**: Per clarification session decision
- Retry with exponential backoff → **Rejected**: API failures are usually persistent

---

### 4. Model Validation & Discovery

**Decision**: Validate model name format (`vendor/model`), suggest popular models on error

**Rationale**:
- OpenRouter supports 100+ models - full list is dynamic and large
- Format validation catches typos early (`gpt-4o` → should be `openai/gpt-4o`)
- Suggest most common models for user convenience

**Implementation**:
- Regex validation: `^[a-z0-9-]+/[a-z0-9-\.]+$`
- Popular models list (hardcoded for UX):
  - `openai/gpt-4o`, `openai/gpt-4o-mini`
  - `anthropic/claude-3-5-sonnet`, `anthropic/claude-3-haiku`
  - `google/gemini-2.0-flash-exp`
  - `mistral/mistral-large`, `cohere/command-r-plus`

**Alternatives Considered**:
- Fetch live model list from OpenRouter API → **Rejected**: Adds latency, API dependency
- Require exact model string with no suggestions → **Rejected**: Poor UX

---

### 5. Testing Strategy

**Decision**: Follow existing provider test patterns (unit + e2e + integration)

**Test Coverage Required**:
1. **Unit Tests** (`test_openrouter.py`):
   - API request formatting (model name, headers, payload)
   - Response parsing (success, error cases)
   - Model name validation
   - Configuration validation (API key presence)

2. **E2E Tests** (`test_real_providers.py`):
   - Real API call with valid OpenRouter key (marked as skipped if no key)
   - Test multiple models (openai/gpt-4o-mini, anthropic/claude-3-haiku)
   - Verify generated commit message format

3. **Integration Tests** (`test_cli_e2e.py`):
   - CLI command with `--provider openrouter`
   - Error handling (invalid key, invalid model)
   - Provider list command shows OpenRouter

4. **Regression Tests**:
   - All 273 existing tests must pass
   - Verify Mistral/Cohere removal doesn't break registry
   - Verify other providers unaffected

**TDD Order**:
1. Write failing unit tests for OpenRouter
2. Write failing tests for Mistral/Cohere removal
3. Implement OpenRouter provider (make unit tests green)
4. Remove Mistral/Cohere (make removal tests green)
5. Update registry and docs (make integration tests green)

---

### 6. Prompt Template Reuse

**Decision**: Create `prompts/openrouter.md` based on existing provider templates

**Rationale**:
- Consistent prompt quality across providers
- Reuse proven commit message generation patterns
- Allow per-provider customization if needed

**Template Content**:
- Based on `prompts/deepseek.md` (most recent, well-tested)
- Include conventional commits format
- Emphasize conciseness and clarity
- No provider-specific instructions (OpenRouter handles routing)

---

### 7. Documentation Updates Required

**Files to Update**:
1. **README.md**:
   - Add OpenRouter to provider list
   - Update installation section (OpenRouter setup)
   - Mark Mistral/Cohere as "via OpenRouter"
   - Update `.env.example` with `OPENROUTER_API_KEY`

2. **CHANGELOG.md** (create if missing):
   - v0.2.0: Add OpenRouter provider
   - v0.2.0: Deprecate Mistral/Cohere (accessible via OpenRouter)

3. **Migration Guide** (add to README or docs/):
   - How to switch from Mistral/Cohere to OpenRouter
   - Model name mapping (e.g., `mistral-tiny` → `mistral/mistral-tiny`)

---

## Summary of Decisions

| Area | Decision | Impact |
|------|----------|--------|
| **API** | OpenAI-compatible endpoint | Reuse existing patterns, minimal code |
| **Compatibility** | Keep all providers except Mistral/Cohere | Zero breaking changes |
| **Fallback** | Manual only (show error + suggestions) | Clear, predictable behavior |
| **Validation** | Format check + popular model suggestions | Good UX, catches errors early |
| **Testing** | TDD with unit + e2e + integration | Maintains 273+ test coverage |
| **Docs** | Update README, add migration guide | Clear communication |

---

## Next Steps (Phase 1)

1. Design data model (none needed - stateless provider)
2. Create API contracts (`contracts/openrouter-api.yaml`)
3. Write failing contract tests
4. Generate quickstart.md with example usage
5. Update CLAUDE.md for agent context
