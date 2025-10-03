# Implementation Plan: Ollama Support (Local AI Models)

**Branch**: `002-ollama-support` | **Date**: 2025-10-02 | **Spec**: [002-ollama-support.md](../002-ollama-support.md)

## Summary
Add Ollama provider to enable free, offline commit message generation using local LLMs (llama3.2, codellama, mistral). Integrates with existing AIProvider abstraction, requires no API keys, and works entirely offline.

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: httpx (already in deps for API providers)
**Storage**: N/A (stateless, reads Ollama state via API)
**Testing**: pytest with mocked Ollama HTTP endpoints
**Target Platform**: Linux/macOS (Ollama supports both)
**Project Type**: Single (extends existing provider system)
**Performance Goals**: <10s for medium models, <30s for large models
**Constraints**: Localhost only (no remote Ollama), requires Ollama 0.1.0+
**Scale/Scope**: Single local Ollama instance per user

## Constitution Check

### ✅ Library-First Architecture
- `src/gitcommit_ai/providers/ollama.py` extends existing `AIProvider` interface
- Reuses `base.py` abstraction (no architecture changes)
- Independently testable with mocked HTTP

### ✅ CLI Interface Mandate
- `gitcommit-ai generate --provider ollama [--model llama3.2]`
- Exit codes: 4=Ollama not installed, 5=model not found, 2=connection error
- JSON output supported via existing `--json` flag

### ✅ Test-First Development
- Tests for Ollama detection (subprocess mocking)
- Tests for streaming response parsing
- Integration tests with recorded Ollama responses

### ✅ Integration Testing Priority
- Mock Ollama HTTP server for tests
- Real Ollama test (optional, requires local Ollama)
- End-to-end: generate → Ollama → commit message

### ✅ Simplicity & YAGNI
- No new dependencies (httpx already used)
- No Ollama SDK (direct HTTP API calls)
- No model management (delegate to `ollama pull`)

**Complexity Tracking**: None. Adds single provider following existing pattern.

## Project Structure

### Documentation (this feature)
```
.specify/specs/002-ollama-support/
├── plan.md              # This file
├── research.md          # Ollama API docs, streaming format
├── data-model.md        # OllamaConfig, ModelInfo classes
├── contracts/
│   └── ollama-provider.md  # OllamaProvider interface
└── tasks.md             # Phase 2: created by /tasks command
```

### Source Code (extends existing structure)
```
src/gitcommit_ai/
├── providers/
│   ├── base.py              # [EXISTING] AIProvider ABC
│   ├── openai.py            # [EXISTING]
│   ├── anthropic.py         # [EXISTING]
│   └── ollama.py            # [NEW] Ollama implementation
├── core/
│   └── config.py            # [MODIFY] Add OLLAMA_HOST, default model
└── cli/
    └── main.py              # [MODIFY] Add ollama to provider choices

tests/
├── unit/
│   ├── test_ollama.py       # [NEW] Ollama provider tests
│   └── test_config.py       # [MODIFY] Test Ollama config
└── integration/
    └── test_ollama_integration.py  # [NEW] Mocked Ollama server
```

## Phase 0: Research

**Output**: `research.md` documenting:

1. **Ollama API Specification**
   - Endpoint: `POST http://localhost:11434/api/generate`
   - Request format: `{"model": "llama3.2", "prompt": "...", "stream": true}`
   - Response: newline-delimited JSON stream
   - Example: `{"response": "fix", "done": false}\n{"response": ": update", "done": true}`

2. **Model Detection**
   - Command: `ollama list` (stdout parsing)
   - Output format: table with NAME, ID, SIZE, MODIFIED columns
   - Error detection: exit code != 0 or command not found

3. **Streaming Response Handling**
   - Parse JSON per line: `json.loads(line)`
   - Accumulate `response` field until `done: true`
   - Timeout handling: httpx timeout parameter

4. **Popular Models Analysis**
   - llama3.2 (3B): fast, good quality
   - codellama (7B): code-focused, slower
   - mistral (7B): balanced performance
   - phi3 (3.8B): Microsoft, efficient

