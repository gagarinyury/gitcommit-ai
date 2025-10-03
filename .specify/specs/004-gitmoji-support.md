# Feature Specification: Gitmoji Support

**Feature Branch**: `004-gitmoji-support`
**Created**: 2025-10-02
**Status**: Draft
**Priority**: Medium (visual appeal + community standard)

## User Scenarios & Testing

### Primary User Story
A developer wants commit messages with emojis that visually indicate the type of change (✨ new feature, 🐛 bug fix, 📝 docs). They enable gitmoji mode and all generated messages include appropriate emojis.

### Acceptance Scenarios

1. **Given** gitmoji enabled, **When** AI detects new feature, **Then** message is `✨ feat: add authentication`

2. **Given** gitmoji enabled, **When** AI detects bug fix, **Then** message is `🐛 fix: resolve memory leak`

3. **Given** gitmoji disabled (default), **When** message generated, **Then** no emoji: `feat: add authentication`

4. **Given** user runs `gitcommit-ai generate --gitmoji`, **Then** single use of gitmoji (doesn't persist)

5. **Given** user runs `gitcommit-ai config set gitmoji true`, **Then** gitmoji enabled globally

### Edge Cases
- What if AI suggests wrong emoji? → User can edit in interactive mode
- Multiple types in one commit? → Use primary type's emoji
- Custom emoji mappings? → Support via config file
- Breaking changes? → Use 💥 prefix

## Requirements

### Functional Requirements

**Core Functionality**
- **FR-059**: System MUST map conventional commit types to gitmoji codes
- **FR-060**: System MUST prepend emoji to commit message when enabled
- **FR-061**: System MUST support `--gitmoji` flag for one-time use
- **FR-062**: System MUST support persistent gitmoji via config

**Emoji Mapping**
- **FR-063**: System MUST use standard gitmoji mappings:
  - ✨ (sparkles) → feat
  - 🐛 (bug) → fix
  - 📝 (memo) → docs
  - 🎨 (art) → style
  - ♻️ (recycle) → refactor
  - ✅ (check) → test
  - 🔧 (wrench) → chore
  - 💥 (boom) → breaking change
  - 🚀 (rocket) → perf
  - 🔒 (lock) → security

**Configuration**
- **FR-064**: System MUST allow custom emoji mappings in config file
- **FR-065**: System MUST support `--no-gitmoji` flag to disable temporarily
- **FR-066**: Config format: `gitmoji.mapping.feat = "🚀"` (override)

**Output Formats**
- **FR-067**: Human-readable: `✨ feat(auth): add JWT support`
- **FR-068**: JSON output includes emoji separately: `{"emoji": "✨", "type": "feat", ...}`
- **FR-069**: Git log compatibility: emoji should be UTF-8 compatible

**Validation**
- **FR-070**: System MUST validate emoji codes (Unicode)
- **FR-071**: System MUST fallback to no-emoji if terminal doesn't support UTF-8

### Key Entities

- **GitmojiMapper**: Maps commit types to emoji codes
- **GitmojiConfig**: Stores enabled state and custom mappings
- **EmojiValidator**: Checks terminal UTF-8 support

---

## Gitmoji Reference Table

| Type | Emoji | Code | Description |
|------|-------|------|-------------|
| feat | ✨ | `:sparkles:` | New feature |
| fix | 🐛 | `:bug:` | Bug fix |
| docs | 📝 | `:memo:` | Documentation |
| style | 🎨 | `:art:` | Formatting |
| refactor | ♻️ | `:recycle:` | Code restructure |
| perf | 🚀 | `:rocket:` | Performance |
| test | ✅ | `:white_check_mark:` | Tests |
| chore | 🔧 | `:wrench:` | Maintenance |
| ci | 👷 | `:construction_worker:` | CI/CD |
| build | 📦 | `:package:` | Build system |
| breaking | 💥 | `:boom:` | Breaking change |
| security | 🔒 | `:lock:` | Security fix |

---

## Configuration Example

```toml
# ~/.gitcommit-ai/config.toml
[gitmoji]
enabled = true

[gitmoji.mapping]
feat = "🚀"  # Override default ✨ with 🚀
fix = "🔥"   # Override default 🐛 with 🔥
```

---

## Technical Constraints

- Emoji rendering depends on terminal font (some don't support all emoji)
- Git supports UTF-8 in commit messages by default
- GitHub/GitLab/Bitbucket all display emoji correctly
- Some CI/CD logs may show raw Unicode (acceptable)

---

## Out of Scope (for MVP)

- Interactive emoji picker
- Emoji search (`:bug:` → 🐛)
- Multiple emoji per commit
- Emoji in commit body (only first line)
- Custom emoji images (only Unicode)

---

## Success Criteria

- ✅ Standard gitmoji mappings implemented
- ✅ `--gitmoji` flag works
- ✅ Persistent config option works
- ✅ Messages display correctly in GitHub/GitLab
- ✅ Fallback for non-UTF-8 terminals
