# Implementation Plan: Additional AI Providers (Gemini, Mistral, Cohere)

**Branch**: `005-more-ai-providers` | **Date**: 2025-10-02 | **Spec**: [005-more-ai-providers.md](../005-more-ai-providers.md)

## Summary
Add support for Google Gemini, Mistral AI, and Cohere to expand provider choice. Each follows existing AIProvider pattern. Includes `providers list` command to show configured providers. Enables users to leverage existing API credits and free tiers (Gemini, Cohere).

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: httpx (existing)
**Storage**: N/A (stateless API calls)
**Testing**: pytest with mocked HTTP responses
**Target Platform**: Linux/macOS (API-based, platform-agnostic)
**Project Type**: Single (extends provider system)
**Performance Goals**: <3s per provider (similar to OpenAI/Anthropic)
**Constraints**: Provider-specific API formats, rate limits vary
**Scale/Scope**: 3 new providers + registry system

## Constitution Check

### ✅ Library-First Architecture
- Each provider = standalone module (`gemini.py`, `mistral.py`, `cohere.py`)
- All implement `AIProvider` interface (no changes to base)
- ProviderRegistry = library for provider discovery

### ✅ CLI Interface Mandate
- `gitcommit-ai generate --provider gemini|mistral|cohere`
- `gitcommit-ai providers list` (new command)
- Exit codes: same as existing (2=API error, 3=config error)

### ✅ Test-First Development
- Tests for each provider (HTTP mocking)
- Tests for ProviderRegistry
- Integration tests with all providers

### ✅ Integration Testing Priority
- Mocked API responses for each provider
- Provider fallback scenarios
- Config validation across providers

### ✅ Simplicity & YAGNI
- No SDKs (direct HTTP like OpenAI/Anthropic)
- No provider abstraction layer beyond AIProvider
- No automatic provider selection (user chooses)

**Complexity Tracking**: None. Replicates existing pattern 3x.

## Project Structure

### Documentation
```
.specify/specs/005-more-ai-providers/
├── plan.md
├── research.md          # API docs for Gemini, Mistral, Cohere
├── provider-comparison.md
└── tasks.md
```

### Source Code
```
src/gitcommit_ai/
├── providers/
│   ├── base.py              # [EXISTING]
│   ├── gemini.py            # [NEW] Google Gemini
│   ├── mistral.py           # [NEW] Mistral AI
│   ├── cohere.py            # [NEW] Cohere
│   └── registry.py          # [NEW] ProviderRegistry
├── core/
│   └── config.py            # [MODIFY] Add new API keys
└── cli/
    └── main.py              # [MODIFY] Add providers list command

tests/
├── unit/
│   ├── test_gemini.py       # [NEW]
│   ├── test_mistral.py      # [NEW]
│   ├── test_cohere.py       # [NEW]
│   └── test_registry.py     # [NEW]
└── integration/
    └── test_all_providers.py # [NEW] Cross-provider tests
```

## Phase 0: Research

**Output**: `research.md` documenting:

1. **Gemini API**
   - Endpoint: `POST /v1/models/gemini-pro:generateContent`
   - Auth: `x-goog-api-key` header
   - Request: `{"contents": [{"parts": [{"text": "..."}]}]}`
   - Response: `{"candidates": [{"content": {"parts": [{"text": "..."}]}}]}`

2. **Mistral API**
   - Endpoint: `POST /v1/chat/completions`
   - Auth: `Authorization: Bearer {key}`
   - Request: OpenAI-compatible format
   - Response: OpenAI-compatible format

3. **Cohere API**
   - Endpoint: `POST /v1/generate`
   - Auth: `Authorization: Bearer {key}`
   - Request: `{"prompt": "...", "model": "command"}`
   - Response: `{"generations": [{"text": "..."}]}`

4. **Provider Registry Design**
   - Auto-discover all AIProvider subclasses
   - Check config status (API key present?)
   - Return sorted list for `providers list` command

## Phase 1: Design

### Provider Implementations

**Gemini (`gemini.py`)**
```python
class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(base_url="https://generativelanguage.googleapis.com")

    async def generate_commit_message(self, diff: GitDiff) -> CommitMessage:
        # Build Gemini request
        # POST to /v1/models/{model}:generateContent
        # Parse response
```

**Mistral (`mistral.py`)**
```python
class MistralProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "mistral-small"):
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(base_url="https://api.mistral.ai")

    async def generate_commit_message(self, diff: GitDiff) -> CommitMessage:
        # OpenAI-compatible format
        # POST to /v1/chat/completions
```

**Cohere (`cohere.py`)**
```python
class CohereProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "command-light"):
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(base_url="https://api.cohere.ai")

    async def generate_commit_message(self, diff: GitDiff) -> CommitMessage:
        # POST to /v1/generate
        # Handle streaming response
```

### Provider Registry (`registry.py`)

```python
class ProviderRegistry:
    @staticmethod
    def list_providers() -> list[ProviderInfo]:
        """Return all available providers with status"""
        providers = [
            ProviderInfo(
                name="openai",
                configured=bool(os.getenv("OPENAI_API_KEY")),
                models=["gpt-4o", "gpt-4o-mini"]
            ),
            # ... for all providers
        ]
        return providers

    @staticmethod
    def get_provider(name: str, **kwargs) -> AIProvider:
        """Factory method to create provider instance"""
        if name == "gemini":
            return GeminiProvider(api_key=..., **kwargs)
        # ... etc
```

### CLI Integration

**Add `providers list` command:**
```bash
$ gitcommit-ai providers list
Available AI Providers:
  ✓ openai      (gpt-4o-mini)         OPENAI_API_KEY configured
  ✓ anthropic   (claude-3-haiku)      ANTHROPIC_API_KEY configured
  ✗ gemini      (gemini-pro)          GEMINI_API_KEY missing
  ✗ mistral     (mistral-small)       MISTRAL_API_KEY missing
  ✓ cohere      (command-light)       COHERE_API_KEY configured
  ✓ ollama      (llama3.2)            Installed, service running
```

## Phase 2: Task Generation Plan

Tasks will cover:
1. **Layer 1**: Gemini provider (tests + impl)
2. **Layer 2**: Mistral provider (tests + impl)
3. **Layer 3**: Cohere provider (tests + impl)
4. **Layer 4**: ProviderRegistry (tests + impl)
5. **Layer 5**: CLI integration (providers list command)

Each layer: TDD (tests → impl → green)

## Progress Tracking

- [x] Initial Constitution Check (passed)
- [ ] Phase 0: Research
- [ ] Phase 1: Design
- [ ] Post-Design Constitution Check
- [ ] Phase 2: Task generation (/tasks)
- [ ] Phase 3-4: Implementation

## Dependencies

**Required from Feature 001:**
- AIProvider base class
- Config system
- CLI infrastructure

**Pattern reuse:**
- OpenAI/Anthropic implementations serve as templates
- Ollama streaming logic applicable to Cohere

## Unresolved Questions

1. **Free tier limits**: Warn users about Gemini/Cohere quotas?
   - **Recommendation**: Show in `providers list` with note

2. **Model selection**: Allow per-provider default models?
   - **Recommendation**: Yes, add to config: `gemini_default_model=gemini-pro`

3. **Fallback chain**: Auto-try next provider on failure?
   - **Recommendation**: No auto-fallback in MVP (suggest manually)

4. **Provider aliases**: Support `--provider google` as alias for `gemini`?
   - **Recommendation**: V2 feature (keep simple for now)
