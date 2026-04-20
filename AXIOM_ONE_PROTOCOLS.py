from __future__ import annotations

"""
AXIOM ONE: Technical State Machine Protocols
Full executable specification for the six core engines.
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from enum import Enum

UTC = UTC
from typing import Any, Protocol

# ============================================================================
# 1. KERNEL PROTOCOLS
# ============================================================================


class KernelState(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    DELETED = "deleted"


class KernelTransition(Enum):
    CREATE = "create"
    ACTIVATE = "activate"
    DEPRECATE = "deprecate"
    REACTIVATE = "reactivate"
    ARCHIVE = "archive"
    DELETE = "delete"
    RESTORE = "restore"


@dataclass(frozen=True)
class ActorRef:
    actor_type: str  # human|agent|system
    actor_id: str
    workspace_id: str
    permissions: Tuple[str, ...]


@dataclass(frozen=True)
class ObjectRef:
    object_id: str
    object_type: str
    workspace_id: str


@dataclass(frozen=True)
class ActionRef:
    action_type: str
    target: ObjectRef
    parameters: dict[str, Any]


@dataclass
class PolicyContext:
    environment: str
    data_class: str
    budget_limit: float
    requires_approval: bool
    supervised: bool


@dataclass
class PolicyResult:
    allowed: bool
    reason: str
    required_approvers: list[str]
    audit_level: str


@dataclass
class AxiomObject:
    id: str
    type: str
    name: str
    workspace_id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    version: int
    status: KernelState
    criticality: str
    security_class: str
    cost_center: str = None
    relations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    audit_ref: str = None


class KernelEngine(Protocol):
    async def create_object(
        self, obj_type: str, initial_data: dict[str, Any], actor: ActorRef, workspace_id: str
    ) -> Tuple[AxiomObject, str]: ...

    async def transition_object(
        self,
        object_id: str,
        transition: KernelTransition,
        actor: ActorRef,
        policy_context: PolicyContext,
    ) -> Tuple[AxiomObject, str]: ...

    async def get_object(self, object_id: str, at_version: int = None) -> AxiomObject: ...

    async def get_object_history(self, object_id: str) -> list[tuple[AxiomObject, str]]: ...

    async def evaluate_policy(
        self, action: ActionRef, target: ObjectRef, actor: ActorRef
    ) -> PolicyResult: ...


# ============================================================================
# 2. GRAPH PROTOCOLS
# ============================================================================


class EdgeType(Enum):
    CONTAINS = "contains"
    DEPENDS_ON = "depends_on"
    CALLS = "calls"
    EMITS_TO = "emits_to"
    READS_FROM = "reads_from"
    WRITES_TO = "writes_to"
    DEPLOYS_FROM = "deploys_from"
    DEPLOYS_TO = "deploys_to"
    IMPACTS = "impacts"
    CAUSED_BY = "caused_by"
    OWNS = "owns"
    GOVERNS = "governs"
    DOCUMENTS = "documents"
    REFERENCES = "references"
    USED_TOOL = "used_tool"
    PRODUCED = "produced"


@dataclass
class Edge:
    id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    created_at: datetime
    created_by: str
    confidence: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


@dataclass
class ImpactReport:
    center_object: str
    affected_objects: list[tuple[str, int]]  # (object_id, depth)
    risk_score: float
    recommended_actions: list[str]


class GraphEngine(Protocol):
    async def create_edge(
        self,
        source: str,
        target: str,
        edge_type: EdgeType,
        actor: ActorRef,
        properties: dict[str, Any] = None,
    ) -> Edge: ...

    async def invalidate_edge(self, edge_id: str, actor: ActorRef, reason: str) -> None: ...

    async def traverse(
        self,
        from_object: str,
        edge_types: list[EdgeType],
        direction: str = "out",
        max_depth: int = 1,
    ) -> list[Edge]: ...

    async def find_paths(
        self, source: str, target: str, allowed_edges: list[EdgeType] = None
    ) -> list[list[Edge]]: ...

    async def compute_blast_radius(self, center_object: str, depth: int = 3) -> ImpactReport: ...


# ============================================================================
# 3. EXECUTION PROTOCOLS
# ============================================================================


class ExecutionState(Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    PREPARING = "preparing"
    RUNNING = "running"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"


@dataclass
class ResourceLimits:
    cpu_cores: float
    memory_mb: int
    disk_mb: int
    network: str  # restricted|unrestricted|none


@dataclass
class ExecutionRequest:
    execution_id: str
    kind: str
    target: str
    environment: str
    permissions: list[str]
    timeout_seconds: int
    resource_limits: ResourceLimits
    command_or_payload: str
    working_directory: str = None
    environment_vars: dict[str, str] = field(default_factory=dict)
    expected_artifacts: list[str] = field(default_factory=list)
    rollback_eligible: bool = False
    rollback_script: str = None


@dataclass
class ExecutionEvent:
    timestamp: datetime
    state: ExecutionState
    message: str
    data: dict[str, Any]


@dataclass
class ArtifactRef:
    artifact_id: str
    artifact_type: str
    storage_path: str
    metadata: dict[str, Any]


@dataclass
class ExecutionReceipt:
    execution_id: str
    request: ExecutionRequest
    started_at: datetime
    completed_at: datetime
    final_state: ExecutionState
    exit_code: int
    stdout: str
    stderr: str
    artifacts: list[ArtifactRef]
    rollback_available: bool


class ExecutionTarget(Protocol):
    async def validate(self, request: ExecutionRequest) -> bool: ...
    async def execute(self, request: ExecutionRequest) -> AsyncIterator[ExecutionEvent]: ...


# ============================================================================
# 4. OBSERVATION PROTOCOLS
# ============================================================================


class TelemetryType(Enum):
    LOG = "log"
    METRIC = "metric"
    TRACE = "trace"
    PROFILE = "profile"
    EVENT = "event"


@dataclass
class TelemetryPoint:
    timestamp: datetime
    type: TelemetryType
    source: str
    data: dict[str, Any]
    execution_id: str = None
    object_id: str = None
    actor_id: str = None
    trace_id: str = None
    span_id: str = None


class ObservationEngine(Protocol):
    async def ingest(self, point: TelemetryPoint) -> None: ...
    async def ingest_batch(self, points: list[TelemetryPoint]) -> None: ...


# ============================================================================
# 5. KNOWLEDGE PROTOCOLS
# ============================================================================


class KnowledgeType(Enum):
    DOC = "doc"
    TICKET = "ticket"
    ADR = "adr"
    RUNBOOK = "runbook"
    RATIONALE = "rationale"


@dataclass
class KnowledgeObject:
    id: str
    knowledge_type: KnowledgeType
    title: str
    content: str
    format: str
    relates_to: list[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    version: int
    embedding_id: str = None


class KnowledgeEngine(Protocol):
    async def create_knowledge(
        self, ktype: KnowledgeType, title: str, content: str, relates_to: list[str], actor: ActorRef
    ) -> KnowledgeObject: ...

    async def search_semantic(
        self, query: str, ktype: KnowledgeType = None
    ) -> list[KnowledgeObject]: ...


# ============================================================================
# 6. AGENT PROTOCOLS
# ============================================================================


class AgentRole(Enum):
    REPO_DEBUGGER = "repo-debugger"
    PATCH_GENERATOR = "patch-generator"
    TEST_WRITER = "test-writer"
    RELEASE_MANAGER = "release-manager"
    INFRA_DEBUGGER = "infra-debugger"
    SECURITY_REVIEWER = "security-reviewer"


@dataclass
class AgentScope:
    repos: list[str]
    paths: list[str]
    environments: list[str]


@dataclass
class AgentRun:
    run_id: str
    agent_role: str
    goal: str
    scope: AgentScope
    tools_allowed: list[str]
    max_steps: int
    budget: float
    approval_policy: str
    memory_mode: str
    status: str


@dataclass
class AgentStep:
    kind: str  # read|write|execute|query
    target: str
    reason: str
    result: str = None
    diff_ref: str = None


@dataclass
class AgentReceipt:
    run_id: str
    steps: list[AgentStep]
    evidence_refs: list[str]
    policies_checked: list[str]
    final_result: str
    rollback_available: bool


class AgentEngine(Protocol):
    async def plan_run(
        self, role: AgentRole, goal: str, scope: AgentScope, actor: ActorRef
    ) -> AgentRun: ...

    async def execute_step(self, run_id: str, step: AgentStep) -> dict[str, Any]: ...

    async def get_receipt(self, run_id: str) -> AgentReceipt: ...


# ============================================================================
# 7. EVENT SOURCING PROTOCOLS
# ============================================================================


@dataclass
class AxiomEvent:
    event_id: str
    timestamp: datetime
    actor_type: str
    actor_id: str
    action: str
    target_object_ids: list[str]
    input_refs: list[str]
    policy_checks: list[str]
    result: str
    diff_ref: str = None
    receipt_ref: str = None
    rollback_ref: str = None


class EventStore(Protocol):
    async def append(self, event: AxiomEvent) -> None: ...
    async def get(self, event_id: str) -> AxiomEvent: ...
    async def get_for_object(self, object_id: str) -> list[AxiomEvent]: ...


# ============================================================================
# 8. COMMAND SYSTEM
# ============================================================================


class CommandType(Enum):
    INSPECT = "inspect"
    EXPLAIN = "explain"
    DIFF = "diff"
    TEST = "test"
    PATCH = "patch"
    SIMULATE = "simulate"
    DEPLOY = "deploy"
    ROLLBACK = "rollback"
    TRACE = "trace"


@dataclass
class Command:
    command_type: CommandType
    target_type: str
    target_id: str
    options: dict[str, Any]
    actor: ActorRef


# ============================================================================
# 9. REPO AUTOPSY PROTOCOLS
# ============================================================================


@dataclass
class StaticIssue:
    category: str
    severity: str
    location: str
    message: str
    suggested_fix: str
    auto_fixable: bool


@dataclass
class AutopsyResult:
    repo_id: str
    static_issues: list[StaticIssue]
    safe_fixes: list[dict[str, Any]]
    patches: list[dict[str, Any]]
    residual_risk: list[str]


# ============================================================================
# 10. SIMULATION PROTOCOLS
# ============================================================================


@dataclass
class SimulationResult:
    confidence: float
    estimated_breakage: list[str]
    rollback_recommendation: str
    required_approvals: list[str]
    cost_impact: float


class SimulationEngine(Protocol):
    async def simulate(
        self, action: str, target_objects: list[str], environment: str
    ) -> SimulationResult: ...


# ============================================================================
# 11. SYSTEM INVARIANTS
# ============================================================================

SYSTEM_INVARIANTS = {
    "OBJECT_IDENTITY": "Every object has exactly one canonical identifier",
    "EVENT_IMMUTABILITY": "Events are append-only and cryptographically verifiable",
    "RELATION_TYPED": "All edges have explicit, schema-validated types",
    "ACTION_RECEIPT": "Every action produces a verifiable receipt",
    "ROLLBACK_ELIGIBILITY": "Every state change has calculable reversibility",
    "POLICY_PRECEDENCE": "Policy checks occur before action dispatch",
    "FULL_TRACEABILITY": "Every effect must be attributable to a cause",
    "COMPLETE_AUDIT": "All operations are recorded in the event log",
}


# ============================================================================
# 12. DATA CONTRACTS
# ============================================================================

DATA_CONTRACTS = {
    "studio_kernel": ["object_lookup", "permission_check", "apply_diff"],
    "forge_execution": ["run_build", "run_test_matrix", "collect_artifacts"],
    "orbit_execution": ["create_release_plan", "deploy", "rollback"],
    "pulse_observation": ["subscribe_logs", "correlate_alerts"],
    "sentinel_kernel": ["evaluate_policy", "record_exceptions"],
    "agent_all": ["read_graph", "request_execution", "emit_receipt"],
}


def create_axiom_object(
    obj_type: str, name: str, workspace_id: str, owner_id: str, **kwargs
) -> AxiomObject:
    """Factory for creating Axiom objects with proper defaults."""
    now = datetime.now(timezone.utc)
    return AxiomObject(
        id=f"ax_{now.timestamp()}",
        type=obj_type,
        name=name,
        workspace_id=workspace_id,
        owner_id=owner_id,
        created_at=now,
        updated_at=now,
        version=1,
        status=KernelState.DRAFT,
        criticality="medium",
        security_class="internal",
        **kwargs,
    )


def create_event(
    actor: ActorRef, action: str, targets: list[str], result: str = "success"
) -> AxiomEvent:
    """Factory for creating events."""
    now = datetime.now(timezone.utc)
    return AxiomEvent(
        event_id=f"evt_{now.timestamp()}",
        timestamp=now,
        actor_type=actor.actor_type,
        actor_id=actor.actor_id,
        action=action,
        target_object_ids=targets,
        input_refs=[],
        policy_checks=[],
        result=result,
    )
