"""
Repo Doctor Ω∞∞∞∞∞ - Unified Graph Substrate

G_repo = (V, E, Φ, Τ) - The unified graph representation of repository state.

Vertex types (Τ):
- module: Python/JS/Go module files
- class: Class definitions
- function: Function/method definitions
- entrypoint: CLI entry points, HTTP handlers
- data_schema: Database tables, Pydantic models, protobuf
- build_artifact: Generated outputs, wheels, containers

Edge types (E):
- depends_on: Import/require dependency
- calls: Function call relationship
- inherits: Class inheritance
- entrypoint_ref: Entrypoint → implementation mapping
- generates: Code generation relationship
- schema_ref: Schema usage/reference
- entangled_with: Cross-module coupling
- temporal_succ: Version history edge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class VertexType(Enum):
    """Τ - Types of vertices in G_repo per Ω∞∞∞∞∞."""

    # Core implementation vertices
    MODULE = auto()
    CLASS = auto()
    FUNCTION = auto()
    ENTRYPOINT = auto()
    DATA_SCHEMA = auto()
    BUILD_ARTIFACT = auto()
    PACKAGE = auto()
    CONFIG = auto()
    TEST = auto()
    DOC = auto()

    # Phase 3: Control system vertices
    CLOCK_NODE = auto()  # Clock/temporal semantics
    CONSISTENCY_DOMAIN = auto()  # Consistency model boundary
    CACHE_NODE = auto()  # Cache architecture
    IDENTITY_AUTHORITY = auto()  # Identity/credential authority
    CREDENTIAL = auto()  # Credential definition
    CAPABILITY = auto()  # Scoped capability
    QUEUE_NODE = auto()  # Queue/retry topology
    BACKPRESSURE_BOUNDARY = auto()  # Flow control boundary
    FALLBACK_NODE = auto()  # Fallback path
    IDEMPOTENCY_BOUNDARY = auto()  # Idempotency boundary
    LINEAGE_NODE = auto()  # Data lineage tracking
    TOMBSTONE = auto()  # Deletion marker
    RETENTION_POLICY = auto()  # Data retention rules
    AUDIT_RECORD = auto()  # Forensic audit entry
    ESCALATION_PATH = auto()  # Escalation route
    CONTROL_LOOP = auto()  # Control system
    AUTOMATION_BOUNDARY = auto()  # Auto/manual boundary
    FAILURE_DOMAIN = auto()  # Failure isolation domain
    NEGATIVE_CAPABILITY = auto()  # Forbidden state/transition
    DEBT_REGISTER = auto()  # Architectural debt tracking

    # Phase 4: State machine and coexistence vertices
    STATE_MACHINE_NODE = auto()  # State machine definition
    FORBIDDEN_STATE_NODE = auto()  # Forbidden state marker
    TRANSITION_NODE = auto()  # State transition
    VERSION_WINDOW_NODE = auto()  # Version compatibility window
    CUTOVER_PHASE_NODE = auto()  # Cutover phase marker
    DUAL_WRITE_NODE = auto()  # Dual-write boundary
    DUAL_READ_NODE = auto()  # Dual-read boundary
    CANARY_NODE = auto()  # Canary deployment marker
    SHADOW_TRAFFIC_NODE = auto()  # Shadow traffic marker
    QUOTA_NODE = auto()  # Rate limit/quota definition
    EXTERNAL_CONTRACT_NODE = auto()  # External system contract
    EXPERIMENT_NODE = auto()  # A/B experiment definition
    FLAG_NODE = auto()  # Feature flag
    BUDGET_NODE = auto()  # Resource/cost budget
    BOTTLENECK_NODE = auto()  # Shared bottleneck
    TEAM_NODE = auto()  # Team/ownership boundary
    KNOWLEDGE_CLUSTER_NODE = auto()  # Knowledge concentration
    INCENTIVE_NODE = auto()  # Incentive structure
    EXCEPTION_NODE = auto()  # Exception/override path
    OVERRIDE_NODE = auto()  # Temporary override
    HOTFIX_NODE = auto()  # Hotfix path
    COMPLIANCE_NODE = auto()  # Compliance requirement
    EVIDENCE_NODE = auto()  # Evidence source
    FRESHNESS_BOUND_NODE = auto()  # Evidence freshness bound
    DECISION_RIGHT_NODE = auto()  # Decision authority

    # Phase 5: Lease, Transaction, and Meta-Stability nodes (14 new)
    LEASE_NODE = auto()  # Lease definition
    LEASE_HOLDER_NODE = auto()  # Lease holder/authority
    TRANSACTION_BOUNDARY_NODE = auto()  # Transaction scope
    SATURATION_POLICY_NODE = auto()  # Saturation handling policy
    HYSTERESIS_RULE_NODE = auto()  # Hysteresis configuration
    SYMMETRY_CLASS_NODE = auto()  # Symmetry equivalence class
    TRUST_DOMAIN_NODE = auto()  # Trust boundary
    HERMETIC_BOUNDARY_NODE = auto()  # Hermeticity enclosure
    IMPOSSIBILITY_CONSTRAINT_NODE = auto()  # Impossibility boundary
    TRADEOFF_DECLARATION_NODE = auto()  # Explicit tradeoff
    DARK_STATE_NODE = auto()  # Unobserved but real state
    NULLSPACE_CLASS_NODE = auto()  # Observational equivalence class
    NONLOCAL_INVARIANT_NODE = auto()  # Global safety property
    CONSERVATION_LAW_NODE = auto()  # Global quantity constraint


class EdgeType(Enum):
    """E - Types of edges in G_repo per Ω∞∞∞∞∞."""

    # Core implementation edges
    DEPENDS_ON = auto()  # Import/require dependency
    CALLS = auto()  # Function call
    INHERITS = auto()  # Class inheritance
    IMPORTS = auto()  # Module import
    ENTRYPOINT_REF = auto()  # Entrypoint → implementation
    GENERATES = auto()  # Code generation
    SCHEMA_REF = auto()  # Schema reference/usage
    ENTANGLED_WITH = auto()  # Cross-module coupling
    TEMPORAL_SUCC = auto()  # Version history
    CONTAINS = auto()  # Parent-child containment
    EXPORTS = auto()  # Public API export

    # Phase 3: Control system edges
    GOVERNS_TIME_FOR = auto()  # Clock semantics control
    CACHES = auto()  # Cache relationship
    INVALIDATES = auto()  # Cache invalidation
    AUTHENTICATES = auto()  # Identity verification
    AUTHORIZES = auto()  # Authorization grant
    GRANTS_CAPABILITY = auto()  # Capability delegation
    QUEUES_TO = auto()  # Queue routing
    BACKPRESSURES = auto()  # Flow control
    FALLS_BACK_TO = auto()  # Fallback path
    MUST_BE_IDEMPOTENT_AT = auto()  # Idempotency boundary
    DERIVED_FROM = auto()  # Lineage relationship
    TOMBSTONES = auto()  # Deletion propagation
    RETAINS = auto()  # Retention policy
    AUDITS = auto()  # Audit trail
    ESCALATES_TO = auto()  # Escalation path
    CONTROLS = auto()  # Control relationship
    AUTOMATES = auto()  # Automation boundary
    SHARES_FAILURE_DOMAIN = auto()  # Failure domain overlap
    FORBIDS_TRANSITION_TO = auto()  # Negative capability
    ACCUMULATES_DEBT_FROM = auto()  # Architectural debt

    # Phase 4: State machine and coexistence edges
    MUST_PRECEDE = auto()  # Temporal precedence
    MAY_COEXIST_WITH = auto()  # Version coexistence allowed
    MUST_NOT_COEXIST_WITH = auto()  # Version incompatibility
    REPLAYS = auto()  # Backfill/replay relationship
    BACKFILLS = auto()  # Data backfill path
    REINDEXES = auto()  # Reindex operation
    CONSUMES_EXTERNAL_FROM = auto()  # External dependency
    RATE_LIMITED_BY = auto()  # Quota constraint
    GUARDED_BY_FLAG = auto()  # Feature flag protection
    MEASURED_BY_BUDGET = auto()  # Budget constraint
    SHARES_BOTTLENECK_WITH = auto()  # Resource coupling
    OWNED_BY_TEAM = auto()  # Team ownership
    KNOWN_BY = auto()  # Knowledge distribution
    INCENTIVIZED_BY = auto()  # Incentive alignment
    EXCEPTS = auto()  # Exception bypass
    OVERRIDES = auto()  # Override relationship
    EXPIRES_AT = auto()  # Override expiration
    REQUIRES_EVIDENCE_FROM = auto()  # Evidence dependency
    DECISION_AUTHORITY = auto()  # Decision authority
    SUPPORTS_SCOPE_OF = auto()  # Evidence scope

    # Phase 5: Lease, Transaction, and Meta-Stability edges (18 new)
    LEASED_BY = auto()  # Lease acquisition
    EXPIRES_UNDER = auto()  # Lease expiry condition
    COMMITS_WITH = auto()  # Transaction atomicity
    SATURATES_UNDER = auto()  # Saturation trigger
    APPLIES_HYSTERESIS_TO = auto()  # Hysteresis application
    SYMMETRIC_WITH = auto()  # Symmetrical equivalence
    BREAKS_SYMMETRY_OF = auto()  # Symmetry breaking
    TRUSTS = auto()  # Trust relationship
    CROSSES_TRUST_DOMAIN = auto()  # Trust boundary crossing
    HERMETIC_UNDER = auto()  # Hermeticity condition
    VIOLATES_IMPOSSIBILITY_BUNDLE_WITH = auto()  # Impossibility violation
    DECLARES_TRADEOFF_AGAINST = auto()  # Explicit tradeoff
    OBSERVATIONALLY_COLLAPSES_INTO = auto()  # Nullspace collapse
    PARTICIPATES_IN_NONLOCAL_INVARIANT = auto()  # Non-local participation
    BOUNDED_BY_CONSERVATION_LAW = auto()  # Conservation constraint


@dataclass
class Vertex:
    """V - A vertex in G_repo."""

    id: str
    type: VertexType
    name: str
    path: str = ""
    line_start: int = 0
    line_end: int = 0
    properties: dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class Edge:
    """E - An edge in G_repo with properties Φ."""

    source: str  # Vertex id
    target: str  # Vertex id
    type: EdgeType
    weight: float = 1.0  # Coupling strength
    properties: dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        return f"{self.source}->{self.target}:{self.type.name}"


@dataclass
class GraphSubstrate:
    """
    G_repo = (V, E, Φ, Τ) - Unified repository graph.

    The graph substrate is the foundational data structure for:
    - Entanglement calculations
    - Collapse operator (C_fail)
    - Path-integral blame assignment
    - Repair optimization
    """

    vertices: dict[str, Vertex] = field(default_factory=dict)
    edges: dict[str, Edge] = field(default_factory=dict)

    # Index by vertex type for efficient queries
    _vertices_by_type: dict[VertexType, set[str]] = field(
        default_factory=lambda: {t: set() for t in VertexType}
    )

    # Index by edge type
    _edges_by_type: dict[EdgeType, set[str]] = field(
        default_factory=lambda: {t: set() for t in EdgeType}
    )

    # Adjacency lists
    _outgoing: dict[str, set[str]] = field(default_factory=dict)
    _incoming: dict[str, set[str]] = field(default_factory=dict)

    def add_vertex(self, vertex: Vertex) -> None:
        """Add a vertex to the graph."""
        self.vertices[vertex.id] = vertex
        self._vertices_by_type[vertex.type].add(vertex.id)
        self._outgoing.setdefault(vertex.id, set())
        self._incoming.setdefault(vertex.id, set())

    def add_edge(self, edge: Edge) -> None:
        """Add an edge to the graph."""
        edge_id = edge.id
        self.edges[edge_id] = edge
        self._edges_by_type[edge.type].add(edge_id)
        self._outgoing[edge.source].add(edge_id)
        self._incoming[edge.target].add(edge_id)

    def get_vertices_by_type(self, vtype: VertexType) -> list[Vertex]:
        """Get all vertices of a specific type."""
        return [self.vertices[v_id] for v_id in self._vertices_by_type[vtype]]

    def get_edges_by_type(self, etype: EdgeType) -> list[Edge]:
        """Get all edges of a specific type."""
        return [self.edges[e_id] for e_id in self._edges_by_type[etype]]

    def get_neighbors(self, vertex_id: str, edge_type: EdgeType | None = None) -> list[Vertex]:
        """Get neighboring vertices."""
        neighbors = []
        for edge_id in self._outgoing.get(vertex_id, []):
            edge = self.edges[edge_id]
            if edge_type is None or edge.type == edge_type:
                if edge.target in self.vertices:
                    neighbors.append(self.vertices[edge.target])
        return neighbors

    def get_predecessors(self, vertex_id: str, edge_type: EdgeType | None = None) -> list[Vertex]:
        """Get predecessor vertices."""
        predecessors = []
        for edge_id in self._incoming.get(vertex_id, []):
            edge = self.edges[edge_id]
            if edge_type is None or edge.type == edge_type:
                if edge.source in self.vertices:
                    predecessors.append(self.vertices[edge.source])
        return predecessors

    @property
    def num_vertices(self) -> int:
        return len(self.vertices)

    @property
    def num_edges(self) -> int:
        return len(self.edges)

    def __repr__(self) -> str:
        return f"GraphSubstrate(vertices={self.num_vertices}, edges={self.num_edges})"


# Singleton instance
_graph_instance: GraphSubstrate | None = None


def get_graph_substrate() -> GraphSubstrate:
    """Get or create the global graph substrate instance."""
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = GraphSubstrate()
    return _graph_instance


def reset_graph_substrate() -> None:
    """Reset the global graph substrate (for testing)."""
    global _graph_instance
    _graph_instance = GraphSubstrate()
