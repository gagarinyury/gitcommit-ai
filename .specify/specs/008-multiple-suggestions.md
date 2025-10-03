# Feature Specification: Multiple Commit Message Suggestions

**Feature Branch**: `008-multiple-suggestions`
**Created**: 2025-10-02
**Status**: Draft
**Input**: User description: "Generate multiple commit message options (3-5) and let user pick the best one interactively"

## Execution Status
- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---

## User Scenarios & Testing

### Primary User Story
A developer has made changes and wants to commit them. Instead of accepting a single AI-generated message, they:
1. Run `gitcommit-ai generate --count 3`
2. AI generates 3 different commit message variants with varying styles/detail levels
3. System displays options in an interactive picker
4. User selects their preferred option using arrow keys or number input
5. If none are satisfactory, user can request regeneration
6. Selected message is used for the commit

### Acceptance Scenarios

1. **Given** a git repository with staged changes, **When** user runs `gitcommit-ai generate --count 3`, **Then** system generates exactly 3 distinct commit message options and displays them in an interactive picker

2. **Given** 3 generated suggestions, **When** user presses arrow keys to navigate and Enter to select, **Then** system uses the selected message for the commit

3. **Given** displayed suggestions, **When** user types a number (1-3) and presses Enter, **Then** system uses that numbered suggestion

4. **Given** displayed suggestions, **When** user types 'r' or 'regenerate', **Then** system generates 3 new suggestions

5. **Given** multiple API providers (OpenAI, Anthropic, Ollama), **When** user requests multiple suggestions, **Then** all suggestions come from the same provider (no mixing)

6. **Given** `--count 5` flag, **When** generation starts, **Then** system generates 5 distinct suggestions (configurable count)

7. **Given** `--json` output flag with `--count 3`, **When** suggestions are generated, **Then** system outputs JSON array of all suggestions (no interactive picker)

### Edge Cases
- What happens when user presses Ctrl+C during selection? → Abort gracefully, no commit created
- What if two suggestions are identical? → System validates uniqueness, regenerates duplicates
- How to handle network errors during multi-generation? → Fail gracefully, show partial results if any succeeded
- What about non-interactive environments (CI/CD)? → `--json` mode for programmatic selection
- What if provider doesn't support temperature parameter? → Fall back to sequential requests with slight prompt variations

---

## Requirements

### Functional Requirements

**Core Functionality**
- **FR-136**: System MUST support `--count N` flag to generate N suggestions (default: 1, max: 10)
- **FR-137**: System MUST generate suggestions with varying creativity/detail levels using temperature parameter
- **FR-138**: System MUST ensure all generated suggestions are unique (different type, scope, or description)
- **FR-139**: System MUST display suggestions in an interactive picker with numbered options
- **FR-140**: System MUST allow selection via arrow keys + Enter or direct number input

**Interaction & UX**
- **FR-141**: User MUST be able to regenerate all suggestions by typing 'r' or 'regenerate'
- **FR-142**: System MUST show preview of each suggestion with syntax highlighting (type in color)
- **FR-143**: System MUST indicate current selection with visual marker (→ arrow or highlight)
- **FR-144**: User MUST be able to cancel selection with Ctrl+C (aborts commit process)
- **FR-145**: System MUST show generation progress for multiple suggestions (spinner/progress bar)

**Provider Integration**
- **FR-146**: All providers (OpenAI, Anthropic, Ollama, etc.) MUST support temperature parameter for variety
- **FR-147**: System MUST use same provider for all suggestions in a single generation
- **FR-148**: Temperature values MUST range from 0.3 (focused) to 0.7 (creative) for suggestions
- **FR-149**: If provider fails for any suggestion, system MUST handle gracefully (show partial results)

**JSON Mode**
- **FR-150**: When `--json` flag is set, system MUST output all suggestions as JSON array
- **FR-151**: JSON output MUST include metadata: provider, model, temperature used for each
- **FR-152**: JSON mode MUST skip interactive picker (for programmatic use)

**Configuration**
- **FR-153**: User MUST be able to set default suggestion count via config file
- **FR-154**: User MUST be able to customize temperature range via config
- **FR-155**: System MUST remember last selected option style (if user prefers short/detailed)

**Statistics Integration**
- **FR-156**: System MUST log which suggestion was selected (for analytics)
- **FR-157**: Statistics MUST track selection patterns (which types/styles users prefer)

### Key Entities

- **SuggestionSet**: Collection of generated commit messages with metadata
  - `suggestions`: list[CommitMessage]
  - `provider`: str (which AI provider generated them)
  - `temperatures`: list[float] (temperature used for each)
  - `generation_time_ms`: int

- **SuggestionSelector**: Interactive picker for user selection
  - `current_index`: int (currently highlighted option)
  - `suggestions`: SuggestionSet
  - `selected`: Optional[CommitMessage]

- **GenerationStrategy**: How to generate multiple suggestions
  - `strategy_type`: Literal["temperature", "parallel", "prompt_variation"]
  - `count`: int
  - `temperature_range`: tuple[float, float]

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
- [x] Scope is clearly bounded (multiple suggestions, not multi-AI comparison)
- [x] Dependencies and assumptions identified (requires temperature support in providers)

---

## Out of Scope (for MVP)

- AI comparison mode (generating suggestions from multiple providers simultaneously)
- Advanced selection criteria (filter by type, sort by confidence score)
- Machine learning to predict user's preferred style
- Collaborative selection (team voting on commit messages)
- Editing suggestions before committing (separate feature)
- Voice/speech selection interface

---

## Competitive Analysis

**aicommits** (8.7k ⭐):
- Uses `--generate N` flag
- Simple numbered list selection
- No temperature control (just parallel API calls)

**opencommit** (6.9k ⭐):
- Interactive arrow-key picker
- Shows checkmark on selected
- No regeneration option

**ai-commit** (462 ⭐):
- Basic numbered selection
- No interactive mode
- Manual typing of choice number

**Our advantage**:
- Temperature-based variety (smarter than parallel calls)
- Regeneration option
- JSON mode for automation
- Statistics tracking
- Better UX (arrow keys + numbers)

---

## Success Metrics

- **Adoption**: 70%+ of users try `--count` flag within first week
- **Engagement**: Average 2.5 suggestions per generation (users explore options)
- **Efficiency**: <500ms overhead compared to single generation
- **Satisfaction**: User survey shows 4.5/5 rating for feature usefulness
- **API Cost**: <2x cost increase compared to single generation (via temperature strategy)
