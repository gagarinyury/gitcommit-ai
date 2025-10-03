# Tasks: Commit Statistics & Analytics

**Prerequisites**: plan.md ✅, Feature 001 ✅

## Phase 3.2: Tests (TDD)
- [ ] **T114** Test StatsDatabase CRUD in `tests/unit/test_stats_db.py`
- [ ] **T115** Test StatsAggregator in `tests/unit/test_aggregator.py`
- [ ] **T116** Test StatsExporter in `tests/unit/test_exporter.py`
- [ ] **T117** Test `stats` CLI command in `tests/unit/test_cli_stats.py`

## Phase 3.3: Implementation
- [ ] **T118** Implement StatsDatabase in `src/gitcommit_ai/stats/database.py`
- [ ] **T119** Implement StatsAggregator in `src/gitcommit_ai/stats/aggregator.py`
- [ ] **T120** Implement StatsExporter in `src/gitcommit_ai/stats/exporter.py`
- [ ] **T121** Add `stats` command to CLI (`src/gitcommit_ai/cli/main.py`)
- [ ] **T122** Add logging to `generate` command (log after successful generation)

## Phase 3.4: Polish
- [ ] **T123** Auto-cleanup old records (>90 days)
- [ ] **T124** Update README with stats usage
- [ ] **T125** Manual test: generate 10 commits, check stats

**Total**: 12 tasks (T114-T125)
