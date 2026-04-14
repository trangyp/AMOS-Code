"""Repo Doctor Ω∞∞∞ - Repository Verification, Dynamics, and Control System

A formal mathematical framework for repository integrity verification,
combining program analysis, graph theory, and optimization.

Mathematical Foundation:
- Repository state vectors in 12-dimensional integrity space
- Hamiltonian degradation model
- Observable fact generation
- SMT-based invariant verification
- Repair optimization

External Substrate Integration:
- Tree-sitter for syntax analysis
- CodeQL for semantic queries
- Joern for code property graphs
- Z3 for satisfiability solving
- Semgrep for fast rule execution
- git bisect for temporal localization
- Sourcegraph for fleet-scale changes

Creator: Trang Phan
Version: Ω∞∞∞.1.0.0
"""

__version__ = "1.0.0"
__codename__ = "OmegaInfinity"

from .invariants.hard import HardInvariant, InvariantResult
from .state.basis import BasisVector, RepositoryState
from .state.observables import Observable, ObservableKind

__all__ = [
    "RepositoryState",
    "BasisVector",
    "Observable",
    "ObservableKind",
    "HardInvariant",
    "InvariantResult",
]
