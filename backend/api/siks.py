from typing import Any

"""SIKS API Router - Super-Intelligence Kernel Stack endpoints."""


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/siks", tags=["siks"])

# ============================================================================
# Pydantic Models
# ============================================================================


class SIKSPipelineRequest(BaseModel):
    """Request to run SIKS pipeline."""

    content: str = Field(..., description="Input content to process")
    context_id: str | None = Field(None, description="Optional context identifier")
    stages: list[str] | None = Field(None, description="Specific stages to run (default: all)")


class SIKSPipelineResponse(BaseModel):
    """Response from SIKS pipeline execution."""

    status: str
    stages_executed: list[str]
    results: dict[str, Any]
    execution_time_ms: float
    siks_enabled: bool


class UnderstandingRequest(BaseModel):
    """Request for understanding kernel."""

    content: str
    context_id: str | None = None


class UnderstandingResponse(BaseModel):
    """Response from understanding kernel."""

    understanding_id: str
    understanding_score: float
    comprehension_depth: str
    explanations_generated: int
    ready_for_transfer: bool


class ProblemFindingRequest(BaseModel):
    """Request for problem finding kernel."""

    content: str
    goals: list[str] | None = None


class ProblemFindingResponse(BaseModel):
    """Response from problem finding kernel."""

    problems_discovered: int
    problems: list[dict[str, Any]]
    hidden_problems: int
    framing_errors: int
    false_goals: int


class CalibrationCheckRequest(BaseModel):
    """Request for calibration check."""

    prediction: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    outcome: bool


class CalibrationCheckResponse(BaseModel):
    """Response from calibration kernel."""

    calibration_state: str
    calibration_gap: float
    well_calibrated: bool
    calibration_history_size: int


# ============================================================================
# SIKS Integration
# ============================================================================

_siks_stack: Any = None
_siks_initialized: bool = False


async def get_siks_stack():
    """Get or initialize SIKS stack."""
    global _siks_stack, _siks_initialized

    if _siks_initialized and _siks_stack is not None:
        return _siks_stack

    try:
        import sys
        from pathlib import Path

        amos_root = Path(__file__).parent.parent.parent.resolve()
        if str(amos_root) not in sys.path:
            sys.path.insert(0, str(amos_root))

        # Import SIKS module
        import importlib.util

        siks_path = amos_root / "amos_superintelligence_stack.py"

        if not siks_path.exists():
            return None

        spec = importlib.util.spec_from_file_location("siks_api", siks_path)
        if spec is None or spec.loader is None:
            return None

        siks_module = importlib.util.module_from_spec(spec)
        sys.modules["siks_api"] = siks_module
        spec.loader.exec_module(siks_module)

        # Initialize stack
        _siks_stack = await siks_module.initialize_superintelligence_stack()
        _siks_initialized = True
        return _siks_stack
    except Exception:
        return None


# ============================================================================
# API Endpoints
# ============================================================================


