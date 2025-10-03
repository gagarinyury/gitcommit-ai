# Feature Specification: DeepSeek Provider + Ollama Quality Improvements

**Feature Branch**: `009-deepseek-ollama-improvements`
**Created**: 2025-10-03
**Status**: Draft
**Priority**: High (cost optimization + quality improvements)

## User Scenarios & Testing

### Primary User Story
A developer wants ultra-cheap AI commit messages ($0.27/1M tokens) using DeepSeek, and when using Ollama locally, expects quality comparable to cloud providers with detailed descriptions and body paragraphs.

### Acceptance Scenarios

1. **Given** DeepSeek API key set, **When** user runs `gitcommit-ai generate --provider deepseek`, **Then** system generates commit using DeepSeek-Chat model

2. **Given** user has Ollama with qwen2.5:7b, **When** generating commit, **Then** message includes body paragraph explaining WHY for significant changes

3. **Given** Ollama provider used, **When** generating commit, **Then** scope is precise (e.g., `feat(auth)` not `feat(auth.py)`)

4. **Given** multiple staged files, **When** using Ollama, **Then** description is specific (e.g., "implement JWT refresh" not "add 8 features")

5. **Given** DeepSeek configured, **When** comparing cost, **Then** DeepSeek is 18x cheaper than GPT-4o

### Edge Cases
- DeepSeek API errors? → Same error handling as OpenAI/Anthropic
- Ollama old models? → README recommends qwen2.5:7b
- Very large diffs (>128K tokens)? → DeepSeek supports up to 128K context
- Prompt too long for Ollama? → Limit file list to 10 files

## Requirements

### Functional Requirements

**DeepSeek Provider**
- **FR-136**: System MUST support DeepSeek API (deepseek-chat, deepseek-coder models)
- **FR-137**: System MUST read DEEPSEEK_API_KEY from environment
- **FR-138**: System MUST use https://api.deepseek.com/v1/chat/completions endpoint
- **FR-139**: System MUST handle DeepSeek OpenAI-compatible format
- **FR-140**: System MUST support cache-hit pricing optimization

**Ollama Improvements - Prompt Engineering**
- **FR-141**: Ollama prompt MUST include "expert software engineer" role
- **FR-142**: Ollama prompt MUST provide 2-3 examples of quality commits
- **FR-143**: Ollama prompt MUST explain WHY vs WHAT principle
- **FR-144**: Ollama prompt MUST request body paragraph for significant changes
- **FR-145**: Ollama prompt MUST enforce imperative mood (add/fix, not added/fixing)
- **FR-146**: Ollama prompt MUST show diff statistics (+additions -deletions)

**Ollama Improvements - Generation Parameters**
- **FR-147**: System MUST set temperature=0.3 for focused output
- **FR-148**: System MUST set top_p=0.9 for quality sampling
- **FR-149**: System MUST set top_k=40 for vocabulary control
- **FR-150**: System MUST set num_predict=256 to allow body generation

**Documentation**
- **FR-151**: README MUST recommend qwen2.5:7b as best quality model
- **FR-152**: README MUST show DeepSeek pricing comparison
- **FR-153**: README MUST provide before/after examples of Ollama quality

### Key Entities

- **DeepSeekProvider**: DeepSeek API implementation (OpenAI-compatible)
- **OllamaProvider**: Enhanced with improved prompt + generation params
- **Config**: Add DEEPSEEK_API_KEY support

---

## DeepSeek Pricing Comparison

| Provider | Model | Input ($/1M tokens) | Output ($/1M tokens) | Typical Commit Cost |
|----------|-------|---------------------|----------------------|---------------------|
| **DeepSeek** | deepseek-chat | **$0.27** | $1.10 | **$0.000054** |
| OpenAI | gpt-4o-mini | $0.15 | $0.60 | $0.000030 |
| OpenAI | gpt-4o | $5.00 | $15.00 | $0.001000 |
| Anthropic | claude-haiku | $0.80 | $4.00 | $0.000160 |
| Ollama | qwen2.5:7b | Free | Free | Free |

**DeepSeek = 2x cost of GPT-4o-mini, 18x cheaper than GPT-4o**

---

## Ollama Quality Improvements

### Current Problems (from research report)

❌ **Vague descriptions**: "add 8 new features"
❌ **No body**: Body generation rate = 0%
❌ **Incorrect scope**: Uses filename `feat(app.py)` instead of module `feat(app)`

### Expected After Improvements

✅ **Specific descriptions**: "implement JWT token refresh mechanism"
✅ **Body included**: 80% of significant changes include explanatory body
✅ **Correct scope**: Uses module name `feat(auth)`

### Example Improvement

**Before:**
```
feat(app): add 8 new features
```

**After:**
```
feat(auth): implement JWT token refresh mechanism

Automated token refresh maintains user sessions without re-authentication,
improving UX and preventing unexpected logouts during active usage.
```

---

## API Endpoints

### DeepSeek
```
POST https://api.deepseek.com/v1/chat/completions
Header: Authorization: Bearer {key}
Body: {
  "model": "deepseek-chat",
  "messages": [{"role": "user", "content": "..."}],
  "temperature": 0.7,
  "max_tokens": 200
}
```

**Response**: OpenAI-compatible format
```json
{
  "choices": [{
    "message": {
      "content": "feat(auth): implement JWT support"
    }
  }]
}
```

---

## Configuration Example

```bash
# DeepSeek (cheap option)
export DEEPSEEK_API_KEY="sk-..."

# Ollama (free option, recommended model)
ollama pull qwen2.5:7b
export OLLAMA_DEFAULT_MODEL="qwen2.5:7b"
```

---

## Out of Scope (for MVP)

- DeepSeek Reasoner (R1) model - more expensive, overkill for commits
- Automatic provider cost tracking
- DeepSeek cache optimization strategies
- Ollama prompt A/B testing framework

---

## Success Criteria

- ✅ DeepSeek provider works with OpenAI-compatible API
- ✅ Ollama generates body paragraphs in 80%+ of significant changes
- ✅ Ollama scope accuracy improves from 70% → 90%
- ✅ README clearly shows DeepSeek as cheapest cloud option
- ✅ All tests pass (TDD methodology)
- ✅ Quality rating: Ollama 8/10 → 9.5/10

---

## Research References

- DeepSeek Pricing: $0.27/1M input tokens (cache miss)
- Ollama Prompt Testing: temperature=0.3, top_p=0.9, top_k=40 optimal
- Model Recommendation: qwen2.5:7b (+0.7s latency, significantly better quality)
