from typing import Any, Dict, Optional

"""Intelligent Task Router API

Routes user requests through reading kernel → orchestrator → execution.
End-to-end intelligent task processing.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from backend.amos_intelligent_router import (
    get_intelligent_router,
)

router = APIRouter()


class RouteRequest(BaseModel):
    text: str
    context: Dict[str, Any] = None


class RouteResponse(BaseModel):
    task_id: str
    routed: bool
    executed: bool
    reading_latency_ms: float
    routing_latency_ms: float
    execution_latency_ms: float
    total_latency_ms: float
    error: Optional[str] = None
    result: Dict[str, Any] = None


class RouteStats(BaseModel):
    total: int
    routed: int
    executed: int
    success_rate: float
    avg_reading_latency_ms: float
    avg_routing_latency_ms: float
    avg_execution_latency_ms: float
    avg_total_latency_ms: float


@router.post("/route", response_model=RouteResponse)
async def route_request(req: RouteRequest) -> RouteResponse:
    """Route a task through reading → orchestrator → execution."""
    router = get_intelligent_router()
    result = await router.route_and_execute(req.text, req.context)

    response_result = None
    if result.result:
        response_result = {
            "task_id": result.result.task_id,
            "success": result.result.success,
            "output": result.result.output,
            "domain": result.result.domain,
            "engines_used": result.result.engines_used,
            "duration_ms": result.result.duration_ms,
        }

    return RouteResponse(
        task_id=result.task_id,
        routed=result.routed,
        executed=result.executed,
        reading_latency_ms=result.reading_latency_ms,
        routing_latency_ms=result.routing_latency_ms,
        execution_latency_ms=result.execution_latency_ms,
        total_latency_ms=result.total_latency_ms,
        error=result.error,
        result=response_result,
    )


@router.post("/execute")
async def execute_task(req: RouteRequest) -> Dict[str, Any]:
    """Execute a task with full feedback."""
    router = get_intelligent_router()
    result = await router.route_and_execute(req.text, req.context)

    if not result.routed:
        return {
            "success": False,
            "stage": "routing_failed",
            "error": result.error,
            "latency_ms": result.total_latency_ms,
        }

    if not result.executed:
        return {
            "success": False,
            "stage": "execution_failed",
            "error": result.error,
            "latency_ms": result.total_latency_ms,
        }

    return {
        "success": True,
        "stage": "completed",
        "task_id": result.task_id,
        "output": result.result.output if result.result else None,
        "domain": result.result.domain if result.result else None,
        "engines": result.result.engines_used if result.result else [],
        "latency_ms": result.total_latency_ms,
    }


@router.get("/stats", response_model=RouteStats)
async def get_router_stats() -> RouteStats:
    """Get routing statistics."""
    router = get_intelligent_router()
    stats = router.get_stats()

    return RouteStats(
        total=stats["total"],
        routed=stats["routed"],
        executed=stats["executed"],
        success_rate=stats["success_rate"],
        avg_reading_latency_ms=stats["avg_reading_latency_ms"],
        avg_routing_latency_ms=stats["avg_routing_latency_ms"],
        avg_execution_latency_ms=stats["avg_execution_latency_ms"],
        avg_total_latency_ms=stats["avg_total_latency_ms"],
    )


@router.get("/health")
async def router_health() -> Dict[str, Any]:
    """Health check for intelligent router."""
    router = get_intelligent_router()
    stats = router.get_stats()

    return {
        "status": "healthy",
        "initialized": router._initialized,
        "total_requests": stats["total"],
        "success_rate": stats["success_rate"],
    }
