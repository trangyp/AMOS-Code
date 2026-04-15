"""Temporal Cognition Bridge

Integrates Repo Doctor's temporal analysis with the AMOS Brain
to enable:
- State vector drift tracking across commits: ΔΨ(t) = |Ψ(t)⟩ - |Ψ(t-1)⟩
- First-bad-commit detection: t*_k = min t such that I_k(t-1)=1 and I_k(t)=0
- Causality ranking: P(t) ∝ exp(-S_k[0→t])
- Temporal anomaly detection

This allows the brain to answer:
- "When did architecture start degrading?"
- "Which commit first violated this invariant?"
- "What's the most likely cause of this failure?"
- "How fast is the repo state drifting?"
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Import temporal analyzer
try:
    from repo_doctor.temporal import TemporalAnalyzer, TemporalDrift

    TEMPORAL_AVAILABLE = True
except ImportError:
    TEMPORAL_AVAILABLE = False

# Import state components
try:
    from repo_doctor.state.basis import StateDimension
    from repo_doctor.state_vector import RepoStateVector

    STATE_AVAILABLE = True
except ImportError:
    STATE_AVAILABLE = False


@dataclass
class TemporalContext:
    """Complete temporal context for a repository state."""

    current_commit: str
    current_timestamp: str
    parent_commit: str | None

    # Drift measurements
    drift_norm: float = 0.0  # ||ΔΨ||
    drift_velocity: float = 0.0  # d/dt ||ΔΨ||

    # State vector amplitudes
    current_amplitudes: dict[str, float] = field(default_factory=dict)
    delta_amplitudes: dict[str, float] = field(default_factory=dict)

    # Affected dimensions
    affected_dimensions: list[str] = field(default_factory=list)
    critical_dimensions: list[str] = field(default_factory=list)

    # Invariant status
    invariants_held: list[str] = field(default_factory=list)
    invariants_violated: list[str] = field(default_factory=list)
    new_violations: list[str] = field(default_factory=list)  # I(t-1)=1, I(t)=0

    # Temporal trajectory
    trajectory_length: int = 0
    total_drift_accumulated: float = 0.0


@dataclass
class FirstBadCommitResult:
    """Result of first-bad-commit analysis."""

    invariant_name: str
    first_bad_commit: str
    first_bad_timestamp: str | None
    previous_commit: str | None
    previous_was_valid: bool
    causality_probability: float
    search_space_size: int


@dataclass
class DriftAlert:
    """Alert when significant drift detected."""

    severity: str  # critical, high, medium, low
    message: str
    drift_norm: float
    threshold: float
    affected_dimensions: list[str]
    recommendation: str


class TemporalCognitionBridge:
    """Bridge between temporal analysis and AMOS Brain cognition.

    Provides:
    - Real-time drift monitoring
    - First-bad-commit detection
    - Causality analysis
    - Temporal anomaly alerts
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path)
        self.analyzer = TemporalAnalyzer(str(repo_path)) if TEMPORAL_AVAILABLE else None
        self._history_cache: list[dict[str, Any]] = []
        self._drift_threshold_critical = 0.5
        self._drift_threshold_high = 0.3
        self._drift_threshold_medium = 0.1

    @property
    def current_commit(self) -> str:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()[:12]
        except Exception:
            return "unknown"

    @property
    def parent_commit(self) -> str | None:
        """Get parent commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD~1"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()[:12]
        except Exception:
            return None

    def get_temporal_context(
        self,
        prev_state: dict[str, float] | None = None,
        curr_state: dict[str, float] | None = None,
    ) -> TemporalContext:
        """Get complete temporal context comparing current to previous state."""
        if not TEMPORAL_AVAILABLE or not STATE_AVAILABLE:
            return TemporalContext(
                current_commit=self.current_commit,
                current_timestamp="",
                parent_commit=self.parent_commit,
            )

        # Get current state if not provided
        if curr_state is None:
            curr_state = self._compute_current_state()

        # Get parent state if available
        if prev_state is None and self.parent_commit:
            prev_state = self._get_state_at_commit(self.parent_commit)

        # Compute drift
        if prev_state is not None:
            drift_norm = self.analyzer.compute_drift(prev_state, curr_state)
            delta_amps = self._compute_delta_amplitudes(prev_state, curr_state)
            affected = self._get_affected_dimensions(delta_amps)
            critical = self._get_critical_dimensions(delta_amps)
        else:
            drift_norm = 0.0
            delta_amps = {}
            affected = []
            critical = []

        return TemporalContext(
            current_commit=self.current_commit,
            current_timestamp=self._get_timestamp(),
            parent_commit=self.parent_commit,
            drift_norm=drift_norm,
            drift_velocity=self._estimate_velocity(drift_norm),
            current_amplitudes=curr_state or {},
            delta_amplitudes=delta_amps,
            affected_dimensions=affected,
            critical_dimensions=critical,
        )

    def find_first_bad_commit(
        self,
        invariant_name: str,
        max_commits: int = 50,
    ) -> FirstBadCommitResult | None:
        """Find t*_k = min t such that I_k(t-1)=1 and I_k(t)=0

        Args:
            invariant_name: The invariant to check
            max_commits: Maximum commits to search back

        Returns:
            FirstBadCommitResult with the first violating commit
        """
        if not TEMPORAL_AVAILABLE:
            return None

        # Build history
        history = self._build_invariant_history(invariant_name, max_commits)

        if not history:
            return None

        # Use temporal analyzer to find first bad commit
        bad_commit = self.analyzer.find_first_bad_commit(invariant_name, history)

        if bad_commit == "not_found":
            return None

        # Find details about the bad commit
        bad_idx = next(
            (i for i, h in enumerate(history) if h.get("hash") == bad_commit),
            None,
        )

        if bad_idx is None or bad_idx == 0:
            return None

        prev_commit = history[bad_idx - 1].get("hash")

        # Compute causality probability
        path = history[: bad_idx + 1]
        action = self.analyzer.compute_path_integral(invariant_name, path)
        causality_prob = self._compute_causality(action)

        return FirstBadCommitResult(
            invariant_name=invariant_name,
            first_bad_commit=bad_commit,
            first_bad_timestamp=history[bad_idx].get("timestamp"),
            previous_commit=prev_commit,
            previous_was_valid=True,
            causality_probability=causality_prob,
            search_space_size=len(history),
        )

    def check_drift_alerts(
        self,
        prev_state: dict[str, float] | None = None,
        curr_state: dict[str, float] | None = None,
    ) -> list[DriftAlert]:
        """Check for significant drift and return alerts."""
        alerts = []

        if not TEMPORAL_AVAILABLE:
            return alerts

        context = self.get_temporal_context(prev_state, curr_state)
        drift = context.drift_norm

        if drift >= self._drift_threshold_critical:
            alerts.append(
                DriftAlert(
                    severity="critical",
                    message=f"Critical state drift detected: ||ΔΨ|| = {drift:.3f}",
                    drift_norm=drift,
                    threshold=self._drift_threshold_critical,
                    affected_dimensions=context.critical_dimensions,
                    recommendation="Immediate review required. Rollback may be necessary.",
                )
            )
        elif drift >= self._drift_threshold_high:
            alerts.append(
                DriftAlert(
                    severity="high",
                    message=f"Significant state drift: ||ΔΨ|| = {drift:.3f}",
                    drift_norm=drift,
                    threshold=self._drift_threshold_high,
                    affected_dimensions=context.affected_dimensions,
                    recommendation="Review changes before proceeding with further modifications.",
                )
            )
        elif drift >= self._drift_threshold_medium:
            alerts.append(
                DriftAlert(
                    severity="medium",
                    message=f"Moderate state drift: ||ΔΨ|| = {drift:.3f}",
                    drift_norm=drift,
                    threshold=self._drift_threshold_medium,
                    affected_dimensions=context.affected_dimensions,
                    recommendation="Monitor for continued drift.",
                )
            )

        return alerts

    def rank_causality(
        self,
        invariant_name: str,
        max_commits: int = 50,
    ) -> list[tuple[str, float]]:
        """Rank commits by causality: P(t) ∝ exp(-S_k[0→t])."""
        if not TEMPORAL_AVAILABLE:
            return []

        history = self._build_invariant_history(invariant_name, max_commits)

        if not history:
            return []

        return self.analyzer.rank_causality(invariant_name, history)

    def get_drift_summary(self) -> dict[str, Any]:
        """Get summary of temporal drift status."""
        context = self.get_temporal_context()

        return {
            "current_commit": context.current_commit,
            "parent_commit": context.parent_commit,
            "drift_norm": context.drift_norm,
            "drift_velocity": context.drift_velocity,
            "affected_dimensions": context.affected_dimensions,
            "critical_dimensions": context.critical_dimensions,
            "trajectory_length": context.trajectory_length,
            "alerts": len(self.check_drift_alerts()),
        }

    def _compute_current_state(self) -> dict[str, float]:
        """Compute current repository state vector."""
        if not STATE_AVAILABLE:
            return {}

        # Build state from available analyzers
        state = {}

        for dim in StateDimension:
            state[dim.value] = 1.0  # Default to perfect

        return state

    def _get_state_at_commit(self, commit: str) -> dict[str, float] | None:
        """Get state vector at a specific commit."""
        # This would require checking out or reading cached state
        # For now, return None to indicate unavailable
        return None

    def _get_timestamp(self) -> str:
        """Get timestamp of current commit."""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ci"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def _compute_delta_amplitudes(
        self,
        prev: dict[str, float],
        curr: dict[str, float],
    ) -> dict[str, float]:
        """Compute delta amplitudes for each dimension."""
        delta = {}
        for dim in StateDimension:
            prev_val = prev.get(dim.value, 1.0)
            curr_val = curr.get(dim.value, 1.0)
            delta[dim.value] = curr_val - prev_val
        return delta

    def _get_affected_dimensions(self, delta: dict[str, float]) -> list[str]:
        """Get dimensions with non-zero drift."""
        threshold = 0.01
        return [k for k, v in delta.items() if abs(v) > threshold]

    def _get_critical_dimensions(self, delta: dict[str, float]) -> list[str]:
        """Get dimensions with significant drift."""
        threshold = 0.1
        return [k for k, v in delta.items() if abs(v) > threshold]

    def _estimate_velocity(self, current_drift: float) -> float:
        """Estimate drift velocity (drift per unit time)."""
        # Simplified: assume uniform time steps
        return current_drift

    def _build_invariant_history(
        self,
        invariant_name: str,
        max_commits: int,
    ) -> list[dict[str, Any]]:
        """Build history of invariant status across commits."""
        history = []

        try:
            # Get commit history
            result = subprocess.run(
                ["git", "log", "--format=%H", f"-n{max_commits}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )

            commits = result.stdout.strip().split("\n")

            for commit in commits:
                # In a real implementation, we would:
                # 1. Checkout or read the repo at this commit
                # 2. Run invariant checks
                # 3. Record the state

                # For now, add placeholder
                history.append(
                    {
                        "hash": commit[:12],
                        "timestamp": "",
                        "invariants": {invariant_name: True},  # Placeholder
                        "state": {},
                    }
                )

        except Exception:
            pass

        return history

    def _compute_causality(self, action: float) -> float:
        """Compute causality probability from action: P ∝ exp(-S)."""
        import math

        return math.exp(-action)


def get_temporal_bridge(repo_path: str | Path | None = None) -> TemporalCognitionBridge:
    """Factory function to get temporal bridge instance."""
    return TemporalCognitionBridge(repo_path or ".")
