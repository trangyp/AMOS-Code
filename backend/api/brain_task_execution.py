"""Brain Task Execution API - Direct brain-powered task execution.

Executes tasks using the real AMOS brain with:
- BrainClient facade for cognitive operations
- MasterOrchestrator for complex workflows
- Agent Fabric Kernel for autonomous agents
- Repo Autopsy Engine for debugging
- Simulation Engine for prediction
"""

from __future__ import annotations


import sys
import time
import uuid
from datetime import datetime, timezone

UTC = timezone.utc
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Setup paths
AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
for p in [AMOS_ROOT, AMOS_ROOT / "clawspring", AMOS_ROOT / "amos_brain"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Import real brain components
try:
    from amos_brain.facade import BrainClient

    _BRAIN_AVAILABLE = True
except ImportError:
    _BRAIN_AVAILABLE = False
    BrainClient = None

try:
    from clawspring.amos_brain.master_orchestrator import (
        MasterOrchestrator,
        OrchestrationResult,
    )

    _ORCHESTRATOR_AVAILABLE = True
except ImportError:
    try:
        from amos_brain.master_orchestrator import (
            MasterOrchestrator,
            OrchestrationResult,
        )

        _ORCHESTRATOR_AVAILABLE = True
    except ImportError:
        _ORCHESTRATOR_AVAILABLE = False

router = APIRouter(prefix="/brain-tasks", tags=["Brain Task Execution"])

# Global instances
_brain_client: BrainClient | None = None
_orchestrator: MasterOrchestrator | None = None


def get_brain_client() -> BrainClient:
    """Get or initialize BrainClient."""
    global _brain_client
    if _brain_client is None and _BRAIN_AVAILABLE:
        _brain_client = BrainClient(repo_path=str(AMOS_ROOT))
    return _brain_client


def get_orchestrator() -> MasterOrchestrator:
    """Get or initialize MasterOrchestrator."""
    global _orchestrator
    if _orchestrator is None and _ORCHESTRATOR_AVAILABLE:
        _orchestrator = MasterOrchestrator()
        _orchestrator.initialize()
    return _orchestrator


class BrainTaskRequest(BaseModel):
    """Request for brain-powered task execution."""

    task: str = Field(..., min_length=1, description="Task description")
    context: dict[str, Any] = Field(default_factory=dict)
    mode: str = Field(default="think", pattern="think|decide|validate|execute")
    priority: str = Field(default="MEDIUM", pattern="LOW|MEDIUM|HIGH|CRITICAL")


class BrainTaskResult(BaseModel):
    """Result from brain task execution."""

    task_id: str
    status: str
    result: dict[str, Any]
    brain_used: bool
    processing_time_ms: float
    timestamp: str


class ComplexWorkflowRequest(BaseModel):
    """Request for complex workflow execution."""

    workflow_description: str = Field(..., min_length=1)
    steps: list[dict[str, Any]] = Field(default_factory=list)
    require_approval: bool = Field(default=False)


class AgentSpawnRequest(BaseModel):
    """Request to spawn an autonomous agent."""

    objective: str = Field(..., min_length=1)
    agent_class: str = Field(default="explorer")
    budget: float = Field(default=1.0, ge=0.0)
    context: dict[str, Any] = Field(default_factory=dict)


class AgentSpawnResult(BaseModel):
    """Result from agent spawning."""

    run_id: str
    agent_id: str
    status: str
    estimated_duration_minutes: int
    budget_allocated: float


class RepoAutopsyRequest(BaseModel):
    """Request for repo autopsy."""

    error_message: str = Field(..., min_length=1)
    error_type: str = Field(default="runtime_exception")
    stack_trace: str = None
    files_involved: list[str] = Field(default_factory=list)


class SimulationRequest(BaseModel):
    """Request for deployment simulation."""

    target: str = Field(..., min_length=1, description="PR or commit to simulate")
    scenarios: list[str] = Field(default_factory=lambda: ["normal", "peak"])


# Store for task results
_task_results: dict[str, dict[str, Any]] = {}


@router.post("/think", response_model=BrainTaskResult)
async def brain_think(request: BrainTaskRequest) -> BrainTaskResult:
    """Execute a 'think' task using the brain.

    Uses BrainClient.think() for cognitive processing with
    legality checking and sigma scoring.
    """
    if not _BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain not available")

    start_time = time.time()
    task_id = f"think_{uuid.uuid4().hex[:12]}"

    try:
        client = get_brain_client()

        # Use real brain think method
        result = client.think(request.task, request.context)

        processing_time = (time.time() - start_time) * 1000

        # Store result
        _task_results[task_id] = {
            "task": request.task,
            "result": result,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        return BrainTaskResult(
            task_id=task_id,
            status="success",
            result=result,
            brain_used=True,
            processing_time_ms=processing_time,
            timestamp=datetime.now(UTC).isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brain think failed: {str(e)}")


@router.post("/decide", response_model=BrainTaskResult)
async def brain_decide(request: BrainTaskRequest) -> BrainTaskResult:
    """Execute a 'decide' task using the brain.

    Uses BrainClient.decide() for decision-making with
    law validation and risk assessment.
    """
    if not _BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain not available")

    start_time = time.time()
    task_id = f"decide_{uuid.uuid4().hex[:12]}"

    try:
        client = get_brain_client()

        # Use real brain decide method
        result = client.decide(request.task, request.context)

        processing_time = (time.time() - start_time) * 1000

        _task_results[task_id] = {
            "task": request.task,
            "result": result,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        return BrainTaskResult(
            task_id=task_id,
            status="success",
            result=result,
            brain_used=True,
            processing_time_ms=processing_time,
            timestamp=datetime.now(UTC).isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brain decide failed: {str(e)}")


@router.post("/validate", response_model=BrainTaskResult)
async def brain_validate(request: BrainTaskRequest) -> BrainTaskResult:
    """Execute a 'validate' task using the brain.

    Uses BrainClient.validate_action() for action validation
    against global laws.
    """
    if not _BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain not available")

    start_time = time.time()
    task_id = f"validate_{uuid.uuid4().hex[:12]}"

    try:
        client = get_brain_client()

        # Use real brain validate method
        result = client.validate_action(request.task, request.context)

        processing_time = (time.time() - start_time) * 1000

        _task_results[task_id] = {
            "task": request.task,
            "result": result,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        return BrainTaskResult(
            task_id=task_id,
            status="success",
            result=result,
            brain_used=True,
            processing_time_ms=processing_time,
            timestamp=datetime.now(UTC).isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brain validate failed: {str(e)}")


@router.post("/execute", response_model=BrainTaskResult)
async def brain_execute(request: BrainTaskRequest) -> BrainTaskResult:
    """Execute full cognitive workflow using MasterOrchestrator.

    Uses MasterOrchestrator.orchestrate_cognitive_task() for
    complex task execution with organism enhancement and prediction.
    """
    if not _ORCHESTRATOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Orchestrator not available")

    start_time = time.time()
    task_id = f"execute_{uuid.uuid4().hex[:12]}"

    try:
        orchestrator = get_orchestrator()

        # Use real orchestrator
        result: OrchestrationResult = orchestrator.orchestrate_cognitive_task(
            task_id=task_id,
            task_description=request.task,
            priority=request.priority,
        )

        processing_time = (time.time() - start_time) * 1000

        # Convert to dict
        result_dict = {
            "task_id": result.task_id,
            "timestamp": result.timestamp,
            "domain": result.domain,
            "analysis": result.analysis,
            "prediction": result.prediction,
            "execution": result.execution,
            "organism_enhancements": result.organism_enhancements,
            "overall_success": result.overall_success,
            "total_duration_ms": result.total_duration_ms,
        }

        _task_results[task_id] = {
            "task": request.task,
            "result": result_dict,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        return BrainTaskResult(
            task_id=task_id,
            status="success" if result.overall_success else "failed",
            result=result_dict,
            brain_used=True,
            processing_time_ms=processing_time,
            timestamp=datetime.now(UTC).isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brain execute failed: {str(e)}")


@router.post("/spawn-agent", response_model=AgentSpawnResult)
async def brain_spawn_agent(request: AgentSpawnRequest) -> AgentSpawnResult:
    """Spawn an autonomous agent using Agent Fabric Kernel.

    Uses BrainClient.spawn_agent() for bounded AI labor.
    """
    if not _BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain not available")

    try:
        client = get_brain_client()

        # Use real agent spawning
        result = client.spawn_agent(
            objective=request.objective,
            agent_class=request.agent_class,
            budget=request.budget,
            context=request.context,
        )

        return AgentSpawnResult(
            run_id=result.get("run_id", "unknown"),
            agent_id=result.get("agent_id", "unknown"),
            status=result.get("status", "unknown"),
            estimated_duration_minutes=result.get("estimated_duration_minutes", 5),
            budget_allocated=result.get("budget_allocated", request.budget),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent spawn failed: {str(e)}")


@router.post("/autopsy", response_model=dict[str, Any])
async def brain_autopsy(request: RepoAutopsyRequest) -> dict[str, Any]:
    """Run repo autopsy using Repo Autopsy Engine.

    Uses BrainClient.autopsy_repo() for automatic debugging.
    """
    if not _BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain not available")

    try:
        client = get_brain_client()

        # Use real autopsy
        result = client.autopsy_repo(
            error_message=request.error_message,
            error_type=request.error_type,
            stack_trace=request.stack_trace,
            files_involved=request.files_involved,
        )

        return {
            "autopsy_id": result.get("autopsy_id", "unknown"),
            "status": result.get("status", "unknown"),
            "phases_completed": result.get("phases_completed", []),
            "fault_locations": result.get("fault_locations", []),
            "generated_fixes": result.get("generated_fixes", []),
            "confidence": result.get("confidence", 0.0),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autopsy failed: {str(e)}")


@router.post("/simulate", response_model=dict[str, Any])
async def brain_simulate(request: SimulationRequest) -> dict[str, Any]:
    """Run deployment simulation using Simulation Engine.

    Uses BrainClient.simulate_deployment() for pre-runtime prediction.
    """
    if not _BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain not available")

    try:
        client = get_brain_client()

        # Build scenarios
        scenarios = []
        for scenario_name in request.scenarios:
            load_factor = {"normal": 1.0, "peak": 2.0, "stress": 5.0}.get(scenario_name, 1.0)
            scenarios.append({"name": scenario_name, "load_factor": load_factor})

        # Use real simulation
        result = client.simulate_deployment(
            target=request.target,
            scenarios=scenarios,
        )

        return {
            "simulation_id": result.get("simulation_id", "unknown"),
            "target": request.target,
            "scenarios_run": len(scenarios),
            "status": result.get("status", "unknown"),
            "recommendation": result.get("recommendation", "unknown"),
            "confidence": result.get("confidence", 0.0),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.get("/result/{task_id}")
async def get_task_result(task_id: str) -> dict[str, Any]:
    """Get result of a previous brain task."""
    if task_id not in _task_results:
        raise HTTPException(status_code=404, detail="Task not found")

    return _task_results[task_id]


@router.get("/health")
async def brain_tasks_health() -> dict[str, Any]:
    """Check brain task execution health."""
    return {
        "brain_available": _BRAIN_AVAILABLE,
        "orchestrator_available": _ORCHESTRATOR_AVAILABLE,
        "stored_results": len(_task_results),
        "components": {
            "brain_client": _brain_client is not None,
            "orchestrator": _orchestrator is not None,
        },
        "timestamp": datetime.now(UTC).isoformat(),
    }
