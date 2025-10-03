# Feature Specification: Additional AI Providers (Gemini, Mistral, Cohere)

**Feature Branch**: `005-more-ai-providers`
**Created**: 2025-10-02
**Status**: Draft
**Priority**: Medium (wider choice = more users)

## User Scenarios & Testing

### Primary User Story
A developer already has API credits with Google Gemini or Mistral AI and wants to use those instead of OpenAI/Anthropic. They configure their provider and GitCommit AI works seamlessly.

### Acceptance Scenarios

1. **Given** Gemini API key set, **When** user runs `gitcommit-ai generate --provider gemini`, **Then** system uses Google Gemini Pro

2. **Given** Mistral API key set, **When** user runs `--provider mistral`, **Then** system uses Mistral-7B or configured model

3. **Given** Cohere API key set, **When** user runs `--provider cohere`, **Then** system uses Command model

4. **Given** multiple providers configured, **When** user runs `gitcommit-ai providers list`, **Then** system shows available providers with status (✓ configured, ✗ missing key)

5. **Given** user switches providers, **When** new provider fails, **Then** system suggests fallback to previous provider

### Edge Cases
- Provider-specific rate limits? → Handle gracefully with retry
- Model costs vary? → Show warning for expensive models
- Provider APIs change? → Version locking in dependencies
- Regional availability? → Clear error messages

## Requirements

### Functional Requirements

**Gemini Support**
- **FR-072**: System MUST support Google Gemini API (gemini-pro, gemini-pro-vision)
- **FR-073**: System MUST read GEMINI_API_KEY or GOOGLE_API_KEY from environment
- **FR-074**: System MUST use https://generativelanguage.googleapis.com/v1/models endpoint
- **FR-075**: System MUST handle Gemini-specific response format

**Mistral Support**
- **FR-076**: System MUST support Mistral AI API (mistral-tiny, mistral-small, mistral-medium)
- **FR-077**: System MUST read MISTRAL_API_KEY from environment
- **FR-078**: System MUST use https://api.mistral.ai/v1/chat/completions endpoint
- **FR-079**: System MUST support Mistral's function calling format

**Cohere Support**
- **FR-080**: System MUST support Cohere API (command, command-light)
- **FR-081**: System MUST read COHERE_API_KEY from environment
- **FR-082**: System MUST use https://api.cohere.ai/v1/generate endpoint
- **FR-083**: System MUST handle Cohere's streaming responses

**Provider Management**
- **FR-084**: System MUST provide `providers list` command showing all available providers
- **FR-085**: System MUST show provider status: configured (✓) or missing key (✗)
- **FR-086**: System MUST allow setting default provider via config
- **FR-087**: System MUST support provider-specific model selection

**Error Handling**
- **FR-088**: System MUST provide clear error messages for each provider's failures
- **FR-089**: System MUST suggest alternative providers when one fails
- **FR-090**: System MUST validate API keys before making requests
- **FR-091**: System MUST handle provider-specific rate limits

### Key Entities

- **GeminiProvider**: Google Gemini implementation
- **MistralProvider**: Mistral AI implementation
- **CohereProvider**: Cohere implementation
- **ProviderRegistry**: Manages all available providers
- **ProviderStatus**: Tracks configuration status for each provider

---

## Provider Comparison

| Provider | Model | Speed | Cost | Quality | Key |
|----------|-------|-------|------|---------|-----|
| OpenAI | gpt-4o-mini | Fast | $ | Excellent | OPENAI_API_KEY |
| Anthropic | claude-haiku | Fast | $ | Excellent | ANTHROPIC_API_KEY |
| Gemini | gemini-pro | Very Fast | Free tier | Good | GEMINI_API_KEY |
| Mistral | mistral-small | Fast | $ | Good | MISTRAL_API_KEY |
| Cohere | command-light | Fast | Free tier | Good | COHERE_API_KEY |
| Ollama | llama3.2 | Slow | Free | Good | (local) |

---

## API Endpoints

### Gemini
```
POST https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent
Header: x-goog-api-key: {key}
Body: {"contents": [{"parts": [{"text": "..."}]}]}
```

### Mistral
```
POST https://api.mistral.ai/v1/chat/completions
Header: Authorization: Bearer {key}
Body: {"model": "mistral-small", "messages": [...]}
```

### Cohere
```
POST https://api.cohere.ai/v1/generate
Header: Authorization: Bearer {key}
Body: {"model": "command", "prompt": "...", "max_tokens": 200}
```

---

## Configuration Example

```toml
# ~/.gitcommit-ai/config.toml
[providers]
default = "gemini"  # Use Gemini by default

[providers.gemini]
model = "gemini-pro"
timeout = 30

[providers.mistral]
model = "mistral-small"
```

---

## Out of Scope (for MVP)

- DeepSeek, Perplexity, Groq (add later)
- Provider cost tracking
- Automatic provider fallback chain
- Provider benchmarking/comparison
- Custom provider plugins

---

## Success Criteria

- ✅ Gemini, Mistral, Cohere fully functional
- ✅ `providers list` command works
- ✅ Easy provider switching
- ✅ Clear documentation for each provider
- ✅ All providers pass same test suite
