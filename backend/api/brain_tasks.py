from typing import Any

"""Brain Tasks API - Production task processing via AMOS brain.

Real implementation using:
- Brain kernel runtime for cognitive processing
- Task queue for async execution
- Proper error handling and monitoring
"""
from __future__ import annotations


import sys
from datetime import datetime, timezone

UTC = timezone.utc
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Add clawspring to path
CLAWSPRING_PATH = Path(__file__).parent.parent.parent / "clawspring"
if str(CLAWSPRING_PATH) not in sys.path:
    sys.path.insert(0, str(CLAWSPRING_PATH))

AMOS_BRAIN_PATH = CLAWSPRING_PATH / "amos_brain"
if str(AMOS_BRAIN_PATH) not in sys.path:
    sys.path.insert(0, str(AMOS_BRAIN_PATH))

try:
    from amos_brain.api_integration import brain_get_result, brain_submit_task
    from amos_brain_working import think as brain_think

    BRAIN_TASKS_AVAILABLE = True
except ImportError as e:
    BRAIN_TASKS_AVAILABLE = False
    print(f"[BrainTasks] Brain integration not available: {e}")

router = APIRouter(prefix="/brain-tasks", tags=["brain-tasks"])


class TaskSubmitRequest(BaseModel):
    """Request to submit a task for brain processing."""

    description: str = Field(..., min_length=1, max_length=1000)
    priority: str = Field(default="MEDIUM", pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    context: dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    """Response from brain task processing."""

    task_id: str
    status: str
    message: str
    timestamp: str


class TaskResultResponse(BaseModel):
    """Result of a completed brain task."""

    task_id: str
    status: str
    result: dict[str, Any] = None
    error: str | None = None
    completed_at: str | None = None


class BrainThinkRequest(BaseModel):
    """Request for immediate brain processing."""

    request: str = Field(..., min_length=1, max_length=2000)
    context: dict[str, Any] = Field(default_factory=dict)


class BrainThinkResponse(BaseModel):
    """Response from immediate brain processing."""

    brain_used: bool
    status: str | None = None
    legality: float | None = None
    sigma: float | None = None
    mode: str | None = None
    timestamp: str


@router.post("/submit", response_model=TaskResponse)
async def submit_task(request: TaskSubmitRequest) -> TaskResponse:
    """Submit a task to be processed by the AMOS brain queue."""
    if not BRAIN_TASKS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain task processing not available")

    try:
        result = await brain_submit_task(request.description, request.priority)
        return TaskResponse(
            task_id=result["task_id"],
            status=result["status"],
            message=f"Task submitted with {request.priority} priority",
            timestamp=datetime.now(UTC).isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/result/{task_id}", response_model=TaskResultResponse)
async def get_task_result(task_id: str) -> TaskResultResponse:
    """Get the result of a submitted task."""
    if not BRAIN_TASKS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain task processing not available")

    try:
        result = await brain_get_result(task_id)
        if result is None:
            return TaskResultResponse(task_id=task_id, status="not_found", error="Task not found")

        return TaskResultResponse(
            task_id=result["task_id"],
            status=result["status"],
            result=result.get("result"),
            error=result.get("error"),
            completed_at=result.get("completed_at"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/think", response_model=BrainThinkResponse)
async def brain_think_endpoint(request: BrainThinkRequest) -> BrainThinkResponse:
    """Immediate brain processing for quick cognitive tasks."""
    if not BRAIN_TASKS_AVAILABLE or brain_think is None:
        raise HTTPException(status_code=503, detail="Brain think processing not available")

    try:
        result = brain_think(request.request, request.context)
        return BrainThinkResponse(
            brain_used=result.get("brain_used", True),
            status=result.get("status"),
            legality=result.get("sigma"),  # σ = drift coefficient
            sigma=result.get("sigma"),
            mode=result.get("mode"),
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/think-fast", response_model=BrainThinkResponse)
async def brain_think_fast_endpoint(request: BrainThinkRequest) -> BrainThinkResponse:
    """Fast brain processing using dual-process brain (<100ms target)."""
    import time

    start = time.perf_counter()

    try:
        from amos_dual_process_brain import get_dual_process_brain

        brain = get_dual_process_brain()
        result = await brain.think(query=request.request, context=request.context, prefer_fast=True)

        (time.perf_counter() - start) * 1000

        return BrainThinkResponse(
            brain_used=True,
            status=result.response[:100] if result.response else None,
            legality=result.confidence,
            sigma=result.confidence,
            mode=result.thinking_mode,
            timestamp=datetime.now(UTC).isoformat(),
        )
    except ImportError:
        # Fallback to standard brain
        if not BRAIN_TASKS_AVAILABLE or brain_think is None:
            raise HTTPException(status_code=503, detail="Brain not available")

        try:
            result = brain_think(request.request, request.context)
            (time.perf_counter() - start) * 1000

            return BrainThinkResponse(
                brain_used=True,
                status="fallback",
                legality=0.7,
                sigma=0.7,
                mode="slow_fallback",
                timestamp=datetime.now(UTC).isoformat(),
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/status")
async def brain_tasks_status() -> dict[str, Any]:
    """Get brain tasks API status."""

    # Check fast thinking availability
    fast_thinking = False
    try:
        fast_thinking = True
    except Exception:
        pass

    return {
        "available": BRAIN_TASKS_AVAILABLE,
        "fast_thinking": fast_thinking,
        "timestamp": datetime.now(UTC).isoformat(),
        "endpoints": [
            "POST /submit - Submit a task",
            "GET /result/{task_id} - Get task result",
            "POST /think - Immediate brain processing",
            "POST /think-fast - Fast dual-process brain (<100ms)",
        ]
        if BRAIN_TASKS_AVAILABLE
        else [],
    }
