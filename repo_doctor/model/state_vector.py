"""
Repo Doctor Omega - State Vector Model

Quantum-formal repository state with 11 dimensions:
|Ψ_repo(t)⟩ = αS|Syntax⟩ + αI|Imports⟩ + αT|Types⟩ + αA|API⟩ + αE|Entrypoints⟩ +
             αP|Packaging⟩ + αR|Runtime⟩ + αD|DocsTestsDemos⟩ + αM|Persistence⟩ +
             αH|History⟩ + αSec|Security⟩

Each amplitude αk ∈ [0,1] represents subsystem integrity.
"""

import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class StateDimension(Enum):
    """The 11 dimensions of repository state."""

    SYNTAX = "syntax"  # Parse integrity
    IMPORTS = "imports"  # Import resolution
    TYPES = "types"  # Type system integrity
    API = "api"  # Public contract integrity
    ENTRYPOINTS = "entrypoints"  # Entrypoint validity
    PACKAGING = "packaging"  # Build/package integrity
    RUNTIME = "runtime"  # Runtime surface integrity
    DOCS_TESTS_DEMOS = "docs_tests_demos"  # Documentation/test alignment
    PERSISTENCE = "persistence"  # Serialization roundtrip
    HISTORY = "history"  # Temporal coherence
    SECURITY = "security"  # Security posture


# Severity weights for Hamiltonian (λk)
# Higher = more critical to repo health
DEFAULT_WEIGHTS: dict[StateDimension, float] = {
    StateDimension.SYNTAX: 1.0,
    StateDimension.IMPORTS: 0.9,
    StateDimension.TYPES: 0.8,
    StateDimension.API: 1.0,  # Highest - public contract drift
    StateDimension.ENTRYPOINTS: 0.95,
    StateDimension.PACKAGING: 0.9,
    StateDimension.RUNTIME: 0.85,
    StateDimension.DOCS_TESTS_DEMOS: 0.6,
    StateDimension.PERSISTENCE: 0.7,
    StateDimension.HISTORY: 0.5,
    StateDimension.SECURITY: 0.95,
}

# Hard-fail threshold per dimension
HARD_FAIL_THRESHOLDS: dict[StateDimension, float] = {
    StateDimension.SYNTAX: 0.95,
    StateDimension.IMPORTS: 0.9,
    StateDimension.TYPES: 0.8,
    StateDimension.API: 0.95,
    StateDimension.ENTRYPOINTS: 0.9,
    StateDimension.PACKAGING: 0.9,
    StateDimension.RUNTIME: 0.8,
    StateDimension.DOCS_TESTS_DEMOS: 0.5,
    StateDimension.PERSISTENCE: 0.8,
    StateDimension.HISTORY: 0.5,
    StateDimension.SECURITY: 0.9,
}

# Score penalties for failed dimensions
SCORE_PENALTIES: dict[StateDimension, int] = {
    StateDimension.SYNTAX: 25,
    StateDimension.IMPORTS: 20,
    StateDimension.TYPES: 15,
    StateDimension.API: 25,
    StateDimension.ENTRYPOINTS: 20,
    StateDimension.PACKAGING: 20,
    StateDimension.RUNTIME: 15,
    StateDimension.DOCS_TESTS_DEMOS: 5,
    StateDimension.PERSISTENCE: 10,
    StateDimension.HISTORY: 0,
    StateDimension.SECURITY: 20,
}


