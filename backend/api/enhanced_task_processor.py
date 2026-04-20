from __future__ import annotations

from typing import Any, Optional

"""Enhanced Task Processor with AMOS Brain Integration.

Processes tasks using AMOS cognitive architecture for intelligent
routing, execution, and error recovery.
"""

import asyncio
import sys
import time
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field

UTC = timezone.utc

# Setup paths for brain imports
AMOS_ROOT = Path(__file__).parent.parent.parent.resolve()
for p in [AMOS_ROOT, AMOS_ROOT / "clawspring", AMOS_ROOT / "clawspring" / "amos_brain"]:
    if str(p) not in sys.path:

router = APIRouter(prefix="/api/v1/enhanced-tasks", tags=["Enhanced Tasks"])

#Lazy imports for brain components
_brain_available: Optional[bool] = None
_kernel_class: Any = None


def _check_brain() -> bool:
    """Check if brain is available."""
    global _brain_available, _kernel_class
    if _brain_available is not None:
        return _brain_available

    try:
        from amos_kernel_runtime import AMOSKernelRuntime  # noqa: E402

        _kernel_class = AMOSKernelRuntime
        _brain_available = True
        return True
    except ImportError:
        _brain_available = False
        return False


# ============================================================================
# Task Models
# ============================================================================


class TaskType(str, Enum):
    """Types of tasks the processor can handle."""

    CODE_ANALYSIS = "code_analysis"
    EQUATION_EXECUTION = "equation_execution"
    DOCUMENT_PROCESSING = "document_processing"
    DATA_TRANSFORMATION = "data_transformation"
    COGNITIVE_REASONING = "cognitive_reasoning"


class TaskPriority(int, Enum):
    """Task priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class TaskRequest(BaseModel):
    """Request to process a task."""

    task_type: TaskType
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    use_brain: bool = Field(default=True, description="Use AMOS brain for processing")
    timeout_seconds: float = Field(default=30.0, ge=1.0, le=300.0)
    context: dict[str, Any] = Field(default_factory=dict)


class TaskResult(BaseModel):
    """Result of task processing."""

    success: bool
    result: Any
    processing_time_ms: float
    brain_enhanced:bool
    cognitive_score: Optional[float] =None
    error_message: Optional[str] = None


class TaskResponse(BaseModel):
    """Response from task processing."""

    task_id: str
    status:str
    result: Optional[TaskResult] = None
    timestamp: str


# ============================================================================
# Task Processors
# ============================================================================


class BaseTaskProcessor:
    """Base class for task processors."""

    async def process(self, payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Process the task payload."""
        raise NotImplementedError


