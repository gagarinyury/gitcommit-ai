# Feature Specification: Commit Statistics & Analytics

**Feature Branch**: `006-commit-statistics`
**Created**: 2025-10-02
**Status**: Draft
**Priority**: Low (nice-to-have, not critical)

## User Scenarios & Testing

### Primary User Story
A developer wants to track their commit quality over time: how many AI-generated commits they've used, which providers are fastest, and trends in commit types. They run `gitcommit-ai stats` to see analytics.

### Acceptance Scenarios

1. **Given** 50 commits generated, **When** user runs `gitcommit-ai stats`, **Then** system shows: total commits, provider breakdown, average response time

2. **Given** statistics enabled, **When** commit is generated, **Then** metadata is logged: timestamp, provider, model, response time, diff size

3. **Given** user runs `gitcommit-ai stats --provider openai`, **Then** system shows OpenAI-specific stats only

4. **Given** user runs `gitcommit-ai stats --period 30d`, **Then** system shows last 30 days statistics

5. **Given** user runs `gitcommit-ai stats --export csv`, **Then** system exports data to stats.csv

### Edge Cases
- Large history (1000+ commits)? → Paginate or aggregate
- Privacy concerns? → Allow disabling stats collection
- Storage limits? → Rotate old logs (keep 90 days)
- Multiple machines? → Per-machine stats (no sync)

## Requirements

### Functional Requirements

**Data Collection**
- **FR-092**: System MUST log each commit generation attempt to local database
- **FR-093**: System MUST record: timestamp, provider, model, success/failure, response time, diff size
- **FR-094**: System MUST allow disabling stats via `--no-stats` flag or config
- **FR-095**: System MUST anonymize data (no code content, only metadata)

**Statistics Display**
- **FR-096**: System MUST provide `stats` command showing summary
- **FR-097**: System MUST show: total commits, success rate, average response time
- **FR-098**: System MUST break down by provider (OpenAI: 30, Anthropic: 20, Ollama: 10)
- **FR-099**: System MUST show commit type distribution (feat: 40%, fix: 30%, docs: 20%, etc.)
- **FR-100**: System MUST show trends: commits per day/week/month

**Filtering & Querying**
- **FR-101**: System MUST support `--provider` filter
- **FR-102**: System MUST support `--period` filter (7d, 30d, 90d, all)
- **FR-103**: System MUST support `--type` filter (feat, fix, etc.)
- **FR-104**: System MUST support date range: `--from 2025-01-01 --to 2025-03-31`

**Export**
- **FR-105**: System MUST support `--export csv` to export raw data
- **FR-106**: System MUST support `--export json` for programmatic access
- **FR-107**: CSV format: timestamp,provider,model,type,success,response_time_ms,diff_lines

**Insights**
- **FR-108**: System MUST show "fastest provider" based on average response time
- **FR-109**: System MUST show "most reliable provider" based on success rate
- **FR-110**: System MUST show "busiest day" (most commits)

**Storage**
- **FR-111**: System MUST store stats in SQLite database at ~/.gitcommit-ai/stats.db
- **FR-112**: System MUST auto-cleanup logs older than 90 days
- **FR-113**: System MUST limit database size to 10MB (rotate if exceeded)

### Key Entities

- **CommitRecord**: Single commit metadata entry
- **StatsDatabase**: SQLite wrapper for queries
- **StatsAggregator**: Computes summary statistics
- **StatsExporter**: Exports to CSV/JSON

---

## Database Schema

```sql
CREATE TABLE commit_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    provider TEXT NOT NULL,
    model TEXT,
    commit_type TEXT,
    success BOOLEAN NOT NULL,
    response_time_ms INTEGER,
    diff_lines INTEGER,
    error_message TEXT
);

CREATE INDEX idx_timestamp ON commit_history(timestamp);
CREATE INDEX idx_provider ON commit_history(provider);
```

---

## Example Output

```bash
$ gitcommit-ai stats

📊 GitCommit AI Statistics (Last 30 days)

Total Commits Generated: 127
Success Rate: 98.4% (125 succeeded, 2 failed)
Average Response Time: 2.3s

By Provider:
  OpenAI    : 80 commits (63%) - avg 1.8s
  Anthropic : 35 commits (28%) - avg 2.5s
  Ollama    : 12 commits (9%)  - avg 8.2s

By Type:
  feat      : 52 commits (41%)
  fix       : 38 commits (30%)
  docs      : 20 commits (16%)
  refactor  : 17 commits (13%)

Trends:
  Busiest Day: 2025-09-15 (18 commits)
  Commits per Day: 4.2 average

⚡ Fastest Provider: OpenAI (1.8s avg)
✅ Most Reliable: Anthropic (100% success)
```

---

## Out of Scope (for MVP)

- Cloud sync (stats are local only)
- Team-wide analytics
- Visual charts (terminal only, no GUI)
- Real-time dashboards
- ML insights ("you commit more on Mondays")

---

## Success Criteria

- ✅ Stats logging works automatically
- ✅ `stats` command displays useful summary
- ✅ Filtering works correctly
- ✅ CSV export functional
- ✅ Database stays under 10MB
- ✅ Privacy preserved (no code content stored)
