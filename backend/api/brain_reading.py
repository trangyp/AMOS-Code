from __future__ import annotations

from typing import Any

"""AMOS Brain-Reading API Endpoints

Exposes the Brain-Reading Kernel for cognitive text processing.
This is NOT language parsing - it is brain-level reading.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Import brain reading kernel
try:
    from amos_brain_reading_integration import BrainReadingIntegrator
    from amos_brain_reading_kernel import get_brain_reading_kernel

    _BRAIN_READING_AVAILABLE = True
except ImportError as e:
    _BRAIN_READING_AVAILABLE = False
    print(f"[BrainReadingAPI] Import error: {e}")

router = APIRouter(prefix="/brain-reading", tags=["brain-reading"])


class BrainReadRequest(BaseModel):
    """Request for brain-level reading."""

    text: str = Field(..., description="Input text to read cognitively")
    context: dict[str, Any] = Field(default_factory=dict, description="AMOS context")
    goals: list[str] = Field(default_factory=list, description="Active goals")


class BrainReadResponse(BaseModel):
    """Response from brain-level reading."""

    utterance_id: str
    intent: str
    intent_confidence: float
    stable: bool
    coherence_score: float
    routing: str
    priority: float
    compiled_goal_type: str
    compiled_objective: str
    constraints: list[str]
    references: list[str]
    conflicts: list[dict[str, Any]]
    ambiguities: list[dict[str, Any]]
    execution_plan: dict[str, Any] = None


@router.post("/read", response_model=BrainReadResponse)
async def brain_read(request: BrainReadRequest) -> BrainReadResponse:
    """
    Execute brain-level reading on input text.

    This endpoint processes text through the Brain-Reading Kernel:
    - Predictive processing (not reactive)
    - Chunk-based analysis (not token-level)
    - Entity binding
    - Salience computation
    - Conflict detection
    - Coherence verification

    Returns a StableRead with routing decision for AMOS subsystems.
    """
    if not _BRAIN_READING_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain-Reading Kernel not available")

    try:
        integrator = BrainReadingIntegrator()

        result = await integrator.process_input(
            text=request.text,
            amos_context=request.context,
            active_goals=request.goals,
        )

        stable_read = result.stable_read

        return BrainReadResponse(
            utterance_id=stable_read.utterance_id,
            intent=stable_read.primary_intent[0].name,
            intent_confidence=stable_read.primary_intent[1],
            stable=stable_read.stable,
            coherence_score=stable_read.coherence_score,
            routing=result.routing_decision,
            priority=result.priority_score,
            compiled_goal_type=stable_read.compiled_goal.goal_type,
            compiled_objective=stable_read.compiled_goal.objective,
            constraints=stable_read.compiled_goal.constraints,
            references=stable_read.reference_structure,
            conflicts=[
                {
                    "id": c.id,
                    "type": c.conflict_type.name,
                    "severity": c.severity,
                    "resolvable": c.resolvable,
                }
                for c in stable_read.conflicts
            ],
            ambiguities=stable_read.ambiguities,
            execution_plan=result.execution_plan,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def brain_reading_status() -> dict[str, Any]:
    """Get Brain-Reading Kernel status."""
    if not _BRAIN_READING_AVAILABLE:
        return {"available": False, "error": "Brain-Reading Kernel not imported"}

    try:
        get_brain_reading_kernel()
        return {
            "available": True,
            "initialized": BrainReadingIntegrator._initialized
            if hasattr(BrainReadingIntegrator, "_initialized")
            else True,
        }
    except Exception as e:
        return {"available": False, "error": str(e)}
