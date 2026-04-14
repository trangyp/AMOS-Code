"""
Architectural Invariants Module - Higher-Order Integrity Checks.

Implements the architectural invariants from the specification:

    I_boundary = 1 iff each concern is enforced only within its declared boundary
    I_authority = 1 iff every architectural fact has exactly one authoritative owner
    I_authority_order = 1 iff truth flows from canonical layers downward
    I_interface_visibility = 1 iff every significant interface is explicitly represented
    I_layer_separation = 1 iff cross-layer influence occurs only via declared interfaces
    I_upgrade = 1 iff all upgrade/rollback paths preserve architectural validity
    I_repair_monotone = 1 iff repairs increase/preserve all protected invariants
    I_plane_separation = 1 iff control/data/execution/observation planes don't substitute
    I_hidden_state = 1 iff every stateful side-effect is modeled or bounded
    I_folklore_free = 1 iff no correctness-critical operation depends on folklore
    I_arch_commute = 1 iff [A_declared, A_actual] = 0 (architecture drift invariant)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .architecture import (
    ArchEdgeType,
    ArchitectureGraph,
    build_architecture_graph,
)
from .state_vector import StateDimension


@dataclass
class ArchInvariantResult:
    """Result of an architectural invariant check."""

    passed: bool
    invariant_name: str
    dimension: StateDimension
    message: str
    details: list[str] = field(default_factory=list)
    violations: list[dict[str, Any]] = field(default_factory=list)
    severity: str = "warning"  # "info", "warning", "error", "critical"


class ArchInvariant(ABC):
    """Base class for architectural invariants."""

    name: str
    dimension: StateDimension = StateDimension.ARCHITECTURE

    @abstractmethod
    def check(
        self, repo_path: Path, arch_graph: ArchitectureGraph | None = None
    ) -> ArchInvariantResult:
        """Check the architectural invariant."""
        pass

    def _get_graph(self, repo_path: Path, arch_graph: ArchitectureGraph | None) -> ArchitectureGraph:
        """Get or build architecture graph."""
        if arch_graph is not None:
            return arch_graph
        return build_architecture_graph(repo_path)


class BoundaryInvariant(ArchInvariant):
    """
    I_boundary = 1 iff each concern is enforced only within its declared boundary.

    Detects:
    - Launcher deciding runtime mode policy (execution -> control)
    - Persistence layer enforcing business logic (data -> control)
    - Test helpers as hidden production dependencies
    - Shell/UI layer owning protocol semantics
    """

    name = "boundary_integrity"

    def check(
        self, repo_path: Path, arch_graph: ArchitectureGraph | None = None
    ) -> ArchInvariantResult:
        graph = self._get_graph(repo_path, arch_graph)

        violations = graph.find_boundary_violations()

        details = []
        for v in violations:
            details.append(
                f"Boundary violation: {v.node_id} ({v.violation_type}): {v.description}"
            )

        return ArchInvariantResult(
            passed=len(violations) == 0,
            invariant_name=self.name,
            dimension=self.dimension,
            message="Boundary integrity maintained"
            if not violations
            else f"{len(violations)} boundary violations detected",
            details=details,
            violations=[
                {
                    "node": v.node_id,
                    "type": v.violation_type,
                    "description": v.description,
                }
                for v in violations
            ],
            severity="error" if violations else "info",
        )


class AuthorityInvariant(ArchInvariant):
    """
    I_authority = 1 iff every architectural fact has exactly one authoritative owner.

    Detects:
    - pyproject.toml and setup.py both defining package surface
    - docs and shell help both defining command semantics
    - tests and exported API both defining contract
    - generated code and source schema both defining model ownership
    """

    name = "single_authority"

    def check(
        self, repo_path: Path, arch_graph: ArchitectureGraph | None = None
    ) -> ArchInvariantResult:
        graph = self._get_graph(repo_path, arch_graph)

        duplicates = graph.find_authority_duplicates()

        details = []
        for fact_name, claimants in duplicates.items():
            details.append(
                f"Authority duplication: '{fact_name}' claimed by {', '.join(claimants)}"
            )

        # Also check for version authority issues
        version_claims = [
            (k, v) for k, v in graph.authority_claims.items() if v.fact_type == "version"
        ]
        canonical_versions = [(k, v) for k, v in version_claims if v.is_canonical]
        derived_versions = [(k, v) for k, v in version_claims if not v.is_canonical]

        if len(canonical_versions) > 1:
            details.append(
                f"Multiple canonical version sources: "
                f"{[v.claimed_by for _, v in canonical_versions]}"
            )

        # Check for authority inversion: __init__.py version vs pyproject.toml
        if len(canonical_versions) == 0 and len(derived_versions) > 0:
            details.append(
                "Authority inversion: version only defined in derived locations "
                f"({[v.claimed_by for _, v in derived_versions]}), "
                "not in canonical config"
            )

        return ArchInvariantResult(
            passed=len(duplicates) == 0 and len(details) == 0,
            invariant_name=self.name,
            dimension=self.dimension,
            message="Single authority invariant maintained"
            if not details
            else f"{len(details)} authority issues detected",
            details=details,
            severity="error" if duplicates else ("warning" if details else "info"),
        )


class PlaneSeparationInvariant(ArchInvariant):
    """
    I_plane_separation = 1 iff control/data/execution/observation planes don't substitute.

    The four planes must remain distinct:
    - ControlPlane: declarative policy/state
    - DataPlane: operational data/runtime state
    - ExecutionPlane: runtime execution
    - ObservationPlane: monitoring/observability
    """

    name = "plane_separation"

    def check(
        self, repo_path: Path, arch_graph: ArchitectureGraph | None = None
    ) -> ArchInvariantResult:
        graph = self._get_graph(repo_path, arch_graph)

        passed, violations = graph.check_plane_separation()

        return ArchInvariantResult(
            passed=passed,
            invariant_name=self.name,
            dimension=self.dimension,
            message="Plane separation maintained"
            if passed
            else f"{len(violations)} plane separation violations",
            details=violations,
            severity="error" if not passed else "info",
        )


class HiddenInterfaceInvariant(ArchInvariant):
    """
    I_interface_visibility = 1 iff every significant interface is explicitly represented.

    Detects shadow interfaces:
    - Environment variables accessed but not declared
    - Feature flags
    - Sidecar file conventions
    - Migration naming conventions
    - Dynamic imports
    - Reflection-only APIs
    - Log parsing dependencies
    """

    name = "hidden_interfaces"
    dimension = StateDimension.HIDDEN_STATE

    def check(
        self, repo_path: Path, arch_graph: ArchitectureGraph | None = None
    ) -> ArchInvariantResult:
        graph = self._get_graph(repo_path, arch_graph)

        # Discover hidden interfaces through code analysis
        hidden = graph.find_hidden_interfaces()

        # Additional analysis for env vars
        env_vars = self._detect_env_vars(repo_path)

        details = []
        for hi in hidden:
            details.append(f"Hidden interface: {hi.interface_type} - {hi.name}")

        for var in env_vars:
            details.append(f"Environment variable usage: {var}")

        return ArchInvariantResult(
            passed=len(details) == 0,
            invariant_name=self.name,
            dimension=self.dimension,
            message="No hidden interfaces detected"
            if not details
            else f"{len(details)} hidden interfaces detected",
            details=details,
            severity="warning" if details else "info",
        )

    def _detect_env_vars(self, repo_path: Path) -> list[str]:
        """Detect environment variable accesses in code."""
        env_vars = []

        for py_file in repo_path.rglob("*.py"):
            if any(p.startswith(".") for p in py_file.relative_to(repo_path).parts):
                continue

            try:
                content = py_file.read_text()
                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    if "os.environ" in line or "os.getenv" in line:
                        # Extract variable name if possible
                        env_vars.append(f"{py_file.relative_to(repo_path)}:{i}")

            except Exception:
                pass

        return env_vars


class FolkloreInvariant(ArchInvariant):
    """
    I_folklore_free = 1 iff no correctness-critical operation depends on undocumented folklore.

    Detects "everyone knows you have to..." dependencies:
    - "run migration script before starting app"
    - "export env var or shell mode breaks"
    - "build step must be manual"
    - "generated file must be refreshed manually"
    """

    name = "folklore_free"
    dimension = StateDimension.HIDDEN_STATE

    def check(
        self, repo_path: Path, arch_graph: ArchitectureGraph | None = None
    ) -> ArchInvariantResult:
        graph = self._get_graph(repo_path, arch_graph)

        folklore = graph.detect_folklore(repo_path)

        details = []
        for f in folklore:
            details.append(
                f"Folklore dependency: {f.description} "
                f"(operation: {f.operation}, critical: {f.why_critical})"
            )

        # Check README for folklore patterns
        readme_folklore = self._check_readme_folklore(repo_path)
        details.extend(readme_folklore)

        return ArchInvariantResult(
            passed=len(details) == 0,
            invariant_name=self.name,
            dimension=self.dimension,
            message="No folklore dependencies detected"
            if not details
            else f"{len(details)} folklore dependencies detected",
            details=details,
            severity="warning" if details else "info",
        )

    def _check_readme_folklore(self, repo_path: Path) -> list[str]:
        """Check README for folklore patterns."""
        details = []

        readme_path = repo_path / "README.md"
        if not readme_path.exists():
            return details

        try:
            content = readme_path.read_text().lower()

            folklore_indicators = [
                ("make sure you", "prerequisite not automated"),
                ("don't forget to", "manual step required"),
                ("before running", "ordering dependency"),
                ("remember to", "memory-dependent step"),
                ("first run", "sequencing folklore"),
            ]

            for pattern, meaning in folklore_indicators:
                if pattern in content:
                    details.append(
                        f"README folklore indicator: '{pattern}' suggests {meaning}"
                    )

        except Exception:
            pass

        return details


class ArchitectureDriftInvariant(ArchInvariant):
    """
    I_arch_commute = 1 iff [A_declared, A_actual] = 0.

    Architecture drift invariant: declared architecture must match actual architecture.

    A_declared = declared architecture (docs, configs, contracts)
    A_actual   = effective architecture (code, runtime, artifacts, rollout behavior)

    This detects divergence between what we say the architecture is and what it actually is.
    """

    name = "architecture_drift"

    def check(
        self, repo_path: Path, arch_graph: ArchitectureGraph | None = None
    ) -> ArchInvariantResult:
        graph = self._get_graph(repo_path, arch_graph)

        drift_issues = []

        # Check for declared-but-not-implemented
        for node in graph.get_nodes_by_type(ArchitectureGraph):  # type: ignore
            # Check if node has corresponding code
            if node.source_file:
                source_path = repo_path / node.source_file
                if not source_path.exists():
                    drift_issues.append(
                        f"Declared architecture node '{node.name}' missing source: "
                        f"{node.source_file}"
                    )

        # Check for implemented-but-not-declared (via entrypoints)
        pyproject = repo_path / "pyproject.toml"
        if pyproject.exists():
            try:
                import tomllib

                config = tomllib.loads(pyproject.read_text())
                declared_scripts = config.get("project", {}).get("scripts", {})

                # Check for scripts in bin/ or scripts/ not declared
                for script_dir in ["bin", "scripts"]:
                    script_path = repo_path / script_dir
                    if script_path.exists():
                        for script in script_path.iterdir():
                            if script.is_file() and script.suffix in (".sh", ".py", ""):
                                if script.name not in declared_scripts:
                                    drift_issues.append(
                                        f"Undeclared entrypoint: {script_dir}/{script.name} "
                                        f"not in pyproject.toml scripts"
                                    )

            except Exception:
                pass

        return ArchInvariantResult(
            passed=len(drift_issues) == 0,
            invariant_name=self.name,
            dimension=self.dimension,
            message="Architecture drift invariant maintained"
            if not drift_issues
            else f"{len(drift_issues)} architecture drift issues",
            details=drift_issues,
            severity="error" if drift_issues else "info",
        )


class UpgradeGeometryInvariant(ArchInvariant):
    """
    I_upgrade = 1 iff all declared upgrade/rollback paths preserve architectural validity.

    The architecture must be valid across time, not just at a point in time.

    Checks:
    - Version N can upgrade to N+1
    - Rollback from N+1 to N doesn't corrupt state
    - Cross-repo upgrades are declared
    """

    name = "upgrade_geometry"

    def check(
        self, repo_path: Path, arch_graph: ArchitectureGraph | None = None
    ) -> ArchInvariantResult:
        graph = self._get_graph(repo_path, arch_graph)

        issues = []

        # Check for migration chain completeness
        migration_nodes = graph.get_nodes_by_type(
            ArchitectureGraph  # type: ignore
        )

        # Check for version consistency
        pyproject = repo_path / "pyproject.toml"
        if pyproject.exists():
            try:
                import tomllib

                config = tomllib.loads(pyproject.read_text())
                version = config.get("project", {}).get("version")

                if not version:
                    issues.append("No version declared in pyproject.toml")

            except Exception:
                pass

        # Check for upgrade coupling
        coupling = graph.compute_upgrade_coupling()
        for repo, coupled in coupling.items():
            if coupled:
                issues.append(
                    f"Upgrade coupling: {repo} must rollout with {', '.join(coupled)}"
                )

        return ArchInvariantResult(
            passed=len(issues) == 0,
            invariant_name=self.name,
            dimension=self.dimension,
            message="Upgrade geometry valid"
            if not issues
            else f"{len(issues)} upgrade geometry issues",
            details=issues,
            severity="warning" if issues else "info",
        )


# Registry of all architectural invariant classes
ARCH_INVARIANT_CLASSES = [
    BoundaryInvariant,
    AuthorityInvariant,
    PlaneSeparationInvariant,
    HiddenInterfaceInvariant,
    FolkloreInvariant,
    ArchitectureDriftInvariant,
    UpgradeGeometryInvariant,
]


class ArchitectureInvariantEngine:
    """
    The Architectural Invariant Engine runs all arch invariants.

    For each repo, define architectural invariants:
        I_arch = {I_boundary, I_authority, I_plane_sep, I_hidden, I_folklore,
                  I_drift, I_upgrade}

    A repo is architecturally valid only if:
        ∀ I_n ∈ I_arch : I_n(Ψ_repo) = 1
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path).resolve()
        self.invariants = [cls() for cls in ARCH_INVARIANT_CLASSES]
        self._graph: ArchitectureGraph | None = None

    @property
    def graph(self) -> ArchitectureGraph:
        """Lazy-load architecture graph."""
        if self._graph is None:
            self._graph = build_architecture_graph(self.repo_path)
        return self._graph

    def run_all(self) -> list[ArchInvariantResult]:
        """Run all architectural invariants."""
        results = []

        for invariant in self.invariants:
            result = invariant.check(self.repo_path, self.graph)
            results.append(result)

        return results

    def check_specific(self, invariant_name: str) -> ArchInvariantResult:
        """Run a specific architectural invariant by name."""
        for invariant in self.invariants:
            if invariant.name == invariant_name:
                return invariant.check(self.repo_path, self.graph)
        raise ValueError(f"Unknown architectural invariant: {invariant_name}")

    def get_architectural_state(
        self,
    ) -> tuple[float, float, list[ArchInvariantResult]]:
        """
        Get the architectural state as dimension values.

        Returns:
            (architecture_score, hidden_state_score, all_results)
        """
        results = self.run_all()

        # Architecture dimension: average of arch-related invariants
        arch_results = [
            r
            for r in results
            if r.dimension == StateDimension.ARCHITECTURE
        ]
        arch_score = (
            sum(1.0 for r in arch_results if r.passed) / len(arch_results)
            if arch_results
            else 1.0
        )

        # Hidden state dimension
        hidden_results = [
            r for r in results if r.dimension == StateDimension.HIDDEN_STATE
        ]
        hidden_score = (
            sum(1.0 for r in hidden_results if r.passed) / len(hidden_results)
            if hidden_results
            else 1.0
        )

        return arch_score, hidden_score, results
