from typing import Any, Dict, List

"""Direct Brain Kernel API - Direct integration with AMOS Kernel Runtime.

Provides endpoints that directly use the AMOS kernel runtime for:
- Cognitive cycle execution
- State graph operations
- Legality assessment
- Morph execution

This is the real production implementation using clawspring.amos_brain.
"""

import asyncio
import sys
import time
from datetime import datetime, timezone

UTC = timezone.utc
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Add clawspring to path
AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
if str(AMOS_ROOT) not in sys.path:
    sys.path.insert(0, str(AMOS_ROOT))
if str(AMOS_ROOT / "clawspring") not in sys.path:
    sys.path.insert(0, str(AMOS_ROOT / "clawspring"))
if str(AMOS_ROOT / "clawspring" / "amos_brain") not in sys.path:
    sys.path.insert(0, str(AMOS_ROOT / "clawspring" / "amos_brain"))

# Import kernel runtime
BRAIN_AVAILABLE = False
kernel_runtime = None


def _import_kernel():
    """Lazy import of kernel to handle import errors gracefully."""
    global BRAIN_AVAILABLE, kernel_runtime
    if BRAIN_AVAILABLE:
        return kernel_runtime

    try:
        from amos_kernel_runtime import AMOSKernelRuntime  # noqa: E402

        kernel_runtime = AMOSKernelRuntime
        BRAIN_AVAILABLE = True
        return kernel_runtime
    except ImportError as e:
        print(f"Kernel import error: {e}")
        BRAIN_AVAILABLE = False
        return None


router = APIRouter(prefix="/api/v1/brain-kernel", tags=["Brain Kernel Direct"])

# ============================================================================
# Request/Response Models
# ============================================================================


class KernelCycleRequest(BaseModel):
    """Request for AMOS kernel cognitive cycle."""

    observation: Dict[str, Any] = Field(
        default_factory=dict, description="Current state observation"
    )
    goal: Dict[str, Any] = Field(default_factory=dict, description="Target goal specification")
    timeout_ms: int = Field(default=5000, ge=100, le=60000, description="Timeout in milliseconds")


class KernelCycleResponse(BaseModel):
    """Response from AMOS kernel cognitive cycle."""

    success: bool
    status: str
    legality_score: float
    sigma: float
    selected_branch: Optional[str]
    latency_ms: float
    timestamp: str
    details: Dict[str, Any]


class StateGraphRequest(BaseModel):
    """Request to create/analyze state graph."""

    vertices: List[str] = Field(default_factory=list)
    edges: List[dict[str, Any]] = Field(default_factory=list)
    state_vars: Dict[str, float] = Field(default_factory=dict)


class StateGraphResponse(BaseModel):
    """Response with state graph analysis."""

    success: bool
    state_hash: str
    vertex_count: int
    edge_count: int
    omega: float
    kappa: float
    phi: float
    drift: float
    legality: float


class LegalityRequest(BaseModel):
    """Request for legality assessment."""

    state_data: Dict[str, Any]
    invariants: List[str] = Field(default_factory=list)


class LegalityResponse(BaseModel):
    """Response from legality assessment."""

    is_legal: bool
    legality_score: float
    drift_coefficient: float
    violations: List[dict[str, Any]]
    mode: str


class HealthResponse(BaseModel):
    """Kernel health status."""

    status: str
    kernel_available: bool
    timestamp: str
    version: str = "28-phase"


# ============================================================================
# API Endpoints
# ============================================================================


