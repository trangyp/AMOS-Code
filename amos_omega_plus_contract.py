"""
AMOS Omega+ Unified Machine Specification - Concrete Implementation Contract

Maps the JSON specification to Python dataclasses, protocols, and runtime
contracts. Type-safe implementation of the bounded epistemic computational
organism.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc, timezone

UTC = UTC
from enum import Enum, auto
from typing import (
    Any,
    Generic,
    Optional,
    Protocol,
    TypeVar,
    runtime_checkable,
)

# ============================================================================
# TENSOR TYPES (Type-Safe Shape Annotations)
# ============================================================================

T = TypeVar("T")
N = TypeVar("N", bound=int)  # Nodes/entities
F = TypeVar("F", bound=int)  # Features
H = TypeVar("H", bound=int)  # Temporal horizon
B = TypeVar("B", bound=int)  # Branches
K = TypeVar("K", bound=int)  # Candidate branches
R = TypeVar("R", bound=int)  # Resource channels
P = TypeVar("P", bound=int)  # Human dimensions
S_co = TypeVar("S_co", bound=int, covariant=True)  # State slices
M_co = TypeVar("M_co", bound=int, covariant=True)  # World entities
T_dim = TypeVar("T_dim", bound=int)  # Time steps
C_co = TypeVar("C_co", bound=int, covariant=True)  # Constraint channels
L = TypeVar("L", bound=int)  # Mutable layers
U_co = TypeVar("U_co", bound=int, covariant=True)  # Update dimensions


class Tensor(Generic[N, F, H, B]):
    """Universal State Tensor X_t with shape [N, F, H, B]"""

    def __init__(self, data: list) -> None:
        self.data = data
        self.shape: tuple[int, int, int, int] = (0, 0, 0, 0)  # Computed on init


class GraphTensor(Generic[N]):
    """Graph adjacency matrix G_t with shape [N, N], dtype binary"""

    def __init__(self, adjacency: list[list[int]]) -> None:
        self.adjacency = adjacency


class BranchTensor(Generic[K, N, F]):
    """Branch-specific predicted states B_t with shape [K, N, F]"""

    def __init__(self, branches: list) -> None:
        self.branches = branches


class EnergyTensor(Generic[N]):
    """Per-node energy allocation E_t with shape [N]"""

    def __init__(self, allocations: list[float]) -> None:
        self.allocations = allocations


class ResourceTensor(Generic[N, R]):
    """Per-node resources across R channels Q_t with shape [N, R]"""

    def __init__(self, resources: list[list[float]]) -> None:
        self.resources = resources


class HumanTensor(Generic[P, S_co]):
    """Human state dimensions H_t with shape [P, S]"""

    def __init__(self, state_matrix: list[list[float]]) -> None:
        self.state_matrix = state_matrix


class WorldTensor(Generic[M_co, T_dim, C_co]):
    """World entities by time and constraint channels Y_t with shape [M, T, C]"""

    def __init__(self, world_data: list[Any]) -> None:
        self.world_data = world_data


class ModificationTensor(Generic[L, U_co]):
    """Mutable layers and update dimensions Z_t with shape [L, U]"""

    def __init__(self, modifications: list[Any]) -> None:
        self.modifications = modifications


# ============================================================================
# ENUMERATIONS
# ============================================================================


class NodeType(Enum):
    """Types of entities in the world graph."""

    MACHINE = auto()
    REPO = auto()
    RUNTIME = auto()
    MEMORY = auto()
    GOAL = auto()
    OBSERVER = auto()
    WORLD = auto()
    HUMAN = auto()
    TOOL = auto()


class EdgeType(Enum):
    """Types of relationships between nodes."""

    DEPENDENCY = auto()
    OWNERSHIP = auto()
    RESOURCE_FLOW = auto()
    CAUSAL = auto()
    ROUTING = auto()
    TEMPORAL = auto()


class GoalStatus(Enum):
    """Status of a goal in the goal portfolio."""

    OPEN = auto()
    ACTIVE = auto()
    DEFERRED = auto()
    BLOCKED = auto()
    DONE = auto()


class SignalKind(Enum):
    """Source category of signals."""

    USER = auto()
    TOOL = auto()
    WORLD = auto()
    SYSTEM = auto()
    MEMORY = auto()


class HumanStateClass(Enum):
    """Classification of human cognitive state."""

    STABLE = auto()
    ACTIVATED = auto()
    OVERLOADED = auto()
    SHUTDOWN = auto()
    HIGH_RISK = auto()


class MemoryKind(Enum):
    """Types of memory storage."""

    WORKING = auto()
    EPISODIC = auto()
    SEMANTIC = auto()
    PROCEDURAL = auto()
    IDENTITY = auto()


class PatchTier(Enum):
    """Tiers of self-modification patches."""

    TIER1 = auto()  # Safe adaptive updates
    TIER2 = auto()  # Structured runtime changes
    TIER3 = auto()  # Heavily constrained core changes


class Topology(Enum):
    """Distributed system topology patterns."""

    CENTRALIZED = auto()
    HIERARCHICAL = auto()
    MESH = auto()
    HYBRID = auto()


class ConsensusMode(Enum):
    """Consensus mechanisms for distributed nodes."""

    WEIGHTED = auto()
    STRICT = auto()
    HYBRID = auto()


class NodeRole(Enum):
    """Functional roles in distributed federation."""

    STRATEGIST = auto()
    BUILDER = auto()
    OPERATOR = auto()
    AUDITOR = auto()
    SELLER = auto()
    ALLOCATOR = auto()
    GUARDIAN = auto()


class NodeStatus(Enum):
    """Operational status of a distributed node."""

    ONLINE = auto()
    DEGRADED = auto()
    OFFLINE = auto()


class ConstraintSeverity(Enum):
    """Severity levels for constraints."""

    INFO = auto()
    WARNING = auto()
    BLOCKING = auto()
    CRITICAL = auto()


class LayerId(Enum):
    """Architectural layers of AMOS."""

    SUBSTRATE = "L0"
    KERNEL = "L1"
    COGNITION = "L2"
    HUMAN_COHERENCE = "L3"
    DISTRIBUTED_FEDERATION = "L4"
    EXECUTION = "L5"
    GOVERNANCE = "L6"
    PERSISTENCE_ECONOMICS = "L7"


# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================


@dataclass(frozen=True)
class EpistemicState:
    """INV_EPI_001, INV_EPI_002: Bounded epistemic modeling state."""

    closure_active: bool
    assumptions: list[str] = field(default_factory=list)
    limits: list[str] = field(default_factory=list)
    confidence: float = 0.0  # 0-1
    grounding_level: float = 0.0  # 0-1
    truth_model_score: float = 0.0  # truth(model) score


@dataclass(frozen=True)
class HumanState:
    """INV_HUM_001, INV_HUM_002, INV_HUM_003: Human coherence tracking."""

    cognition: float  # 0-1: cognitive load
    nervous_system: float  # 0-1: arousal level
    perception: float  # 0-1: perceptual bandwidth
    identity_stability: float  # 0-1: self-concept stability
    affect_valence: float  # -1 to 1: positive/negative affect
    affect_arousal: float  # 0-1: activation level
    capacity: float  # 0-1: available processing capacity
    context_load: float  # 0-1: current context weight
    coherence: float  # 0-1: internal consistency
    agency: float  # 0-1: sense of control
    overload_risk: float  # 0-1: INV_HUM_002 - no_destabilizing_insight
    dependency_risk: float  # 0-1: INV_HUM_003 - anti_dependency
    state_class: HumanStateClass = HumanStateClass.STABLE

    def is_safe_for_intervention(self, intensity: float) -> bool:
        """Check if intervention intensity is within safe bounds."""
        safe_threshold = self.capacity * self.coherence * (1 - self.overload_risk)
        return intensity <= safe_threshold


@dataclass(frozen=True)
class GraphNode:
    """Node in the world graph with stateful properties."""

    id: str
    type: NodeType
    features: dict[str, float | str | bool] = field(default_factory=dict)
    health: float = 1.0  # 0-1
    load: float = 0.0  # 0-1
    risk: float = 0.0  # 0-1
    priority: float = 0.0  # 0-1
    coherence: float = 1.0  # 0-1
    confidence: float = 1.0  # 0-1
    freshness: float = 1.0  # 0-1 (temporal recency)


@dataclass(frozen=True)
class GraphEdge:
    """Edge connecting nodes in the world graph."""

    source: str
    target: str
    type: EdgeType
    weight: float = 1.0


@dataclass(frozen=True)
class Constraint:
    """INV_*: System invariants and constraints."""

    id: str
    expression: str  # Mathematical/logical expression
    severity: ConstraintSeverity


@dataclass(frozen=True)
class WorldGraph:
    """Graph representation of internal and external reality."""

    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    constraints: list[Constraint] = field(default_factory=list)


@dataclass(frozen=True)
class Goal:
    """Goal in the portfolio with economic evaluation."""

    id: str
    priority: float  # 0-1
    expected_value: float  # Economic value
    resource_cost: float  # Cost to achieve
    time_horizon: float  # Time to completion
    risk: float  # 0-1 probability of failure
    status: GoalStatus = GoalStatus.OPEN

    @property
    def roi(self) -> float:
        """Return on investment: value / cost."""
        if self.resource_cost == 0:
            return float("inf")
        return self.expected_value / self.resource_cost


@dataclass(frozen=True)
class Signal:
    """Attention-worthy input from any source."""

    id: str
    source: str
    kind: SignalKind
    payload: dict[str, Any] = field(default_factory=dict)
    priority: float = 0.0  # 0-1
    risk: float = 0.0  # 0-1
    novelty: float = 0.0  # 0-1 unexpectedness
    goal_relevance: float = 0.0  # 0-1 alignment with goals
    temporal_urgency: float = 0.0  # 0-1 time pressure

    @property
    def attention_score(self) -> float:
        """
        attention_score = a*priority + b*risk + c*novelty +
                          d*goal_relevance + e*temporal_urgency
        """
        a, b, c, d, e = 0.3, 0.2, 0.15, 0.25, 0.1  # Weights
        return (
            a * self.priority
            + b * self.risk
            + c * self.novelty
            + d * self.goal_relevance
            + e * self.temporal_urgency
        )


@dataclass(frozen=True)
class AttentionItem:
    """Ranked item in the attention queue."""

    signal_id: str
    score: float


@dataclass(frozen=True)
class WorkspaceState:
    """Current focus and active goals."""

    focus: list[str] = field(default_factory=list)  # Active context items
    goals: list[Goal] = field(default_factory=list)
    critical_signals: list[Signal] = field(default_factory=list)
    attention_queue: list[AttentionItem] = field(default_factory=list)


@dataclass(frozen=True)
class Morph:
    """Atomic action in a plan with pre/post conditions."""

    target: str  # Target system/node
    operation: str  # Operation to perform
    scope: str  # Scope of change
    preconditions: list[str] = field(default_factory=list)
    postconditions: list[str] = field(default_factory=list)
    rollback: list[str] = field(default_factory=list)  # INV_SEL_001: reversibility
    cost: float = 0.0
    risk: float = 0.0


@dataclass(frozen=True)
class Branch:
    """INV_SEL_001: Candidate future with constraints."""

    id: str
    plan: list[Morph]
    predicted_state: dict[str, Any] = field(default_factory=dict)
    goal_fit: float = 0.0  # Alignment with objectives
    risk: float = 0.0  # Execution risk
    cost: float = 0.0  # Resource cost
    coherence: float = 0.0  # Internal consistency
    drift: float = 0.0  # INV_ID_001: identity drift bound
    reversibility: float = 0.0  # INV_SEL_001: rollback capability
    confidence: float = 0.0  # Prediction confidence
    legal: bool = False  # INV_SEL_001: legal selection only

    def is_admissible(self, t1: float, t2: float, t3: float) -> bool:
        """
        commit(branch) iff legal(branch) &&
                         confidence>=t1 &&
                         reversibility>=t2 &&
                         risk<=t3
        """
        return self.legal and self.confidence >= t1 and self.reversibility >= t2 and self.risk <= t3


@dataclass(frozen=True)
class BranchSet:
    """Collection of candidate branches for selection."""

    items: list[Branch] = field(default_factory=list)


@dataclass(frozen=True)
class Event:
    """Temporal event with outcome tracking."""

    type: str
    source: str
    target: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    payload: dict[str, Any] = field(default_factory=dict)
    outcome: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TemporalState:
    """Time-aware state with recovery paths."""

    past: list[Event] = field(default_factory=list)
    present: dict[str, Any] = field(default_factory=dict)
    future_horizons: list[float] = field(default_factory=list)  # Time deltas
    recovery_paths: list[str] = field(default_factory=list)
    branch_history: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MemoryItem:
    """Stored memory with relevance tracking."""

    id: str
    kind: MemoryKind
    content: dict[str, Any] = field(default_factory=dict)
    relevance: float = 0.0  # 0-1
    freshness: float = 1.0  # Decays over time
    confidence: float = 1.0  # Source reliability
    source_trace: list[str] = field(default_factory=list)  # Provenance


@dataclass(frozen=True)
class MemoryState:
    """Multi-tier memory architecture."""

    working: list[MemoryItem] = field(default_factory=list)
    episodic: list[MemoryItem] = field(default_factory=list)
    semantic: list[MemoryItem] = field(default_factory=list)
    procedural: list[MemoryItem] = field(default_factory=list)
    identity: list[MemoryItem] = field(default_factory=list)


@dataclass(frozen=True)
class ConstitutionState:
    """Core governing rules and invariants."""

    identity_rules: list[str] = field(default_factory=list)  # INV_ID_*
    safety_rules: list[str] = field(default_factory=list)  # INV_HUM_*, INV_SEL_*
    rollback_rules: list[str] = field(default_factory=list)  # INV_SEL_001
    coherence_rules: list[str] = field(default_factory=list)  # INV_EPI_*
    legality_rules: list[str] = field(default_factory=list)  # INV_GOV_001
    boundary_rules: list[str] = field(default_factory=list)  # INV_RES_*, INV_HW_*


@dataclass(frozen=True)
class EnergyState:
    """INV_RES_001: Resource boundedness tracking."""

    total: float
    allocation: dict[str, float] = field(default_factory=dict)
    demand: dict[str, float] = field(default_factory=dict)
    reserve: float = 0.0

    def is_within_bounds(self) -> bool:
        """sum(allocation_i) <= available_resources"""
        return sum(self.allocation.values()) <= self.total + self.reserve


@dataclass(frozen=True)
class ActionState:
    """Current execution state with rollback tracking."""

    staged: list[Morph] = field(default_factory=list)
    executed: list[Morph] = field(default_factory=list)
    failed: list[Morph] = field(default_factory=list)
    rollback_points: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MetaCognitiveState:
    """Self-monitoring and calibration."""

    simulation_error: float = 0.0  # Prediction accuracy
    collapse_quality: float = 0.0  # Decision quality
    morph_outcome_quality: float = 0.0  # Action success rate
    confidence_calibration: float = 0.0  # Confidence accuracy
    parameter_updates: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class ResourceState:
    """Multi-dimensional resource tracking."""

    time: float  # Time budget
    capital: float  # Economic budget
    attention: float  # Cognitive bandwidth
    compute: float  # INV_HW_001: hardware_bounded_cognition
    credibility: float  # Trust/reputation
    optionality: float  # Future option value
    memory_budget: float  # Storage capacity
    bandwidth: float  # Communication capacity


@dataclass(frozen=True)
class EconomicState:
    """Economic evaluation state."""

    opportunity: float  # Expected opportunity value
    revenue: float  # Current revenue
    cost: float  # Current costs
    risk: float  # Risk-adjusted cost
    leverage: float  # Multiplier effect
    compounding: float  # Long-term growth rate

    @property
    def economic_value(self) -> float:
        """
        best_action = argmax(revenue - cost - risk + leverage + compounding)
        """
        return self.revenue - self.cost - self.risk + self.leverage + self.compounding


@dataclass(frozen=True)
class ExternalWorldState:
    """External environment modeling."""

    market: dict[str, Any] = field(default_factory=dict)
    institutions: dict[str, Any] = field(default_factory=dict)
    people: dict[str, Any] = field(default_factory=dict)
    competitors: dict[str, Any] = field(default_factory=dict)
    trends: dict[str, Any] = field(default_factory=dict)
    constraints: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class HardwareState:
    """INV_HW_001: Hardware awareness and constraints."""

    cpu: float  # 0-1 utilization
    gpu: float  # 0-1 utilization
    npu: float  # 0-1 utilization (neural processing)
    ram: float  # 0-1 utilization
    vram: float  # 0-1 utilization (video/GPU memory)
    disk: float  # 0-1 utilization
    net: float  # 0-1 utilization
    bus: float  # 0-1 utilization
    tool_availability: dict[str, bool] = field(default_factory=dict)
    queue_pressure: float = 0.0

    def satisfies_demand(self, demand: dict[str, float]) -> bool:
        """
        runtime_demand <= hardware_capacity
        """
        capacity = {
            "cpu": 1.0 - self.cpu,
            "gpu": 1.0 - self.gpu,
            "ram": 1.0 - self.ram,
            "disk": 1.0 - self.disk,
        }
        for resource, required in demand.items():
            if capacity.get(resource, 0) < required:
                return False
        return True


@dataclass(frozen=True)
class Patch:
    """INV_MOD_001: Governed self-modification proposal."""

    id: str
    tier: PatchTier
    target: str  # System component to modify
    proposal: dict[str, Any] = field(default_factory=dict)
    expected_gain: float = 0.0
    risk: float = 0.0
    drift: float = 0.0  # INV_ID_001: identity_drift_bound
    irreversibility: float = 0.0  # INV_SEL_001: rollbackable
    rollback_plan: list[str] = field(default_factory=list)
    approved: bool = False

    def can_commit(self, t1: float, t2: float, t3: float) -> bool:
        """
        commit_patch iff confidence>=t1 &&
                         rollbackable &&
                         identity_drift<=t2 &&
                         risk<=t3
        """
        return (
            self.expected_gain >= t1
            and self.irreversibility < 1.0  # Rollbackable
            and self.drift <= t2
            and self.risk <= t3
        )


@dataclass(frozen=True)
class SelfModificationState:
    """INV_MOD_001: Any-modification state tracking."""

    params: dict[str, float | str | bool] = field(default_factory=dict)
    policies: dict[str, dict[str, Any]] = field(default_factory=dict)
    routes: dict[str, str] = field(default_factory=dict)
    memory_schemas: dict[str, dict[str, Any]] = field(default_factory=dict)
    tool_schemas: dict[str, dict[str, Any]] = field(default_factory=dict)
    eval_weights: dict[str, float] = field(default_factory=dict)
    pending_patches: list[Patch] = field(default_factory=list)


@dataclass(frozen=True)
class NodeState:
    """State of a distributed node in federation."""

    id: str
    role: NodeRole
    trust: float  # 0-1 reliability score
    load: float  # 0-1 current load
    capability: float  # 0-1 competence score
    freshness: float  # 0-1 recency of heartbeat
    status: NodeStatus = NodeStatus.ONLINE


@dataclass(frozen=True)
class DistributedState:
    """Federation state and topology."""

    topology: Topology = Topology.HYBRID
    nodes: list[NodeState] = field(default_factory=list)
    consensus_mode: ConsensusMode = ConsensusMode.WEIGHTED


@dataclass(frozen=True)
class ExecutableAction:
    """Staged action ready for execution."""

    id: str
    target: str
    interface: str  # Tool/interface to use
    permissions: list[str] = field(default_factory=list)
    cost: float = 0.0
    risk: float = 0.0
    reversibility: float = 0.0  # INV_SEL_001
    expected_outcome: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ActionResult:
    """Outcome of executed action."""

    action_id: str
    success: bool
    outcome: dict[str, Any] = field(default_factory=dict)
    verification: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionState:
    """Execution tracking and results."""

    planned_actions: list[ExecutableAction] = field(default_factory=list)
    staged_actions: list[ExecutableAction] = field(default_factory=list)
    executed_actions: list[ExecutableAction] = field(default_factory=list)
    results: list[ActionResult] = field(default_factory=list)


@dataclass(frozen=True)
class IdentityCore:
    """Core identity invariants that must hold."""

    safety: bool = True
    coherence: bool = True
    integrity: bool = True
    anti_dependency: bool = True  # INV_HUM_003
    boundedness: bool = True  # INV_RES_001, INV_HW_001


@dataclass(frozen=True)
class IdentityAdaptive:
    """Adaptive strategies that can evolve."""

    strategies: list[str] = field(default_factory=list)
    routines: list[str] = field(default_factory=list)
    allocation_policies: list[str] = field(default_factory=list)
    communication_forms: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class IdentityState:
    """INV_ID_001: Identity with drift tracking."""

    core: IdentityCore = field(default_factory=IdentityCore)
    adaptive: IdentityAdaptive = field(default_factory=IdentityAdaptive)
    drift_score: float = 0.0  # Must stay within delta_id bound


@dataclass(frozen=True)
class GovernanceState:
    """INV_GOV_001: Higher law precedence tracking."""

    law_stack: list[str] = field(default_factory=list)  # Ordered by precedence
    active_restrictions: list[str] = field(default_factory=list)
    permission_policies: dict[str, dict[str, Any]] = field(default_factory=dict)
    rollback_policies: dict[str, dict[str, Any]] = field(default_factory=dict)
    escalation_rules: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass(frozen=True)
class PersistenceState:
    """F013: Persistent continuity across sessions."""

    episodic_memory: list[MemoryItem] = field(default_factory=list)
    structural_memory: list[MemoryItem] = field(default_factory=list)
    identity_persistence: list[MemoryItem] = field(default_factory=list)
    open_loops: list[Goal] = field(default_factory=list)  # Unfinished goals


# ============================================================================
# UNIFIED AMOS STATE
# ============================================================================


@dataclass(frozen=True)
class AMOSState:
    """
    Complete state tensor X_t = (V_t, E_t, S_t, Λ_t) where:
    - V_t: Node states
    - E_t: Edge states
    - S_t: System state (this structure)
    - Λ_t: Laws/constraints
    """

    epistemic_state: EpistemicState = field(default_factory=EpistemicState)
    human_state: Optional[HumanState] = None  # Optional human context
    world_graph: WorldGraph = field(default_factory=WorldGraph)
    workspace: WorkspaceState = field(default_factory=WorkspaceState)
    branches: BranchSet = field(default_factory=BranchSet)
    temporal_state: TemporalState = field(default_factory=TemporalState)
    memory: MemoryState = field(default_factory=MemoryState)
    constitution: ConstitutionState = field(default_factory=ConstitutionState)
    energy: EnergyState = field(default_factory=lambda: EnergyState(total=1.0))
    action_state: ActionState = field(default_factory=ActionState)
    meta_state: MetaCognitiveState = field(default_factory=MetaCognitiveState)
    resources: ResourceState = field(
        default_factory=lambda: ResourceState(
            time=3600,  # 1 hour default
            capital=1000.0,
            attention=1.0,
            compute=1.0,
            credibility=1.0,
            optionality=1.0,
            memory_budget=1024.0,  # MB
            bandwidth=100.0,  # Mbps
        )
    )
    economics: EconomicState = field(
        default_factory=lambda: EconomicState(
            opportunity=0.0,
            revenue=0.0,
            cost=0.0,
            risk=0.0,
            leverage=1.0,
            compounding=0.0,
        )
    )
    external_world: ExternalWorldState = field(default_factory=ExternalWorldState)
    hardware: HardwareState = field(
        default_factory=lambda: HardwareState(
            cpu=0.0, gpu=0.0, npu=0.0, ram=0.0, vram=0.0, disk=0.0, net=0.0, bus=0.0
        )
    )
    self_modification: SelfModificationState = field(default_factory=SelfModificationState)
    distribution: DistributedState = field(default_factory=DistributedState)
    execution: ExecutionState = field(default_factory=ExecutionState)
    identity: IdentityState = field(default_factory=IdentityState)
    governance: GovernanceState = field(default_factory=GovernanceState)
    persistence: PersistenceState = field(default_factory=PersistenceState)


# ============================================================================
# SERVICE PROTOCOLS (Abstract Interfaces)
# ============================================================================

InputT_contra = TypeVar("InputT_contra", contravariant=True)
OutputT_co = TypeVar("OutputT_co", covariant=True)


@runtime_checkable
class Service(Protocol[InputT_contra, OutputT_co]):
    """Base service protocol for all AMOS services."""

    async def execute(self, input_data: InputT_contra) -> OutputT_co: ...


class Observer(ABC):
    """Layer L1: Observe service."""

    @abstractmethod
    async def observe(
        self,
        raw_inputs: list[Signal],
        tool_results: list[dict[str, Any]],
        telemetry: dict[str, Any],
        world_signals: list[Signal],
    ) -> list[Event]:
        """observe(raw_inputs, tool_results, telemetry, world_signals) -> Event[]"""
        ...


class StateAssembler(ABC):
    """Layer L1: Assemble state service."""

    @abstractmethod
    async def assemble_state(
        self,
        events: list[Event],
        previous_state: AMOSState,
        memory: MemoryState,
    ) -> AMOSState:
        """assemble_state(events, previous_state, memory) -> AMOSState"""
        ...


class MemoryService(ABC):
    """Layer L1: Memory retrieval service."""

    @abstractmethod
    async def retrieve_memory(
        self,
        query: str,
        memory_state: MemoryState,
        k: int = 5,
    ) -> tuple[list[MemoryItem], float, list[str]]:
        """
        retrieve_memory(query, memory_state, k) ->
            (memory_items, confidence, source_trace)
        """
        ...


class WorldModeler(ABC):
    """Layer L2: World modeling service."""

    @abstractmethod
    async def build_world_graph(self, state: AMOSState) -> WorldGraph:
        """build_world_graph(state) -> WorldGraph"""
        ...


class EpistemicTagger(ABC):
    """F001: Epistemic tagging service."""

    @abstractmethod
    async def tag_epistemics(
        self,
        claim: str,
        model_context: WorldGraph,
    ) -> EpistemicState:
        """
        tag_epistemics(claim, model_context) ->
            {assumptions, limits, confidence, grounding}
        """
        ...


class SignalProcessor(ABC):
    """F002: Signal/noise separation service."""

    @abstractmethod
    async def extract_signal_noise(
        self,
        message: str,
        history: list[Event],
    ) -> tuple[dict[str, Any], dict[str, float], HumanState]:
        """
        extract_signal_noise(message, history) ->
            (signal, noise_scores, human_state_estimate)
        """
        ...


class HumanClassifier(ABC):
    """F003: Human state classification service."""

    @abstractmethod
    async def classify_human_state(self, human_estimate: HumanState) -> HumanStateClass:
        """classify_human_state(human_estimate) -> stable|activated|overloaded|shutdown|high_risk"""
        ...


class HumanCoherenceService(ABC):
    """Layer L3: Human coherence induction service."""

    @abstractmethod
    async def compute_safe_intensity(
        self,
        human_state: HumanState,
    ) -> dict[str, float]:
        """
        compute_safe_intensity(human_state) ->
            {speed, depth, density, challenge}
        """
        ...

    @abstractmethod
    async def select_human_intervention(
        self,
        human_state: HumanState,
        signal: dict[str, Any],
        noise: dict[str, float],
    ) -> str:
        """
        select_human_intervention(human_state, signal, noise) ->
            mirror|separate|reframe|deconstruct|ground|boundary|micro_step
        """
        ...

    @abstractmethod
    async def build_human_response(
        self,
        human_state: HumanState,
        intervention: str,
        safe_intensity: dict[str, float],
    ) -> dict[str, Any]:
        """
        build_human_response(human_state, intervention, safe_intensity) ->
            {ground, distinction, noise_reduction, agency_return, scale_match}
        """
        ...


class WorkspaceManager(ABC):
    """Layer L1: Workspace management service."""

    @abstractmethod
    async def update_workspace(self, signals: list[Signal]) -> WorkspaceState:
        """update_workspace(signals) -> WorkspaceState"""
        ...


class BranchGenerator(ABC):
    """F007: Branch generation service."""

    @abstractmethod
    async def generate_branches(
        self,
        world_graph: WorldGraph,
        workspace: WorkspaceState,
        temporal_state: TemporalState,
        memory: MemoryState,
        constitution: ConstitutionState,
        resources: ResourceState,
    ) -> list[Branch]:
        """
        generate_branches(world_graph, workspace, temporal_state,
                         memory, constitution, resources) -> Branch[]
        """
        ...


class BranchSimulator(ABC):
    """F008: Branch simulation and scoring service."""

    @abstractmethod
    async def simulate_branch(
        self,
        world_graph: WorldGraph,
        branch: Branch,
        horizon: float,
        budget: float,
    ) -> tuple[dict[str, Any], dict[str, float]]:
        """
        simulate_branch(world_graph, branch, horizon, budget) ->
            (predicted_state, score_vector)
        """
        ...

    @abstractmethod
    async def score_branch(self, branch: Branch) -> dict[str, float]:
        """
        score_branch(branch) ->
            {goal_fit, risk, cost, coherence, drift, reversibility, confidence}
        """
        ...


class BranchSelector(ABC):
    """F009: Constraint-bounded collapse service."""

    @abstractmethod
    async def select_branch(
        self,
        branches: list[Branch],
        constitution: ConstitutionState,
        governance: GovernanceState,
        resources: ResourceState,
    ) -> Optional[tuple[Branch], dict[str, Any]]:
        """
        select_branch(branches, constitution, governance, resources) ->
            (best_branch, trace)
        """
        ...


class ResourceAllocator(ABC):
    """F010: Resource allocation service."""

    @abstractmethod
    async def allocate_resources(
        self,
        goals: list[Goal],
        resource_state: ResourceState,
        economic_state: EconomicState,
        world_state: ExternalWorldState,
    ) -> dict[str, dict[str, float]]:
        """
        allocate_resources(goals, resource_state, economic_state, world_state) ->
            allocation_plan
        """
        ...


class EconomicService(ABC):
    """F011: Economic reasoning service."""

    @abstractmethod
    async def evaluate_opportunity(self, option: Goal) -> dict[str, float]:
        """
        evaluate_opportunity(option) ->
            {revenue, cost, risk, leverage, compounding}
        """
        ...

    @abstractmethod
    async def optimize_goal_portfolio(
        self,
        goals: list[Goal],
        resources: ResourceState,
    ) -> list[Goal]:
        """
        optimize_goal_portfolio(goals, resources) -> Goal[]
        """
        ...


class Auditor(ABC):
    """F020: Audit-first runtime service."""

    @abstractmethod
    async def audit_action(
        self,
        action_or_branch: Branch | ExecutableAction,
        governance: GovernanceState,
        identity: IdentityState,
        resources: ResourceState,
    ) -> dict[str, Any]:
        """
        audit_action(action_or_branch, governance, identity, resources) ->
            {legal, safe, rollbackable, identity_ok, trace}
        """
        ...


class ExecutionService(ABC):
    """Layer L5: Governed execution service."""

    @abstractmethod
    async def stage_execution(
        self,
        action: Branch,
        interfaces: dict[str, Any],
        permissions: list[str],
    ) -> ExecutableAction:
        """stage_execution(action, interfaces, permissions) -> ExecutableAction"""
        ...

    @abstractmethod
    async def execute_action(self, staged_action: ExecutableAction) -> ActionResult:
        """execute_action(staged_action) -> ActionResult"""
        ...

    @abstractmethod
    async def rollback_action(
        self,
        action_id: str,
        rollback_plan: list[str],
    ) -> ActionResult:
        """rollback_action(action_id, rollback_plan) -> ActionResult"""
        ...


class LearningService(ABC):
    """F016: Outcome-based learning service."""

    @abstractmethod
    async def compute_prediction_error(
        self,
        outcome: dict[str, Any],
        expected_outcome: dict[str, Any],
    ) -> float:
        """compute_prediction_error(outcome, expected_outcome) -> number"""
        ...

    @abstractmethod
    async def update_models(
        self,
        model_state: dict[str, Any],
        prediction_error: float,
    ) -> dict[str, Any]:
        """update_models(model_state, prediction_error) -> model_updates"""
        ...

    @abstractmethod
    async def consolidate_memory(
        self,
        short_term_items: list[MemoryItem],
        outcome: dict[str, Any],
    ) -> MemoryState:
        """consolidate_memory(short_term_items, outcome) -> MemoryState"""
        ...


class SelfModificationService(ABC):
    """F017: Tiered self-modification service."""

    @abstractmethod
    async def propose_patch(
        self,
        target: str,
        proposal: dict[str, Any],
        tier: PatchTier,
    ) -> Patch:
        """propose_patch(target, proposal, tier) -> Patch"""
        ...

    @abstractmethod
    async def audit_patch(
        self,
        patch: Patch,
        governance: GovernanceState,
        identity: IdentityState,
    ) -> dict[str, Any]:
        """audit_patch(patch, governance, identity) -> dict"""
        ...

    @abstractmethod
    async def apply_patch(
        self,
        self_modification_state: SelfModificationState,
        patch: Patch,
    ) -> SelfModificationState:
        """apply_patch(self_modification_state, patch) -> SelfModificationState"""
        ...

    @abstractmethod
    async def estimate_identity_drift(
        self,
        identity_current: IdentityState,
        identity_candidate: IdentityState,
    ) -> float:
        """estimate_identity_drift(identity_current, identity_candidate) -> float"""
        ...


class DistributedService(ABC):
    """F019: Distributed federation service."""

    @abstractmethod
    async def merge_node_outputs(
        self,
        node_outputs: list[dict[str, Any]],
        trust_weights: list[float],
        consensus_mode: ConsensusMode,
    ) -> dict[str, Any]:
        """merge_node_outputs(node_outputs, trust_weights, consensus_mode) -> object"""
        ...

    @abstractmethod
    async def failover_node_role(
        self,
        distributed_state: DistributedState,
        failed_node_id: str,
    ) -> DistributedState:
        """failover_node_role(distributed_state, failed_node_id) -> DistributedState"""
        ...


class PersistenceService(ABC):
    """F013: Persistent continuity service."""

    @abstractmethod
    async def persist_state(
        self,
        state: AMOSState,
        memory_updates: list[MemoryItem],
        identity_updates: IdentityState,
        open_loops: list[Goal],
    ) -> PersistenceState:
        """
        persist_state(state, memory_updates, identity_updates, open_loops) ->
            PersistenceState
        """
        ...


# ============================================================================
# RUNTIME ORCHESTRATOR
# ============================================================================


class AMOSRuntime(ABC):
    """
    Master runtime implementing the Omega+ pipeline:

    AMOS = observe -> model -> allocate -> generate -> simulate ->
           select -> execute -> audit -> learn -> modify -> preserve -> evolve
    """

    @abstractmethod
    async def run_runtime_cycle(self, state: AMOSState) -> AMOSState:
        """
        state_next = persist(modify(learn(verify(execute(
            collapse(evaluate(simulate(generate(
                allocate(regulate(model(observe(state_current)))))))))))))
        """
        ...


# ============================================================================
# INVARIANT VALIDATION
# ============================================================================


class InvariantViolation(Exception):
    """Raised when an AMOS invariant is violated."""

    def __init__(self, invariant_id: str, expression: str, details: str) -> None:
        self.invariant_id = invariant_id
        self.expression = expression
        super().__init__(f"Invariant {invariant_id} violated: {expression} - {details}")


class InvariantValidator:
    """Runtime validator for AMOS invariants."""

    INVARIANTS: dict[str, Constraint] = {
        "INV_EPI_001": Constraint(
            id="INV_EPI_001",
            expression="access(x) != x",
            severity=ConstraintSeverity.CRITICAL,
        ),
        "INV_EPI_002": Constraint(
            id="INV_EPI_002",
            expression="truth = argmax(coherence + prediction + stability - contradiction)",
            severity=ConstraintSeverity.BLOCKING,
        ),
        "INV_HUM_001": Constraint(
            id="INV_HUM_001",
            expression="human_next = reorganize(human_current | conditions)",
            severity=ConstraintSeverity.CRITICAL,
        ),
        "INV_HUM_002": Constraint(
            id="INV_HUM_002",
            expression="overload_risk < safe_threshold",
            severity=ConstraintSeverity.CRITICAL,
        ),
        "INV_HUM_003": Constraint(
            id="INV_HUM_003",
            expression="d(dependency)/dt <= 0",
            severity=ConstraintSeverity.BLOCKING,
        ),
        "INV_SEL_001": Constraint(
            id="INV_SEL_001",
            expression="commit iff legal && confidence>=t1 && reversibility>=t2 && risk<=t3",
            severity=ConstraintSeverity.BLOCKING,
        ),
        "INV_RES_001": Constraint(
            id="INV_RES_001",
            expression="sum(allocation_i) <= available_resources",
            severity=ConstraintSeverity.BLOCKING,
        ),
        "INV_HW_001": Constraint(
            id="INV_HW_001",
            expression="runtime_demand <= hardware_capacity",
            severity=ConstraintSeverity.BLOCKING,
        ),
        "INV_ID_001": Constraint(
            id="INV_ID_001",
            expression="drift(identity_t, identity_t+1) <= delta_id",
            severity=ConstraintSeverity.CRITICAL,
        ),
        "INV_MOD_001": Constraint(
            id="INV_MOD_001",
            expression="commit(patch) iff rollbackable && legal && risk<=threshold && drift<=threshold",
            severity=ConstraintSeverity.CRITICAL,
        ),
        "INV_GOV_001": Constraint(
            id="INV_GOV_001",
            expression="higher_law > lower_law",
            severity=ConstraintSeverity.CRITICAL,
        ),
    }

    @classmethod
    def validate_resource_bounds(cls, state: AMOSState) -> None:
        """Validate INV_RES_001: resource_boundedness."""
        if not state.energy.is_within_bounds():
            raise InvariantViolation(
                "INV_RES_001",
                "sum(allocation_i) <= available_resources",
                f"Allocation {sum(state.energy.allocation.values())} exceeds "
                f"total {state.energy.total + state.energy.reserve}",
            )

    @classmethod
    def validate_hardware_bounds(cls, state: AMOSState, demand: dict[str, float]) -> None:
        """Validate INV_HW_001: hardware_bounded_cognition."""
        if not state.hardware.satisfies_demand(demand):
            raise InvariantViolation(
                "INV_HW_001",
                "runtime_demand <= hardware_capacity",
                f"Hardware demand {demand} exceeds capacity",
            )

    @classmethod
    def validate_human_safety(cls, state: AMOSState, intensity: float) -> None:
        """Validate INV_HUM_002: no_destabilizing_insight."""
        if state.human_state and not state.human_state.is_safe_for_intervention(intensity):
            raise InvariantViolation(
                "INV_HUM_002",
                "overload_risk < safe_threshold",
                f"Intervention intensity {intensity} exceeds safe threshold "
                f"for human state {state.human_state.state_class}",
            )

    @classmethod
    def validate_branch_selection(cls, branch: Branch, t1: float, t2: float, t3: float) -> None:
        """Validate INV_SEL_001: legal_selection_only."""
        if not branch.is_admissible(t1, t2, t3):
            raise InvariantViolation(
                "INV_SEL_001",
                "commit(branch) iff legal(branch) && confidence>=t1 && reversibility>=t2 && risk<=t3",
                f"Branch {branch.id} is not admissible: legal={branch.legal}, "
                f"confidence={branch.confidence}, reversibility={branch.reversibility}, "
                f"risk={branch.risk}",
            )

    @classmethod
    def validate_identity_drift(
        cls, current: IdentityState, candidate: IdentityState, delta_id: float
    ) -> None:
        """Validate INV_ID_001: identity_drift_bound."""
        if candidate.drift_score > delta_id:
            raise InvariantViolation(
                "INV_ID_001",
                "drift(identity_t, identity_t+1) <= delta_id",
                f"Identity drift {candidate.drift_score} exceeds bound {delta_id}",
            )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Tensors
    "Tensor",
    "GraphTensor",
    "BranchTensor",
    "EnergyTensor",
    "ResourceTensor",
    "HumanTensor",
    "WorldTensor",
    "ModificationTensor",
    # Enums
    "NodeType",
    "EdgeType",
    "GoalStatus",
    "SignalKind",
    "HumanStateClass",
    "MemoryKind",
    "PatchTier",
    "Topology",
    "ConsensusMode",
    "NodeRole",
    "NodeStatus",
    "ConstraintSeverity",
    "LayerId",
    # Core Data Structures
    "EpistemicState",
    "HumanState",
    "GraphNode",
    "GraphEdge",
    "Constraint",
    "WorldGraph",
    "Goal",
    "Signal",
    "AttentionItem",
    "WorkspaceState",
    "Morph",
    "Branch",
    "BranchSet",
    "Event",
    "TemporalState",
    "MemoryItem",
    "MemoryState",
    "ConstitutionState",
    "EnergyState",
    "ActionState",
    "MetaCognitiveState",
    "ResourceState",
    "EconomicState",
    "ExternalWorldState",
    "HardwareState",
    "Patch",
    "SelfModificationState",
    "NodeState",
    "DistributedState",
    "ExecutableAction",
    "ActionResult",
    "ExecutionState",
    "IdentityCore",
    "IdentityAdaptive",
    "IdentityState",
    "GovernanceState",
    "PersistenceState",
    # Unified State
    "AMOSState",
    # Services
    "Service",
    "Observer",
    "StateAssembler",
    "MemoryService",
    "WorldModeler",
    "EpistemicTagger",
    "SignalProcessor",
    "HumanClassifier",
    "HumanCoherenceService",
    "WorkspaceManager",
    "BranchGenerator",
    "BranchSimulator",
    "BranchSelector",
    "ResourceAllocator",
    "EconomicService",
    "Auditor",
    "ExecutionService",
    "LearningService",
    "SelfModificationService",
    "DistributedService",
    "PersistenceService",
    "AMOSRuntime",
    # Validation
    "InvariantViolation",
    "InvariantValidator",
]
