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
    ArchitectureDriftInvariant,
    ArchitectureInvariantEngine,
    AuthorityInvariant,
    BoundaryInvariant,
    FolkloreInvariant,
    HiddenInterfaceInvariant,
    PlaneSeparationInvariant,
    UpgradeGeometryInvariant,
)
from .architecture import (
    ArchEdge,
    ArchEdgeType,
    ArchitectureBuilder,
    ArchitectureGraph,
    ArchNode,
    ArchNodeType,
    PlaneType,
    build_architecture_graph,
)
from .bisect_engine import BisectEngine, BisectResult
from .cli import main
from .contracts import ContractAnalyzer
from .entrypoints import EntrypointAnalyzer
from .history import DriftAnalyzer
# Modular invariants (18 total)
from .invariants import (
    APIInvariant,
    ArtifactInvariant,
    AuthorizationInvariant,
    EntrypointInvariant,
    EnvironmentInvariant,
    HistoryInvariant,
    ImportInvariant,
    Invariant,
    InvariantEngine,
    InvariantResult,
    InvariantSeverity,
    MigrationInvariant,
    ObservabilityInvariant,
    PackagingInvariant,
    ParseInvariant,
    PerformanceInvariant,
    PersistenceInvariant,
    RuntimeInvariant,
    SecurityInvariant,
    StatusInvariant,
    TestsInvariant,
    TypeInvariant,
)
from .packaging import PackagingAnalyzer
from .persistence import PersistenceAnalyzer
from .repair_optimizer import (
    RepairPlan,
)
from .repair_plan import RepairPlan, RepairPlanner
from .sensors import SensorResult, SensorSuite
from .state_vector import RepoStateVector, StateDimension

# Ω∞∞∞ Triple-Infinity modules

__version__ = "0.2.0-arch"
__all__ = [
    # Core state
    "RepoStateVector",
    "StateDimension",
    # Modular invariants (Ω∞ system)
    "Invariant",
    "InvariantResult",
    "InvariantSeverity",
    "InvariantEngine",
    "ParseInvariant",
    "ImportInvariant",
    "TypeInvariant",
    "APIInvariant",
    "EntrypointInvariant",
    "PackagingInvariant",
    "RuntimeInvariant",
    "PersistenceInvariant",
    "StatusInvariant",
    "TestsInvariant",
    "SecurityInvariant",
    "HistoryInvariant",
    "ArtifactInvariant",
    "AuthorizationInvariant",
    "EnvironmentInvariant",
    "MigrationInvariant",
    "ObservabilityInvariant",
    "PerformanceInvariant",
    # Architectural layer
    "ArchInvariantResult",
    "ArchitectureInvariantEngine",
    "BoundaryInvariant",
    "AuthorityInvariant",
    "PlaneSeparationInvariant",
    "HiddenInterfaceInvariant",
    "FolkloreInvariant",
    "ArchitectureDriftInvariant",
    "UpgradeGeometryInvariant",
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
    "DriftAnalyzer",
    # Tools
    "BisectEngine",
    "BisectResult",
    "RepairPlanner",
    "RepairPlan",
    "SensorSuite",
    "SensorResult",
    "main",
]
