"""SQLite database for commit statistics."""
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class CommitRecord:
    """Single commit metadata record."""
    id: Optional[int]
    timestamp: str
    provider: str
    model: Optional[str]
    commit_type: Optional[str]
    success: bool
    response_time_ms: Optional[int]
    diff_lines: Optional[int]


class StatsDatabase:
    """SQLite wrapper for commit statistics."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database.

        Args:
            db_path: Path to SQLite database (defaults to ~/.gitcommit-ai/stats.db).
        """
        if db_path is None:
            home = Path.home()
            gitcommit_dir = home / ".gitcommit-ai"
            gitcommit_dir.mkdir(exist_ok=True)
            db_path = gitcommit_dir / "stats.db"

        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commit_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                provider TEXT NOT NULL,
                model TEXT,
                commit_type TEXT,
                success INTEGER NOT NULL,
                response_time_ms INTEGER,
                diff_lines INTEGER
            )
        """)

        # Index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON commit_records(timestamp)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_provider
            ON commit_records(provider)
        """)

        conn.commit()
        conn.close()

    def insert(self, record: CommitRecord) -> int:
        """Insert a commit record.

        Args:
            record: CommitRecord to insert.

        Returns:
            ID of inserted record.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO commit_records
            (timestamp, provider, model, commit_type, success, response_time_ms, diff_lines)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            record.timestamp,
            record.provider,
            record.model,
            record.commit_type,
            1 if record.success else 0,
            record.response_time_ms,
            record.diff_lines
        ))

        record_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return record_id

    def get_all(self, limit: Optional[int] = None) -> list[CommitRecord]:
        """Get all commit records.

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of CommitRecord objects.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM commit_records ORDER BY timestamp DESC"
        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_record(row) for row in rows]

    def get_by_provider(self, provider: str) -> list[CommitRecord]:
        """Get records for specific provider."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM commit_records WHERE provider = ? ORDER BY timestamp DESC",
            (provider,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_record(row) for row in rows]

    def get_by_date_range(self, start: str, end: str) -> list[CommitRecord]:
        """Get records within date range.

        Args:
            start: Start date (ISO format: YYYY-MM-DD).
            end: End date (ISO format: YYYY-MM-DD).

        Returns:
            List of CommitRecord objects.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM commit_records
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp DESC
        """, (start, end))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_record(row) for row in rows]

    def get_by_id(self, record_id: int) -> Optional[CommitRecord]:
        """Get record by ID.

        Args:
            record_id: ID of the record.

        Returns:
            CommitRecord if found, None otherwise.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM commit_records WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        conn.close()

        return self._row_to_record(row) if row else None

    def delete(self, record_id: int) -> None:
        """Delete record by ID.

        Args:
            record_id: ID of the record to delete.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM commit_records WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()

    def count(self) -> int:
        """Get total number of records."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM commit_records")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def count_total(self) -> int:
        """Get total number of records."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM commit_records")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def cleanup_old_records(self, days: int = 90) -> int:
        """Delete records older than specified days.

        Args:
            days: Number of days to keep.

        Returns:
            Number of deleted records.
        """
        from datetime import timedelta

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM commit_records WHERE timestamp < ?",
            (cutoff_date,)
        )

        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()

        return deleted_count

    def _row_to_record(self, row: sqlite3.Row) -> CommitRecord:
        """Convert database row to CommitRecord."""
        return CommitRecord(
            id=row["id"],
            timestamp=row["timestamp"],
            provider=row["provider"],
            model=row["model"],
            commit_type=row["commit_type"],
            success=bool(row["success"]),
            response_time_ms=row["response_time_ms"],
            diff_lines=row["diff_lines"]
        )
