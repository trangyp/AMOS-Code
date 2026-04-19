"""Drift tracker for measuring repository evolution.

Tracks state changes across commits:
- Per-subsystem drift
- Cumulative energy changes
- Trend analysis
"""

from dataclasses import dataclass, field
from typing import Any

from .temporal_substrate import CommitState, TemporalSubstrate


@dataclass
class DriftTrend:
    """Trend analysis for a subsystem."""

    subsystem: str
    slope: float  # Rate of change
    volatility: float  # Variance in changes
    current_value: float
    trend_direction: str  # "improving", "degrading", "stable"


@dataclass
class DriftReport:
    """Comprehensive drift report."""

    repository: str
    total_drift: float
    energy_trend: float
    trends: list[DriftTrend] = field(default_factory=list)
    destabilizing_commits: list[tuple[str, float]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "repository": self.repository,
            "total_drift": self.total_drift,
            "energy_trend": self.energy_trend,
            "trends": [
                {
                    "subsystem": t.subsystem,
                    "slope": t.slope,
                    "volatility": t.volatility,
                    "current": t.current_value,
                    "direction": t.trend_direction,
                }
                for t in self.trends
            ],
            "destabilizing_commits": [
                {"commit": c, "drift": d} for c, d in self.destabilizing_commits
            ],
        }


class DriftTracker:
    """Drift tracker for repository evolution analysis.

    Tracks state changes across commits and identifies trends:
    - Which subsystems are degrading
    - Energy trends
    - Destabilizing commits

    Usage:
        tracker = DriftTracker("/path/to/repo")

        # Generate drift report
        report = tracker.analyze_drift(commits=100)

        print(f"Total drift: {report.total_drift}")
        for trend in report.trends:
            print(f"  {trend.subsystem}: {trend.trend_direction}")
    """

    def __init__(self, repo_path: str):
        self.substrate = TemporalSubstrate(repo_path)

    def analyze_drift(
        self,
        commits: int = 100,
        threshold: float = 0.5,
    ) -> DriftReport:
        """Analyze drift over commit history.

        Args:
            commits: Number of commits to analyze
            threshold: Drift threshold for reporting

        Returns:
            DriftReport with analysis
        """
        # Get commit history
        history = self.substrate.get_commit_history(max_commits=commits)

        if len(history) < 2:
            return DriftReport(
                repository=str(self.substrate.repo_path),
                total_drift=0.0,
                energy_trend=0.0,
            )

        # Compute drifts between consecutive commits
        drifts = []
        for i in range(len(history) - 1):
            drift = self.substrate.measure_drift(history[i], history[i + 1])
            drifts.append(drift)

        # Calculate total drift
        total_drift = sum(d.drift_norm for d in drifts)

        # Calculate energy trend
        energy_start = history[0].energy
        energy_end = history[-1].energy
        energy_trend = energy_end - energy_start

        # Analyze per-subsystem trends
        trends = self._analyze_trends(history)

        # Identify destabilizing commits
        destabilizing = [(d.to_commit, d.drift_norm) for d in drifts if d.drift_norm > threshold]
        destabilizing.sort(key=lambda x: x[1], reverse=True)

        return DriftReport(
            repository=str(self.substrate.repo_path),
            total_drift=total_drift,
            energy_trend=energy_trend,
            trends=trends,
            destabilizing_commits=destabilizing[:10],  # Top 10
        )

    def _analyze_trends(self, history: list[CommitState]) -> list[DriftTrend]:
        """Analyze trends for each subsystem."""
        if not history:
            return []

        # Collect all subsystem keys
        all_keys: Set[str] = set()
        for state in history:
            all_keys.update(state.state_vector.keys())

        trends = []

        for key in sorted(all_keys):
            # Get values for this subsystem
            values = [state.state_vector.get(key, 1.0) for state in history]

            if len(values) < 2:
                continue

            # Calculate slope (simple linear trend)
            n = len(values)
            x_mean = (n - 1) / 2
            y_mean = sum(values) / n

            numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
            denominator = sum((i - x_mean) ** 2 for i in range(n))

            slope = numerator / denominator if denominator != 0 else 0

            # Calculate volatility (standard deviation of changes)
            changes = [values[i + 1] - values[i] for i in range(n - 1)]
            if changes:
                mean_change = sum(changes) / len(changes)
                variance = sum((c - mean_change) ** 2 for c in changes) / len(changes)
                volatility = variance**0.5
            else:
                volatility = 0

            # Determine trend direction
            if slope < -0.01:
                direction = "improving"
            elif slope > 0.01:
                direction = "degrading"
            else:
                direction = "stable"

            trends.append(
                DriftTrend(
                    subsystem=key,
                    slope=slope,
                    volatility=volatility,
                    current_value=values[-1],
                    trend_direction=direction,
                )
            )

        # Sort by degradation severity
        return sorted(
            trends,
            key=lambda t: t.slope if t.slope > 0 else -t.slope,
            reverse=True,
        )

    def get_drift_timeseries(
        self,
        subsystem: str,
        commits: int = 50,
    ) -> list[tuple[str, float]]:
        """Get timeseries data for a subsystem.

        Args:
            subsystem: Subsystem name
            commits: Number of commits

        Returns:
            List of (commit_hash, value) tuples
        """
        history = self.substrate.get_commit_history(max_commits=commits)

        return [(state.commit_hash, state.state_vector.get(subsystem, 1.0)) for state in history]

    def predict_stability(
        self,
        horizon: int = 10,
    ) -> dict[str, float]:
        """Predict future stability based on trends.

        Args:
            horizon: Number of commits to project forward

        Returns:
            Dictionary of predicted subsystem values
        """
        history = self.substrate.get_commit_history(max_commits=50)

        if not history:
            return {}

        trends = self._analyze_trends(history)

        predictions = {}
        for trend in trends:
            # Simple linear projection
            predicted = trend.current_value + trend.slope * horizon
            # Clamp to [0, 1]
            predictions[trend.subsystem] = max(0.0, min(1.0, predicted))

        return predictions
