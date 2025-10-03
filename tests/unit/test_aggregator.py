"""Tests for statistics aggregator."""
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from gitcommit_ai.stats.aggregator import StatsAggregator, StatsSummary
from gitcommit_ai.stats.database import CommitRecord, StatsDatabase


@pytest.fixture
def temp_db_with_data() -> StatsDatabase:
    """Create database with sample data."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    db = StatsDatabase(db_path=db_path)

    # Insert sample records
    now = datetime.now()
    records = [
        CommitRecord(None, (now - timedelta(days=1)).isoformat(), "openai", "gpt-4o", "feat", True, 1000, 50),
        CommitRecord(None, (now - timedelta(days=1)).isoformat(), "openai", "gpt-4o", "fix", True, 1200, 30),
        CommitRecord(None, now.isoformat(), "anthropic", "claude-3-haiku", "docs", True, 800, 20),
        CommitRecord(None, now.isoformat(), "anthropic", "claude-3-haiku", "test", False, 5000, 100),
        CommitRecord(None, now.isoformat(), "ollama", "llama3.2", "feat", True, 2000, 60),
    ]

    for rec in records:
        db.insert(rec)

    yield db
    db_path.unlink(missing_ok=True)


class TestStatsAggregator:
    """Test statistics aggregation."""

    def test_get_summary_all_records(self, temp_db_with_data: StatsDatabase) -> None:
        """Aggregates statistics from all records."""
        aggregator = StatsAggregator(temp_db_with_data)
        summary = aggregator.get_summary()

        assert isinstance(summary, StatsSummary)
        assert summary.total_commits == 5
        assert 0.0 <= summary.success_rate <= 1.0
        assert summary.avg_response_time_ms is not None

    def test_get_summary_calculates_success_rate(self, temp_db_with_data: StatsDatabase) -> None:
        """Calculates success rate correctly."""
        aggregator = StatsAggregator(temp_db_with_data)
        summary = aggregator.get_summary()

        # 4 successful out of 5 total = 0.8
        assert summary.success_rate == pytest.approx(0.8, rel=0.01)

    def test_get_summary_filters_by_provider(self, temp_db_with_data: StatsDatabase) -> None:
        """Filters statistics by provider."""
        aggregator = StatsAggregator(temp_db_with_data)
        summary = aggregator.get_summary(provider="openai")

        assert summary.total_commits == 2
        assert summary.success_rate == 1.0  # Both OpenAI commits successful
        assert summary.provider_breakdown == {"openai": 2}

    def test_get_summary_provider_breakdown(self, temp_db_with_data: StatsDatabase) -> None:
        """Provides breakdown by provider."""
        aggregator = StatsAggregator(temp_db_with_data)
        summary = aggregator.get_summary()

        assert summary.provider_breakdown["openai"] == 2
        assert summary.provider_breakdown["anthropic"] == 2
        assert summary.provider_breakdown["ollama"] == 1

    def test_get_summary_type_breakdown(self, temp_db_with_data: StatsDatabase) -> None:
        """Provides breakdown by commit type."""
        aggregator = StatsAggregator(temp_db_with_data)
        summary = aggregator.get_summary()

        assert summary.type_breakdown["feat"] == 2
        assert summary.type_breakdown["fix"] == 1
        assert summary.type_breakdown["docs"] == 1
        assert summary.type_breakdown["test"] == 1

    def test_get_summary_identifies_fastest_provider(self, temp_db_with_data: StatsDatabase) -> None:
        """Identifies provider with fastest avg response time."""
        aggregator = StatsAggregator(temp_db_with_data)
        summary = aggregator.get_summary()

        # anthropic has avg (800 + 5000) / 2 = 2900ms
        # openai has avg (1000 + 1200) / 2 = 1100ms
        # ollama has 2000ms
        # So openai should be fastest
        assert summary.fastest_provider == "openai"

    def test_get_summary_empty_database(self) -> None:
        """Handles empty database gracefully."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = Path(f.name)
        db = StatsDatabase(db_path=db_path)
        aggregator = StatsAggregator(db)

        summary = aggregator.get_summary()
        assert summary.total_commits == 0
        assert summary.success_rate == 0.0
        assert summary.fastest_provider is None

        db_path.unlink()


class TestStatsSummary:
    """Test StatsSummary dataclass."""

    def test_stats_summary_creation(self) -> None:
        """Can create StatsSummary instance."""
        summary = StatsSummary(
            total_commits=100,
            success_rate=0.95,
            avg_response_time_ms=1200.5,
            provider_breakdown={"openai": 60, "anthropic": 40},
            type_breakdown={"feat": 50, "fix": 30, "docs": 20},
            fastest_provider="anthropic",
            most_reliable_provider="openai"
        )

        assert summary.total_commits == 100
        assert summary.success_rate == 0.95
        assert summary.fastest_provider == "anthropic"
