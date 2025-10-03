"""Export statistics to CSV and JSON."""
import csv
import json
from pathlib import Path

from gitcommit_ai.stats.database import CommitRecord


class StatsExporter:
    """Export commit records to various formats."""

    @staticmethod
    def to_csv(records: list[CommitRecord], output_path: Path) -> None:
        """Export records to CSV.

        Args:
            records: List of CommitRecord objects.
            output_path: Path to output CSV file.
        """
        with open(output_path, "w", newline="") as csvfile:
            fieldnames = [
                "timestamp",
                "provider",
                "model",
                "commit_type",
                "success",
                "response_time_ms",
                "diff_lines"
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for record in records:
                writer.writerow({
                    "timestamp": record.timestamp,
                    "provider": record.provider,
                    "model": record.model or "",
                    "commit_type": record.commit_type or "",
                    "success": "true" if record.success else "false",
                    "response_time_ms": record.response_time_ms or "",
                    "diff_lines": record.diff_lines or ""
                })

    @staticmethod
    def to_json(records: list[CommitRecord], output_path: Path) -> None:
        """Export records to JSON.

        Args:
            records: List of CommitRecord objects.
            output_path: Path to output JSON file.
        """
        data = [
            {
                "id": record.id,
                "timestamp": record.timestamp,
                "provider": record.provider,
                "model": record.model,
                "commit_type": record.commit_type,
                "success": record.success,
                "response_time_ms": record.response_time_ms,
                "diff_lines": record.diff_lines
            }
            for record in records
        ]

        with open(output_path, "w") as jsonfile:
            json.dump(data, jsonfile, indent=2)
