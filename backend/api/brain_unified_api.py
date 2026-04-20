"""Brain Unified API - Single endpoint for all brain operations.

Combines all brain capabilities into a unified interface:
- Cognitive processing (think, decide, validate)
- Agent operations (spawn, monitor)
- Memory operations (store, recall)
- Simulation (deployment impact prediction)
- Autopsy (automatic debugging)
- Orchestration (complex workflows)

Uses real BrainClient facade and MasterOrchestrator.
"""
from __future__ import annotations


import sys
import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

UTC = timezone.utc

# Setup paths
AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
for p in [AMOS_ROOT, AMOS_ROOT / "clawspring", AMOS_ROOT / "amos_brain"]:
    if str(p) not in sys.path:

# Import brain components
try:
    from amos_brain.facade import BrainClient

    _BRAIN_AVAILABLE = True
except ImportError:
    _BRAIN_AVAILABLE = False
    BrainClient = None

try:
    from clawspring.amos_brain.master_orchestrator import MasterOrchestrator

    _ORCHESTRATOR_AVAILABLE = True
except ImportError:
    try:
        from amos_brain.master_orchestrator import MasterOrchestrator

        _ORCHESTRATOR_AVAILABLE = True
    except ImportError:
        _ORCHESTRATOR_AVAILABLE = False

router = APIRouter(prefix="/brain-unified", tags=["Brain Unified API"])


class OperationType(str, Enum):
    """Supported brain operations."""

    THINK = "think"
    DECIDE = "decide"
    VALIDATE = "validate"
    EXECUTE = "execute"
    SPAWN_AGENT = "spawn_agent"
    SIMULATE = "simulate"
    AUTOPSY = "autopsy"


class UnifiedRequest(BaseModel):
    """Unified request for any brain operation."""

    operation: OperationType
    input: str = Field(..., min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)
    priority: str = Field(default="MEDIUM")
    options: dict[str, Any] = Field(default_factory=dict)


class UnifiedResponse(BaseModel):
    """Unified response from brain operations."""

    operation: str
    request_id: str
    status: str
    result: dict[str, Any]
    brain_used: bool
    processing_time_ms: float
    timestamp: str


#Global instances
_brain_client: Optional[BrainClient] =None
_orchestrator: Optional[MasterOrchestrator] = None


def _get_brain() -> Optional[BrainClient]:
    """Get or initialize BrainClient."""
    global _brain_client
    if _brain_client is None and _BRAIN_AVAILABLE:
        _brain_client = BrainClient(repo_path=str(AMOS_ROOT))
    return _brain_client


def _get_orchestrator() -> Optional[MasterOrchestrator]:
    """Get or initialize MasterOrchestrator."""
    global _orchestrator
    if _orchestrator is None and _ORCHESTRATOR_AVAILABLE:
        _orchestrator = MasterOrchestrator()
        _orchestrator.initialize()
    return _orchestrator


