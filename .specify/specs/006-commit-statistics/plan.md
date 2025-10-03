# Implementation Plan: Commit Statistics & Analytics

**Branch**: `006-commit-statistics` | **Date**: 2025-10-02 | **Spec**: [006-commit-statistics.md](../006-commit-statistics.md)

## Summary
Track AI commit generation metadata (provider, model, response time, success rate) in local SQLite database. Provide `stats` command for analytics, filtering, and export (CSV/JSON). Privacy-focused: no code content stored, only metadata.

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: sqlite3 (stdlib)
**Storage**: `~/.gitcommit-ai/stats.db` (SQLite)
**Testing**: pytest with temp database
**Project Type**: Single (extends CLI)
**Performance Goals**: <100ms for queries, <10ms for logging
**Constraints**: Max 10MB database size, 90-day retention
**Scale/Scope**: Local machine only (no sync)

## Constitution Check
✅ All principles satisfied. Library-first (stats/ module), CLI command, TDD, simple (sqlite3 stdlib).

## Project Structure
```
src/gitcommit_ai/
├── stats/
│   ├── __init__.py
│   ├── database.py      # [NEW] SQLite wrapper
│   ├── aggregator.py    # [NEW] Stats computation
│   └── exporter.py      # [NEW] CSV/JSON export
└── cli/
    └── main.py          # [MODIFY] Add stats command

tests/
└── unit/
    ├── test_stats_db.py
    ├── test_aggregator.py
    └── test_exporter.py
```

## Database Schema
```sql
CREATE TABLE commit_records (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT,
    commit_type TEXT,
    success INTEGER NOT NULL,
    response_time_ms INTEGER,
    diff_lines INTEGER
);
```

## Tasks Summary
- T114-T120: Tests (database, aggregator, exporter, CLI)
- T121-T125: Implementation (database, aggregator, exporter, CLI, logging)
- T126-T128: Polish (cleanup, docs, manual test)

Total: 15 tasks

## Dependencies
Requires Feature 001 (CLI, generate command) to log stats during generation.