class CodeAnalysisProcessor(BaseTaskProcessor):
    """Analyze code using cognitive patterns."""

    async def process(self, payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        code = payload.get("code", "")
        language = payload.get("language", "python")

        # Basic metrics
        lines = code.split("\n")
        non_empty = [l for l in lines if l.strip()]

        analysis = {
            "total_lines": len(lines),
            "code_lines": len(non_empty),
            "blank_lines": len(lines) - len(non_empty),
            "language": language,
            "complexity_estimate": len(non_empty) / max(len(lines), 1),
            "suggestions": [],
        }

        # Add brain-enhanced suggestions if available
        if _check_brain():
            analysis["suggestions"].append("Use AMOS cognitive architecture for deeper analysis")

        return analysis


class EquationExecutionProcessor(BaseTaskProcessor):
    """Execute equations with error handling."""

    async def process(self, payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        equation_name = payload.get("equation", "")
        params = payload.get("parameters", {})

        # Try to find and execute equation
        try:
            # Look in unified registry

            from amos_unified_equation_registry import UnifiedEquationRegistry

            registry = UnifiedEquationRegistry()
            await registry.initialize()

            eq_func = registry.get_equation(equation_name)
            if eq_func:
                result = eq_func(**params)
                return {"equation": equation_name, "result": result, "status": "success"}
            else:
                return {"equation": equation_name, "error": "Not found", "status": "failed"}

        except Exception as e:
            return {"equation": equation_name, "error": str(e), "status": "error"}


class CognitiveReasoningProcessor(BaseTaskProcessor):
    """Use AMOS brain for cognitive reasoning tasks."""

    async def process(self, payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        if not _check_brain():
            return {"error": "AMOS Brain not available", "brain_enhanced": False}

        query = payload.get("query", "")
        goal = payload.get("goal", "reason")

        # Create kernel and execute cognitive cycle
        kernel = _kernel_class()

        try:
            result = await asyncio.wait_for(
                kernel.execute_cycle(
                    {"content": query, "source": "task_processor"}, {"type": goal}
                ),
                timeout=10.0,
            )

            return {
                "brain_enhanced": True,
                "status": result.get("status"),
                "legality": result.get("legality"),
                "sigma": result.get("sigma"),
                "branch": result.get("selected_branch"),
            }

        except TimeoutError:
            return {"error": "Cognitive processing timed out", "brain_enhanced": True}
        except Exception as e:
            return {"error": str(e), "brain_enhanced": True}


# ============================================================================
# Task Router
# ============================================================================

_PROCESSORS: dict[TaskType, BaseTaskProcessor] = {
    TaskType.CODE_ANALYSIS: CodeAnalysisProcessor(),
    TaskType.EQUATION_EXECUTION: EquationExecutionProcessor(),
    TaskType.COGNITIVE_REASONING: CognitiveReasoningProcessor(),
}


async def route_and_process(task: TaskRequest) -> TaskResult:
    """Route task to appropriate processor and execute."""
    start = time.perf_counter()

    # Get processor
    processor = _PROCESSORS.get(task.task_type)
    if not processor:
        elapsed = (time.perf_counter() - start) * 1000
        return TaskResult(
            success=False,
            result=None,
            processing_time_ms=elapsed,
            brain_enhanced=False,
            error_message=f"No processor for task type: {task.task_type}",
        )

    try:
        # Process with timeout
        result = await asyncio.wait_for(
            processor.process(task.payload, task.context), timeout=task.timeout_seconds
        )

        elapsed = (time.perf_counter() - start) * 1000

        return TaskResult(
            success=True,
            result=result,
            processing_time_ms=elapsed,
            brain_enhanced=task.use_brain and _check_brain(),
        )

    except TimeoutError:
        elapsed = (time.perf_counter() - start) * 1000
        return TaskResult(
            success=False,
            result=None,
            processing_time_ms=elapsed,
            brain_enhanced=False,
            error_message=f"Task timed out after {task.timeout_seconds}s",
        )

    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        return TaskResult(
            success=False,
            result=None,
            processing_time_ms=elapsed,
            brain_enhanced=False,
            error_message=f"{type(e).__name__}: {str(e)}",
        )


# ============================================================================
# API Endpoints
# ============================================================================


@router.post("/process", response_model=TaskResponse)
async def process_task(request: TaskRequest) -> TaskResponse:
    """Process a task with optional brain enhancement."""
    task_id = f"task-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"

    result = await route_and_process(request)

    return TaskResponse(
        task_id=task_id,
        status="completed" if result.success else "failed",
        result=result,
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.post("/process-async")
async def process_task_async(
    request: TaskRequest, background_tasks: BackgroundTasks
) -> dict[str, Any]:
    """Submit task for async processing."""
    task_id = f"async-task-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"

    # For async, just return immediately
    return {
        "task_id": task_id,
        "status": "queued",
        "task_type": request.task_type.value,
        "timestamp": datetime.now(UTC).isoformat(),
        "poll_endpoint": f"/api/v1/enhanced-tasks/status/{task_id}",
    }


@router.get("/status/{task_id}")
async def get_task_status(task_id: str) -> dict[str, Any]:
    """Get status of a task (placeholder for full implementation)."""
    return {
        "task_id": task_id,
        "status": "completed",  # In real impl, check task store
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/health")
async def task_processor_health() -> dict[str, Any]:
    """Check task processor health."""
    return {
        "status": "healthy",
        "brain_available": _check_brain(),
        "processors": list(p.value for p in _PROCESSORS.keys()),
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/types")
async def list_task_types() -> list[dict[str, Any]]:
    """List available task types."""
    return [
        {
            "type": t.value,
            "description": t.name.replace("_", " ").title(),
            "brain_enhanced": t == TaskType.COGNITIVE_REASONING,
        }
        for t in TaskType
    ]