@router.post("/process", response_model=UnifiedResponse)
async def process_unified(request: UnifiedRequest) -> UnifiedResponse:
    """Process any brain operation through unified interface.

    This endpoint routes to the appropriate brain subsystem based on operation type:
    - think: BrainClient.think()
    - decide: BrainClient.decide()
    - validate: BrainClient.validate_action()
    - execute: MasterOrchestrator.orchestrate_cognitive_task()
    - spawn_agent: BrainClient.spawn_agent()
    - simulate: BrainClient.simulate_deployment()
    - autopsy: BrainClient.autopsy_repo()
    """
    start_time = time.time()
    request_id = f"unified_{uuid.uuid4().hex[:12]}"

    brain = _get_brain()
    orchestrator = _get_orchestrator()

    if not brain and not orchestrator:
        raise HTTPException(status_code=503, detail="Brain not available")

    try:
        result: dict[str, Any] = {}

        if request.operation == OperationType.THINK and brain:
            result = brain.think(request.input, request.context)

        elif request.operation == OperationType.DECIDE and brain:
            result = brain.decide(request.input, request.context)

        elif request.operation == OperationType.VALIDATE and brain:
            result = brain.validate_action(request.input, request.context)

        elif request.operation == OperationType.EXECUTE and orchestrator:
            orch_result = orchestrator.orchestrate_cognitive_task(
                task_id=request_id,
                task_description=request.input,
                priority=request.priority,
            )
            result = {
                "task_id": orch_result.task_id,
                "domain": orch_result.domain,
                "overall_success": orch_result.overall_success,
                "analysis": orch_result.analysis,
                "execution": orch_result.execution,
            }

        elif request.operation == OperationType.SPAWN_AGENT and brain:
            result = brain.spawn_agent(
                objective=request.input,
                agent_class=request.options.get("agent_class", "explorer"),
                budget=request.options.get("budget", 1.0),
                context=request.context,
            )

        elif request.operation == OperationType.SIMULATE and brain:
            scenarios = request.options.get(
                "scenarios",
                [
                    {"name": "normal", "load_factor": 1.0},
                    {"name": "peak", "load_factor": 2.0},
                ],
            )
            result = brain.simulate_deployment(
                target=request.input,
                scenarios=scenarios,
            )

        elif request.operation == OperationType.AUTOPSY and brain:
            result = brain.autopsy_repo(
                error_message=request.input,
                error_type=request.options.get("error_type", "runtime_exception"),
                stack_trace=request.options.get("stack_trace"),
                files_involved=request.options.get("files_involved", []),
            )

        else:
            raise HTTPException(
                status_code=400, detail=f"Operation {request.operation} not available"
            )

        processing_time = (time.time() - start_time) * 1000

        return UnifiedResponse(
            operation=request.operation.value,
            request_id=request_id,
            status="success",
            result=result,
            brain_used=True,
            processing_time_ms=processing_time,
            timestamp=datetime.now(UTC).isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brain operation failed: {str(e)}")


@router.get("/operations")
async def list_operations() -> dict[str, Any]:
    """List available brain operations and their status."""
    brain = _get_brain()
    orchestrator = _get_orchestrator()

    operations = {}

    for op in OperationType:
        available = False
        if op in [
            OperationType.THINK,
            OperationType.DECIDE,
            OperationType.VALIDATE,
            OperationType.SPAWN_AGENT,
            OperationType.SIMULATE,
            OperationType.AUTOPSY,
        ]:
            available = brain is not None
        elif op == OperationType.EXECUTE:
            available = orchestrator is not None

        operations[op.value] = {
            "available": available,
            "description": _get_operation_description(op),
        }

    return {
        "operations": operations,
        "brain_available": brain is not None,
        "orchestrator_available": orchestrator is not None,
        "timestamp": datetime.now(UTC).isoformat(),
    }


def _get_operation_description(op: OperationType) -> str:
    """Get description for operation type."""
    descriptions = {
        OperationType.THINK: "Cognitive processing with legality checking",
        OperationType.DECIDE: "Decision-making with law validation",
        OperationType.VALIDATE: "Action validation against global laws",
        OperationType.EXECUTE: "Full workflow execution with orchestration",
        OperationType.SPAWN_AGENT: "Spawn bounded autonomous agent",
        OperationType.SIMULATE: "Pre-runtime deployment prediction",
        OperationType.AUTOPSY: "Automatic error debugging",
    }
    return descriptions.get(op, "Unknown operation")


@router.get("/health")
async def unified_health() -> dict[str, Any]:
    """Check unified API health and component status."""
    brain = _get_brain()
    orchestrator = _get_orchestrator()

    return {
        "status": "healthy" if (brain or orchestrator) else "degraded",
        "components": {
            "brain_client": {
                "available": brain is not None,
                "initialized": _brain_client is not None,
            },
            "orchestrator": {
                "available": orchestrator is not None,
                "initialized": _orchestrator is not None,
            },
        },
        "capabilities": {
            "cognitive": brain is not None,
            "orchestration": orchestrator is not None,
            "agents": brain is not None,
            "simulation": brain is not None,
            "autopsy": brain is not None,
        },
        "timestamp": datetime.now(UTC).isoformat(),
    }