@dataclass
class RepoStateVector:
    """
    Repository state vector |Ψ_repo(t)>.

    Represents complete repository health at time t.
    Each dimension normalized to [0,1] where 1 is perfect.
    """

    # State amplitudes for each dimension (αk)
    amplitudes: dict[StateDimension, float] = field(default_factory=dict)

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    commit_hash: str = ""
    branch: str = ""
    repo_path: str = ""

    # Per-dimension failure details
    failures: dict[StateDimension, list[str]] = field(default_factory=dict)

    # Custom weights (optional override)
    weights: dict[StateDimension, float] = field(default_factory=lambda: DEFAULT_WEIGHTS.copy())

    def __post_init__(self):
        """Ensure all dimensions have amplitudes."""
        for dim in StateDimension:
            if dim not in self.amplitudes:
                self.amplitudes[dim] = 1.0  # Default to perfect
            if dim not in self.failures:
                self.failures[dim] = []

    def get(self, dimension: StateDimension) -> float:
        """Get amplitude for specific dimension."""
        return self.amplitudes.get(dimension, 0.0)

    def set(self, dimension: StateDimension, value: float, failures: List[str] = None):
        """Set amplitude for specific dimension."""
        self.amplitudes[dimension] = max(0.0, min(1.0, value))
        if failures:
            self.failures[dimension] = failures

    def energy(self) -> float:
        """
        Calculate repository energy: E_repo = Σ λk (1 - αk)²

        Returns
        -------
            Scalar degradation energy. Low = healthy, high = degraded.

        """
        total = 0.0
        for dim, alpha in self.amplitudes.items():
            weight = self.weights.get(dim, 1.0)
            total += weight * (1 - alpha) ** 2
        return total

    def score(self) -> int:
        """
        Calculate repository score (0-100).

        Score = 100 - Σ penalties for failed dimensions
        """
        score = 100
        for dim, alpha in self.amplitudes.items():
            threshold = HARD_FAIL_THRESHOLDS.get(dim, 0.9)
            if alpha < threshold:
                penalty = SCORE_PENALTIES.get(dim, 5)
                score -= penalty
        return max(0, score)

    def is_healthy(self, threshold: float = 0.9) -> bool:
        """Check if all dimensions meet threshold."""
        return all(alpha >= threshold for alpha in self.amplitudes.values())

    def is_releaseable(self) -> tuple[bool, list[str]]:
        """
        Check if repository is releaseable.

        Hard-fail classes must all pass:
        - syntax, imports, API, entrypoints, packaging
        """
        hard_fail_dims = [
            StateDimension.SYNTAX,
            StateDimension.IMPORTS,
            StateDimension.API,
            StateDimension.ENTRYPOINTS,
            StateDimension.PACKAGING,
        ]

        blockers = []
        for dim in hard_fail_dims:
            threshold = HARD_FAIL_THRESHOLDS.get(dim, 0.9)
            if self.amplitudes.get(dim, 0.0) < threshold:
                blockers.append(f"{dim.value}: {', '.join(self.failures.get(dim, ['failed']))}")

        return len(blockers) == 0, blockers

    def drift(self, other: RepoStateVector) -> dict[StateDimension, float]:
        """
        Calculate temporal drift: ΔΨ(t) = Ψ(t) - Ψ(t-1)
        """
        return {
            dim: self.amplitudes.get(dim, 0.0) - other.amplitudes.get(dim, 0.0)
            for dim in StateDimension
        }

    def drift_norm(self, other: RepoStateVector) -> float:
        """
        Calculate drift magnitude: ||ΔΨ|| = sqrt(Σ (Δαk)²)
        """
        delta = self.drift(other)
        return math.sqrt(sum(d**2 for d in delta.values()))

    def worst_dimensions(self, n: int = 3) -> list[tuple[StateDimension, float]]:
        """Get n worst dimensions by amplitude."""
        sorted_dims = sorted(self.amplitudes.items(), key=lambda x: x[1])
        return sorted_dims[:n]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "timestamp": self.timestamp,
            "commit_hash": self.commit_hash,
            "branch": self.branch,
            "repo_path": self.repo_path,
            "amplitudes": {dim.value: alpha for dim, alpha in self.amplitudes.items()},
            "failures": {dim.value: fails for dim, fails in self.failures.items() if fails},
            "energy": self.energy(),
            "score": self.score(),
            "healthy": self.is_healthy(),
            "releaseable": self.is_releaseable()[0],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RepoStateVector:
        """Deserialize from dictionary."""
        amplitudes = {StateDimension(k): v for k, v in data.get("amplitudes", {}).items()}
        failures = {StateDimension(k): v for k, v in data.get("failures", {}).items()}
        return cls(
            amplitudes=amplitudes,
            failures=failures,
            timestamp=data.get("timestamp"),
            commit_hash=data.get("commit_hash", ""),
            branch=data.get("branch", ""),
            repo_path=data.get("repo_path", ""),
        )

    def __repr__(self) -> str:
        amps = ", ".join(f"{d.value}={a:.2f}" for d, a in self.amplitudes.items())
        return f"RepoStateVector({amps}, energy={self.energy():.3f}, score={self.score()})"


