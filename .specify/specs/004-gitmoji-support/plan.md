# Implementation Plan: Gitmoji Support

**Branch**: `004-gitmoji-support` | **Date**: 2025-10-02 | **Spec**: [004-gitmoji-support.md](../004-gitmoji-support.md)

## Summary
Add emoji support to commit messages using gitmoji standard. Maps conventional commit types (feat, fix, docs) to visual emojis (✨, 🐛, 📝). Configurable via CLI flag or persistent config.

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: Standard library only (no emoji library needed, use raw UTF-8)
**Storage**: Config file for persistent settings
**Testing**: pytest with emoji validation tests
**Target Platform**: Linux/macOS (UTF-8 terminals)
**Project Type**: Single (extends message formatting)
**Performance Goals**: Zero overhead (<1ms emoji mapping)
**Constraints**: Terminal UTF-8 support required
**Scale/Scope**: 10 standard emoji mappings, extensible to custom

## Constitution Check

### ✅ Library-First Architecture
- `src/gitcommit_ai/gitmoji/mapper.py` - emoji mapping logic
- `src/gitcommit_ai/gitmoji/validator.py` - UTF-8 validation
- Independent of CLI/config

### ✅ CLI Interface Mandate
- `gitcommit-ai generate --gitmoji` (one-time)
- `gitcommit-ai generate --no-gitmoji` (disable)
- Exit codes unchanged

### ✅ Test-First Development
- Tests for emoji mapping
- Tests for UTF-8 validation
- Tests for config integration

### ✅ Integration Testing Priority
- Generate with --gitmoji flag
- Config persistence
- Terminal compatibility

### ✅ Simplicity & YAGNI
- No external emoji library
- Simple dict-based mapping
- No complex rendering logic

**Complexity Tracking**: None. Simple feature using Python's native UTF-8 support.

## Project Structure

### Documentation
```
.specify/specs/004-gitmoji-support/
├── plan.md
├── tasks.md
└── gitmoji-table.md  # Reference table
```

### Source Code
```
src/gitcommit_ai/
├── gitmoji/
│   ├── __init__.py
│   ├── mapper.py            # [NEW] GitmojiMapper class
│   └── validator.py         # [NEW] Terminal UTF-8 check
├── generator/
│   └── message.py           # [MODIFY] Add emoji field
└── cli/
    └── main.py              # [MODIFY] Add --gitmoji flag

tests/
└── unit/
    ├── test_gitmoji_mapper.py    # [NEW]
    └── test_gitmoji_validator.py # [NEW]
```

## Design

### Emoji Mapping (`mapper.py`)
```python
GITMOJI_MAP = {
    "feat": "✨",
    "fix": "🐛",
    "docs": "📝",
    "style": "🎨",
    "refactor": "♻️",
    "test": "✅",
    "chore": "🔧",
    "perf": "🚀",
    "security": "🔒",
}

class GitmojiMapper:
    @staticmethod
    def get_emoji(commit_type: str) -> str | None:
        """Get emoji for commit type."""
        return GITMOJI_MAP.get(commit_type)

    @staticmethod
    def format_message(message: CommitMessage, use_gitmoji: bool) -> str:
        """Format message with optional emoji prefix."""
        if use_gitmoji:
            emoji = GitmojiMapper.get_emoji(message.type)
            if emoji:
                return f"{emoji} {message.format()}"
        return message.format()
```

### Message Model Update
```python
@dataclass
class CommitMessage:
    type: str
    scope: str | None
    description: str
    body: str | None
    breaking_changes: list[str]
    emoji: str | None = None  # [NEW]

    def format(self, with_emoji: bool = False) -> str:
        """Format conventional commit."""
        base = f"{self.type}"
        if self.scope:
            base += f"({self.scope})"
        base += f": {self.description}"

        if with_emoji and self.emoji:
            return f"{self.emoji} {base}"
        return base
```

## Tasks Breakdown

### Phase 1: Tests (RED)
- T085-T090: Gitmoji mapper tests (6 tests)
- T091-T092: Validator tests (2 tests)
- T093-T094: CLI integration tests (2 tests)

### Phase 2: Implementation (GREEN)
- T095: Implement GitmojiMapper
- T096: Implement validator
- T097: Update CommitMessage model
- T098: Update CLI with --gitmoji flag

### Phase 3: Polish
- T099: Update README
- T100: Add gitmoji table doc

## Dependencies

**Required from Features 001-003:**
- CommitMessage dataclass
- CLI infrastructure
- Config system (for persistent gitmoji setting)

## Unresolved Questions

1. **Config format**: TOML vs JSON?
   - **Recommendation**: Reuse existing config system

2. **Breaking change emoji**: 💥 prefix or replace type emoji?
   - **Recommendation**: Add 💥 prefix: `💥 feat!: breaking change`

3. **Terminal detection**: How to check UTF-8 support?
   - **Recommendation**: Check `sys.stdout.encoding == 'utf-8'`
