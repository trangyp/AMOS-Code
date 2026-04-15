"""
Repo Doctor Ω∞ - Temporal Analysis

Temporal evolution:
|Ψ_repo(t+1)⟩ = U_t |Ψ_repo(t)⟩

Drift: ΔΨ(t) = |Ψ_repo(t)⟩ - |Ψ_repo(t-1)⟩

First bad commit: t*_k = min t such that I_k(t-1)=1 and I_k(t)=0
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .state.basis import StateDimension


@dataclass
class TemporalDrift:
    """Drift measurement between commits."""

    commit_hash: str
    timestamp: str
    drift_norm: float
    affected_dimensions: list[str]
    delta_amplitudes: dict[str, float]


class TemporalAnalyzer:
    """
    Analyze temporal evolution and find first bad commits.
    """

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.history: list[dict[str, Any]] = []

    def compute_drift(
        self,
        prev_state: dict[str, float],
        curr_state: dict[str, float],
    ) -> float:
        """
        Compute drift norm: ||ΔΨ|| = sqrt(Σk (Δαk)²)
        """
        import math

        total = 0.0
        for dim in StateDimension:
            delta = curr_state.get(dim.value, 1.0) - prev_state.get(dim.value, 1.0)
            total += delta**2

        return math.sqrt(total)

    def find_first_bad_commit(
        self,
        invariant_name: str,
        history: list[dict[str, Any]],
    ) -> str:
        """
        Find t*_k = min t such that I_k(t-1)=1 and I_k(t)=0
        """
        prev_valid = True

        for commit in history:
            curr_valid = commit.get("invariants", {}).get(invariant_name, True)

            if prev_valid and not curr_valid:
                return commit.get("hash", "unknown")

            prev_valid = curr_valid

        return "not_found"

    def compute_path_integral(
        self,
        invariant: str,
        path: list[dict[str, Any]],
    ) -> float:
        """
        Compute action: S_k[path] = Στ (a1·||ΔΨ|| + a2·ΔEnt + ...)
        """
        action = 0.0

        for i in range(1, len(path)):
            prev = path[i - 1].get("state", {})
            curr = path[i].get("state", {})

            drift = self.compute_drift(prev, curr)
            action += drift

        return action

    def rank_causality(
        self,
        invariant: str,
        commits: list[dict[str, Any]],
    ) -> list[tuple[str, float]]:
        """
        Rank commits by causality: P(t) ∝ exp(-S_k[0→t])
        """
        import math

        results = []

        for i, commit in enumerate(commits):
            path = commits[: i + 1]
            action = self.compute_path_integral(invariant, path)
            prob = math.exp(-action)
            results.append((commit.get("hash", "unknown"), prob))

        return sorted(results, key=lambda x: -x[1])
