# Tasks: Git Hooks Integration

**Prerequisites**: plan.md ✅, Feature 001 ✅

## Phase 3.2: Tests (TDD)

- [ ] **T075** [P] Test hook template generation in `tests/unit/test_hook_template.py`
- [ ] **T076** [P] Test HookManager.install() in `tests/unit/test_hook_manager.py`
- [ ] **T077** [P] Test HookManager.uninstall() in `tests/unit/test_hook_manager.py`
- [ ] **T078** [P] Test hook detection in `tests/unit/test_hook_manager.py` (is_installed)
- [ ] **T079** Test hook execution in `tests/integration/test_hooks_e2e.py` (temp repo + actual hook)

## Phase 3.3: Implementation

- [ ] **T080** Create hook script template in `src/gitcommit_ai/hooks/template.py`
- [ ] **T081** Implement HookManager in `src/gitcommit_ai/hooks/manager.py`
- [ ] **T082** Add CLI commands in `src/gitcommit_ai/cli/main.py`:
  - `install-hooks [--force]`
  - `uninstall-hooks [--force]`
  - `debug-hooks`

## Phase 3.4: Polish

- [ ] **T083** [P] Update README with hooks usage
- [ ] **T084** Manual test: install hooks, run `git commit`, verify editor opens with AI message

**Total**: 10 tasks (T075-T084)
