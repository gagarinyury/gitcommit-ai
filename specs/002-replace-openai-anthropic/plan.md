
# Implementation Plan: Add OpenRouter Provider, Remove Mistral/Cohere

**Branch**: `002-replace-openai-anthropic` | **Date**: 2025-10-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-replace-openai-anthropic/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
**Primary Requirement**: Replace Mistral and Cohere direct provider implementations with a single OpenRouter provider that provides unified access to 100+ AI models (including Mistral, Cohere, OpenAI, Anthropic, Gemini, and others) through one API key.

**Scope**:
- Add OpenRouter provider (OpenAI-compatible API)
- Remove Mistral and Cohere provider implementations
- Keep all existing providers (OpenAI, Anthropic, Gemini, DeepSeek, Ollama) for fallback/choice
- Maintain 100% backward compatibility for existing users
- No automatic fallback - users manually select provider on failure

**Value**: Simplified configuration (1 key for 100+ models), reduced codebase (2 fewer providers), preserved user choice (all major providers still available)

## Technical Context
**Language/Version**: Python 3.11+ (leveraging async/await, type hints)
**Primary Dependencies**: httpx (HTTP client for async API calls), python-dotenv (environment configuration)
**Storage**: N/A (stateless CLI tool, optional SQLite for stats tracking)
**Testing**: pytest, pytest-asyncio, pytest-mock (273 existing tests must pass)
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)
**Project Type**: Single project (CLI tool with library core)
**Performance Goals**: <2s commit message generation (API latency dependent), support for 1000+ line diffs
**Constraints**: Backward compatibility (no breaking changes), minimal dependencies (stdlib preferred), provider abstraction maintained
**Scale/Scope**: 6 AI providers → 5 (remove 2, add 1), ~15K LOC total, maintain 273+ tests

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. Library-First Architecture**: ✅ PASS
- OpenRouter provider will be standalone library (`src/gitcommit_ai/providers/openrouter.py`)
- Reusable interface inheriting from `AIProvider` base class
- Self-contained, independently testable

**II. CLI Interface Mandate**: ✅ PASS
- Accessible via `gitcommit-ai generate --provider openrouter --model <model>`
- JSON output supported (`--json` flag)
- Text-based error messages to stderr
- Exit codes: 0 = success, non-zero = failure

**III. Test-First Development**: ✅ PASS (TDD mandatory)
- Write failing tests first for OpenRouter provider
- Write failing tests for Mistral/Cohere removal
- All 273 existing tests must remain green
- New tests for OpenRouter integration

**IV. Integration Testing Priority**: ✅ PASS
- Real OpenRouter API integration tests (similar to existing provider tests)
- E2E CLI workflow tests with OpenRouter
- Backward compatibility tests (existing providers still work)

**V. Simplicity and YAGNI**: ✅ PASS
- Reuse existing provider abstraction (no new patterns)
- OpenRouter provider follows same structure as OpenAI (OpenAI-compatible API)
- Remove unused code (Mistral, Cohere providers)
- Minimal changes to core architecture

**Technology Constraints**: ✅ PASS
- Python 3.11+ (existing requirement)
- httpx for HTTP (already used)
- No new dependencies required
- Provider abstraction already exists

**Violations**: NONE

**Constitution Version**: 1.0.0

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/gitcommit_ai/
├── providers/
│   ├── base.py                    # AIProvider abstract base class
│   ├── openai.py                  # ✅ Keep (fallback option)
│   ├── anthropic.py               # ✅ Keep (fallback option)
│   ├── gemini.py                  # ✅ Keep (fallback option)
│   ├── deepseek.py                # ✅ Keep (cheapest option)
│   ├── ollama.py                  # ✅ Keep (default, free, local)
│   ├── openrouter.py              # 🆕 ADD (new unified provider)
│   ├── mistral.py                 # ❌ REMOVE
│   ├── cohere.py                  # ❌ REMOVE
│   └── registry.py                # ⚠️ UPDATE (add openrouter, remove mistral/cohere)
├── cli/
│   ├── main.py                    # ⚠️ UPDATE (provider help text)
│   └── setup.py                   # OpenRouter setup wizard (optional)
├── core/
│   └── config.py                  # ⚠️ UPDATE (OPENROUTER_API_KEY env var)
└── prompts/
    └── openrouter.md              # 🆕 ADD (prompt template)

