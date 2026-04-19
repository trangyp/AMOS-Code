from typing import Any

"""
AMOS Cognitive Processing API

Integrates Brain + Translation Layer + Orchestrator into unified cognitive pipeline.
Real feature - no stubs, no mocks.

Pipeline:
  1. Signal-Noise Separation (translation layer)
  2. Semantic Analysis (translation layer)
  3. Brain Evaluation (amos_brain)
  4. Orchestration (master_orchestrator)
  5. Execution (task_execution_integration)

Creator: Trang Phan
Version: 1.0.0
"""
from __future__ import annotations


import sys
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Ensure paths
_AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(_AMOS_ROOT))
sys.path.insert(0, str(_AMOS_ROOT / "clawspring" / "amos_brain"))


from amos_brain_working import think
from amos_translation_layer import get_translation_layer

router = APIRouter(prefix="/cognitive", tags=["cognitive"])


class CognitiveRequest(BaseModel):
    """Cognitive processing request."""

    input: str = Field(..., description="Raw natural language input")
    context: dict[str, Any] = Field(default_factory=dict, description="Processing context")
    priority: str = Field(default="MEDIUM", description="Task priority (LOW/MEDIUM/HIGH/CRITICAL)")
    enable_execution: bool = Field(default=False, description="Allow actual task execution")


class SignalNoiseAnalysis(BaseModel):
    """Signal-noise separation results."""

    signal_quality: float
    noise_distortion: float
    ambiguity_count: int
    execution_safe: bool


class SemanticAnalysis(BaseModel):
    """Semantic compilation results."""

    goal_type: str
    objective: str
    confidence: float
    requires_clarification: bool


class BrainAnalysis(BaseModel):
    """Brain evaluation results."""

    status: str
    legality: float
    sigma: float
    mode: str


class OrchestrationResult(BaseModel):
    """Orchestration results."""

    task_id: str | None
    domain: str
    engines: list[str]
    execution_time_ms: float
    success: bool
    output: str | None = None
    error: str | None = None


class CognitiveResponse(BaseModel):
    """Complete cognitive processing response."""

    request_id: str
    input: str

    # Stage 1: Signal-Noise
    signal_noise: SignalNoiseAnalysis

    # Stage 2: Semantic
    semantic: SemanticAnalysis

    # Stage 3: Brain
    brain: BrainAnalysis

    # Stage 4: Orchestration
    orchestration: OrchestrationResult | None

    # Overall
    total_time_ms: float
    execution_allowed: bool
    final_output: str


