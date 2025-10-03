"""Statistics aggregation and analysis."""
from collections import Counter
from dataclasses import dataclass
from typing import Optional

from gitcommit_ai.stats.database import CommitRecord, StatsDatabase


@dataclass
class StatsSummary:
    """Aggregated statistics summary."""
    total_commits: int
    success_rate: float
    avg_response_time_ms: Optional[float]
    provider_breakdown: dict[str, int]
    type_breakdown: dict[str, int]
    fastest_provider: Optional[str]
    most_reliable_provider: Optional[str]


class StatsAggregator:
    """Compute statistics from commit records."""

    def __init__(self, db: StatsDatabase):
        """Initialize aggregator.

        Args:
            db: StatsDatabase instance.
        """
        self.db = db

    def get_summary(
        self,
        provider: Optional[str] = None,
        days: Optional[int] = None
    ) -> StatsSummary:
        """Get aggregated statistics summary.

        Args:
            provider: Filter by provider (optional).
            days: Filter by last N days (optional).

        Returns:
            StatsSummary object.
        """
        # Get records
        if provider:
            records = self.db.get_by_provider(provider)
        elif days:
            from datetime import datetime, timedelta
            end = datetime.now().isoformat()
            start = (datetime.now() - timedelta(days=days)).isoformat()
            records = self.db.get_by_date_range(start, end)
        else:
            records = self.db.get_all()

        if not records:
            return StatsSummary(
                total_commits=0,
                success_rate=0.0,
                avg_response_time_ms=None,
                provider_breakdown={},
                type_breakdown={},
                fastest_provider=None,
                most_reliable_provider=None
            )

        # Compute metrics
        total = len(records)
        successes = sum(1 for r in records if r.success)
        success_rate = (successes / total) if total > 0 else 0.0

        # Average response time
        response_times = [r.response_time_ms for r in records if r.response_time_ms]
        avg_response = sum(response_times) / len(response_times) if response_times else None

        # Provider breakdown
        provider_counts = Counter(r.provider for r in records)

        # Type breakdown
        type_counts = Counter(r.commit_type for r in records if r.commit_type)

        # Fastest provider (lowest avg response time)
        fastest = self._get_fastest_provider(records)

        # Most reliable provider (highest success rate)
        most_reliable = self._get_most_reliable_provider(records)

        return StatsSummary(
            total_commits=total,
            success_rate=success_rate,
            avg_response_time_ms=avg_response,
            provider_breakdown=dict(provider_counts),
            type_breakdown=dict(type_counts),
            fastest_provider=fastest,
            most_reliable_provider=most_reliable
        )

    def _get_fastest_provider(self, records: list[CommitRecord]) -> Optional[str]:
        """Determine fastest provider by average response time."""
        from collections import defaultdict

        provider_times: defaultdict[str, list[int]] = defaultdict(list)

        for record in records:
            if record.response_time_ms:
                provider_times[record.provider].append(record.response_time_ms)

        if not provider_times:
            return None

        # Calculate averages
        provider_avgs = {
            provider: sum(times) / len(times)
            for provider, times in provider_times.items()
        }

        # Return provider with lowest average
        return min(provider_avgs, key=provider_avgs.get)

    def _get_most_reliable_provider(self, records: list[CommitRecord]) -> Optional[str]:
        """Determine most reliable provider by success rate."""
        from collections import defaultdict

        provider_stats: defaultdict[str, dict[str, int]] = defaultdict(
            lambda: {"total": 0, "success": 0}
        )

        for record in records:
            provider_stats[record.provider]["total"] += 1
            if record.success:
                provider_stats[record.provider]["success"] += 1

        if not provider_stats:
            return None

        # Calculate success rates
        provider_rates = {
            provider: (stats["success"] / stats["total"])
            for provider, stats in provider_stats.items()
        }

        # Return provider with highest success rate
        return max(provider_rates, key=provider_rates.get)

    def get_recent_commits(self, limit: int = 10) -> list[CommitRecord]:
        """Get recent commit records.

        Args:
            limit: Maximum number of records.

        Returns:
            List of most recent CommitRecord objects.
        """
        return self.db.get_all(limit=limit)
