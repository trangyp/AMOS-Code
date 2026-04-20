from typing import Any

"""FastLoop Brain API - High-performance cognitive endpoints."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Add paths
_AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
from amos_fastloop_brain_bridge import execute_with_brain, get_brain_bridge

router = APIRouter(prefix="/fastloop", tags=["fastloop"])


class FastLoopRequest(BaseModel):
    request: str
    context: dict[str, Any] = {}


class FastLoopResponse(BaseModel):
    success: bool
    output: dict[str, Any]
    latency_ms: float
    path_taken: str
    engines_used: list[str]
    branch_count: int
    laws_checked: list[str]


@router.post("/execute", response_model=FastLoopResponse)
async def fastloop_execute(request: FastLoopRequest) -> FastLoopResponse:
    """Execute request through FastLoop-Brain bridge."""
    try:
        result = await execute_with_brain(request.request, request.context)
        return FastLoopResponse(
            success=result.success,
            output=result.output,
            latency_ms=result.latency_ms,
            path_taken=result.path_taken,
            engines_used=result.engines_used,
            branch_count=result.branch_count,
            laws_checked=result.laws_checked,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def fastloop_stats() -> dict[str, Any]:
    """Get FastLoop bridge statistics."""
    bridge = get_brain_bridge()
    return bridge.get_stats()
