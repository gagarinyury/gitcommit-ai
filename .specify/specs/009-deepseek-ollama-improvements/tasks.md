# Tasks: DeepSeek Provider + Ollama Quality Improvements

**Prerequisites**: plan.md ✅, Feature 001 (AIProvider base) ✅

## Phase 3.2: Tests (TDD)

### DeepSeek Provider Tests
- [ ] **T114** Test DeepSeekProvider init in `tests/unit/test_deepseek.py`
- [ ] **T115** Test generate_commit_message() with mocked HTTP (OpenAI-compatible response)
- [ ] **T116** Test DeepSeek API error handling (401 Unauthorized, 429 Rate Limit, 500 Server Error)
- [ ] **T117** Test response parsing (OpenAI format → CommitMessage)
- [ ] **T118** Test model selection (deepseek-chat, deepseek-coder)
- [ ] **T119** Test missing API key raises ValueError

### Ollama Prompt Improvement Tests
- [ ] **T120** Test improved prompt contains "expert software engineer" role
- [ ] **T121** Test improved prompt includes 2+ commit examples
- [ ] **T122** Test improved prompt mentions WHY vs WHAT principle
- [ ] **T123** Test improved prompt requests body for significant changes
- [ ] **T124** Test improved prompt enforces imperative mood
- [ ] **T125** Test prompt shows diff statistics (+additions -deletions)
- [ ] **T126** Test file list limited to 10 files max

### Ollama Generation Parameters Tests
- [ ] **T127** Test payload includes options.temperature=0.3
- [ ] **T128** Test payload includes options.top_p=0.9
- [ ] **T129** Test payload includes options.top_k=40
- [ ] **T130** Test payload includes options.num_predict=256

### Integration Tests
- [ ] **T131** Test DeepSeek E2E with real API (marked @pytest.mark.e2e)
- [ ] **T132** Test Ollama generates body paragraph for significant diff

## Phase 3.3: Implementation

### DeepSeek Provider
- [ ] **T133** Implement DeepSeekProvider in `src/gitcommit_ai/providers/deepseek.py`
- [ ] **T134** Update Config with DEEPSEEK_API_KEY in `src/gitcommit_ai/core/config.py`
- [ ] **T135** Add deepseek to CLI provider choices in `src/gitcommit_ai/cli/main.py`
- [ ] **T136** Update provider registry to include DeepSeek

### Ollama Improvements
- [ ] **T137** Replace _build_prompt() with improved version in `src/gitcommit_ai/providers/ollama.py`
- [ ] **T138** Add generation parameters to payload in _stream_response() method

## Phase 3.4: Documentation

- [ ] **T139** Update README.md with DeepSeek setup instructions
- [ ] **T140** Add DeepSeek pricing comparison table to README
- [ ] **T141** Update Ollama section with qwen2.5:7b recommendation
- [ ] **T142** Add before/after examples of Ollama quality improvements
- [ ] **T143** Update supported models table with DeepSeek

## Phase 3.5: Manual Testing

- [ ] **T144** Manual test: DeepSeek with real API key (verify $0.27/1M pricing)
- [ ] **T145** Manual test: Ollama with qwen2.5:7b (verify body generation)
- [ ] **T146** Manual test: Compare Ollama quality before/after (3 commits)
- [ ] **T147** Manual test: All 7 providers work (openai, anthropic, gemini, mistral, cohere, deepseek, ollama)

**Total**: 34 tasks (T114-T147)

## Dependency Graph

```
Tests Layer 1: T114-T119 (DeepSeek) → parallel
Tests Layer 2: T120-T126 (Ollama Prompt) → parallel
Tests Layer 3: T127-T130 (Ollama Params) → parallel
Tests Layer 4: T131-T132 (Integration) → depends on Layer 1-3
             ↓
Impl Layer 1: T133-T136 (DeepSeek) → sequential
Impl Layer 2: T137-T138 (Ollama) → sequential
             ↓
Docs: T139-T143 (parallel)
             ↓
Manual: T144-T147 (sequential validation)
```

## Notes

### DeepSeek Implementation Strategy
- Copy `openai.py` → rename to `deepseek.py`
- Change base URL: `https://api.deepseek.com/v1`
- Change env var: `DEEPSEEK_API_KEY`
- API is 100% OpenAI-compatible (no format changes needed)

### Ollama Prompt Strategy
- Prompt length: ~40 lines (tested, fits in context)
- Examples: 3 commit examples (feat with body, fix without, test without)
- Role: "expert software engineer" primes model for quality
- WHY emphasis: "explain reasoning" improves body generation
- Imperative mood: explicit instruction reduces "added" → "add"

### Ollama Parameters Strategy
- temperature=0.3: Reduces randomness (tested optimal)
- top_p=0.9: Quality sampling threshold
- top_k=40: Limits vocabulary to top 40 tokens
- num_predict=256: Allows body generation (default 128 too short)

### Testing Strategy
1. **Unit tests**: Mock HTTP for DeepSeek, validate prompt structure for Ollama
2. **Integration tests**: E2E with real APIs (marked for CI skip)
3. **Manual tests**: Human validation of quality improvements

### Expected Test Results
- Phase 3.2 (Tests): All tests RED ❌ (code doesn't exist yet)
- Phase 3.3 (Implementation): All tests GREEN ✅
- Phase 3.5 (Manual): Human verification of quality claims

## Success Criteria

### DeepSeek
- ✅ All unit tests pass
- ✅ E2E test with real API succeeds
- ✅ Cost verified: $0.27/1M tokens
- ✅ Quality comparable to GPT-4o-mini

### Ollama
- ✅ Prompt tests validate all improvements (role, examples, WHY, body, imperative)
- ✅ Parameter tests validate correct payload structure
- ✅ Manual testing shows body generation in 80%+ significant changes
- ✅ Manual testing shows improved scope accuracy (module vs filename)
- ✅ No speed regression (still ~5s for qwen2.5:7b)

### Documentation
- ✅ README clearly shows DeepSeek as cheapest cloud option
- ✅ README recommends qwen2.5:7b for Ollama quality
- ✅ Before/after examples demonstrate improvements
