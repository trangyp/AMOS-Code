from typing import Any, Dict, Optional

"""Integrated Brain API - Production-ready cognitive endpoints.

Uses AMOS brain with proper timeout handling and progress tracking
to prevent 'taking a long time' errors.
"""

import asyncio
from datetime import datetime, timezone

UTC = timezone.utc

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

# Import AMOS brain with fallback
try:
    from amos_brain import decide, get_brain, think, validate

    BRAIN_AVAILABLE = True
except ImportError:
    BRAIN_AVAILABLE = False

try:
    from amos_brain.facade import BrainClient

    BRAIN_CLIENT_AVAILABLE = True
except ImportError:
    BRAIN_CLIENT_AVAILABLE = False

router = APIRouter(prefix="/api/v1/brain-integrated", tags=["Brain Integrated"])


class CognitiveRequest(BaseModel):
    """Request for cognitive processing."""

    query: str = Field(..., min_length=1, max_length=10000)
    mode: str = Field(default="auto", pattern="^(auto|fast|deep|analytical)$")
    context: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: float = Field(default=30.0, ge=1.0, le=300.0)


class CognitiveResponse(BaseModel):
    """Response from cognitive processing."""

    success: bool
    content: str
    confidence: float
    mode: str
    latency_ms: float
    timestamp: str
    law_compliant: Optional[bool] = None


class HealthResponse(BaseModel):
    """Brain health status."""

    status: str
    brain_available: bool
    client_available: bool
    timestamp: str


@router.get("/health", response_model=HealthResponse)
async def brain_health() -> HealthResponse:
    """Check brain system health."""
    return HealthResponse(
        status="healthy" if BRAIN_AVAILABLE else "degraded",
        brain_available=BRAIN_AVAILABLE,
        client_available=BRAIN_CLIENT_AVAILABLE,
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.post("/think", response_model=CognitiveResponse)
async def brain_think_endpoint(request: CognitiveRequest) -> CognitiveResponse:
    """Execute cognitive thinking with timeout protection.

    Prevents 'taking a long time' errors by enforcing request timeout.
    """
    if not BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain system not available")

    start_time = datetime.now(UTC)

    try:
        # Execute with timeout to prevent hanging
        result = await asyncio.wait_for(
            asyncio.to_thread(think, request.query, request.context),
            timeout=request.timeout_seconds,
        )

        end_time = datetime.now(UTC)
        latency_ms = (end_time - start_time).total_seconds() * 1000

        return CognitiveResponse(
            success=getattr(result, "success", True),
            content=getattr(result, "content", str(result)),
            confidence=getattr(result, "confidence", 0.8),
            mode=request.mode,
            latency_ms=latency_ms,
            timestamp=end_time.isoformat(),
            law_compliant=getattr(result, "law_compliant", None),
        )

    except TimeoutError:
        raise HTTPException(
            status_code=504, detail=f"Thinking operation timed out after {request.timeout_seconds}s"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brain error: {str(e)}")


@router.post("/decide", response_model=CognitiveResponse)
async def brain_decide_endpoint(request: CognitiveRequest) -> CognitiveResponse:
    """Execute decision-making with timeout protection."""
    if not BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain system not available")

    start_time = datetime.now(UTC)

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(decide, request.query, request.context),
            timeout=request.timeout_seconds,
        )

        end_time = datetime.now(UTC)
        latency_ms = (end_time - start_time).total_seconds() * 1000

        return CognitiveResponse(
            success=True,
            content=str(result),
            confidence=0.85,
            mode="decision",
            latency_ms=latency_ms,
            timestamp=end_time.isoformat(),
        )

    except TimeoutError:
        raise HTTPException(
            status_code=504, detail=f"Decision operation timed out after {request.timeout_seconds}s"
        )


@router.post("/validate", response_model=CognitiveResponse)
async def brain_validate_endpoint(request: CognitiveRequest) -> CognitiveResponse:
    """Execute validation with timeout protection."""
    if not BRAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Brain system not available")

    start_time = datetime.now(UTC)

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(validate, request.query, request.context),
            timeout=request.timeout_seconds,
        )

        end_time = datetime.now(UTC)
        latency_ms = (end_time - start_time).total_seconds() * 1000

        return CognitiveResponse(
            success=True,
            content=str(result),
            confidence=0.9,
            mode="validation",
            latency_ms=latency_ms,
            timestamp=end_time.isoformat(),
        )

    except TimeoutError:
        raise HTTPException(
            status_code=504, detail=f"Validation timed out after {request.timeout_seconds}s"
        )


# Background task processing for long-running operations
async def process_long_thinking(task_id: str, query: str, context: dict) -> None:
    """Process long-running thinking in background."""
    if not BRAIN_AVAILABLE:
        return

    # This would update a task status in database/cache
    # For now, just execute
    try:
        think(query, context)
    except Exception:
        pass  # Background tasks should not raise


@router.post("/think-async")
async def brain_think_async(
    request: CognitiveRequest, background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Submit async thinking task - returns immediately, processes in background."""
    task_id = f"think-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"

    background_tasks.add_task(process_long_thinking, task_id, request.query, request.context)

    return {
        "task_id": task_id,
        "status": "submitted",
        "query": request.query[:100] + "..." if len(request.query) > 100 else request.query,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.post("/think-fast", response_model=CognitiveResponse)
async def brain_think_fast_endpoint(request: CognitiveRequest) -> CognitiveResponse:
    """Fast thinking with dual-process architecture (<100ms target).

    Uses System 1 (fast) thinking with cache, rules, and patterns.
    Falls back to System 2 (slow) only if confidence is low.
    """
    import time

    start = time.perf_counter()

    try:
        from amos_dual_process_brain import get_dual_process_brain

        brain = get_dual_process_brain()
        result = await brain.think(query=request.query, context=request.context, prefer_fast=True)

        elapsed = (time.perf_counter() - start) * 1000

        return CognitiveResponse(
            success=True,
            content=result.response,
            confidence=result.confidence,
            mode=result.thinking_mode,
            latency_ms=elapsed,
            timestamp=datetime.now(UTC).isoformat(),
            law_compliant=None,
        )
    except ImportError:
        # Fallback to standard thinking
        if not BRAIN_AVAILABLE:
            raise HTTPException(status_code=503, detail="Brain not available")

        result = think(request.query, request.context)
        elapsed = (time.perf_counter() - start) * 1000

        return CognitiveResponse(
            success=True,
            content=getattr(result, "content", str(result)),
            confidence=getattr(result, "confidence", 0.8),
            mode="fallback_slow",
            latency_ms=elapsed,
            timestamp=datetime.now(UTC).isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fast thinking error: {str(e)}")