tests/
├── unit/
│   ├── test_openrouter.py         # 🆕 ADD (unit tests)
│   ├── test_mistral.py            # ❌ REMOVE
│   ├── test_cohere.py             # ❌ REMOVE
│   └── test_registry.py           # ⚠️ UPDATE
├── e2e/
│   └── test_real_providers.py     # ⚠️ UPDATE (add OpenRouter, remove Mistral/Cohere)
└── integration/
    └── test_cli_e2e.py            # ⚠️ UPDATE (provider list tests)
```

**Structure Decision**: Single project (CLI tool). Core library in `src/gitcommit_ai/`, tests mirror source structure. OpenRouter provider follows same pattern as existing providers (inherits from `AIProvider`, implements async `generate_commit_message()`). No architectural changes needed.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
1. **From contracts/openrouter-api.yaml**:
   - Task: Write failing contract test for OpenRouter API request format
   - Task: Write failing contract test for OpenRouter API response parsing
   - Task: Write failing contract test for error responses (401, 429, 503)

2. **From data-model.md**:
   - Task: Write failing test for OpenRouterProvider initialization
   - Task: Write failing test for model name validation (regex)
   - Task: Write failing test for API key validation

3. **From quickstart.md test scenarios**:
   - Task: Write failing E2E test for basic commit generation via OpenRouter
   - Task: Write failing E2E test for multiple model support
   - Task: Write failing integration test for error message formatting
   - Task: Write failing integration test for provider list command

4. **Implementation tasks** (TDD - make tests green):
   - Task: Implement OpenRouterProvider class (inherit from AIProvider)
   - Task: Implement model name validation logic
   - Task: Implement API request formatting (OpenAI-compatible)
   - Task: Implement response parsing (extract commit message)
   - Task: Implement error handling (401, 429, 503)
   - Task: Add OpenRouter to registry.py
   - Task: Create prompts/openrouter.md template

5. **Removal tasks**:
   - Task: Remove Mistral provider (mistral.py, test_mistral.py)
   - Task: Remove Cohere provider (cohere.py, test_cohere.py)
   - Task: Update registry.py (remove mistral/cohere entries)
   - Task: Update CLI help text (remove mistral/cohere from --provider options)

6. **Documentation tasks**:
   - Task: Update README.md (add OpenRouter, mark Mistral/Cohere as deprecated)
   - Task: Update .env.example (add OPENROUTER_API_KEY)
   - Task: Create migration guide for Mistral/Cohere users

7. **Validation tasks**:
   - Task: Run all 273 existing tests (ensure backward compatibility)
   - Task: Run new OpenRouter tests (ensure feature works)
   - Task: Manual smoke test (try all providers)

**Ordering Strategy**:
- TDD strictly enforced: All tests before implementation
- Contract tests first (API shape)
- Unit tests second (logic)
- Integration tests third (CLI workflow)
- Implementation fourth (make tests green)
- Removal fifth (delete old code)
- Documentation sixth (update guides)
- Validation last (full test suite)

**Parallelization Markers**:
- [P] Contract tests (independent)
- [P] Unit tests (independent)
- [P] Provider removal (independent files)
- [S] Sequential: Implementation depends on tests, docs depend on implementation

**Estimated Output**: ~35 tasks in dependency order

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) ✅
- [x] Phase 1: Design complete (/plan command) ✅
- [x] Phase 2: Task planning complete (/plan command - describe approach only) ✅
- [x] Phase 3: Tasks generated (/tasks command) ✅ **42 tasks ready**
- [ ] Phase 4: Implementation complete ⏭️ NEXT STEP (execute tasks.md)
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS ✅
- [x] Post-Design Constitution Check: PASS ✅
- [x] All NEEDS CLARIFICATION resolved ✅
- [x] Complexity deviations documented (NONE) ✅

**Artifacts Generated**:
- [x] research.md (Phase 0)
- [x] data-model.md (Phase 1)
- [x] contracts/openrouter-api.yaml (Phase 1)
- [x] quickstart.md (Phase 1)
- [x] CLAUDE.md updated (Phase 1)
- [x] tasks.md (Phase 3) **42 tasks, TDD enforced**

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
