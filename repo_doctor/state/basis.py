"""
Repo Doctor Ω∞ - State Basis

The 12 basis states for repository state space:
|S⟩ syntax |I⟩ imports |T⟩ types |A⟩ API |E⟩ entrypoints |Pk⟩ packaging
|Rt⟩ runtime |D⟩ docs/demos/tests |Ps⟩ persistence |St⟩ status |Sec⟩ security |H⟩ history
"""

from __future__ import annotations

from enum import Enum


class StateDimension(Enum):
    """12 dimensions of repository state space."""

    SYNTAX = "syntax"  # |S⟩ parse integrity
    IMPORTS = "imports"  # |I⟩ import resolution
    TYPES = "types"  # |T⟩ type/signature integrity
    API = "api"  # |A⟩ public API contract
    ENTRYPOINTS = "entrypoints"  # |E⟩ entrypoint/launcher integrity
    PACKAGING = "packaging"  # |Pk⟩ build/packaging integrity
    RUNTIME = "runtime"  # |Rt⟩ runtime behavior
    DOCS_TESTS_DEMOS = "docs_tests_demos"  # |D⟩ documentation alignment
    PERSISTENCE = "persistence"  # |Ps⟩ serialization roundtrip
    STATUS = "status"  # |St⟩ status truthfulness
    SECURITY = "security"  # |Sec⟩ security posture
    HISTORY = "history"  # |H⟩ temporal stability


class StateBasis:
    """
    Basis state management for repository Hilbert space.
    """

    # Severity weights for Hamiltonian (λk)
    WEIGHTS: dict[StateDimension, float] = {
        StateDimension.SYNTAX: 100.0,
        StateDimension.IMPORTS: 90.0,
        StateDimension.TYPES: 70.0,
        StateDimension.API: 95.0,
        StateDimension.ENTRYPOINTS: 90.0,
        StateDimension.PACKAGING: 90.0,
        StateDimension.RUNTIME: 80.0,
        StateDimension.PERSISTENCE: 70.0,
        StateDimension.STATUS: 65.0,
        StateDimension.SECURITY: 100.0,
        StateDimension.DOCS_TESTS_DEMOS: 35.0,
        StateDimension.HISTORY: 55.0,
    }

    # Collapse thresholds (θk)
    THRESHOLDS: dict[StateDimension, float] = {
        StateDimension.SYNTAX: 0.95,
        StateDimension.IMPORTS: 0.90,
        StateDimension.TYPES: 0.80,
        StateDimension.API: 0.95,
        StateDimension.ENTRYPOINTS: 0.90,
        StateDimension.PACKAGING: 0.90,
        StateDimension.RUNTIME: 0.80,
        StateDimension.PERSISTENCE: 0.80,
        StateDimension.STATUS: 0.85,
        StateDimension.SECURITY: 0.95,
        StateDimension.DOCS_TESTS_DEMOS: 0.50,
        StateDimension.HISTORY: 0.60,
    }

    @classmethod
    def get_weight(cls, dim: StateDimension) -> float:
        """Get Hamiltonian weight for dimension."""
        return cls.WEIGHTS.get(dim, 50.0)

    @classmethod
    def get_threshold(cls, dim: StateDimension) -> float:
        """Get collapse threshold for dimension."""
        return cls.THRESHOLDS.get(dim, 0.80)

    @classmethod
    def all_dimensions(cls) -> list[StateDimension]:
        """Return all basis dimensions."""
        return list(StateDimension)

    @classmethod
    def hard_fail_dimensions(cls) -> list[StateDimension]:
        """Dimensions that cause hard failure when collapsed."""
        return [
            StateDimension.SYNTAX,
            StateDimension.IMPORTS,
            StateDimension.API,
            StateDimension.ENTRYPOINTS,
            StateDimension.PACKAGING,
            StateDimension.SECURITY,
        ]
