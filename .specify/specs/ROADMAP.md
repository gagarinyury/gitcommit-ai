# GitCommit AI - Product Roadmap

**Updated**: 2025-10-02
**Status**: Active Development

---

## 🎯 Vision

Make GitCommit AI the **#1 AI-powered commit message tool** by combining:
- 🆓 Free local models (Ollama)
- 🤖 Automation (Git hooks + GitHub Actions)
- 🎨 Beautiful output (Gitmoji)
- 📊 Insights (Statistics)
- 🌐 Choice (6+ AI providers)

---

## ✅ Phase 1: MVP (COMPLETED)

**Status**: ✅ Done (100%)
**Release**: v0.1.0

### Features
- ✅ OpenAI & Anthropic support
- ✅ Conventional commits format
- ✅ CLI with JSON output
- ✅ Git diff parsing
- ✅ Test coverage (69 tests)
- ✅ Python 3.11+ support

---

## 🚀 Phase 2: Feature Parity (PLANNED)

**Target**: Q1 2026
**Goal**: Match feature set of top competitors (aicommits, aicommit2)

### Feature 002: Ollama Support ⭐ Priority: HIGH
**Spec**: [002-ollama-support.md](./002-ollama-support.md)
**Why**: Free local AI models = zero API costs
**Requirements**: FR-021 to FR-039 (19 requirements)

**Key Deliverables:**
- Ollama provider implementation
- Model detection & validation
- Progress indicators for slow models
- Offline mode support

**Success Metrics:**
- Users can run `--provider ollama` without API keys
- Works completely offline
- <10s response time for medium models

---

### Feature 003: Git Hooks Integration ⭐ Priority: HIGH
**Spec**: [003-git-hooks.md](./003-git-hooks.md)
**Why**: Automation = killer feature (aicommits has 8.7k stars because of this)
**Requirements**: FR-040 to FR-058 (19 requirements)

**Key Deliverables:**
- `install-hooks` command
- `prepare-commit-msg` hook script
- Error handling (don't block commits)
- Uninstall command

**Success Metrics:**
- One-command install
- Automatic generation on `git commit`
- User can edit/abort in editor

---

### Feature 004: Gitmoji Support ⭐ Priority: MEDIUM
**Spec**: [004-gitmoji-support.md](./004-gitmoji-support.md)
**Why**: Visual appeal + community standard
**Requirements**: FR-059 to FR-071 (13 requirements)

**Key Deliverables:**
- Standard gitmoji mappings
- `--gitmoji` flag
- Custom emoji config
- UTF-8 validation

**Success Metrics:**
- ✨ feat: messages render correctly
- Configurable via config file
- Works on GitHub/GitLab

---

### Feature 005: More AI Providers ⭐ Priority: MEDIUM
**Spec**: [005-more-ai-providers.md](./005-more-ai-providers.md)
**Why**: Wider choice = more users
**Requirements**: FR-072 to FR-091 (20 requirements)

**Key Deliverables:**
- Google Gemini support
- Mistral AI support
- Cohere support
- `providers list` command

**Success Metrics:**
- 6 total providers (OpenAI, Anthropic, Gemini, Mistral, Cohere, Ollama)
- Easy provider switching
- Clear status indicators

---

### Feature 006: Commit Statistics ⭐ Priority: LOW
**Spec**: [006-commit-statistics.md](./006-commit-statistics.md)
**Why**: Insights = engagement
**Requirements**: FR-092 to FR-113 (22 requirements)

**Key Deliverables:**
- SQLite stats database
- `stats` command
- CSV/JSON export
- Provider comparison

**Success Metrics:**
- Tracks 1000+ commits without performance issues
- Privacy preserved (no code content)
- Useful insights displayed

---

### Feature 007: GitHub Action ⭐ Priority: MEDIUM
**Spec**: [007-github-action.md](./007-github-action.md)
**Why**: CI/CD automation for teams
**Requirements**: FR-114 to FR-135 (22 requirements)

**Key Deliverables:**
- GitHub Action published to Marketplace
- Commit validation in PRs
- AI suggestions as PR comments
- Auto-fix mode

**Success Metrics:**
- <2 min execution time
- 100+ teams using in production
- 4.5+ star rating on Marketplace

---

## 📊 Feature Summary

| Feature | Priority | Requirements | Estimated Effort | Value |
|---------|----------|--------------|------------------|-------|
| 002: Ollama | HIGH | 19 | 3 days | ⭐⭐⭐⭐⭐ Free = huge |
| 003: Git Hooks | HIGH | 19 | 2 days | ⭐⭐⭐⭐⭐ Automation wins |
| 004: Gitmoji | MEDIUM | 13 | 1 day | ⭐⭐⭐ Visual appeal |
| 005: More AI | MEDIUM | 20 | 4 days | ⭐⭐⭐⭐ More choice |
| 006: Statistics | LOW | 22 | 3 days | ⭐⭐ Nice-to-have |
| 007: GitHub Action | MEDIUM | 22 | 5 days | ⭐⭐⭐⭐ Teams love it |

**Total**: 115 new requirements, ~18 days effort

---

## 🎯 Recommended Implementation Order

### Sprint 1 (Week 1-2)
1. **Feature 002: Ollama** — Enables free usage (huge value)
2. **Feature 003: Git Hooks** — Automation is critical for adoption

### Sprint 2 (Week 3-4)
3. **Feature 005: More Providers** — Gemini/Mistral/Cohere
4. **Feature 004: Gitmoji** — Quick win, visual impact

### Sprint 3 (Week 5-6)
5. **Feature 007: GitHub Action** — For teams
6. **Feature 006: Statistics** — Polish feature

---

## 🏆 Success Criteria (Phase 2 Complete)

- [ ] 1,000+ GitHub stars (vs aicommits' 8,700)
- [ ] 500+ weekly downloads on PyPI
- [ ] 6 AI providers supported
- [ ] <2s average response time
- [ ] 95%+ test coverage maintained
- [ ] Featured on GitHub Trending
- [ ] Mentioned in AI tooling articles

---

## 📝 Next Steps

1. **Review Specs** — Validate requirements with team
2. **Prioritize** — Confirm Ollama + Git Hooks first
3. **Create Plans** — Run `/plan` for each feature
4. **Break into Tasks** — Run `/tasks` for implementation
5. **Implement** — TDD for each feature
6. **Release** — v0.2.0 with Ollama + Hooks

---

## 🤝 Contributing

Want to implement a feature? See individual specs for detailed requirements:

- [002-ollama-support.md](./002-ollama-support.md)
- [003-git-hooks.md](./003-git-hooks.md)
- [004-gitmoji-support.md](./004-gitmoji-support.md)
- [005-more-ai-providers.md](./005-more-ai-providers.md)
- [006-commit-statistics.md](./006-commit-statistics.md)
- [007-github-action.md](./007-github-action.md)

Each spec follows **Spec-Driven Development** methodology — implement with confidence! 🚀
