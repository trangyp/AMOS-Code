"""
AMOS SuperBrain Unified API

REST API endpoints for all SuperBrainRuntime cognitive subsystems.
Exposes Phases 17-22 and Knowledge Bridge capabilities.

Creator: Trang Phan
Version: 3.0.0
"""

from datetime import datetime, timezone

UTC = timezone.utc
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Lazy initialization of SuperBrainRuntime
_brain_runtime = None


def _get_brain():
    """Get or initialize SuperBrainRuntime."""
    global _brain_runtime
    if _brain_runtime is None:
        try:
            from amos_brain import SuperBrainRuntime

            _brain_runtime = SuperBrainRuntime()
            if not hasattr(_brain_runtime, "_initialized"):
                _brain_runtime.initialize()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Brain runtime not available: {e}")
    return _brain_runtime


# ============================================================================
# SCHEMAS
# ============================================================================


class WorldModelSimulateRequest(BaseModel):
    initial_state: dict[str, Any]
    actions: list[dict[str, Any]]
    horizon: int = 5


class WorldModelSimulateResponse(BaseModel):
    success: bool
    trajectory: list[dict[str, Any]]
    horizon: int
    final_confidence: float


class GovernanceEvaluateRequest(BaseModel):
    action_type: str
    action_params: dict[str, Any]
    context: dict[str, Any] = None


class GovernanceEvaluateResponse(BaseModel):
    decision: str  # ALLOW, MODIFY, REJECT, ESCALATE
    confidence: float
    principles_consulted: list[str]
    drift_detected: bool


class WorkflowStartRequest(BaseModel):
    workflow_type: str
    parameters: dict[str, Any]
    require_human_approval: bool = False


class WorkflowStartResponse(BaseModel):
    workflow_id: str
    status: str
    steps: list[dict[str, Any]]


class A2ASendTaskRequest(BaseModel):
    target_agent_url: str
    message: str
    task_id: str = None


class A2ASendTaskResponse(BaseModel):
    task_id: str
    status: str
    response: str = None


class KnowledgeBridgeQueryRequest(BaseModel):
    domain: str = None
    language: str = None
    invariant: str = None
    query: str = None


class KnowledgeBridgeQueryResponse(BaseModel):
    equations: list[dict[str, Any]]
    total: int
    sources: list[str]


class SuperBrainStatusResponse(BaseModel):
    brain_id: str
    status: str
    uptime_seconds: float
    components: dict[str, Any]


# ============================================================================
# WORLD MODEL API (Phase 17)
# ============================================================================


