# Feature Specification: Ollama Support (Local AI Models)

**Feature Branch**: `002-ollama-support`
**Created**: 2025-10-02
**Status**: Draft
**Priority**: High (enables free usage without API keys)

## User Scenarios & Testing

### Primary User Story
A developer wants to use GitCommit AI without paying for OpenAI/Anthropic APIs. They install Ollama locally, run a model like `llama3.2` or `codellama`, and use it for commit message generation entirely offline.

### Acceptance Scenarios

1. **Given** Ollama is installed and running locally, **When** user runs `gitcommit-ai generate --provider ollama`, **Then** system connects to local Ollama instance and generates commit message

2. **Given** Ollama is not installed, **When** user tries `--provider ollama`, **Then** system displays helpful error: "Ollama not found. Install: https://ollama.ai"

3. **Given** Ollama is installed but no model pulled, **When** user runs command, **Then** system suggests: "No model found. Run: ollama pull llama3.2"

4. **Given** user has multiple Ollama models, **When** user runs `gitcommit-ai generate --provider ollama --model codellama`, **Then** system uses specified model

5. **Given** Ollama service is down, **When** user tries to generate, **Then** system displays: "Cannot connect to Ollama at localhost:11434"

### Edge Cases
- What if Ollama is running on custom port? → Support `OLLAMA_HOST` env variable
- What if model response is malformed? → Fallback parsing, retry once
- What if local model is slow (>30s)? → Show progress indicator
- Multiple Ollama instances? → Use first available or from config

## Requirements

### Functional Requirements

**Core Functionality**
- **FR-021**: System MUST detect if Ollama is installed (`ollama list` command)
- **FR-022**: System MUST connect to Ollama API at localhost:11434 (default)
- **FR-023**: System MUST support custom Ollama host via OLLAMA_HOST environment variable
- **FR-024**: System MUST list available Ollama models when requested
- **FR-025**: System MUST allow user to specify model via `--model` flag

**Model Management**
- **FR-026**: System MUST validate that requested model exists locally
- **FR-027**: System MUST provide helpful error if model not found (suggest `ollama pull`)
- **FR-028**: System MUST support popular models: llama3.2, codellama, mistral, phi3
- **FR-029**: System MUST handle model-specific context limits

**Generation**
- **FR-030**: System MUST send prompt to Ollama using /api/generate endpoint
- **FR-031**: System MUST stream responses from Ollama (show progress)
- **FR-032**: System MUST parse Ollama response into CommitMessage format
- **FR-033**: System MUST handle malformed responses gracefully

**Performance**
- **FR-034**: System MUST timeout after 60s (configurable)
- **FR-035**: System MUST show progress indicator for slow models
- **FR-036**: System MUST cache model metadata to avoid repeated checks

**Configuration**
- **FR-037**: User MUST be able to set default Ollama model in config
- **FR-038**: System MUST work offline (no internet required)
- **FR-039**: System MUST validate Ollama connection before sending prompt

### Key Entities

- **OllamaProvider**: Implements AIProvider interface for Ollama
- **OllamaConfig**: Stores host, port, default model, timeout settings
- **ModelInfo**: Metadata about available Ollama models (name, size, modified)

---

## Technical Constraints

- Ollama API uses HTTP POST to localhost:11434/api/generate
- Response is JSON stream (newline-delimited)
- No authentication required (local only)
- Models can be 1GB+ (check disk space)
- Response time varies: 2s (small models) to 30s+ (large models)

---

## Out of Scope (for MVP)

- Ollama model installation via CLI
- Model quantization selection (Q4, Q5, Q8)
- Multiple Ollama instances (use only default)
- Ollama remote server support (only localhost)
- Custom Ollama parameters (temperature, top_p)

---

## Success Criteria

- ✅ User can generate commits with `--provider ollama` without API keys
- ✅ System detects Ollama installation status
- ✅ Clear error messages for common issues
- ✅ Works completely offline
- ✅ Performance acceptable for medium models (<10s)
