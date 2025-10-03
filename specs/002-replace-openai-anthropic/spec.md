# Feature Specification: Replace Multiple Cloud Providers with OpenRouter

**Feature Branch**: `002-replace-openai-anthropic`
**Created**: 2025-10-03
**Status**: Draft
**Input**: User description: "Replace OpenAI, Anthropic, Gemini, Mistral, Cohere providers with single OpenRouter provider"

## Execution Flow (main)
```
1. Parse user description from Input
   → Feature: Simplify provider architecture by consolidating 5 cloud providers into 1
2. Extract key concepts from description
   → Actors: users configuring AI providers
   → Actions: configure, select model, generate commit messages
   → Data: API keys, model selection, commit messages
   → Constraints: maintain backward compatibility, don't break existing users
3. For each unclear aspect:
   → Marked with [NEEDS CLARIFICATION]
4. Fill User Scenarios & Testing section
   → Clear user flow: configure once, access all models
5. Generate Functional Requirements
   → All requirements testable
6. Identify Key Entities
   → Provider configuration, model selection
7. Run Review Checklist
   → Check for implementation details
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## Clarifications

### Session 2025-10-03
- Q: When OpenRouter API is unavailable or returns an error, what should the system do? → A: Show error only - Display clear error message, suggest manual switch to `--provider openai/anthropic/gemini/deepseek/ollama` if user has those keys configured. No automatic fallback.

---

## User Scenarios & Testing

### Primary User Story
As a developer using gitcommit-ai, I want simplified access to Mistral and Cohere models without managing separate API keys, while retaining the ability to use direct providers (OpenAI, Anthropic, Gemini, DeepSeek, Ollama) when needed.

**Current situation (Mistral/Cohere):**
- Must create separate Mistral and Cohere accounts
- Obtain 2 additional API keys
- Configure 2 environment variables
- Limited to only those providers' models

**After this feature:**
- **Option 1 (Recommended)**: Use OpenRouter for access to Mistral, Cohere, and 100+ other models with 1 API key
- **Option 2 (Fallback)**: Continue using direct providers (OpenAI, Anthropic, Gemini, DeepSeek) if preferred
- **Option 3 (Free)**: Use Ollama locally (unchanged, still default)

### Acceptance Scenarios

1. **Given** user has OpenRouter API key, **When** user runs `gitcommit-ai generate --provider openrouter --model openai/gpt-4o`, **Then** system generates commit message using GPT-4o through OpenRouter

2. **Given** user has OpenRouter API key, **When** user runs `gitcommit-ai generate --provider openrouter --model anthropic/claude-3-5-sonnet`, **Then** system generates commit message using Claude through OpenRouter

3. **Given** user has legacy OpenAI API key configured, **When** user runs `gitcommit-ai generate --provider openai`, **Then** system still works with direct OpenAI provider (backward compatibility)

4. **Given** user runs `gitcommit-ai providers`, **When** OpenRouter key is configured, **Then** system shows OpenRouter as configured with access to 100+ models

5. **Given** user has no API keys, **When** user runs `gitcommit-ai generate`, **Then** system defaults to Ollama (local, free) - unchanged behavior

### Edge Cases
- What happens when OpenRouter API key is invalid? System MUST show clear error message with link to https://openrouter.ai/keys
- What happens when user specifies non-existent model? System MUST validate model name and show available models
- What happens when existing users upgrade? System MUST continue working with their existing provider configurations (OpenAI, Anthropic, etc.)
- What happens when OpenRouter is down? System MUST show error message suggesting manual fallback: "Try `--provider openai`, `--provider anthropic`, `--provider deepseek`, or `--provider ollama` if you have those configured"

## Requirements

### Functional Requirements

- **FR-001**: System MUST support OpenRouter as a new provider with single API key configuration
- **FR-002**: System MUST allow users to access OpenAI models (gpt-4o, gpt-4o-mini, gpt-3.5-turbo) through OpenRouter
- **FR-003**: System MUST allow users to access Anthropic models (claude-3-opus, claude-3-5-sonnet, claude-3-haiku) through OpenRouter
- **FR-004**: System MUST allow users to access Google Gemini models (gemini-2.0-flash, gemini-2.5-pro) through OpenRouter
- **FR-005**: System MUST allow users to access Mistral models (mistral-tiny, mistral-small, mistral-large) through OpenRouter
- **FR-006**: System MUST allow users to access Cohere models (command, command-light) through OpenRouter
- **FR-007**: System MUST keep all direct providers (OpenAI, Anthropic, Gemini, DeepSeek) for manual fallback when OpenRouter unavailable
- **FR-008**: System MUST keep Ollama as default provider (free, local, no breaking changes)
- **FR-009**: System MUST remove only Mistral and Cohere direct providers (replaced by OpenRouter access)
- **FR-010**: When OpenRouter fails, system MUST display error with suggestion to use alternative providers manually
- **FR-011**: Documentation MUST show OpenRouter as recommended way to access premium models
- **FR-012**: `.env.example` MUST include OpenRouter configuration example
- **FR-013**: System MUST validate OpenRouter API key format and provide helpful error messages
- **FR-014**: `gitcommit-ai providers` command MUST list OpenRouter with available model categories
- **FR-015**: System MUST preserve all existing tests for backward compatibility

### Non-Functional Requirements

- **NFR-001**: Migration MUST NOT break existing user configurations
- **NFR-002**: New provider architecture MUST reduce codebase complexity (fewer providers to maintain)
- **NFR-003**: Documentation MUST clearly communicate migration path for users of legacy providers
- **NFR-004**: All existing tests MUST pass (273 tests)

### Key Entities

- **Provider Configuration**: Represents user's API key setup
  - Ollama (default, no key needed)
  - OpenRouter (recommended for premium models - unified access to 100+ models)
  - Direct providers (OpenAI, Anthropic, Gemini, DeepSeek - available for fallback or preference)
  - Removed providers (Mistral, Cohere - only accessible via OpenRouter)

- **Model Selection**: Represents which AI model to use
  - Format: `provider/model-name` (e.g., `openai/gpt-4o`, `anthropic/claude-3-5-sonnet`)
  - OpenRouter uses unified model naming across all providers
  - Backward compatible with simple model names for legacy providers

---

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities resolved (clarification session completed)
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---

## Success Metrics

- **Simplified access**: OpenRouter provides 1-key access to Mistral + Cohere + 100+ other models
- **Preserved choice**: Users can still use direct providers (OpenAI, Anthropic, Gemini, DeepSeek, Ollama) as alternatives
- **Reduced codebase**: Remove 2 provider implementations (Mistral, Cohere), add 1 unified OpenRouter provider
- **Maintained backward compatibility**: 0 breaking changes for existing users
- **All tests passing**: 273+ tests (including new OpenRouter tests)
