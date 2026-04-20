from __future__ import annotations

"""Temporal substrate for repository evolution tracking.

Tracks repository state across commits:
- State vector evolution: |Ψ_repo(t)⟩
- Drift measurement: ||ΔΨ(t)||
- Per-invariant history
"""

import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class CommitState:
    """Repository state at a specific commit."""

    commit_hash: str
    timestamp: datetime
    author: str
    message: str
    state_vector: dict[str, float] = field(default_factory=dict)
    energy: float = 0.0
    invariant_results: dict[str, bool] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        """Check if all hard invariants hold."""
        return all(self.invariant_results.values()) if self.invariant_results else True


@dataclass
class DriftMeasurement:
    """Drift between two commits."""

    from_commit: str
    to_commit: str
    delta_vector: dict[str, float] = field(default_factory=dict)
    drift_norm: float = 0.0
    failed_invariants: list[str] = field(default_factory=list)


class TemporalSubstrate:
    """Temporal substrate for tracking repository evolution.

    Implements the quantum-inspired temporal mechanics:
    - State evolution: |Ψ(t+1)⟩ = U_t |Ψ(t)⟩
    - Drift: ||ΔΨ(t)|| = sqrt(Σ (Δαk)²)
    - Per-invariant first-bad-commit detection

    Usage:
        substrate = TemporalSubstrate("/path/to/repo")

        # Get commit history
        commits = substrate.get_commit_history()

        # Measure drift
        drift = substrate.measure_drift(commits[0], commits[-1])

        # Find first bad commit for invariant
        first_bad = substrate.find_first_bad_commit("I_api")
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self._state_cache: dict[str, CommitState] = {}

    def get_commit_history(self, max_commits: int = 100) -> list[CommitState]:
        """Get commit history from git log.

        Args:
            max_commits: Maximum number of commits to fetch

        Returns:
            List of commit states
        """
        commits = []

        try:
            cmd = [
                "git",
                "log",
                f"--max-count={max_commits}",
                "--format=%H|%ai|%an|%s",
                "--reverse",  # Oldest first
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if "|" in line:
                        parts = line.split("|", 3)
                        if len(parts) >= 4:
                            commit_hash, timestamp_str, author, message = parts

                            try:
                                timestamp = datetime.fromisoformat(timestamp_str.replace(" ", "T"))
                            except ValueError:
                                timestamp = datetime.now()

                            state = CommitState(
                                commit_hash=commit_hash,
                                timestamp=timestamp,
                                author=author,
                                message=message,
                            )
                            commits.append(state)

        except Exception:
            pass

        return commits

    def measure_drift(
        self,
        from_state: CommitState,
        to_state: CommitState,
    ) -> DriftMeasurement:
        """Measure drift between two commits.

        Implements: ||ΔΨ|| = sqrt(Σ (Δαk)²)

        Args:
            from_state: Starting commit state
            to_state: Ending commit state

        Returns:
            Drift measurement
        """
        # Compute delta vector
        delta: dict[str, float] = {}
        all_keys = set(from_state.state_vector.keys()) | set(to_state.state_vector.keys())

        for key in all_keys:
            from_val = from_state.state_vector.get(key, 1.0)  # Default to healthy
            to_val = to_state.state_vector.get(key, 1.0)
            delta[key] = to_val - from_val

        # Compute norm: ||ΔΨ|| = sqrt(Σ (Δαk)²)
        drift_norm = sum(d**2 for d in delta.values()) ** 0.5

        # Find failed invariants
        failed = []
        for inv, passed in to_state.invariant_results.items():
            if not passed:
                # Check if it was passing in from_state
                if from_state.invariant_results.get(inv, True):
                    failed.append(inv)

        return DriftMeasurement(
            from_commit=from_state.commit_hash,
            to_commit=to_state.commit_hash,
            delta_vector=delta,
            drift_norm=drift_norm,
            failed_invariants=failed,
        )

    def find_first_bad_commit(
        self,
        invariant: str,
        good_commit: str = None,
        bad_commit: str = None,
    ) -> str:
        """Find first commit where invariant fails.

        Args:
            invariant: Invariant name to check
            good_commit: Known good commit (default: earliest)
            bad_commit: Known bad commit (default: HEAD)

        Returns:
            First bad commit hash or None
        """
        commits = self.get_commit_history()
        if not commits:
            return None

        # Determine bounds
        if good_commit is None:
            good_commit = commits[0].commit_hash
        if bad_commit is None:
            bad_commit = commits[-1].commit_hash

        # Binary search through commits
        good_idx = next(
            (i for i, c in enumerate(commits) if c.commit_hash == good_commit),
            0,
        )
        bad_idx = next(
            (i for i, c in enumerate(commits) if c.commit_hash == bad_commit),
            len(commits) - 1,
        )

        # Ensure good is before bad
        if good_idx >= bad_idx:
            return None

        # Simple linear search for now (can optimize with binary search)
        for i in range(good_idx + 1, bad_idx + 1):
            commit = commits[i]
            if invariant in commit.invariant_results:
                if not commit.invariant_results[invariant]:
                    return commit.commit_hash

        return None

    def get_commit_at(self, commit_hash: str) -> Optional[CommitState]:
        """Get state for specific commit."""
        if commit_hash in self._state_cache:
            return self._state_cache[commit_hash]

        # Fetch from git
        commits = self.get_commit_history(max_commits=1000)
        for c in commits:
            if c.commit_hash == commit_hash:
                self._state_cache[commit_hash] = c
                return c

        return None

    def compute_evolution_path(
        self,
        start_commit: str,
        end_commit: str,
    ) -> list[DriftMeasurement]:
        """Compute drift path between two commits.

        Returns:
            List of drift measurements between consecutive commits
        """
        commits = self.get_commit_history()
        if not commits:
            return []

        # Find range
        start_idx = next(
            (i for i, c in enumerate(commits) if c.commit_hash == start_commit),
            None,
        )
        end_idx = next(
            (i for i, c in enumerate(commits) if c.commit_hash == end_commit),
            None,
        )

        if start_idx is None or end_idx is None:
            return []

        # Compute drift for each step
        drifts = []
        for i in range(start_idx, end_idx):
            drift = self.measure_drift(commits[i], commits[i + 1])
            drifts.append(drift)

        return drifts

    def identify_destabilizing_commits(
        self,
        threshold: float = 0.5,
    ) -> list[tuple[str, float]]:
        """Identify commits with high drift.

        Args:
            threshold: Minimum drift to report

        Returns:
            List of (commit_hash, drift_norm) tuples
        """
        commits = self.get_commit_history()
        if len(commits) < 2:
            return []

        destabilizing = []
        for i in range(len(commits) - 1):
            drift = self.measure_drift(commits[i], commits[i + 1])
            if drift.drift_norm > threshold:
                destabilizing.append((commits[i + 1].commit_hash, drift.drift_norm))

        # Sort by drift norm descending
        return sorted(destabilizing, key=lambda x: x[1], reverse=True)