class StateVectorBuilder:
    """Builder for constructing state vectors from sensor data."""

    def __init__(self, repo_path: str = ""):
        self.repo_path = repo_path
        self.amplitudes: dict[StateDimension, float] = {}
        self.failures: dict[StateDimension, list[str]] = {}

    def from_observables(self, observables: Dict[str, float]) -> StateVectorBuilder:
        """
        Build amplitudes from observables using exponential decay:
        αk = exp(-Σj wk,j · oj)
        """
        # Syntax amplitude from parse errors
        if "parse_errors" in observables:
            self.amplitudes[StateDimension.SYNTAX] = math.exp(-observables["parse_errors"] * 0.5)
            if observables["parse_errors"] > 0:
                self.failures[StateDimension.SYNTAX] = [
                    f"{observables['parse_errors']} parse errors"
                ]

        # Import amplitude from unresolved imports
        if "unresolved_imports" in observables:
            self.amplitudes[StateDimension.IMPORTS] = math.exp(
                -observables["unresolved_imports"] * 0.3
            )
            if observables["unresolved_imports"] > 0:
                self.failures[StateDimension.IMPORTS] = [
                    f"{observables['unresolved_imports']} unresolved imports"
                ]

        # API amplitude from signature mismatches
        if "signature_mismatches" in observables:
            self.amplitudes[StateDimension.API] = math.exp(
                -observables["signature_mismatches"] * 0.5
            )
            if observables["signature_mismatches"] > 0:
                self.failures[StateDimension.API] = [
                    f"{observables['signature_mismatches']} API mismatches"
                ]

        # Entrypoint amplitude from missing entrypoints
        if "missing_entrypoints" in observables:
            self.amplitudes[StateDimension.ENTRYPOINTS] = math.exp(
                -observables["missing_entrypoints"] * 0.8
            )
            if observables["missing_entrypoints"] > 0:
                self.failures[StateDimension.ENTRYPOINTS] = [
                    f"{observables['missing_entrypoints']} missing entrypoints"
                ]

        # Test amplitude from test failures
        if "test_failures" in observables:
            total = observables.get("total_tests", 1)
            failures = observables["test_failures"]
            self.amplitudes[StateDimension.DOCS_TESTS_DEMOS] = 1.0 - (failures / max(total, 1))
            if failures > 0:
                self.failures[StateDimension.DOCS_TESTS_DEMOS] = [
                    f"{failures}/{total} tests failed"
                ]

        # Security amplitude from findings
        if "security_findings" in observables:
            critical = observables.get("critical_findings", 0)
            high = observables.get("high_findings", 0)
            self.amplitudes[StateDimension.SECURITY] = math.exp(-(critical * 1.0 + high * 0.5))
            if critical > 0 or high > 0:
                self.failures[StateDimension.SECURITY] = [
                    f"{critical} critical, {high} high severity"
                ]

        # Fill defaults for missing dimensions
        for dim in StateDimension:
            if dim not in self.amplitudes:
                self.amplitudes[dim] = 1.0

        return self

    def build(self) -> RepoStateVector:
        """Construct final state vector."""
        return RepoStateVector(
            amplitudes=self.amplitudes.copy(),
            failures=self.failures.copy(),
            repo_path=self.repo_path,
        )
