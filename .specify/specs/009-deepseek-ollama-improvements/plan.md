# Implementation Plan: DeepSeek Provider + Ollama Quality Improvements

**Branch**: `009-deepseek-ollama-improvements` | **Date**: 2025-10-03 | **Spec**: [009-deepseek-ollama-improvements.md](../009-deepseek-ollama-improvements.md)

## Summary
Add DeepSeek as cheapest cloud provider ($0.27/1M tokens, 18x cheaper than GPT-4o) and dramatically improve Ollama quality through prompt engineering + generation parameters. Ollama improvements target: body generation 0%→80%, scope accuracy 70%→90%, overall quality 8/10→9.5/10.

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: httpx (existing)
**Storage**: N/A (stateless API calls)
**Testing**: pytest with mocked HTTP responses + Ollama prompt validation
**Target Platform**: Linux/macOS (API-based, platform-agnostic)
**Project Type**: Single (1 new provider + 1 enhancement)
**Performance Goals**: DeepSeek <3s, Ollama unchanged (~5s)
**Constraints**: OpenAI-compatible API for DeepSeek, Ollama prompt length <2048 tokens
**Scale/Scope**: 1 new provider + 4 Ollama improvements (prompt + 3 params)

## Constitution Check

### ✅ Library-First Architecture
- DeepSeekProvider = standalone module (`deepseek.py`)
- Implements existing `AIProvider` interface (no changes to base)
- Ollama improvements confined to `ollama.py` (no new modules)

### ✅ CLI Interface Mandate
- `gitcommit-ai generate --provider deepseek`
- Existing `--provider ollama` unchanged (transparent improvements)
- Exit codes: same as existing (2=API error, 3=config error)

### ✅ Test-First Development
- Tests for DeepSeekProvider (HTTP mocking)
- Tests for Ollama prompt improvements (validate prompt structure)
- Tests for Ollama generation params (validate payload)

### ✅ Integration Testing Priority
- Mocked DeepSeek API responses
- Ollama prompt quality validation (contains role, examples, WHY)
- Ollama params validation (temperature=0.3, top_p=0.9, top_k=40)

### ✅ Simplicity & YAGNI
- DeepSeek uses OpenAI-compatible format (minimal code)
- No new abstraction layers
- Ollama improvements = prompt string + 4 params (no architectural changes)

**Complexity Tracking**: None. DeepSeek replicates OpenAI pattern, Ollama changes are localized.

## Project Structure

### Documentation
```
.specify/specs/009-deepseek-ollama-improvements/
├── plan.md              # [THIS FILE]
├── tasks.md             # Task breakdown (TDD)
└── research.md          # DeepSeek API docs + Ollama testing results
```

### Source Code
```
src/gitcommit_ai/
├── providers/
│   ├── base.py          # [EXISTING] No changes
│   ├── deepseek.py      # [NEW] DeepSeek provider
│   ├── ollama.py        # [MODIFY] Improved prompt + params
│   └── openai.py        # [REFERENCE] DeepSeek follows same pattern
├── core/
│   └── config.py        # [MODIFY] Add DEEPSEEK_API_KEY
└── cli/
    └── main.py          # [MODIFY] Add deepseek to provider choices

tests/
├── unit/
│   ├── test_deepseek.py    # [NEW] DeepSeek provider tests
│   └── test_ollama.py      # [MODIFY] Add prompt + params tests
└── fixtures/
    └── deepseek_responses/ # [NEW] Mock API responses
```

## Phase 0: Research

**Output**: `research.md` documenting:

1. **DeepSeek API**
   - Endpoint: `POST https://api.deepseek.com/v1/chat/completions`
   - Auth: `Authorization: Bearer {key}`
   - Request: OpenAI-compatible (messages array)
   - Response: OpenAI-compatible (choices[0].message.content)
   - Pricing: $0.27/1M input (cache miss), $1.10/1M output

2. **Ollama Prompt Analysis**
   - Current: 10 lines, no examples, no body instruction
   - Target: ~40 lines, 2-3 examples, explicit body requirement
   - Testing: temperature=0.3 produces best quality (tested)

3. **Ollama Generation Params**
   - Defaults: temperature≈0.8 (too random)
   - Optimal: temp=0.3, top_p=0.9, top_k=40, num_predict=256
   - Source: Research report testing with qwen2.5:3b and :7b

## Phase 1: Design

### DeepSeek Provider (`deepseek.py`)

**Pattern**: Copy `openai.py`, change base URL and API key env var

```python
class DeepSeekProvider(AIProvider):
    """DeepSeek AI provider (OpenAI-compatible API)."""

    def __init__(self, api_key: str | None = None, model: str = "deepseek-chat"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not set")

        self.model = model
        self.client = httpx.AsyncClient(
            base_url="https://api.deepseek.com/v1",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

    async def generate_commit_message(self, diff: GitDiff) -> CommitMessage:
        # Build messages (same as OpenAI)
        prompt = self._build_prompt(diff)

        # POST to /chat/completions (OpenAI-compatible)
        response = await self.client.post(
            "/chat/completions",
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 200
            }
        )

        # Parse response (OpenAI-compatible)
        data = response.json()
        message_text = data["choices"][0]["message"]["content"]
        return self._parse_response(message_text)

    def _build_prompt(self, diff: GitDiff) -> str:
        # Same prompt as OpenAI provider
        ...

    def _parse_response(self, response: str) -> CommitMessage:
        # Same parsing as OpenAI provider
        ...
```

