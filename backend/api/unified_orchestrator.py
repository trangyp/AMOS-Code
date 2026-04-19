"""Unified Orchestrator API - Direct MasterOrchestrator integration.

Exposes the real MasterOrchestrator from clawspring/amos_brain with:
- Full cognitive task orchestration
- Organism bridge integration
- Predictive analysis
- Task execution
- Mathematical framework analysis
"""

from __future__ import annotations


import sys
import time
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Setup paths
AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
for p in [AMOS_ROOT, AMOS_ROOT / "clawspring", AMOS_ROOT / "amos_brain"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Import real MasterOrchestrator
try:
    from clawspring.amos_brain.master_orchestrator import (
        MasterOrchestrator,
        OrchestrationResult,
    )

    _ORCHESTRATOR_AVAILABLE = True
except ImportError:
    try:
        from amos_brain.master_orchestrator import (
            MasterOrchestrator,
            OrchestrationResult,
        )

        _ORCHESTRATOR_AVAILABLE = True
    except ImportError:
        _ORCHESTRATOR_AVAILABLE = False

router = APIRouter(prefix="/orchestrator", tags=["Unified Orchestrator"])

# Global orchestrator instance
_orchestrator: MasterOrchestrator | None = None


def get_orchestrator() -> MasterOrchestrator:
    """Get or initialize the MasterOrchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MasterOrchestrator()
        _orchestrator.initialize()
    return _orchestrator


class OrchestrateRequest(BaseModel):
    """Request to orchestrate a cognitive task."""

    task_description: str = Field(..., min_length=1)
    priority: str = Field(default="MEDIUM", pattern="LOW|MEDIUM|HIGH|CRITICAL")
    context: dict[str, Any] = Field(default_factory=dict)
    enable_prediction: bool = Field(default=True)
    enable_organism: bool = Field(default=True)


class OrchestrationAnalysis(BaseModel):
    """Analysis results from orchestration."""

    domain: str
    recommended_engines: list[str]
    risk_level: str
    confidence: float


class OrchestrationPrediction(BaseModel):
    """Prediction results from orchestration."""

    success_probability: float
    estimated_duration_ms: float
    risk_factors: list[str]


class OrchestrationExecution(BaseModel):
    """Execution results from orchestration."""

    success: bool
    output: str
    error: str
    execution_type: str
    engines_used: list[str]


class OrchestrationOrganismEnhancement(BaseModel):
    """Organism enhancement results."""

    coherence_boost: float
    health_awareness: bool
    stress_level: str
    enhancements_applied: list[str]


class OrchestrateResponse(BaseModel):
    """Complete orchestration response."""

    task_id: str
    timestamp: str
    overall_success: bool
    total_duration_ms: float

    # Components
    analysis: OrchestrationAnalysis
    prediction: OrchestrationPrediction
    execution: OrchestrationExecution
    organism_enhancements: OrchestrationOrganismEnhancement

    # Raw data
    raw_result: dict[str, Any]


@router.post("/orchestrate", response_model=OrchestrateResponse)
async def orchestrate_task(request: OrchestrateRequest) -> OrchestrateResponse:
    """Execute full cognitive workflow with MasterOrchestrator.

    This endpoint uses the real MasterOrchestrator to:
    1. Analyze cognitive domain
    2. Apply organism enhancements
    3. Run predictive analysis
    4. Execute the task
    5. Return comprehensive results
    """
    if not _ORCHESTRATOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="MasterOrchestrator not available")

    start_time = time.time()

    try:
        orchestrator = get_orchestrator()

        # Generate task ID
        task_id = f"orch_{int(start_time * 1000)}"

        # Execute orchestration
        result: OrchestrationResult = orchestrator.orchestrate_cognitive_task(
            task_id=task_id,
            task_description=request.task_description,
            priority=request.priority,
        )

        total_duration = (time.time() - start_time) * 1000

        # Build analysis component
        analysis = OrchestrationAnalysis(
            domain=result.domain,
            recommended_engines=result.analysis.get("recommended_engines", []),
            risk_level=result.analysis.get("risk_level", "unknown"),
            confidence=result.analysis.get("confidence", 0.0),
        )

        # Build prediction component (if available)
        prediction = None
        if result.prediction:
            prediction = OrchestrationPrediction(
                success_probability=result.prediction.get("success_probability", 0.0),
                estimated_duration_ms=result.prediction.get("estimated_duration_ms", 0.0),
                risk_factors=result.prediction.get("risk_factors", []),
            )

        # Build execution component
        execution = OrchestrationExecution(
            success=result.execution.get("success", False) if result.execution else False,
            output=result.execution.get("output", "") if result.execution else "",
            error=result.execution.get("error") if result.execution else None,
            execution_type=result.execution.get("execution_type", "unknown")
            if result.execution
            else "unknown",
            engines_used=result.execution.get("engines_used", []) if result.execution else [],
        )

        # Build organism enhancement component
        organism = None
        if result.organism_enhancements:
            organism = OrchestrationOrganismEnhancement(
                coherence_boost=result.organism_enhancements.get("coherence_boost", 0.0),
                health_awareness=result.organism_enhancements.get("health_awareness", False),
                stress_level=result.organism_enhancements.get("stress_level", "normal"),
                enhancements_applied=result.organism_enhancements.get("enhancements_applied", []),
            )

        return OrchestrateResponse(
            task_id=result.task_id,
            timestamp=result.timestamp,
            overall_success=result.overall_success,
            total_duration_ms=total_duration,
            analysis=analysis,
            prediction=prediction,
            execution=execution,
            organism_enhancements=organism,
            raw_result={
                "domain": result.domain,
                "analysis": result.analysis,
                "prediction": result.prediction,
                "execution": result.execution,
                "organism_enhancements": result.organism_enhancements,
                "mathematical_analysis": result.mathematical_analysis,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")


@router.get("/history")
async def get_orchestration_history(limit: int = 10) -> list[dict[str, Any]]:
    """Get recent orchestration history."""
    if not _ORCHESTRATOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="MasterOrchestrator not available")

    try:
        orchestrator = get_orchestrator()
        history = orchestrator._orchestration_history[-limit:]

        return [
            {
                "task_id": h.task_id,
                "timestamp": h.timestamp,
                "domain": h.domain,
                "overall_success": h.overall_success,
                "total_duration_ms": h.total_duration_ms,
            }
            for h in history
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.get("/status")
async def get_orchestrator_status() -> dict[str, Any]:
    """Get MasterOrchestrator status."""
    if not _ORCHESTRATOR_AVAILABLE:
        return {
            "available": False,
            "initialized": False,
            "components": {
                "organism_bridge": False,
                "predictive": False,
                "task_executor": False,
                "math_engine": False,
            },
        }

    try:
        orchestrator = get_orchestrator()

        return {
            "available": True,
            "initialized": orchestrator._initialized,
            "components": {
                "organism_bridge": orchestrator._organism_bridge is not None,
                "predictive": orchestrator._predictive is not None,
                "task_executor": orchestrator._task_executor is not None,
                "math_engine": orchestrator._math_engine is not None,
            },
            "history_count": len(orchestrator._orchestration_history),
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
        }


@router.post("/quick")
async def quick_orchestrate(task_description: str, priority: str = "MEDIUM") -> dict[str, Any]:
    """Quick orchestration endpoint with minimal response."""
    if not _ORCHESTRATOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="MasterOrchestrator not available")

    try:
        orchestrator = get_orchestrator()
        task_id = f"quick_{int(time.time() * 1000)}"

        result: OrchestrationResult = orchestrator.orchestrate_cognitive_task(
            task_id=task_id,
            task_description=task_description,
            priority=priority,
        )

        return {
            "task_id": result.task_id,
            "success": result.overall_success,
            "domain": result.domain,
            "output": result.execution.get("output", "") if result.execution else "",
            "duration_ms": result.total_duration_ms,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick orchestration failed: {str(e)}")
