"""Tests for statistics database."""
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from gitcommit_ai.stats.database import CommitRecord, StatsDatabase


@pytest.fixture
def temp_db() -> StatsDatabase:
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    db = StatsDatabase(db_path=db_path)
    yield db
    db_path.unlink(missing_ok=True)


class TestStatsDatabase:
    """Test database operations."""

    def test_database_initialization_creates_schema(self, temp_db: StatsDatabase) -> None:
        """Database creation initializes schema."""
        assert temp_db.db_path.exists()
        # Verify table exists by inserting
        record = CommitRecord(
            id=None,
            timestamp=datetime.now().isoformat(),
            provider="openai",
            model="gpt-4o",
            commit_type="feat",
            success=True,
            response_time_ms=1500,
            diff_lines=50
        )
        record_id = temp_db.insert(record)
        assert record_id > 0

    def test_insert_returns_record_id(self, temp_db: StatsDatabase) -> None:
        """Insert returns auto-incremented ID."""
        record = CommitRecord(
            id=None,
            timestamp="2025-10-02T12:00:00",
            provider="anthropic",
            model="claude-3-haiku",
            commit_type="fix",
            success=True,
            response_time_ms=2000,
            diff_lines=100
        )
        record_id = temp_db.insert(record)
        assert isinstance(record_id, int)
        assert record_id > 0

    def test_get_by_id_retrieves_record(self, temp_db: StatsDatabase) -> None:
        """Can retrieve record by ID."""
        record = CommitRecord(
            id=None,
            timestamp="2025-10-02T12:00:00",
            provider="openai",
            model="gpt-4o-mini",
            commit_type="docs",
            success=True,
            response_time_ms=800,
            diff_lines=20
        )
        record_id = temp_db.insert(record)
        retrieved = temp_db.get_by_id(record_id)

        assert retrieved is not None
        assert retrieved.id == record_id
        assert retrieved.provider == "openai"
        assert retrieved.commit_type == "docs"

    def test_get_by_id_returns_none_for_nonexistent(self, temp_db: StatsDatabase) -> None:
        """Returns None for nonexistent ID."""
        retrieved = temp_db.get_by_id(99999)
        assert retrieved is None

    def test_get_all_returns_all_records(self, temp_db: StatsDatabase) -> None:
        """Returns all records in descending timestamp order."""
        records = [
            CommitRecord(None, "2025-10-02T10:00:00", "openai", "gpt-4o", "feat", True, 1000, 50),
            CommitRecord(None, "2025-10-02T11:00:00", "anthropic", "claude-3-haiku", "fix", True, 1500, 75),
            CommitRecord(None, "2025-10-02T12:00:00", "ollama", "llama3.2", "docs", False, 3000, 25),
        ]

        for rec in records:
            temp_db.insert(rec)

        all_records = temp_db.get_all()
        assert len(all_records) == 3
        # DESC order: newest first (12:00 → 11:00 → 10:00)
        assert all_records[0].provider == "ollama"
        assert all_records[1].provider == "anthropic"
        assert all_records[2].provider == "openai"

    def test_get_by_provider_filters_correctly(self, temp_db: StatsDatabase) -> None:
        """Filters records by provider."""
        temp_db.insert(CommitRecord(None, "2025-10-02T10:00:00", "openai", "gpt-4o", "feat", True, 1000, 50))
        temp_db.insert(CommitRecord(None, "2025-10-02T11:00:00", "anthropic", "claude", "fix", True, 1500, 75))
        temp_db.insert(CommitRecord(None, "2025-10-02T12:00:00", "openai", "gpt-4o-mini", "docs", True, 800, 25))

        openai_records = temp_db.get_by_provider("openai")
        assert len(openai_records) == 2
        assert all(r.provider == "openai" for r in openai_records)

    def test_delete_removes_record(self, temp_db: StatsDatabase) -> None:
        """Delete removes record from database."""
        record = CommitRecord(None, "2025-10-02T12:00:00", "openai", "gpt-4o", "feat", True, 1000, 50)
        record_id = temp_db.insert(record)

        temp_db.delete(record_id)
        retrieved = temp_db.get_by_id(record_id)
        assert retrieved is None

    def test_count_returns_total_records(self, temp_db: StatsDatabase) -> None:
        """Count returns total number of records."""
        for i in range(5):
            temp_db.insert(CommitRecord(None, f"2025-10-02T{i:02d}:00:00", "openai", "gpt-4o", "feat", True, 1000, 50))

        assert temp_db.count() == 5


class TestCommitRecord:
    """Test CommitRecord dataclass."""

    def test_commit_record_creation(self) -> None:
        """Can create CommitRecord instance."""
        record = CommitRecord(
            id=1,
            timestamp="2025-10-02T12:00:00",
            provider="openai",
            model="gpt-4o",
            commit_type="feat",
            success=True,
            response_time_ms=1500,
            diff_lines=100
        )

        assert record.id == 1
        assert record.provider == "openai"
        assert record.success is True
