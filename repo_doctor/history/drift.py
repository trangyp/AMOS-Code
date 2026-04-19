"""
Temporal Drift Analysis

Drift: ΔΨ(t) = |Ψ_repo(t)⟩ - |Ψ_repo(t-1)⟩
Drift norm: ||ΔΨ|| = sqrt(Σk (Δαk)²)
"""

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class TemporalDrift:
    """Drift measurement between commits."""

    commit_hash: str
    timestamp: datetime
    drift_norm: float
    affected_dimensions: List[str]
    delta_amplitudes: Dict[str, float]

    def is_significant(self, threshold: float = 0.1) -> bool:
        """Check if drift exceeds significance threshold."""
        return self.drift_norm > threshold


class DriftAnalyzer:
    """
    Analyze temporal evolution and detect drift.

    Drift norm: ||ΔΨ|| = sqrt(Σk (Δαk)²)
    """

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.history: list[dict[str, Any]] = []

    def compute_drift(
        self,
        prev_state: Dict[str, float],
        curr_state: Dict[str, float],
    ) -> float:
        """
        Compute drift norm: ||ΔΨ|| = sqrt(Σk (Δαk)²)
        """
        total = 0.0
        all_dims = set(prev_state.keys()) | set(curr_state.keys())

        for dim in all_dims:
            prev = prev_state.get(dim, 1.0)
            curr = curr_state.get(dim, 1.0)
            delta = curr - prev
            total += delta**2

        return math.sqrt(total)

    def compute_drift_vector(
        self,
        prev_state: Dict[str, float],
        curr_state: Dict[str, float],
    ) -> dict[str, float]:
        """Compute per-dimension drift."""
        result = {}
        all_dims = set(prev_state.keys()) | set(curr_state.keys())

        for dim in all_dims:
            prev = prev_state.get(dim, 1.0)
            curr = curr_state.get(dim, 1.0)
            result[dim] = curr - prev

        return result

    def find_destabilizing_commits(
        self,
        history: list[dict[str, Any]],
        top_n: int = 5,
    ) -> list[tuple[str, float]]:
        """
        Find top N commits by drift magnitude.

        Returns: [(commit_hash, drift_norm), ...]
        """
        drifts = []

        for i in range(1, len(history)):
            prev = history[i - 1].get("state", {})
            curr = history[i].get("state", {})
            drift = self.compute_drift(prev, curr)
            commit = history[i].get("hash", "unknown")
            drifts.append((commit, drift))

        return sorted(drifts, key=lambda x: -x[1])[:top_n]

    def detect_anomalies(
        self,
        history: list[dict[str, Any]],
        threshold: float = 0.2,
    ) -> List[TemporalDrift]:
        """Detect anomalous drift events."""
        anomalies = []

        for i in range(1, len(history)):
            prev = history[i - 1].get("state", {})
            curr = history[i].get("state", {})
            drift = self.compute_drift(prev, curr)

            if drift > threshold:
                delta = self.compute_drift_vector(prev, curr)
                affected = [d for d, v in delta.items() if abs(v) > 0.05]

                anomalies.append(
                    TemporalDrift(
                        commit_hash=history[i].get("hash", "unknown"),
                        timestamp=history[i].get("timestamp", datetime.now()),
                        drift_norm=drift,
                        affected_dimensions=affected,
                        delta_amplitudes=delta,
                    )
                )

        return anomalies
