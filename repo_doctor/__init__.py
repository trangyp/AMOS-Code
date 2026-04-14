"""
Repo Doctor - Deterministic Repository Diagnostic System

A quantum-inspired state-space model for repository health analysis.

Core equation:
    Ψ_repo(t) = [s(t), i(t), b(t), τ(t), p(t), a(t), d(t), c(t), h(t), σ(t),
                 αArch(t), αHidden(t)]

Invariant law:
    ∀ I_n ∈ I : I_n(Ψ_repo) = 1

Architectural layer:
    G_arch = (V_arch, E_arch, Φ_arch)
    I_arch = {I_boundary, I_authority, I_plane_sep, I_hidden, I_folklore, ...}
"""

from .arch_invariants import (
    ArchInvariantResult,
    ArchitectureInvariantEngine,
    BoundaryInvariant,
    AuthorityInvariant,
)
from .architecture import (
    ArchEdge,
    ArchEdgeType,
    ArchNode,
    ArchNodeType,
    ArchitectureGraph,
    ArchitectureBuilder,
    PlaneType,
    build_architecture_graph,
)
from .bisect_engine import BisectEngine, BisectResult
from .cli import main
from .contracts import ContractAnalyzer
from .entrypoints import EntrypointAnalyzer
from .history import HistoryAnalyzer
from .invariants_legacy import InvariantEngine, InvariantResult
from .packaging import PackagingAnalyzer
from .persistence import PersistenceAnalyzer
from .repair_plan import RepairPlan, RepairPlanner
from .sensors import SensorResult, SensorSuite
from .state_vector import RepoStateVector, StateDimension

__version__ = "0.2.0-arch"
__all__ = [
    # Core state
    "RepoStateVector",
    "StateDimension",
    # Legacy invariants
    "InvariantEngine",
    "InvariantResult",
    # Architectural layer
    "ArchInvariantResult",
    "ArchitectureInvariantEngine",
    "BoundaryInvariant",
    "AuthorityInvariant",
    "ArchitectureGraph",
    "ArchitectureBuilder",
    "ArchNode",
    "ArchNodeType",
    "ArchEdge",
    "ArchEdgeType",
    "PlaneType",
    "build_architecture_graph",
    # Analyzers
    "ContractAnalyzer",
    "PackagingAnalyzer",
    "EntrypointAnalyzer",
    "PersistenceAnalyzer",
    "HistoryAnalyzer",
    # Tools
    "BisectEngine",
    "BisectResult",
    "RepairPlanner",
    "RepairPlan",
    "SensorSuite",
    "SensorResult",
    "main",
]
