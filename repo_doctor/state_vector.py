"""
State Vector Module - Quantum-inspired Repository State Model

Defines the repository state vector Ψ_repo(t) and operations on it.

Extended state vector with architectural layer:
    Ψ_repo(t) = [
        s(t),       # syntax integrity
        i(t),       # import / module integrity
        b(t),       # build integrity
        τ(t),       # test integrity
        p(t),       # packaging integrity
        a(t),       # API contract integrity
        d(t),       # dependency integrity
        c(t),       # config / entrypoint integrity
        h(t),       # history stability
        σ(t),       # security integrity
        αArch(t),   # architectural integrity
        αHidden(t)  # hidden state integrity
    ]

All dimensions normalized to [0, 1].

Architecture layer captures:
    - Boundary integrity (I_boundary)
    - Authority distribution (I_authority)
    - Plane separation (I_plane_separation)
    - Hidden interfaces (I_interface_visibility)
    - Folklore dependencies (I_folklore_free)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StateDimension(Enum):
    """The 12 dimensions of repository state (10 local + 2 architectural)."""

    SYNTAX = "s"  # s(t) - syntax integrity
    IMPORT = "i"  # i(t) - import/module integrity
    BUILD = "b"  # b(t) - build integrity
    TEST = "tau"  # τ(t) - test integrity
    PACKAGING = "p"  # p(t) - packaging integrity
    API = "a"  # a(t) - API contract integrity
    DEPENDENCY = "d"  # d(t) - dependency integrity
    CONFIG = "c"  # c(t) - config/entrypoint integrity
    HISTORY = "h"  # h(t) - history stability
    SECURITY = "sigma"  # σ(t) - security integrity
    ARCHITECTURE = "arch"  # αArch(t) - architectural integrity
    HIDDEN_STATE = "hs"  # αHidden(t) - hidden state integrity


STATE_DIMENSIONS = list(StateDimension)

# Default weights for energy calculation
DEFAULT_WEIGHTS: dict[StateDimension, float] = {
    StateDimension.SYNTAX: 1.0,
    StateDimension.IMPORT: 1.0,
    StateDimension.BUILD: 0.9,
    StateDimension.TEST: 0.8,
    StateDimension.PACKAGING: 1.0,
    StateDimension.API: 0.9,
    StateDimension.DEPENDENCY: 0.7,
    StateDimension.CONFIG: 0.8,
    StateDimension.HISTORY: 0.5,
    StateDimension.SECURITY: 1.0,
    StateDimension.ARCHITECTURE: 0.85,  # Architectural integrity
    StateDimension.HIDDEN_STATE: 0.6,  # Hidden state modeling
}

# Scoring penalties (from spec)
SCORE_PENALTIES = {
    StateDimension.SYNTAX: 20,
    StateDimension.IMPORT: 20,
    StateDimension.BUILD: 0,  # Build failures cascade to other dimensions
    StateDimension.TEST: 0,
    StateDimension.PACKAGING: 20,
    StateDimension.API: 15,
    StateDimension.DEPENDENCY: 0,
    StateDimension.CONFIG: 10,
    StateDimension.HISTORY: 0,
    StateDimension.SECURITY: 10,
    StateDimension.ARCHITECTURE: 15,  # Architectural failures are significant
    StateDimension.HIDDEN_STATE: 5,  # Hidden state issues are warnings
}

# Hard-fail classes (release blocking)
HARD_FAIL_DIMENSIONS = {
    StateDimension.SYNTAX,
    StateDimension.IMPORT,
    StateDimension.PACKAGING,
    StateDimension.API,
    StateDimension.CONFIG,
}


@dataclass
class RepoStateVector:
    """
    Quantum-inspired repository state vector.

    Represents the complete health state of a repository at time t.
    Each dimension is normalized to [0, 1] where 1 is perfect health.
    """

    # State values for each dimension
    values: dict[StateDimension, float] = field(default_factory=dict)

    # Metadata
    timestamp: str | None = None
    commit_hash: str | None = None
    branch: str | None = None

    # Per-dimension failure details
    failures: dict[StateDimension, list[str]] = field(default_factory=dict)

    # Custom weights (optional)
    weights: dict[StateDimension, float] = field(default_factory=lambda: DEFAULT_WEIGHTS.copy())

    def __post_init__(self):
        """Ensure all dimensions have values, defaulting to 0."""
        for dim in STATE_DIMENSIONS:
            if dim not in self.values:
                self.values[dim] = 0.0
            if dim not in self.failures:
                self.failures[dim] = []

    def get(self, dimension: StateDimension) -> float:
        """Get value for a specific dimension."""
        return self.values.get(dimension, 0.0)

    def set(self, dimension: StateDimension, value: float, failures: list[str] | None = None):
        """Set value for a specific dimension."""
        self.values[dimension] = max(0.0, min(1.0, value))
        if failures:
            self.failures[dimension] = failures

    def is_healthy(self, threshold: float = 1.0) -> bool:
        """
        Check if repository is fully healthy.

        Healthy repo: Ψ_repo ≈ 1⃗ (all dimensions at 1.0)
        """
        return all(v >= threshold for v in self.values.values())

    def is_releaseable(self) -> tuple[bool, list[str]]:
        """
        Check if repository is releaseable.

        Hard-fail classes must all pass:
        - parse (syntax)
        - import
        - packaging
        - API
        - entrypoints (config)
        """
        blockers = []
        for dim in HARD_FAIL_DIMENSIONS:
            if self.values.get(dim, 0.0) < 1.0:
                blockers.append(f"{dim.value}: {', '.join(self.failures.get(dim, ['failed']))}")
        return len(blockers) == 0, blockers

    def energy(self) -> float:
        """
        Calculate repo energy: E_repo = Σ w_k · (1 - Ψ_k)^2

        Low energy = stable
        High energy = structurally degraded
        """
        total = 0.0
        for dim, value in self.values.items():
            weight = self.weights.get(dim, 1.0)
            total += weight * (1 - value) ** 2
        return total

    def score(self) -> int:
        """
        Calculate repo score (0-100).

        Score_repo = 100 - Σ penalties for failed dimensions
        """
        score = 100
        for dim, value in self.values.items():
            if value < 1.0:
                penalty = SCORE_PENALTIES.get(dim, 5)
                score -= penalty
        return max(0, score)

    def delta(self, other: RepoStateVector) -> dict[StateDimension, float]:
        """
        Calculate temporal drift: ΔΨ(t) = Ψ_repo(t) - Ψ_repo(t-1)
        """
        return {
            dim: self.values.get(dim, 0.0) - other.values.get(dim, 0.0) for dim in STATE_DIMENSIONS
        }

    def drift_magnitude(self, other: RepoStateVector) -> float:
        """
        Calculate drift magnitude: ||ΔΨ(t)|| = sqrt(Σ (ΔΨ_k)^2)
        """
        delta = self.delta(other)
        return math.sqrt(sum(d**2 for d in delta.values()))

    def worst_dimensions(self, n: int = 3) -> list[tuple[StateDimension, float]]:
        """Get the n worst dimensions by value."""
        sorted_dims = sorted(self.values.items(), key=lambda x: x[1])
        return sorted_dims[:n]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "timestamp": self.timestamp,
            "commit_hash": self.commit_hash,
            "branch": self.branch,
            "values": {dim.value: val for dim, val in self.values.items()},
            "failures": {dim.value: fails for dim, fails in self.failures.items() if fails},
            "energy": self.energy(),
            "score": self.score(),
            "healthy": self.is_healthy(),
            "releaseable": self.is_releaseable()[0],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RepoStateVector:
        """Deserialize from dictionary."""
        values = {StateDimension(k): v for k, v in data.get("values", {}).items()}
        failures = {StateDimension(k): v for k, v in data.get("failures", {}).items()}
        return cls(
            values=values,
            failures=failures,
            timestamp=data.get("timestamp"),
            commit_hash=data.get("commit_hash"),
            branch=data.get("branch"),
        )

    def __repr__(self) -> str:
        vals = ", ".join(f"{d.value}={v:.2f}" for d, v in self.values.items())
        return f"RepoStateVector({vals}, energy={self.energy():.3f}, score={self.score()})"


def collapse_failure(state: RepoStateVector) -> str | None:
    """
    Failure localization operator.

    C_fail(Ψ_repo) → argmin subsystem S such that I_S = 0

    Returns the smallest failing subsystem category.
    """
    # Map dimensions to subsystems
    subsystem_map = {
        StateDimension.SYNTAX: "syntax",
        StateDimension.IMPORT: "imports",
        StateDimension.BUILD: "build",
        StateDimension.TEST: "tests",
        StateDimension.PACKAGING: "packaging",
        StateDimension.API: "api_contracts",
        StateDimension.DEPENDENCY: "dependencies",
        StateDimension.CONFIG: "entrypoints",
        StateDimension.HISTORY: "history",
        StateDimension.SECURITY: "security",
        StateDimension.ARCHITECTURE: "architecture",
        StateDimension.HIDDEN_STATE: "hidden_state",
    }

    # Find failing dimensions
    failing = [dim for dim, val in state.values.items() if val < 1.0]

    if not failing:
        return None

    # Priority order for collapse (most specific first)
    priority = [
        StateDimension.PACKAGING,
        StateDimension.CONFIG,
        StateDimension.API,
        StateDimension.ARCHITECTURE,
        StateDimension.IMPORT,
        StateDimension.SYNTAX,
        StateDimension.BUILD,
        StateDimension.TEST,
        StateDimension.DEPENDENCY,
        StateDimension.SECURITY,
        StateDimension.HIDDEN_STATE,
        StateDimension.HISTORY,
    ]

    for dim in priority:
        if dim in failing:
            return subsystem_map[dim]

    return "unknown"


def format_state_report(state: RepoStateVector) -> str:
    """Generate a formatted state report."""
    lines = [
        "=" * 60,
        "REPO STATE VECTOR REPORT",
        "=" * 60,
        f"Commit: {state.commit_hash or 'N/A'}",
        f"Branch: {state.branch or 'N/A'}",
        f"Timestamp: {state.timestamp or 'N/A'}",
        "-" * 60,
    ]

    for dim in STATE_DIMENSIONS:
        val = state.values.get(dim, 0.0)
        status = "✓" if val >= 1.0 else "✗"
        lines.append(f"  [{status}] {dim.value:6} = {val:.3f}")
        for fail in state.failures.get(dim, []):
            lines.append(f"      → {fail}")

    lines.extend(
        [
            "-" * 60,
            f"Energy:        {state.energy():.4f}",
            f"Score:         {state.score()}/100",
            f"Healthy:       {state.is_healthy()}",
        ]
    )

    releaseable, blockers = state.is_releaseable()
    lines.append(f"Releaseable:   {releaseable}")
    if blockers:
        lines.append("  Blockers:")
        for b in blockers:
            lines.append(f"    - {b}")

    collapsed = collapse_failure(state)
    if collapsed:
        lines.append(f"Collapsed Subsystem: {collapsed}")

    lines.append("=" * 60)

    return "\n".join(lines)