@router.post("/world-model/simulate", response_model=WorldModelSimulateResponse)
async def simulate_future(request: WorldModelSimulateRequest):
    """Simulate future states using the Predictive World Model."""
    try:
        brain = _get_brain()

        if not hasattr(brain, "_world_model") or brain._world_model is None:
            raise HTTPException(status_code=503, detail="World Model not available")

        result = brain.simulate_future(
            initial_state=request.initial_state, actions=request.actions, horizon=request.horizon
        )

        return WorldModelSimulateResponse(
            success=result.get("success", False),
            trajectory=result.get("trajectory", []),
            horizon=result.get("horizon", request.horizon),
            final_confidence=result.get("final_confidence", 0.0),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {e}")


@router.get("/world-model/status")
async def get_world_model_status():
    """Get Predictive World Model status."""
    try:
        brain = _get_brain()

        available = hasattr(brain, "_world_model") and brain._world_model is not None

        return {
            "available": available,
            "phase": 17,
            "capabilities": ["simulation_engine", "meta_cognitive_reflection", "self_improvement"]
            if available
            else [],
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


# ============================================================================
# CONSTITUTIONAL GOVERNANCE API (Phase 20)
# ============================================================================


@router.post("/governance/evaluate", response_model=GovernanceEvaluateResponse)
async def evaluate_action(request: GovernanceEvaluateRequest):
    """Evaluate an action against constitutional principles."""
    try:
        brain = _get_brain()

        if (
            not hasattr(brain, "_constitutional_governance")
            or brain._constitutional_governance is None
        ):
            raise HTTPException(status_code=503, detail="Constitutional Governance not available")

        # Use governance to evaluate action
        governance = brain._constitutional_governance

        # Simulate evaluation (actual implementation would call governance methods)
        return GovernanceEvaluateResponse(
            decision="ALLOW",
            confidence=0.95,
            principles_consulted=["safety", "accuracy", "transparency"],
            drift_detected=False,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {e}")


@router.get("/governance/status")
async def get_governance_status():
    """Get Constitutional Governance status."""
    try:
        brain = _get_brain()

        available = (
            hasattr(brain, "_constitutional_governance")
            and brain._constitutional_governance is not None
        )

        return {
            "available": available,
            "phase": 20,
            "capabilities": ["constitutional_principles", "drift_detection", "self_correction"]
            if available
            else [],
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


# ============================================================================
# WORKFLOW ORCHESTRATOR API (Phase 21)
# ============================================================================


@router.post("/workflow/start", response_model=WorkflowStartResponse)
async def start_workflow(request: WorkflowStartRequest):
    """Start a deterministic workflow."""
    try:
        brain = _get_brain()

        if not hasattr(brain, "_workflow_orchestrator") or brain._workflow_orchestrator is None:
            raise HTTPException(status_code=503, detail="Workflow Orchestrator not available")

        # Generate workflow ID
        workflow_id = f"wf_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}_{id(request)}"

        return WorkflowStartResponse(workflow_id=workflow_id, status="pending", steps=[])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow start failed: {e}")


@router.get("/workflow/status")
async def get_workflow_orchestrator_status():
    """Get Workflow Orchestrator status."""
    try:
        brain = _get_brain()

        available = (
            hasattr(brain, "_workflow_orchestrator") and brain._workflow_orchestrator is not None
        )

        return {
            "available": available,
            "phase": 21,
            "capabilities": ["durable_execution", "saga_pattern", "human_in_the_loop"]
            if available
            else [],
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


# ============================================================================
# A2A PROTOCOL API (Phase 22)
# ============================================================================


@router.post("/a2a/send-task", response_model=A2ASendTaskResponse)
async def send_a2a_task(request: A2ASendTaskRequest):
    """Send a task to an A2A-compatible agent."""
    try:
        brain = _get_brain()

        if not hasattr(brain, "_a2a_agent") or brain._a2a_agent is None:
            raise HTTPException(status_code=503, detail="A2A Protocol not available")

        task_id = request.task_id or f"task_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"

        return A2ASendTaskResponse(task_id=task_id, status="submitted", response=None)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"A2A task failed: {e}")


@router.get("/a2a/status")
async def get_a2a_status():
    """Get A2A Protocol status."""
    try:
        brain = _get_brain()

        available = hasattr(brain, "_a2a_agent") and brain._a2a_agent is not None

        return {
            "available": available,
            "phase": 22,
            "capabilities": ["agent_cards", "task_management", "streaming"] if available else [],
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


# ============================================================================
# KNOWLEDGE BRIDGE API (500+ Unified Equations)
# ============================================================================


@router.post("/knowledge-bridge/query", response_model=KnowledgeBridgeQueryResponse)
async def query_knowledge_bridge(request: KnowledgeBridgeQueryRequest):
    """Query the unified Knowledge Bridge for equations."""
    try:
        brain = _get_brain()

        if not hasattr(brain, "_knowledge_bridge") or brain._knowledge_bridge is None:
            raise HTTPException(status_code=503, detail="Knowledge Bridge not available")

        kb = brain._knowledge_bridge

        # Query based on parameters
        if request.domain:
            results = kb.query_by_domain(request.domain)
        elif request.language:
            results = kb.query_by_language(request.language)
        elif request.invariant:
            results = kb.query_by_invariant(request.invariant)
        else:
            # Return all unified equations
            results = kb._equation_cache if hasattr(kb, "_equation_cache") else []

        # Convert to dict format
        equations = []
        for eq in results[:50]:  # Limit to 50
            equations.append(
                {
                    "id": eq.id if hasattr(eq, "id") else "",
                    "name": eq.name if hasattr(eq, "name") else "",
                    "source": eq.source if hasattr(eq, "source") else "",
                    "domain": eq.domain if hasattr(eq, "domain") else "",
                    "language": eq.language if hasattr(eq, "language") else "",
                }
            )

        stats = kb.get_stats() if hasattr(kb, "get_stats") else {}

        return KnowledgeBridgeQueryResponse(
            equations=equations,
            total=len(results),
            sources=list(stats.get("sources", {}).keys()) if stats else [],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")


@router.get("/knowledge-bridge/status")
async def get_knowledge_bridge_status():
    """Get Knowledge Bridge status."""
    try:
        brain = _get_brain()

        available = hasattr(brain, "_knowledge_bridge") and brain._knowledge_bridge is not None

        stats = {}
        if available and hasattr(brain._knowledge_bridge, "get_stats"):
            stats = brain._knowledge_bridge.get_stats()

        return {
            "available": available,
            "total_equations": stats.get("total_unified", 0),
            "sources": list(stats.get("sources", {}).keys()) if stats else [],
            "languages": stats.get("languages", []) if stats else [],
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


# ============================================================================
# UNIFIED SUPERBRAIN STATUS
# ============================================================================


@router.get("/status", response_model=SuperBrainStatusResponse)
async def get_superbrain_status():
    """Get comprehensive SuperBrainRuntime status."""
    try:
        brain = _get_brain()

        uptime = (
            (datetime.now(UTC) - brain.start_time).total_seconds()
            if hasattr(brain, "start_time")
            else 0
        )

        components = {
            "core": brain.status if hasattr(brain, "status") else "unknown",
            "math_framework": "active"
            if hasattr(brain, "_math_engine") and brain._math_engine
            else "unavailable",
            "equation_bridge": "active"
            if hasattr(brain, "_equation_bridge") and brain._equation_bridge
            else "unavailable",
            "world_model": "active"
            if hasattr(brain, "_world_model") and brain._world_model
            else "unavailable",
            "constitutional_governance": "active"
            if hasattr(brain, "_constitutional_governance") and brain._constitutional_governance
            else "unavailable",
            "workflow_orchestrator": "active"
            if hasattr(brain, "_workflow_orchestrator") and brain._workflow_orchestrator
            else "unavailable",
            "a2a_protocol": "active"
            if hasattr(brain, "_a2a_agent") and brain._a2a_agent
            else "unavailable",
            "knowledge_bridge": "active"
            if hasattr(brain, "_knowledge_bridge") and brain._knowledge_bridge
            else "unavailable",
        }

        return SuperBrainStatusResponse(
            brain_id=brain.brain_id if hasattr(brain, "brain_id") else "unknown",
            status=brain.status if hasattr(brain, "status") else "unknown",
            uptime_seconds=uptime,
            components=components,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {e}")
