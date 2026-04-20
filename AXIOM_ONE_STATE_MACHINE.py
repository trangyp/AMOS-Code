from __future__ import annotations

"""AXIOM ONE: Executable State Machine Implementation"""

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from enum import Enum
from typing import Any, Optional, Protocol


class ObjectState(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ExecutionState(Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Actor:
    id: str
    type: str
    workspace_id: str
    permissions: list[str] = field(default_factory=list)


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
    state: ObjectState
    criticality: str
    security_class: str
    relations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    id: str
    source_id: str
    target_id: str
    edge_type: str
    created_at: datetime
    is_active: bool = True


@dataclass
class ExecutionRequest:
    id: str
    kind: str
    target: str
    environment: str
    command: str
    timeout_seconds: int = 300
    rollback_eligible: bool = False


@dataclass
class ExecutionReceipt:
    execution_id: str
    state: ExecutionState
    started_at: datetime
    completed_at: datetime
    exit_code: int
    stdout: str = ""
    artifacts: list[str] = field(default_factory=list)


@dataclass
class AgentStep:
    kind: str
    target: str
    reason: str
    result: str = None


class KernelEngine(Protocol):
    async def create(self, obj_type: str, data: dict, actor: Actor) -> AxiomObject: ...
    async def transition(self, obj_id: str, to_state: ObjectState, actor: Actor) -> AxiomObject: ...
    async def get(self, obj_id: str) -> Optional[AxiomObject]: ...
    async def check_policy(self, action: str, target: str, actor: Actor) -> bool: ...


class GraphEngine(Protocol):
    async def link(self, source: str, target: str, edge_type: str, actor: Actor) -> Edge: ...
    async def traverse(self, from_id: str, edge_type: str, depth: int = 1) -> list[Edge]: ...
    async def blast_radius(self, center_id: str, depth: int = 3) -> list[str]: ...


class ExecutionEngine(Protocol):
    async def submit(self, request: ExecutionRequest) -> str: ...
    async def execute(self, exec_id: str) -> AsyncIterator[ExecutionState]: ...
    async def get_receipt(self, exec_id: str) -> ExecutionReceipt: ...


class AxiomStateMachine:
    """Master state machine coordinating all six engines."""

    def __init__(self, kernel: KernelEngine, graph: GraphEngine, execution: ExecutionEngine):
        self.kernel = kernel
        self.graph = graph
        self.execution = execution

    async def create_object(
        self, obj_type: str, name: str, actor: Actor, **metadata
    ) -> AxiomObject:
        """STATE TRANSITION: Create new object."""
        if not await self.kernel.check_policy("create", obj_type, actor):
            raise PermissionError(f"Actor {actor.id} cannot create {obj_type}")
        data = {"name": name, **metadata}
        return await self.kernel.create(obj_type, data, actor)

    async def link_objects(self, source: str, target: str, edge_type: str, actor: Actor) -> Edge:
        """STATE TRANSITION: Create relationship."""
        if not await self.kernel.check_policy("link", source, actor):
            raise PermissionError(f"Actor {actor.id} cannot link objects")
        return await self.graph.link(source, target, edge_type, actor)

    async def execute_action(self, request: ExecutionRequest, actor: Actor) -> ExecutionReceipt:
        """STATE TRANSITION: Execute command."""
        if not await self.kernel.check_policy(f"execute:{request.kind}", request.target, actor):
            raise PermissionError("Execution not permitted")
        exec_id = await self.execution.submit(request)
        async for _ in self.execution.execute(exec_id):
            pass
        return await self.execution.get_receipt(exec_id)

    async def compute_impact(self, object_id: str) -> list[str]:
        """QUERY: Compute blast radius."""
        return await self.graph.blast_radius(object_id, depth=3)


# Core engine factory
def create_axiom_object(obj_type: str, name: str, workspace_id: str, owner_id: str) -> AxiomObject:
    now = datetime.now(UTC)
    return AxiomObject(
        id=f"ax_{now.timestamp()}",
        type=obj_type,
        name=name,
        workspace_id=workspace_id,
        owner_id=owner_id,
        created_at=now,
        updated_at=now,
        version=1,
        state=ObjectState.DRAFT,
        criticality="medium",
        security_class="internal",
    )