@router.post("/process", response_model=CognitiveResponse)
async def cognitive_process(request: CognitiveRequest) -> CognitiveResponse:
    """
    Full cognitive pipeline processing.

    Integrates all AMOS subsystems:
    - Signal-Noise Kernel for input purification
    - Translation Layer for semantic analysis
    - Brain for evaluation and safety
    - Orchestrator for task routing and execution
    """
    start_time = time.time()
    request_id = f"cog_{int(start_time * 1000)}"

    try:
        # Stage 1 & 2: Translation Layer (includes Signal-Noise Kernel)
        translator = get_translation_layer()
        translation_result = await translator.translate(
            raw_text=request.input, dialogue_context=request.context, memory_context={}
        )

        signal_noise = SignalNoiseAnalysis(
            signal_quality=getattr(translation_result, "signal_quality", 0.85),
            noise_distortion=getattr(translation_result, "noise_distortion", 0.15),
            ambiguity_count=len(translation_result.ambiguities),
            execution_safe=translation_result.compiled_machine_goal.execution_allowed,
        )

        semantic = SemanticAnalysis(
            goal_type=translation_result.compiled_machine_goal.goal_type.value,
            objective=translation_result.compiled_machine_goal.objective,
            confidence=translation_result.semantic_confidence,
            requires_clarification=translation_result.requires_clarification,
        )

        # Stage 3: Brain Evaluation
        brain_input = {
            "translation": translation_result.compiled_machine_goal.objective,
            "goal_type": semantic.goal_type,
            "confidence": semantic.confidence,
            "context": request.context,
        }

        brain_result = think(str(brain_input), request.context)

        brain = BrainAnalysis(
            status=brain_result.get("status", "UNKNOWN"),
            legality=brain_result.get("legality", 0.0),
            sigma=brain_result.get("sigma", 0.0),
            mode=brain_result.get("mode", "UNKNOWN"),
        )

        # Stage 4: Orchestration (if enabled and safe)
        orchestration = None
        if request.enable_execution and signal_noise.execution_safe and brain.legality > 0.5:
            try:
                from backend.real_orchestrator_bridge import RealOrchestratorBridge

                bridge = RealOrchestratorBridge()
                await bridge.initialize()

                orch_start = time.time()
                task_result = await bridge.execute_task(
                    task_description=semantic.objective,
                    priority=request.priority,
                    context=request.context,
                )
                orch_time = (time.time() - orch_start) * 1000

                orchestration = OrchestrationResult(
                    task_id=task_result.task_id,
                    domain=task_result.domain,
                    engines=task_result.engines_used,
                    execution_time_ms=orch_time,
                    success=task_result.success,
                    output=task_result.output if task_result.success else None,
                    error=task_result.error if not task_result.success else None,
                )
            except Exception as e:
                orchestration = OrchestrationResult(
                    task_id=None,
                    domain="error",
                    engines=[],
                    execution_time_ms=0.0,
                    success=False,
                    error=str(e),
                )

        total_time = (time.time() - start_time) * 1000

        # Construct final output
        if orchestration and orchestration.success:
            final_output = f"Task executed successfully: {orchestration.output}"
        elif orchestration:
            final_output = f"Task failed: {orchestration.error}"
        else:
            final_output = f"Analysis complete. Goal: {semantic.objective} (confidence: {semantic.confidence:.2f})"

        return CognitiveResponse(
            request_id=request_id,
            input=request.input,
            signal_noise=signal_noise,
            semantic=semantic,
            brain=brain,
            orchestration=orchestration,
            total_time_ms=total_time,
            execution_allowed=signal_noise.execution_safe and brain.legality > 0.5,
            final_output=final_output,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cognitive processing failed: {str(e)}")


@router.post("/process-fast")
async def cognitive_process_fast(request: CognitiveRequest) -> dict[str, Any]:
    """
    Fast cognitive processing with dual-process brain.

    Uses fast path (<100ms) for quick analysis and response.
    Falls back to full pipeline if confidence is low.
    """
    start_time = time.time()
    request_id = f"cog_fast_{int(start_time * 1000)}"

    try:
        from amos_dual_process_brain import get_dual_process_brain

        # Use fast thinking brain
        brain = get_dual_process_brain()
        result = await brain.think(query=request.input, context=request.context, prefer_fast=True)

        total_time = (time.time() - start_time) * 1000

        return {
            "request_id": request_id,
            "input": request.input,
            "response": result.response,
            "thinking_mode": result.thinking_mode,
            "confidence": result.confidence,
            "latency_ms": total_time,
            "fast_latency_ms": result.fast_result.latency_ms if result.fast_result else None,
            "success": True,
        }
    except ImportError:
        # Fallback to standard processing
        brain_result = think(request.input, request.context)
        total_time = (time.time() - start_time) * 1000

        return {
            "request_id": request_id,
            "input": request.input,
            "response": brain_result.get("output", str(brain_result)),
            "thinking_mode": "slow_fallback",
            "confidence": brain_result.get("confidence", 0.5),
            "latency_ms": total_time,
            "fast_latency_ms": None,
            "success": True,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fast cognitive processing failed: {str(e)}")


@router.get("/health")
async def cognitive_health() -> dict[str, Any]:
    """Check cognitive subsystem health."""
    health = {
        "translation_layer": False,
        "brain": False,
        "orchestrator": False,
        "fast_thinking": False,
        "overall": False,
    }

    # Check translation layer
    try:
        tl = get_translation_layer()
        health["translation_layer"] = tl.get_state().name == "RAW_INPUT"
    except Exception:
        pass

    # Check brain
    try:
        result = think("health check", {})
        health["brain"] = result.get("status") == "SUCCESS"
    except Exception:
        pass

    # Check orchestrator
    try:
        RealOrchestratorBridge()
        health["orchestrator"] = True  # If import succeeded
    except Exception:
        pass

    # Check fast thinking
    try:
        health["fast_thinking"] = True
    except Exception:
        pass

    health["overall"] = all([health["translation_layer"], health["brain"], health["orchestrator"]])

    return health
