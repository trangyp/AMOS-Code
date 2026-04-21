from __future__ import annotations

from typing import Any, Optional

"""AMOS Brain v2 API - Production brain-powered endpoints.

Real cognitive task processing via:
- MasterOrchestrator cognitive routing
- OrganismBridge enhancement
- Async task queue

Owner: Trang Phan
"""


import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Add project root and clawspring to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(PROJECT_ROOT / "clawspring") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "clawspring"))

try:
    from amos_brain.api_integration import (
        brain_get_result,
        brain_process_sync,
        brain_submit_task,
        get_brain_api,
    )

    BRAIN_AVAILABLE = True
except ImportError as e:
    BRAIN_AVAILABLE = False
    print(f"[BrainV2] Brain integration not available: {e}")

# Import integrated brain components
try:
    # Try importing with clawspring in path
    from amos_brain.integrated_brain_api import (
        BrainResponse,
    )
    from amos_brain.integrated_brain_api import (
        get_brain_api as get_integrated_brain,
    )

    INTEGRATED_BRAIN_AVAILABLE = True
except ImportError as e:
    INTEGRATED_BRAIN_AVAILABLE = False
    print(f"[BrainV2] Integrated brain not available: {e}")

router = APIRouter(prefix="/brain-v2", tags=["brain-v2"])


class TaskRequest(BaseModel):
    """Request for brain task processing."""

    description: str
    priority: str = "MEDIUM"


class TaskResponse(BaseModel):
    """Response from brain task processing."""

    task_id: str
    status:str
    domain: Optional[str] = None
    success: bool = False
    duration_ms: float = 0.0
    engines_used: list[str] = []
    result: dict[str, Any] = {}


class TaskStatusResponse(BaseModel):
    """Task status response."""

    task_id: str
    status: str
    description: str
    priority:str
    created_at: Optional[str] =None
    started_at: Optional[str] =None
    completed_at: Optional[str] = None
    result: dict[str, Any] =None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Brain health response."""

    status: str
    initialized: bool
    workers: int


@router.post("/process", response_model=TaskResponse)
async def process_task_sync(request: TaskRequest) -> TaskResponse:
    """Process task synchronously using brain."""
    if not BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain not available")

    try:
        result = await brain_process_sync(request.description, request.priority)
        return TaskResponse(
            task_id=result["task_id"],
            status="completed",
            domain=result.get("domain"),
            success=result.get("success", False),
            duration_ms=result.get("duration_ms", 0.0),
            engines_used=result.get("engines_used", []),
            result=result.get("result", {}),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit", response_model=TaskResponse)
async def submit_task_async(request: TaskRequest) -> TaskResponse:
    """Submit task to brain queue."""
    if not BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain not available")

    try:
        result = await brain_submit_task(request.description, request.priority)
        return TaskResponse(
            task_id=result["task_id"],
            status="submitted",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """Get task status from brain queue."""
    if not BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain not available")

    task = await brain_get_result(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskStatusResponse(
        task_id=task["task_id"],
        status=task["status"],
        description=task["description"],
        priority=task["priority"],
        created_at=task.get("created_at"),
        started_at=task.get("started_at"),
        completed_at=task.get("completed_at"),
        result=task.get("result"),
        error=task.get("error"),
    )


@router.get("/health", response_model=HealthResponse)
async def brain_health() -> HealthResponse:
    """Check brain health."""
    if not BRAIN_AVAILABLE:
        return HealthResponse(status="unavailable", initialized=False, workers=0)

    try:
        api = await get_brain_api()
        health = await api.health_check()
        return HealthResponse(
            status=health.get("status", "unknown"),
            initialized=health.get("initialized", False),
            workers=health.get("workers", 0),
        )
    except Exception as e:
        return HealthResponse(
            status=f"error: {e}",
            initialized=False,
            workers=0,
        )


# Integrated Brain API Endpoints
class IntegratedQueryRequest(BaseModel):
    """Request for integrated brain processing."""

    query: str
    mode: str = "auto"
    context: dict[str, Any] = {}


class IntegratedQueryResponse(BaseModel):
    """Response from integrated brain."""

    response: str
    latency_ms: float
    mode: str
    confidence: float
    components_used: list[str]


@router.post("/query", response_model=IntegratedQueryResponse)
async def integrated_query(request: IntegratedQueryRequest) -> IntegratedQueryResponse:
    """Process query using integrated brain with all components."""
    if not INTEGRATED_BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Integrated brain not available")

    try:
        brain = get_integrated_brain()
        result = await brain.process(request.query, mode=request.mode, context=request.context)
        return IntegratedQueryResponse(
            response=result.response,
            latency_ms=result.latency_ms,
            mode=result.mode,
            confidence=result.confidence,
            components_used=result.components_used,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/think-fast")
async def brain_think_fast(request: IntegratedQueryRequest) -> dict[str, Any]:
    """Fast thinking using dual-process brain (<100ms target)."""
    import time

    start_time = time.perf_counter()

    try:
        from amos_dual_process_brain import get_dual_process_brain

        brain = get_dual_process_brain()
        result = await brain.think(query=request.query, context=request.context, prefer_fast=True)

        total_latency = (time.perf_counter() - start_time) * 1000

        return {
            "response": result.response,
            "thinking_mode": result.thinking_mode,
            "confidence": result.confidence,
            "latency_ms": total_latency,
            "fast_latency_ms": result.fast_result.latency_ms if result.fast_result else None,
            "success": True,
        }
    except Exception as e:
        # Fallback to standard brain
        try:
            if not INTEGRATED_BRAIN_AVAILABLE:
                raise HTTPException(status_code=503, detail="Brain not available")

            brain = get_integrated_brain()
            result = await brain.process(request.query, mode="fast", context=request.context)
            total_latency = (time.perf_counter() - start_time) * 1000

            return {
                "response": result.response,
                "thinking_mode": "fast_fallback",
                "confidence": result.confidence,
                "latency_ms": total_latency,
                "fast_latency_ms": None,
                "success": True,
            }
        except Exception as fallback_error:
            raise HTTPException(
                status_code=500,
                detail=f"Fast thinking failed: {e}. Fallback also failed: {fallback_error}",
            )


@router.get("/stats")
async def brain_stats() -> dict[str, Any]:
    """Get brain system statistics."""
    if not INTEGRATED_BRAIN_AVAILABLE:
        return {"error": "Integrated brain not available"}

    try:
        brain = get_integrated_brain()
        return brain.get_stats()
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import asyncio

    async def test():
        print("Brain v2 API Test")
        print("=" * 60)

        # Test health
        health = await brain_health()
        print(f"Health: {health.status} (workers={health.workers})")

        # Test sync processing
        if BRAIN_AVAILABLE:
            result = await process_task_sync(
                TaskRequest(description="Design microservices architecture")
            )
            print("\nSync Result:")
            print(f"  Task ID: {result.task_id}")
            print(f"  Domain: {result.domain}")
            print(f"  Success: {result.success}")
            print(f"  Duration: {result.duration_ms:.1f}ms")

            # Test async submission
            submit = await submit_task_async(
                TaskRequest(description="Optimize database queries", priority="HIGH")
            )
            print(f"\nAsync Submitted: {submit.task_id}")

            # Check status
            await asyncio.sleep(2)
            status = await get_task_status(submit.task_id)
            print(f"Status: {status.status}")

        print("\n" + "=" * 60)

    asyncio.run(test())
