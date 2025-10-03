# Tasks: External Prompt Templates System

**Status:** Planning
**Approach:** TDD (Test-Driven Development)

## Phase 1: Test Infrastructure (RED) 🔴

### T201: Write PromptLoader Tests
- [ ] Create `tests/unit/test_prompt_loader.py`
- [ ] Test: `test_loads_default_template_from_package`
- [ ] Test: `test_loads_user_override_when_exists`
- [ ] Test: `test_renders_template_with_variables`
- [ ] Test: `test_caches_loaded_templates`
- [ ] Test: `test_raises_error_on_missing_template`
- [ ] Test: `test_handles_malformed_template`
- [ ] **Expected:** All tests FAIL (PromptLoader doesn't exist yet)

## Phase 2: Implementation (GREEN) 🟢

### T202: Create Prompts Module Structure
- [ ] Create `src/gitcommit_ai/prompts/__init__.py`
- [ ] Create `src/gitcommit_ai/prompts/loader.py`
- [ ] Create `src/gitcommit_ai/prompts/templates/` directory

### T203: Implement PromptLoader Class
- [ ] Implement `__init__()` with default/user paths
- [ ] Implement `load(provider: str) -> str` method
- [ ] Implement `render(template: str, **vars) -> str` method
- [ ] Implement template caching
- [ ] Implement user override logic (prefers ~/.gitcommit-ai/)
- [ ] **Expected:** Tests from T201 now PASS ✅

### T204: Create Default Templates
- [ ] Create `templates/deepseek.txt` (extract from current code)
- [ ] Create `templates/ollama.txt` (extract from current code)
- [ ] Create `templates/openai.txt` (extract from current code)
- [ ] Create `templates/anthropic.txt` (extract from current code)
- [ ] Create `templates/gemini.txt` (extract from current code)
- [ ] Create `templates/mistral.txt` (extract from current code)
- [ ] Create `templates/cohere.txt` (extract from current code)

## Phase 3: Migration (TDD for Each Provider) 🔄

### T205: Migrate DeepSeek (Pilot)
- [ ] **RED:** Write test `test_deepseek_uses_external_prompt`
- [ ] **GREEN:** Update `DeepSeekProvider._build_prompt()` to use PromptLoader
- [ ] **GREEN:** Verify `test_deepseek_uses_external_prompt` passes
- [ ] Verify all existing DeepSeek tests still pass
- [ ] Manual test: `gitcommit-ai generate --provider deepseek`

### T206: Migrate Ollama
- [ ] **RED:** Write test `test_ollama_uses_external_prompt`
- [ ] **GREEN:** Update `OllamaProvider._build_prompt()` to use PromptLoader
- [ ] Verify all existing Ollama tests still pass

### T207: Migrate OpenAI
- [ ] **RED:** Write test `test_openai_uses_external_prompt`
- [ ] **GREEN:** Update `OpenAIProvider._build_prompt()` to use PromptLoader
- [ ] Verify all existing OpenAI tests still pass

### T208: Migrate Anthropic
- [ ] **RED:** Write test `test_anthropic_uses_external_prompt`
- [ ] **GREEN:** Update `AnthropicProvider._build_prompt()` to use PromptLoader
- [ ] Verify all existing Anthropic tests still pass

### T209: Migrate Gemini
- [ ] **RED:** Write test `test_gemini_uses_external_prompt`
- [ ] **GREEN:** Update `GeminiProvider._build_prompt()` to use PromptLoader
- [ ] Verify all existing Gemini tests still pass

### T210: Migrate Mistral
- [ ] **RED:** Write test `test_mistral_uses_external_prompt`
- [ ] **GREEN:** Update `MistralProvider._build_prompt()` to use PromptLoader
- [ ] Verify all existing Mistral tests still pass

### T211: Migrate Cohere
- [ ] **RED:** Write test `test_cohere_uses_external_prompt`
- [ ] **GREEN:** Update `CohereProvider._build_prompt()` to use PromptLoader
- [ ] Verify all existing Cohere tests still pass

## Phase 4: User Overrides (TDD) 🎨

### T212: Test User Override System
- [ ] **RED:** Test `test_user_can_override_deepseek_prompt`
- [ ] **GREEN:** Create `~/.gitcommit-ai/prompts/deepseek.txt` in test
- [ ] Verify override is actually used
- [ ] **RED:** Test `test_user_override_with_custom_variables`
- [ ] **GREEN:** Implement custom variable support

## Phase 5: Documentation 📚

### T213: Create Prompt Documentation
- [ ] Create `src/gitcommit_ai/prompts/templates/README.md`
- [ ] Document available variables
- [ ] Document override mechanism
- [ ] Add example custom prompts

### T214: Update Main README
- [ ] Add "Customizing Prompts" section
- [ ] Show example of overriding a prompt
- [ ] Link to templates README

### T215: Add Examples
- [ ] Create example: "Shorter commit messages"
- [ ] Create example: "Include ticket numbers"
- [ ] Create example: "Team-specific format"

## Phase 6: Final Testing & Polish ✨

### T216: Integration Testing
- [ ] Test all 7 providers with default prompts
- [ ] Test all 7 providers with user overrides
- [ ] Test prompt caching works
- [ ] Test error handling (missing template)

### T217: Performance Testing
- [ ] Measure prompt loading time (should be <1ms cached)
- [ ] Verify no regression in generation speed
- [ ] Profile template rendering

### T218: Code Cleanup
- [ ] Remove old hardcoded prompts from providers
- [ ] Add type hints to PromptLoader
- [ ] Run linter (ruff)
- [ ] Run type checker (mypy)

## Success Criteria ✅

- [ ] All 260+ existing tests pass
- [ ] All new PromptLoader tests pass
- [ ] Each provider has external template
- [ ] User override system works
- [ ] Documentation complete
- [ ] No performance regression

## Dependencies

- Phase 2 depends on Phase 1 (need tests first)
- Phase 3 depends on Phase 2 (need PromptLoader)
- Phase 4 depends on Phase 3 (need migrations done)
- Phase 5 can happen in parallel with Phase 4
- Phase 6 requires all previous phases

## Estimation

- Phase 1: 30 min (write tests)
- Phase 2: 45 min (implement PromptLoader)
- Phase 3: 1.5 hours (migrate 7 providers)
- Phase 4: 30 min (user overrides)
- Phase 5: 45 min (documentation)
- Phase 6: 30 min (testing & polish)

**Total: ~4 hours**
