# Tasks: Gitmoji Support

**Prerequisites**: plan.md ✅, Features 001-003 ✅

## Phase 3.2: Tests (TDD - RED)

- [ ] **T085** Test gitmoji mapping in `tests/unit/test_gitmoji_mapper.py`:
  - feat → ✨
  - fix → 🐛
  - docs → 📝
  - Unknown type → None
- [ ] **T086** [P] Test format_message with gitmoji enabled
- [ ] **T087** [P] Test format_message with gitmoji disabled
- [ ] **T088** [P] Test custom emoji mappings (if configured)
- [ ] **T089** [P] Test breaking change emoji (💥)
- [ ] **T090** [P] Test emoji in JSON output

- [ ] **T091** Test UTF-8 validation in `tests/unit/test_gitmoji_validator.py`:
  - Terminal supports UTF-8 → True
  - Terminal doesn't support UTF-8 → False
- [ ] **T092** [P] Test fallback behavior when UTF-8 unsupported

- [ ] **T093** Test CLI --gitmoji flag in `tests/unit/test_cli.py`
- [ ] **T094** [P] Test CLI --no-gitmoji flag

## Phase 3.3: Implementation (GREEN)

- [ ] **T095** Implement GitmojiMapper in `src/gitcommit_ai/gitmoji/mapper.py`:
  - GITMOJI_MAP dictionary
  - get_emoji(type) method
  - format_message() method
- [ ] **T096** Implement validator in `src/gitcommit_ai/gitmoji/validator.py`:
  - supports_utf8() function
- [ ] **T097** Update CommitMessage in `src/gitcommit_ai/generator/message.py`:
  - Add emoji field (optional)
  - Add format(with_emoji=False) parameter
- [ ] **T098** Update CLI in `src/gitcommit_ai/cli/main.py`:
  - Add --gitmoji flag
  - Add --no-gitmoji flag
  - Apply emoji when flag set

## Phase 3.4: Polish

- [ ] **T099** Update README with gitmoji examples
- [ ] **T100** Create gitmoji reference table in `.specify/specs/004-gitmoji-support/gitmoji-table.md`

**Total**: 16 tasks (T085-T100)