### Ollama Prompt Improvement (`ollama.py:220-243`)

**Before** (10 lines):
```python
prompt = f"""Generate a concise git commit message in conventional commit format for these changes:

Files changed:
{files}

Changes: {diff_summary}

Format: <type>(<scope>): <description>
Types: feat, fix, docs, style, refactor, test, chore

Return ONLY the commit message, nothing else."""
```

**After** (~40 lines with role, examples, WHY, body):
```python
file_details = "\n".join([
    f"- {f.path} ({f.change_type}, +{f.additions} -{f.deletions})"
    for f in diff.files[:10]
])

prompt = f"""You are an expert software engineer writing git commit messages following conventional commits specification.

CONTEXT:
Files changed:
{file_details}

Total changes: +{diff.total_additions} -{diff.total_deletions} lines

TASK:
Analyze the changes and write a precise commit message:
1. Determine PRIMARY purpose: feat (new capability), fix (bug repair), test (tests only), docs (documentation), refactor (code restructure), chore (maintenance)
2. Specify exact scope (module/component name, e.g., 'auth', 'parser', 'api')
3. Write clear description in imperative mood (e.g., "add", "fix", "update", not "added" or "adding")
4. Add body paragraph (2-3 sentences) explaining WHY/context if change is significant

FORMAT:
type(scope): brief description (under 50 chars)

[Body paragraph explaining reasoning - ONLY if change is significant]

EXAMPLES:
feat(auth): implement JWT token refresh mechanism

Automated token refresh maintains user sessions without re-authentication, improving UX and preventing unexpected logouts.

fix(parser): resolve null pointer in date parsing

test(utils): add integration tests for file handling

OUTPUT:
Return ONLY the commit message without markdown or explanation."""
```

### Ollama Generation Parameters (`ollama.py:164-169`)

**Before**:
```python
payload = {
    "model": self.model,
    "prompt": prompt,
    "stream": self.config.stream,
}
```

**After** (add `options` dict):
```python
payload = {
    "model": self.model,
    "prompt": prompt,
    "stream": self.config.stream,
    "options": {
        "temperature": 0.3,    # Focused output (vs default ~0.8)
        "top_p": 0.9,          # Quality sampling
        "top_k": 40,           # Vocabulary control
        "num_predict": 256,    # Allow body generation (vs default 128)
    }
}
```

### CLI Integration

**Add DeepSeek to provider choices** (`cli/main.py`):
```python
@click.option(
    "--provider",
    type=click.Choice(["openai", "anthropic", "gemini", "mistral", "cohere", "deepseek", "ollama"]),
    help="AI provider to use"
)
```

**Config update** (`core/config.py`):
```python
@dataclass
class Config:
    # ... existing fields
    deepseek_api_key: str | None = None

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            # ... existing
            deepseek_api_key=os.getenv("DEEPSEEK_API_KEY"),
        )
```

## Phase 2: Task Generation Plan

Tasks will cover:
1. **Layer 1**: DeepSeek provider (tests → impl → green)
2. **Layer 2**: Ollama prompt improvement (tests → impl → green)
3. **Layer 3**: Ollama generation params (tests → impl → green)
4. **Layer 4**: Documentation (README updates)

Each layer: TDD (tests → impl → green)

## Progress Tracking

- [x] Initial Constitution Check (passed)
- [x] Phase 0: Research (completed, see report)
- [x] Phase 1: Design (completed)
- [ ] Post-Design Constitution Check
- [ ] Phase 2: Task generation (/tasks)
- [ ] Phase 3: TDD Implementation

## Dependencies

**Required from Feature 001:**
- AIProvider base class ✅
- Config system ✅
- CLI infrastructure ✅

**Pattern reuse:**
- DeepSeek = copy OpenAI provider pattern (change URL + env var)
- Ollama improvements = localized changes in existing file

## Unresolved Questions

1. **DeepSeek cache optimization**: Use cache-hit pricing?
   - **Recommendation**: V2 feature (requires prompt caching strategy)

2. **Ollama prompt length**: Will 40-line prompt fit in context?
   - **Recommendation**: Limit file list to 10 files (tested, works)

3. **Model recommendation**: Force qwen2.5:7b or just recommend?
   - **Recommendation**: Just recommend in README (user choice)

4. **DeepSeek model selection**: Support deepseek-coder?
   - **Recommendation**: Yes, add model parameter (default: deepseek-chat)

## Expected Outcomes

### DeepSeek
- ✅ 18x cheaper than GPT-4o
- ✅ OpenAI-compatible (easy integration)
- ✅ Same quality as GPT-4o-mini

### Ollama
- ✅ Body generation: 0% → 80%
- ✅ Scope accuracy: 70% → 90%
- ✅ Overall quality: 8/10 → 9.5/10
- ✅ No speed regression (~5s unchanged)
