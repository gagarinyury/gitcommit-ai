"""Tests for statistics exporter."""
import csv
import json
import tempfile
from pathlib import Path

import pytest

from gitcommit_ai.stats.database import CommitRecord
from gitcommit_ai.stats.exporter import StatsExporter


@pytest.fixture
def sample_records() -> list[CommitRecord]:
    """Create sample commit records."""
    return [
        CommitRecord(1, "2025-10-02T10:00:00", "openai", "gpt-4o", "feat", True, 1000, 50),
        CommitRecord(2, "2025-10-02T11:00:00", "anthropic", "claude-3-haiku", "fix", True, 1500, 75),
        CommitRecord(3, "2025-10-02T12:00:00", "ollama", "llama3.2", "docs", False, 3000, 25),
    ]


class TestStatsExporter:
    """Test statistics export functionality."""

    def test_to_csv_creates_file(self, sample_records: list[CommitRecord]) -> None:
        """Creates CSV file with records."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            output_path = Path(f.name)

        StatsExporter.to_csv(sample_records, output_path)

        assert output_path.exists()
        output_path.unlink()

    def test_to_csv_correct_format(self, sample_records: list[CommitRecord]) -> None:
        """CSV has correct header and rows."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            output_path = Path(f.name)

        StatsExporter.to_csv(sample_records, output_path)

        with open(output_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)

            assert len(rows) == 3
            assert rows[0]["provider"] == "openai"
            assert rows[0]["commit_type"] == "feat"
            assert rows[0]["success"] == "true"

        output_path.unlink()

    def test_to_csv_handles_null_values(self) -> None:
        """CSV export handles null/None values."""
        records = [
            CommitRecord(1, "2025-10-02T10:00:00", "openai", None, None, True, None, None),
        ]

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            output_path = Path(f.name)

        StatsExporter.to_csv(records, output_path)

        with open(output_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)

            assert rows[0]["model"] == ""
            assert rows[0]["commit_type"] == ""
            assert rows[0]["response_time_ms"] == ""

        output_path.unlink()

    def test_to_json_creates_file(self, sample_records: list[CommitRecord]) -> None:
        """Creates JSON file with records."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            output_path = Path(f.name)

        StatsExporter.to_json(sample_records, output_path)

        assert output_path.exists()
        output_path.unlink()

    def test_to_json_correct_format(self, sample_records: list[CommitRecord]) -> None:
        """JSON has correct structure."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            output_path = Path(f.name)

        StatsExporter.to_json(sample_records, output_path)

        with open(output_path, "r") as jsonfile:
            data = json.load(jsonfile)

            assert isinstance(data, list)
            assert len(data) == 3
            assert data[0]["provider"] == "openai"
            assert data[0]["commit_type"] == "feat"
            assert data[0]["success"] is True

        output_path.unlink()

    def test_to_json_preserves_types(self, sample_records: list[CommitRecord]) -> None:
        """JSON export preserves data types."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            output_path = Path(f.name)

        StatsExporter.to_json(sample_records, output_path)

        with open(output_path, "r") as jsonfile:
            data = json.load(jsonfile)

            # Check types
            assert isinstance(data[0]["id"], int)
            assert isinstance(data[0]["success"], bool)
            assert isinstance(data[0]["response_time_ms"], int)
            assert isinstance(data[0]["diff_lines"], int)

        output_path.unlink()

    def test_to_json_handles_null_values(self) -> None:
        """JSON export handles null/None values."""
        records = [
            CommitRecord(1, "2025-10-02T10:00:00", "openai", None, None, True, None, None),
        ]

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            output_path = Path(f.name)

        StatsExporter.to_json(records, output_path)

        with open(output_path, "r") as jsonfile:
            data = json.load(jsonfile)

            assert data[0]["model"] is None
            assert data[0]["commit_type"] is None
            assert data[0]["response_time_ms"] is None

        output_path.unlink()
