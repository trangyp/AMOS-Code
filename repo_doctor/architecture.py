"""
Architecture Graph Module - Higher-Order Repository Modeling

Defines the architectural state space αArch layered above local repo state.

Architecture Graph:
    G_arch = (V_arch, E_arch, Φ_arch)

Where:
    V_arch = architectural nodes (Service, Library, SchemaAuthority, etc.)
    E_arch = architectural edges (owns_truth_of, derives_from, generates, etc.)
    Φ_arch = node/edge properties and constraints

Key Invariants:
    I_boundary = 1 iff each concern is enforced only within its declared boundary
    I_authority = 1 iff every architectural fact has exactly one authoritative owner
    I_derivation = 1 iff every non-canonical artifact is mechanically derivable
    I_rollout_coupling = 1 iff all mutually dependent repos are declared as coupled
    I_plane_separation = 1 iff control/data/execution/observation planes don't substitute
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional


class ArchNodeType(Enum):
    """Architectural node classes - the building blocks of system architecture."""

    SERVICE = auto()  # Runtime service
    LIBRARY = auto()  # Code library
    PACKAGE = auto()  # Deployable package
    SCHEMA_AUTHORITY = auto()  # Owns schema truth
    CODEGEN_AUTHORITY = auto()  # Owns generated code
    POLICY = auto()  # Policy engine
    RUNTIME_MODE = auto()  # Runtime mode definition
    LAUNCHER = auto()  # Launch mechanism
    SHELL = auto()  # CLI shell
    SERVER = auto()  # Server component
    PERSISTENCE_BOUNDARY = auto()  # Data persistence layer
    MIGRATION_CHAIN = auto()  # Migration sequence
    PERMISSION_BOUNDARY = auto()  # Auth/permission layer
    OBSERVABILITY = auto()  # Metrics, logs, traces
    BUILD_TARGET = auto()  # Build artifact
    ARTIFACT = auto()  # Generated/derived artifact
    RELEASE = auto()  # Release unit
    OWNER = auto()  # Organizational owner
    REPO = auto()  # Repository container
    CONTRACT = auto()  # Interface contract


class ArchEdgeType(Enum):
    """Architectural edge classes - relationships between nodes."""

    OWNS_TRUTH_OF = auto()  # Canonical authority
    DERIVES_FROM = auto()  # Mechanical derivation
    GENERATES = auto()  # Codegen/production
    ACTIVATES = auto()  # Runtime activation
    WRAPS = auto()  # Encapsulation
    LAUNCHES = auto()  # Launch relationship
    DEPENDS_ON = auto()  # Dependency
    UPGRADES_BEFORE = auto()  # Upgrade ordering
    MUST_ROLLOUT_WITH = auto()  # Coupled rollout
    MUST_MIGRATE_WITH = auto()  # Coupled migration
    OBSERVES = auto()  # Observability attachment
    AUTHORIZES = auto()  # Auth delegation
    CROSSES_BOUNDARY = auto()  # Boundary crossing
    PUBLISHES_CONTRACT_TO = auto()  # Contract provider
    CONSUMES_CONTRACT_FROM = auto()  # Contract consumer


class PlaneType(Enum):
    """The four architectural planes."""

    CONTROL = auto()  # Declarative policy/state
    DATA = auto()  # Operational data
    EXECUTION = auto()  # Runtime execution
    OBSERVATION = auto()  # Monitoring/observability


@dataclass
class ArchNode:
    """A node in the architecture graph."""

    id: str
    node_type: ArchNodeType
    name: str
    plane: Optional[PlaneType] = None
    owner: str = None
    source_file: str = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ArchNode):
            return NotImplemented
        return self.id == other.id


@dataclass
class ArchEdge:
    """An edge in the architecture graph."""

    source: str  # Node ID
    target: str  # Node ID
    edge_type: ArchEdgeType
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash((self.source, self.target, self.edge_type))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ArchEdge):
            return NotImplemented
        return (self.source, self.target, self.edge_type) == (
            other.source,
            other.target,
            other.edge_type,
        )


@dataclass
class AuthorityClaim:
    """A claim of authority over an architectural fact."""

    fact_type: str  # e.g., "api_schema", "command_contract", "version"
    fact_name: str  # The specific fact being claimed
    claimed_by: str  # Node ID claiming authority
    derived_at: list[str] = field(default_factory=list)  # Nodes deriving from this
    is_canonical: bool = True


@dataclass
class BoundaryViolation:
    """A violation of architectural boundaries."""

    node_id: str
    expected_plane: PlaneType
    actual_plane: PlaneType
    violation_type: str  # e.g., "policy_in_execution", "data_in_control"
    description: str


@dataclass
class HiddenInterface:
    """An interface not explicitly declared in architecture."""

    interface_type: str  # env_var, file_convention, dynamic_import, etc.
    name: str
    consumers: list[str] = field(default_factory=list)  # Node IDs
    description: str = ""


@dataclass
class UpgradePath:
    """An upgrade/rollback path between versions."""

    from_version: str
    to_version: str
    requires_migration: bool = False
    can_rollback: bool = True
    coupled_repos: list[str] = field(default_factory=list)


@dataclass
class FolkloreDependency:
    """An undocumented operational dependency."""

    description: str
    operation: str  # What needs to be done
    why_critical: str  # Why this affects correctness
    nodes_involved: list[str] = field(default_factory=list)


class ArchitectureGraph:
    """
    The architecture graph G_arch = (V_arch, E_arch, Φ_arch).

    Models the system architecture above the code level:
    - Authority distribution
    - Plane separation
    - Boundary integrity
    - Upgrade topology
    """

    def __init__(self, repo_path: Optional[Path] = None):
        self.repo_path = repo_path
        self.nodes: dict[str, ArchNode] = {}
        self.edges: list[ArchEdge] = []
        self.authority_claims: dict[str, AuthorityClaim] = {}  # fact_name -> claim
        self.boundary_violations: list[BoundaryViolation] = []
        self.hidden_interfaces: list[HiddenInterface] = []
        self.upgrade_paths: list[UpgradePath] = []
        self.folklore_deps: list[FolkloreDependency] = []

    def add_node(
        self,
        node_id: str,
        node_type: ArchNodeType,
        name: str,
        plane: Optional[PlaneType] = None,
        owner: str = None,
        source_file: str = None,
        metadata: dict[str, Any] = None,
    ) -> ArchNode:
        """Add a node to the architecture graph."""
        node = ArchNode(
            id=node_id,
            node_type=node_type,
            name=name,
            plane=plane,
            owner=owner,
            source_file=source_file,
            metadata=metadata or {},
        )
        self.nodes[node_id] = node
        return node

    def add_edge(
        self,
        source: str,
        target: str,
        edge_type: ArchEdgeType,
        weight: float = 1.0,
        metadata: dict[str, Any] = None,
    ) -> ArchEdge:
        """Add an edge to the architecture graph."""
        edge = ArchEdge(
            source=source,
            target=target,
            edge_type=edge_type,
            weight=weight,
            metadata=metadata or {},
        )
        self.edges.append(edge)
        return edge

    def claim_authority(
        self,
        fact_type: str,
        fact_name: str,
        node_id: str,
        is_canonical: bool = True,
    ) -> AuthorityClaim:
        """Register an authority claim."""
        claim = AuthorityClaim(
            fact_type=fact_type,
            fact_name=fact_name,
            claimed_by=node_id,
            is_canonical=is_canonical,
        )
        self.authority_claims[fact_name] = claim
        return claim

    def get_node(self, node_id: str) -> Optional[ArchNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def get_edges_from(self, node_id: str) -> list[ArchEdge]:
        """Get all edges originating from a node."""
        return [e for e in self.edges if e.source == node_id]

    def get_edges_to(self, node_id: str) -> list[ArchEdge]:
        """Get all edges targeting a node."""
        return [e for e in self.edges if e.target == node_id]

    def get_nodes_by_type(self, node_type: ArchNodeType) -> list[ArchNode]:
        """Get all nodes of a specific type."""
        return [n for n in self.nodes.values() if n.node_type == node_type]

    def get_nodes_by_plane(self, plane: PlaneType) -> list[ArchNode]:
        """Get all nodes in a specific plane."""
        return [n for n in self.nodes.values() if n.plane == plane]

    def get_authority_owner(self, fact_name: str) -> str:
        """Get the node that owns authority for a fact."""
        claim = self.authority_claims.get(fact_name)
        if claim and claim.is_canonical:
            return claim.claimed_by
        return None

    def find_authority_duplicates(self) -> dict[str, list[str]]:
        """
        Find facts with multiple authority claims.

        Returns: {fact_name: [node_ids claiming authority]}
        """
        # Group by fact type and name
        from collections import defaultdict

        claims_by_fact: dict[str, list[str]] = defaultdict(list)

        for fact_name, claim in self.authority_claims.items():
            if claim.is_canonical:
                claims_by_fact[fact_name].append(claim.claimed_by)

        # Find duplicates
        duplicates = {fact: nodes for fact, nodes in claims_by_fact.items() if len(nodes) > 1}

        return duplicates

    def find_boundary_violations(self) -> list[BoundaryViolation]:
        """
        Find components enforcing policy outside their declared boundary.

        Examples
        --------
        - Launcher (execution) deciding policy (control)
        - Persistence layer (data) enforcing business logic (control)

        """
        violations = []

        for node in self.nodes.values():
            if node.plane is None:
                continue

            # Check edges for boundary crossing issues
            for edge in self.get_edges_from(node.id):
                # Launcher should not activate policy nodes directly
                if (
                    node.node_type == ArchNodeType.LAUNCHER
                    and edge.edge_type == ArchEdgeType.ACTIVATES
                ):
                    target = self.get_node(edge.target)
                    if target and target.node_type == ArchNodeType.POLICY:
                        violations.append(
                            BoundaryViolation(
                                node_id=node.id,
                                expected_plane=PlaneType.EXECUTION,
                                actual_plane=PlaneType.CONTROL,
                                violation_type="launcher_activates_policy",
                                description=f"Launcher {node.name} activates policy {target.name}",
                            )
                        )

                # Data plane nodes should not generate control plane outputs
                if node.plane == PlaneType.DATA and edge.edge_type == ArchEdgeType.GENERATES:
                    target = self.get_node(edge.target)
                    if target and target.plane == PlaneType.CONTROL:
                        violations.append(
                            BoundaryViolation(
                                node_id=node.id,
                                expected_plane=PlaneType.DATA,
                                actual_plane=PlaneType.CONTROL,
                                violation_type="data_generates_control",
                                description=f"Data node {node.name} generates control output {target.name}",
                            )
                        )

        self.boundary_violations = violations
        return violations

    def find_hidden_interfaces(self) -> list[HiddenInterface]:
        """
        Discover interfaces that exist in practice but not in declared architecture.

        These are detected by analyzing:
        - Environment variable access
        - File naming conventions
        - Dynamic imports
        - Log parsing dependencies
        """
        # This would require code analysis
        # For now, return previously discovered interfaces
        return self.hidden_interfaces

    def detect_folklore(self, repo_path: Path) -> list[FolkloreDependency]:
        """
        Detect operational folklore - "everyone knows you have to..." dependencies.

        Examples
        --------
        - "run migration script before starting app"
        - "export env var or shell mode breaks"
        - "build step must be manual"

        """
        folklore = []

        # Check for common folklore indicators in docs
        readme_path = repo_path / "README.md"
        if readme_path.exists():
            content = readme_path.read_text()

            # Patterns suggesting folklore
            folklore_patterns = [
                ("make sure you", "undocumented prerequisite"),
                ("don't forget to", "manual step required"),
                ("before running", "ordering dependency"),
                ("must export", "env var folklore"),
                ("first, run", "sequencing folklore"),
            ]

            for pattern, category in folklore_patterns:
                if pattern.lower() in content.lower():
                    folklore.append(
                        FolkloreDependency(
                            description=f"README suggests folklore: '{pattern}'",
                            operation=category,
                            why_critical="Manual steps often forgotten, breaking automation",
                        )
                    )

        # Check for script dependencies that aren't declared
        scripts_dir = repo_path / "scripts"
        if scripts_dir.exists():
            for script in scripts_dir.iterdir():
                if script.is_file() and script.suffix in (".sh", ".py"):
                    folklore.append(
                        FolkloreDependency(
                            description=f"Script {script.name} may have undeclared dependencies",
                            operation=f"run {script.name}",
                            why_critical="Script prerequisites may not be automated",
                            nodes_involved=[str(script)],
                        )
                    )

        self.folklore_deps = folklore
        return folklore

    def check_plane_separation(self) -> tuple[bool, list[str]]:
        """
        Check if control/data/execution/observation planes are properly separated.

        Returns: (passed, list of violations)
        """
        violations = []

        # Control plane nodes should not depend on execution plane nodes
        control_nodes = self.get_nodes_by_plane(PlaneType.CONTROL)
        for node in control_nodes:
            for edge in self.get_edges_from(node.id):
                source_node = self.get_node(edge.source)
                target_node = self.get_node(edge.target)

                if source_node and target_node:
                    # Control should not derive from execution
                    if (
                        source_node.plane == PlaneType.CONTROL
                        and target_node.plane == PlaneType.EXECUTION
                        and edge.edge_type == ArchEdgeType.DERIVES_FROM
                    ):
                        violations.append(
                            f"Control node {node.name} derives from execution node {target_node.name}"
                        )

        return len(violations) == 0, violations

    def compute_upgrade_coupling(self) -> dict[str, list[str]]:
        """
        Compute which repos/services must rollout together.

        Returns: {repo_id: [coupled_repo_ids]}
        """
        coupling: dict[str, list[str]] = {}

        for edge in self.edges:
            if edge.edge_type == ArchEdgeType.MUST_ROLLOUT_WITH:
                if edge.source not in coupling:
                    coupling[edge.source] = []
                if edge.target not in coupling[edge.source]:
                    coupling[edge.source].append(edge.target)

                # Symmetric
                if edge.target not in coupling:
                    coupling[edge.target] = []
                if edge.source not in coupling[edge.target]:
                    coupling[edge.target].append(edge.source)

        return coupling

    def to_dict(self) -> dict[str, Any]:
        """Serialize architecture graph to dictionary."""
        return {
            "nodes": [
                {
                    "id": n.id,
                    "type": n.node_type.name,
                    "name": n.name,
                    "plane": n.plane.name if n.plane else None,
                    "owner": n.owner,
                    "source_file": n.source_file,
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "type": e.edge_type.name,
                    "weight": e.weight,
                }
                for e in self.edges
            ],
            "authority_claims": {
                k: {
                    "fact_type": v.fact_type,
                    "claimed_by": v.claimed_by,
                    "is_canonical": v.is_canonical,
                }
                for k, v in self.authority_claims.items()
            },
            "boundary_violations": [
                {
                    "node": v.node_id,
                    "type": v.violation_type,
                    "description": v.description,
                }
                for v in self.boundary_violations
            ],
            "hidden_interfaces": [
                {
                    "type": hi.interface_type,
                    "name": hi.name,
                    "consumers": hi.consumers,
                }
                for hi in self.hidden_interfaces
            ],
            "folklore_deps": [
                {
                    "description": fd.description,
                    "operation": fd.operation,
                    "why_critical": fd.why_critical,
                }
                for fd in self.folklore_deps
            ],
        }


class ArchitectureBuilder:
    """
    Builds an architecture graph from repository analysis.

    Discovers:
    - Nodes from package structure
    - Authority claims from configuration
    - Planes from code patterns
    - Boundaries from imports
    """

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.graph = ArchitectureGraph(repo_path)

    def build_from_repo(self) -> ArchitectureGraph:
        """Build architecture graph from repository structure."""
        self._discover_package_nodes()
        self._discover_entrypoint_nodes()
        self._discover_authority_claims()
        self._discover_hidden_interfaces()
        return self.graph

    def _discover_package_nodes(self) -> None:
        """Discover package/library nodes from repo structure."""
        # Find all packages (directories with __init__.py)
        for init_file in self.repo_path.rglob("__init__.py"):
            rel_path = init_file.relative_to(self.repo_path)
            parts = list(rel_path.parent.parts)

            # Skip hidden directories
            if any(p.startswith(".") for p in parts):
                continue

            pkg_name = ".".join(parts) if parts else self.repo_path.name
            node_id = f"pkg:{pkg_name}"

            self.graph.add_node(
                node_id=node_id,
                node_type=ArchNodeType.LIBRARY,
                name=pkg_name,
                plane=PlaneType.DATA,  # Libraries are in data plane
                source_file=str(rel_path),
            )

    def _discover_entrypoint_nodes(self) -> None:
        """Discover entrypoint nodes from pyproject.toml."""
        pyproject = self.repo_path / "pyproject.toml"
        if not pyproject.exists():
            return

        try:
            import tomllib

            config = tomllib.loads(pyproject.read_text())
            scripts = config.get("project", {}).get("scripts", {})

            for name, entrypoint in scripts.items():
                node_id = f"entry:{name}"

                self.graph.add_node(
                    node_id=node_id,
                    node_type=ArchNodeType.LAUNCHER,
                    name=name,
                    plane=PlaneType.EXECUTION,
                    metadata={"entrypoint": entrypoint},
                )

                # Parse module from entrypoint
                if ":" in entrypoint:
                    module_path = entrypoint.split(":")[0]
                    pkg_node_id = f"pkg:{module_path.split('.')[0]}"

                    if pkg_node_id in self.graph.nodes:
                        self.graph.add_edge(
                            source=node_id,
                            target=pkg_node_id,
                            edge_type=ArchEdgeType.LAUNCHES,
                        )

        except Exception:
            pass

    def _discover_authority_claims(self) -> None:
        """Discover authority claims from configuration files."""
        # pyproject.toml claims version authority
        pyproject = self.repo_path / "pyproject.toml"
        if pyproject.exists():
            try:
                import tomllib

                config = tomllib.loads(pyproject.read_text())
                project = config.get("project", {})

                if project.get("version"):
                    self.graph.claim_authority(
                        fact_type="version",
                        fact_name="package_version",
                        node_id="config:pyproject",
                        is_canonical=True,
                    )

                if project.get("scripts"):
                    self.graph.claim_authority(
                        fact_type="entrypoints",
                        fact_name="console_scripts",
                        node_id="config:pyproject",
                        is_canonical=True,
                    )

            except Exception:
                pass

        # Check for version in __init__.py
        for init_file in self.repo_path.rglob("__init__.py"):
            try:
                content = init_file.read_text()
                if "__version__" in content:
                    rel_path = init_file.relative_to(self.repo_path)
                    node_id = f"file:{rel_path}"

                    # This could duplicate authority - detected by invariant
                    self.graph.claim_authority(
                        fact_type="version",
                        fact_name="package_version",
                        node_id=node_id,
                        is_canonical=False,  # Mark as derived
                    )
            except Exception:
                pass

    def _discover_hidden_interfaces(self) -> None:
        """Discover hidden interfaces through code analysis."""
        # Look for environment variable usage
        for py_file in self.repo_path.rglob("*.py"):
            if any(p.startswith(".") for p in py_file.relative_to(self.repo_path).parts):
                continue

            try:
                content = py_file.read_text()

                # Detect os.environ access
                if "os.environ" in content or "os.getenv" in content:
                    self.graph.hidden_interfaces.append(
                        HiddenInterface(
                            interface_type="env_var",
                            name=f"env_access_in_{py_file.name}",
                            description=f"Environment variable access in {py_file}",
                        )
                    )

                # Detect dynamic imports
                if "__import__" in content or "importlib" in content:
                    self.graph.hidden_interfaces.append(
                        HiddenInterface(
                            interface_type="dynamic_import",
                            name=f"dynamic_import_in_{py_file.name}",
                            description=f"Dynamic import in {py_file}",
                        )
                    )

            except Exception:
                pass


def build_architecture_graph(repo_path: str | Path) -> ArchitectureGraph:
    """Build an architecture graph from a repository."""
    repo_path = Path(repo_path)
    builder = ArchitectureBuilder(repo_path)
    return builder.build_from_repo()
