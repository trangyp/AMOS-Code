from typing import Any, Dict, List, Optional

"""Reading Kernel API Router

Exposes AMOSExecutableCore reading pipeline as REST endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from backend.amos_reading_kernel import (
    ResponseMode,
    get_reading_service,
)

router = APIRouter()


class ReadRequest(BaseModel):
    text: str
    context: Dict[str, Any] = None


class SegmentResponse(BaseModel):
    text: str
    kind: str
    start: int
    end: int


class StableReadResponse(BaseModel):
    input_class: str
    primary_goal: Optional[str]
    constraints: List[str]
    ambiguities: List[str]
    references: List[str]
    confidence: float
    clarification_questions: List[str]


class VerifiedGoalResponse(BaseModel):
    mode: str
    objective: str
    constraints: List[str]
    executable: bool
    confidence: float
    reason: str


class ExecutionPlanResponse(BaseModel):
    action_type: str
    domain: str
    priority: str
    estimated_steps: int
    requires_review: bool


class ReadResponse(BaseModel):
    request_id: str
    raw_text: str
    normalized_text: str
    speech_act: str
    segments: List[SegmentResponse]
    references: List[str]
    constraints: List[str]
    goals: List[str]
    risks: List[str]
    stable_read: StableReadResponse
    verified_goal: VerifiedGoalResponse
    execution_plan: Optional[ExecutionPlanResponse]
    suggested_action: Optional[str]
    latency_ms: float


@router.post("/read", response_model=ReadResponse)
async def read_request(req: ReadRequest) -> ReadResponse:
    """Process text through AMOS reading kernel."""
    service = get_reading_service()
    result = service.process(req.text, req.context)

    plan = result.execution_plan
    execution_plan = None
    if plan:
        execution_plan = ExecutionPlanResponse(
            action_type=plan["action_type"],
            domain=plan["domain"],
            priority=plan["priority"],
            estimated_steps=plan["estimated_steps"],
            requires_review=plan["requires_review"],
        )

    return ReadResponse(
        request_id=result.request_id,
        raw_text=result.parsed.raw_text,
        normalized_text=result.parsed.normalized_text,
        speech_act=result.parsed.speech_act.value,
        segments=[
            SegmentResponse(
                text=s.text,
                kind=s.kind.value,
                start=s.start,
                end=s.end,
            )
            for s in result.parsed.segments
        ],
        references=result.parsed.references,
        constraints=result.parsed.constraints,
        goals=result.parsed.goals,
        risks=result.parsed.risks,
        stable_read=StableReadResponse(
            input_class=result.stable_read.input_class.value,
            primary_goal=result.stable_read.primary_goal,
            constraints=result.stable_read.constraints,
            ambiguities=result.stable_read.ambiguities,
            references=result.stable_read.references,
            confidence=result.stable_read.confidence,
            clarification_questions=result.stable_read.clarification_questions,
        ),
        verified_goal=VerifiedGoalResponse(
            mode=result.verified_goal.mode.value,
            objective=result.verified_goal.objective,
            constraints=result.verified_goal.constraints,
            executable=result.verified_goal.executable,
            confidence=result.verified_goal.confidence,
            reason=result.verified_goal.reason,
        ),
        execution_plan=execution_plan,
        suggested_action=result.suggested_action,
        latency_ms=result.latency_ms,
    )


@router.post("/understand")
async def understand_task(req: ReadRequest) -> Dict[str, Any]:
    """Quick task understanding endpoint."""
    service = get_reading_service()
    result = service.process(req.text, req.context)

    return {
        "understood": result.verified_goal.mode == ResponseMode.ANSWER,
        "can_execute": result.verified_goal.executable,
        "needs_clarification": result.verified_goal.mode == ResponseMode.CLARIFY,
        "confidence": result.verified_goal.confidence,
        "primary_goal": result.stable_read.primary_goal,
        "ambiguities": result.stable_read.ambiguities,
        "clarification_questions": result.stable_read.clarification_questions,
        "suggested_domain": result.execution_plan.get("domain") if result.execution_plan else None,
        "suggested_action": result.suggested_action,
        "latency_ms": result.latency_ms,
    }


@router.get("/health")
async def reading_kernel_health() -> Dict[str, Any]:
    """Health check for reading kernel service."""
    service = get_reading_service()
    history = service.get_history(limit=1)

    return {
        "status": "healthy",
        "initialized": True,
        "history_count": len(service._history),
        "last_request_latency_ms": history[0].latency_ms if history else None,
    }