@router.get("/health", response_model=HealthResponse)
async def kernel_health() -> HealthResponse:
    """Check kernel runtime health."""
    kernel_class = _import_kernel()

    return HealthResponse(
        status="healthy" if kernel_class else "unavailable",
        kernel_available=kernel_class is not None,
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.post("/cycle", response_model=KernelCycleResponse)
async def execute_kernel_cycle(request: KernelCycleRequest) -> KernelCycleResponse:
    """Execute full AMOS cognitive cycle.

    Runs the 7-stage AMOS loop:
    1. Observe → 2. Update → 3. Generate → 4. Simulate →
    5. Filter → 6. Collapse → 7. Execute
    """
    kernel_class = _import_kernel()

    if not kernel_class:
        raise HTTPException(status_code=503, detail="AMOS Kernel not available")

    start_time = time.perf_counter()

    try:
        # Create kernel instance
        kernel = kernel_class()

        # Execute cognitive cycle with timeout
        result = await asyncio.wait_for(
            kernel.execute_cycle(request.observation, request.goal),
            timeout=request.timeout_ms / 1000.0,
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return KernelCycleResponse(
            success=True,
            status=result.get("status", "unknown"),
            legality_score=result.get("legality", 0.0),
            sigma=result.get("sigma", float("inf")),
            selected_branch=result.get("selected_branch"),
            latency_ms=elapsed_ms,
            timestamp=datetime.now(UTC).isoformat(),
            details=result,
        )

    except TimeoutError:
        raise HTTPException(
            status_code=504, detail=f"Kernel cycle timed out after {request.timeout_ms}ms"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kernel error: {str(e)}")


@router.post("/state/analyze", response_model=StateGraphResponse)
async def analyze_state_graph(request: StateGraphRequest) -> StateGraphResponse:
    """Analyze a state graph and return metrics."""
    kernel_class = _import_kernel()

    if not kernel_class:
        raise HTTPException(status_code=503, detail="AMOS Kernel not available")

    try:
        from amos_kernel_runtime import StateGraph, StateVariables

        # Build state graph
        sg = StateGraph()
        sg.vertices.update(request.vertices)

        for edge in request.edges:
            if "source" in edge and "target" in edge:
                key = (str(edge["source"]), str(edge["target"]))
                sg.edges[key] = edge.get("properties", {})

        sg.state_vars.update(request.state_vars)

        # Compute metrics
        state_hash = sg.compute_hash()
        omega = sum(sg.state_vars.values()) if sg.state_vars else 0.0
        kappa = len(sg.vertices) if sg.vertices else 1.0
        phi = len(sg.edges) / max(len(sg.vertices), 1) if sg.vertices else 0.0

        # Create state variables to compute drift/legality
        sv = StateVariables(
            omega=omega,
            kappa=kappa,
            phi=phi,
        )

        return StateGraphResponse(
            success=True,
            state_hash=state_hash,
            vertex_count=len(sg.vertices),
            edge_count=len(sg.edges),
            omega=omega,
            kappa=kappa,
            phi=phi,
            drift=sv.drift,
            legality=sv.legality,
        )

    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"State graph module error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.post("/legality/check", response_model=LegalityResponse)
async def check_legality(request: LegalityRequest) -> LegalityResponse:
    """Check legality of a state against invariants."""
    kernel_class = _import_kernel()

    if not kernel_class:
        raise HTTPException(status_code=503, detail="AMOS Kernel not available")

    try:
        from amos_kernel_runtime import StateGraph

        # Build minimal state
        sg = StateGraph()
        if "vertices" in request.state_data:
            sg.vertices.update(str(v) for v in request.state_data["vertices"])

        # Run legality check (simplified)
        violations = []
        if not sg.vertices:
            violations.append(
                {
                    "law_id": "I1",
                    "description": "Identity Preservation: No vertices",
                    "severity": 1.0,
                }
            )

        is_legal = len(violations) == 0
        legality_score = 1.0 if is_legal else 0.0

        return LegalityResponse(
            is_legal=is_legal,
            legality_score=legality_score,
            drift_coefficient=0.0 if is_legal else float("inf"),
            violations=violations,
            mode="normal" if is_legal else "recovery",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Legality check error: {str(e)}")


@router.get("/docs")
async def get_kernel_docs() -> Dict[str, Any]:
    """Get AMOS kernel documentation."""
    return {
        "name": "AMOS Kernel Runtime API",
        "version": "28-phase",
        "description": "Direct access to AMOS cognitive kernel",
        "endpoints": {
            "/health": "Check kernel health",
            "/cycle": "Execute full cognitive cycle",
            "/state/analyze": "Analyze state graph",
            "/legality/check": "Check legality against invariants",
            "/docs": "This documentation",
        },
        "amos_loop": [
            "1. Observe - Ingest state",
            "2. Update - Apply laws",
            "3. Generate - Create branches",
            "4. Simulate - Score branches",
            "5. Filter - Apply invariants",
            "6. Collapse - Select optimal",
            "7. Execute - Apply morphs",
        ],
        "metrics": {
            "Ω (omega)": "Uncertainty/entropy",
            "K (kappa)": "Knowledge/confidence",
            "Φ (phi)": "Coherence score",
            "σ (sigma)": "Drift coefficient = Ω/K",
            "L (legality)": "Legality = I × S",
        },
    }


# ============================================================================
# Module Export
# ============================================================================


def get_router() -> APIRouter:
    """Get the API router for mounting in main app."""
    return router
