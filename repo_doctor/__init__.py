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

# NOTE: All submodule imports are lazy-loaded via __getattr__ below
# to avoid ~30ms cumulative import time when any repo_doctor module is imported

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

# Lazy loading cache
_lazy_modules: dict[str, object] = {}


def __getattr__(name: str) -> object:
    """Lazy load submodules on first access."""
    if name in _lazy_modules:
        return _lazy_modules[name]

    # Map of names to their module and attribute
    _import_map = {
        # state_vector
        "RepoStateVector": (".state_vector", "RepoStateVector"),
        "StateDimension": (".state_vector", "StateDimension"),
        # invariants
        "Invariant": (".invariants", "Invariant"),
        "InvariantResult": (".invariants", "InvariantResult"),
        "InvariantSeverity": (".invariants", "InvariantSeverity"),
        "InvariantEngine": (".invariants", "InvariantEngine"),
        "ParseInvariant": (".invariants", "ParseInvariant"),
        "ImportInvariant": (".invariants", "ImportInvariant"),
        "TypeInvariant": (".invariants", "TypeInvariant"),
        "APIInvariant": (".invariants", "APIInvariant"),
        "EntrypointInvariant": (".invariants", "EntrypointInvariant"),
        "PackagingInvariant": (".invariants", "PackagingInvariant"),
        "RuntimeInvariant": (".invariants", "RuntimeInvariant"),
        "PersistenceInvariant": (".invariants", "PersistenceInvariant"),
        "StatusInvariant": (".invariants", "StatusInvariant"),
        "TestsInvariant": (".invariants", "TestsInvariant"),
        "SecurityInvariant": (".invariants", "SecurityInvariant"),
        "HistoryInvariant": (".invariants", "HistoryInvariant"),
        "ArtifactInvariant": (".invariants", "ArtifactInvariant"),
        "AuthorizationInvariant": (".invariants", "AuthorizationInvariant"),
        "EnvironmentInvariant": (".invariants", "EnvironmentInvariant"),
        "MigrationInvariant": (".invariants", "MigrationInvariant"),
        "ObservabilityInvariant": (".invariants", "ObservabilityInvariant"),
        "PerformanceInvariant": (".invariants", "PerformanceInvariant"),
        # arch_invariants
        "ArchInvariantResult": (".arch_invariants", "ArchInvariantResult"),
        "ArchitectureInvariantEngine": (".arch_invariants", "ArchitectureInvariantEngine"),
        "BoundaryInvariant": (".arch_invariants", "BoundaryInvariant"),
        "AuthorityInvariant": (".arch_invariants", "AuthorityInvariant"),
        "PlaneSeparationInvariant": (".arch_invariants", "PlaneSeparationInvariant"),
        "HiddenInterfaceInvariant": (".arch_invariants", "HiddenInterfaceInvariant"),
        "FolkloreInvariant": (".arch_invariants", "FolkloreInvariant"),
        "ArchitectureDriftInvariant": (".arch_invariants", "ArchitectureDriftInvariant"),
        "UpgradeGeometryInvariant": (".arch_invariants", "UpgradeGeometryInvariant"),
        # architecture
        "ArchitectureGraph": (".architecture", "ArchitectureGraph"),
        "ArchitectureBuilder": (".architecture", "ArchitectureBuilder"),
        "ArchNode": (".architecture", "ArchNode"),
        "ArchNodeType": (".architecture", "ArchNodeType"),
        "ArchEdge": (".architecture", "ArchEdge"),
        "ArchEdgeType": (".architecture", "ArchEdgeType"),
        "PlaneType": (".architecture", "PlaneType"),
        "build_architecture_graph": (".architecture", "build_architecture_graph"),
        # analyzers
        "ContractAnalyzer": (".contracts", "ContractAnalyzer"),
        "PackagingAnalyzer": (".packaging", "PackagingAnalyzer"),
        "EntrypointAnalyzer": (".entrypoints", "EntrypointAnalyzer"),
        "PersistenceAnalyzer": (".persistence", "PersistenceAnalyzer"),
        "DriftAnalyzer": (".history", "DriftAnalyzer"),
        # tools
        "BisectEngine": (".bisect_engine", "BisectEngine"),
        "BisectResult": (".bisect_engine", "BisectResult"),
        "RepairPlanner": (".repair_plan", "RepairPlanner"),
        "RepairPlan": (".repair_plan", "RepairPlan"),
        "SensorSuite": (".sensors", "SensorSuite"),
        "SensorResult": (".sensors", "SensorResult"),
        "main": (".cli", "main"),
    }

    if name in _import_map:
        module_path, attr_name = _import_map[name]
        module = __import__(module_path, globals(), locals(), [attr_name], 1)
        result = getattr(module, attr_name)
        _lazy_modules[name] = result
        return result

    raise AttributeError(f"module 'repo_doctor' has no attribute '{name}'")
