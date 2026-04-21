from __future__ import annotations

from typing import Any, Optional

"""Brain-Powered API Endpoints - Direct brain integration for main backend.

These endpoints use the real AMOS brain kernel for cognitive processing.
Add these to main.py via: app.include_router(brain_powered_router)
"""

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

UTC = timezone.utc

# Setup paths
AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
for p in [AMOS_ROOT, AMOS_ROOT / "clawspring", AMOS_ROOT / "clawspring" / "amos_brain"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

router = APIRouter(prefix="/api/v1/brain-powered", tags=["Brain Powered"])

#Lazy imports
_brain_available: Optional[bool] = None


def _check_brain() -> bool:
    """Check if brain is available."""
    global _brain_available
    if _brain_available is not None:
        return _brain_available
    try:
        from amos_kernel_runtime import AMOSKernelRuntime  # noqa: E402

        _brain_available = True
        return True
    except ImportError:
        _brain_available = False
        return False


# ============================================================================
# Request/Response Models
# ============================================================================


class CognitiveQueryRequest(BaseModel):
    """Request for brain-powered cognitive query."""

    query: str = Field(..., min_length=1, max_length=10000)
    context: dict[str, Any] = Field(default_factory=dict)
    goal_type: str = Field(default="cognitive_task")
    timeout_ms: int = Field(default=5000, ge=100, le=30000)


class CognitiveQueryResponse(BaseModel):
    """Response from brain-powered query."""

    success: bool
    query: str
    response: str
    thinking_mode: str
    legality_score: float
    sigma: float
    confidence: float
    latency_ms: float
    timestamp: str


class BrainStatusResponse(BaseModel):
    """Brain system status."""

    available: bool
    initialized: bool
    kernel_version: str
    memory_entries: int
    cognitive_cycles_today: int
    timestamp: str


class StateAnalysisRequest(BaseModel):
    """Request for state graph analysis."""

    entities: list[str] = Field(default_factory=list)
    relations: list[dict[str, Any]] = Field(default_factory=list)
    metrics: dict[str, float] = Field(default_factory=dict)


class StateAnalysisResponse(BaseModel):
    """State graph analysis response."""

    state_hash: str
    entity_count: int
    relation_count: int
    omega: float
    kappa: float
    phi: float
    drift: float
    legality: float
    timestamp: str


# ============================================================================
# Brain-Powered Endpoints
# ============================================================================


@router.get("/status", response_model=BrainStatusResponse)
async def get_brain_status() -> BrainStatusResponse:
    """Get brain system status."""
    available = _check_brain()

    # Try to get real metrics
    memory_entries = 0
    cycles_today = 0

    if available:
        try:
            from amos_brain.memory import get_brain_memory

            memory = get_brain_memory()
            history = memory.get_reasoning_history(limit=1000)
            memory_entries = len(history)

            today = datetime.now(UTC).date()
            cycles_today = sum(
                1
                for h in history
                if datetime.fromisoformat(h.get("timestamp", "1970-01-01")).date() == today
            )
        except Exception:
            pass

    return BrainStatusResponse(
        available=available,
        initialized=available,
        kernel_version="28-phase" if available else "unavailable",
        memory_entries=memory_entries,
        cognitive_cycles_today=cycles_today,
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.post("/query", response_model=CognitiveQueryResponse)
async def brain_query(request: CognitiveQueryRequest) -> CognitiveQueryResponse:
    """Execute brain-powered cognitive query.

    Uses AMOS kernel runtime for real cognitive processing.
    """
    if not _check_brain():
        raise HTTPException(status_code=503, detail="Brain not available")

    import asyncio

    start = time.perf_counter()
    kernel = AMOSKernelRuntime()

    try:
        result = await asyncio.wait_for(
            kernel.execute_cycle(
                {"content": request.query, "context": request.context}, {"type": request.goal_type}
            ),
            timeout=request.timeout_ms / 1000.0,
        )

        elapsed = (time.perf_counter() - start) * 1000

        # Format response based on result
        status = result.get("status", "unknown")
        if status == "REJECTED":
            response_text = (
                f"Query rejected by constitution gate. Reason: {result.get('reason', 'Unknown')}"
            )
        else:
            response_text = (
                f"Cognitive cycle completed. "
                f"Selected branch: {result.get('selected_branch', 'N/A')}. "
                f"Legality: {result.get('legality', 0):.3f}"
            )

        return CognitiveQueryResponse(
            success=True,
            query=request.query,
            response=response_text,
            thinking_mode="deep" if result.get("sigma", 0) > 0.5 else "fast",
            legality_score=result.get("legality", 0.0),
            sigma=result.get("sigma", 0.0),
            confidence=1.0 - min(result.get("sigma", 1.0), 1.0),
            latency_ms=elapsed,
            timestamp=datetime.now(UTC).isoformat(),
        )

    except TimeoutError:
        raise HTTPException(status_code=504, detail="Query timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brain error: {str(e)}")


@router.post("/analyze-state", response_model=StateAnalysisResponse)
async def analyze_state(request: StateAnalysisRequest) -> StateAnalysisResponse:
    """Analyze state graph using AMOS brain."""
    if not _check_brain():
        raise HTTPException(status_code=503, detail="Brain not available")

    from amos_kernel_runtime import StateGraph, StateVariables

    # Build state graph
    sg = StateGraph()
    sg.vertices.update(request.entities)

    for rel in request.relations:
        if "source" in rel and "target" in rel:
            key = (str(rel["source"]), str(rel["target"]))
            sg.edges[key] = rel.get("properties", {})

    sg.state_vars.update(request.metrics)

    # Compute metrics
    state_hash = sg.compute_hash()
    omega = sum(sg.state_vars.values()) if sg.state_vars else 0.0
    kappa = len(sg.vertices) if sg.vertices else 1.0
    phi = len(sg.edges) / max(len(sg.vertices), 1) if sg.vertices else 0.0

    sv = StateVariables(omega=omega, kappa=kappa, phi=phi)

    return StateAnalysisResponse(
        state_hash=state_hash,
        entity_count=len(sg.vertices),
        relation_count=len(sg.edges),
        omega=omega,
        kappa=kappa,
        phi=phi,
        drift=sv.drift,
        legality=sv.legality,
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.get("/recent-activity")
async def get_recent_brain_activity(limit: int = 10) -> list[dict[str, Any]]:
    """Get recent brain activity from memory."""
    if not _check_brain():
        return []

    try:
        memory = get_brain_memory()
        history = memory.get_reasoning_history(limit=limit)

        return [
            {
                "timestamp": h.get("timestamp"),
                "type": h.get("type", "unknown"),
                "confidence": h.get("confidence_score", 0),
                "domain": h.get("domain", "general"),
            }
            for h in history
        ]
    except Exception:
        return []