5. **Error Scenarios**
   - Ollama not installed: subprocess FileNotFoundError
   - Service not running: httpx ConnectError
   - Model not found: API returns 404
   - Malformed response: JSON decode error

## Phase 1: Design

**Outputs**: `data-model.md`, `contracts/ollama-provider.md`

### Data Model (`data-model.md`)
```python
@dataclass
class OllamaConfig:
    host: str = "http://localhost:11434"  # from OLLAMA_HOST
    default_model: str = "llama3.2"
    timeout_seconds: int = 60
    stream: bool = True

@dataclass
class ModelInfo:
    name: str
    size: str  # e.g., "4.7 GB"
    modified: datetime

class OllamaResponse:
    """Streaming response accumulator"""
    response: str = ""
    done: bool = False
```

### Contract (`contracts/ollama-provider.md`)

```python
class OllamaProvider(AIProvider):
    """Ollama local AI provider implementation"""

    def __init__(self, config: OllamaConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=config.timeout_seconds)

    async def generate_commit_message(self, diff: GitDiff) -> CommitMessage:
        """Generate message using local Ollama model"""
        # 1. Validate Ollama is running
        # 2. Check model exists
        # 3. Send prompt
        # 4. Stream and parse response
        # 5. Convert to CommitMessage

    @staticmethod
    def is_installed() -> bool:
        """Check if ollama CLI is available"""
        # Run: ollama list
        # Return: True if exit code 0

    async def list_models() -> list[ModelInfo]:
        """Get available Ollama models"""
        # Parse: ollama list output

    def validate_config(self) -> list[str]:
        """Returns missing/invalid config"""
        # Check: Ollama installed, service running
```

### Integration Points

**Modify `src/gitcommit_ai/core/config.py`:**
```python
class Config:
    # ... existing fields ...
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    ollama_default_model: str = "llama3.2"
```

**Modify `src/gitcommit_ai/cli/main.py`:**
```python
parser.add_argument(
    "--provider",
    choices=["openai", "anthropic", "ollama"],  # Add ollama
    default="openai"
)
parser.add_argument(
    "--model",
    help="Model to use (provider-specific)"
)
```

## Phase 2: Task Generation Plan

The `/tasks` command will create `tasks.md` by:

1. **Layer 0: Data models** (OllamaConfig, ModelInfo)
2. **Layer 1: Ollama detection** (is_installed, list_models)
3. **Layer 2: Provider implementation** (OllamaProvider class)
4. **Layer 3: CLI integration** (add ollama to choices)
5. **Layer 4: Integration tests** (mocked Ollama server)

Each task follows TDD:
- Write test describing behavior
- Run test (should fail - red)
- Implement feature
- Run test (should pass - green)

## Progress Tracking

- [x] Initial Constitution Check (passed)
- [ ] Phase 0: Research (pending)
- [ ] Phase 1: Design artifacts (pending)
- [ ] Post-Design Constitution Check (pending)
- [ ] Phase 2: Task generation (delegated to /tasks)
- [ ] Phase 3-4: Implementation (delegated to developer)

## Dependencies on Feature 001

**Required from 001-ai-commit-messages:**
- `AIProvider` base class (`src/gitcommit_ai/providers/base.py`)
- `GitDiff` and `CommitMessage` dataclasses
- CLI arg parsing infrastructure
- Config loading system

**Assumption**: Feature 001 is fully implemented before starting 002.

## Unresolved Questions

1. **Model recommendation**:
   - **Decision needed**: Which model should be default? llama3.2 (fast) vs codellama (code-focused)?
   - **Recommendation**: llama3.2 (smaller, faster, good enough for commit messages)

2. **Progress indicator**:
   - **Decision needed**: Show spinner during generation? Print dots?
   - **Recommendation**: Print "Generating..." on stderr, spinner if >5s

3. **Model auto-pull**:
   - **Decision needed**: Offer to `ollama pull` missing model?
   - **Recommendation**: No auto-pull in MVP (requires user approval, slow). Show command instead.

4. **Ollama version compatibility**:
   - **Decision needed**: Minimum Ollama version required?
   - **Recommendation**: 0.1.0+ (streaming API stable), check with `ollama --version`