@router.post("/pipeline", response_model=SIKSPipelineResponse)
async def run_siks_pipeline(request: SIKSPipelineRequest) -> SIKSPipelineResponse:
    """Execute SIKS pipeline on input content."""
    import time

    start_time = time.time()

    stack = await get_siks_stack()

    if stack is None:
        return SIKSPipelineResponse(
            status="siks_not_available",
            stages_executed=[],
            results={},
            execution_time_ms=0.0,
            siks_enabled=False,
        )

    try:
        # Build context
        ctx = {"content": request.content, "context_id": request.context_id or "api_request"}

        # Determine stages
        stages = request.stages or list(stack.kernels.keys())

        # Execute pipeline
        result = await stack.execute_pipeline(ctx, stages=stages)

        execution_time = (time.time() - start_time) * 1000

        return SIKSPipelineResponse(
            status=result.get("status", "unknown"),
            stages_executed=result.get("stages_executed", []),
            results=result.get("stage_results", {}),
            execution_time_ms=execution_time,
            siks_enabled=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SIKS pipeline error: {str(e)}")


@router.post("/understand", response_model=UnderstandingResponse)
async def run_understanding_kernel(request: UnderstandingRequest) -> UnderstandingResponse:
    """Execute understanding kernel on content."""
    stack = await get_siks_stack()

    if stack is None:
        raise HTTPException(status_code=503, detail="SIKS stack not available")

    try:
        ctx = {"content": request.content, "context_id": request.context_id or "understanding_api"}

        result = await stack.execute_pipeline(ctx, stages=["understanding_kernel"])
        understanding_result = result.get("stage_results", {}).get("understanding_kernel", {})

        return UnderstandingResponse(
            understanding_id=understanding_result.get("understanding_id", ""),
            understanding_score=understanding_result.get("understanding_score", 0.0),
            comprehension_depth=understanding_result.get("comprehension_depth", "unknown"),
            explanations_generated=understanding_result.get("explanations_generated", 0),
            ready_for_transfer=understanding_result.get("ready_for_transfer", False),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Understanding kernel error: {str(e)}")


@router.post("/find-problems", response_model=ProblemFindingResponse)
async def run_problem_finding_kernel(request: ProblemFindingRequest) -> ProblemFindingResponse:
    """Execute problem finding kernel to detect hidden issues."""
    stack = await get_siks_stack()

    if stack is None:
        raise HTTPException(status_code=503, detail="SIKS stack not available")

    try:
        ctx = {
            "content": request.content,
            "goals": request.goals or [request.content],
            "context_id": "problem_finding_api",
        }

        result = await stack.execute_pipeline(ctx, stages=["problem_finding_kernel"])
        pf_result = result.get("stage_results", {}).get("problem_finding_kernel", {})

        return ProblemFindingResponse(
            problems_discovered=pf_result.get("problems_discovered", 0),
            problems=pf_result.get("problems", []),
            hidden_problems=pf_result.get("hidden_problems", 0),
            framing_errors=pf_result.get("framing_errors", 0),
            false_goals=pf_result.get("false_goals", 0),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Problem finding kernel error: {str(e)}")


@router.post("/check-calibration", response_model=CalibrationCheckResponse)
async def run_calibration_check(request: CalibrationCheckRequest) -> CalibrationCheckResponse:
    """Check calibration of confidence vs accuracy."""
    stack = await get_siks_stack()

    if stack is None:
        raise HTTPException(status_code=503, detail="SIKS stack not available")

    try:
        ctx = {
            "prediction": request.prediction,
            "confidence": request.confidence,
            "outcome": request.outcome,
            "context_id": "calibration_api",
        }

        result = await stack.execute_pipeline(ctx, stages=["calibration_kernel"])
        cal_result = result.get("stage_results", {}).get("calibration_kernel", {})

        return CalibrationCheckResponse(
            calibration_state=cal_result.get("calibration_state", "UNKNOWN"),
            calibration_gap=cal_result.get("calibration_gap", 0.0),
            well_calibrated=cal_result.get("well_calibrated", False),
            calibration_history_size=cal_result.get("calibration_history_size", 0),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calibration kernel error: {str(e)}")


@router.get("/status")
async def get_siks_status() -> dict[str, Any]:
    """Get SIKS stack status."""
    stack = await get_siks_stack()

    if stack is None:
        return {"enabled": False, "initialized": False, "kernels_count": 0, "available_kernels": []}

    return {
        "enabled": True,
        "initialized": True,
        "kernels_count": len(stack.kernels),
        "available_kernels": list(stack.kernels.keys()),
    }


@router.get("/kernels")
async def list_kernels() -> dict[str, Any]:
    """List all available SIKS kernels."""
    stack = await get_siks_stack()

    if stack is None:
        return {"kernels": [], "count": 0}

    kernel_info = []
    for name, kernel in stack.kernels.items():
        kernel_info.append(
            {
                "name": name,
                "status": getattr(kernel, "status", "unknown").name
                if hasattr(getattr(kernel, "status", None), "name")
                else str(getattr(kernel, "status", "unknown")),
                "initialized": getattr(kernel, "initialized", False),
            }
        )

    return {"kernels": kernel_info, "count": len(kernel_info)}
