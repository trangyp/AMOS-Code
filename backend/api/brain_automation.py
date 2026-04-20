#!/usr/bin/env python3
"""AMOS Brain Automation API - FastAPI router for brain task automation.

Following FastAPI best practices 2024:
- Async routes for I/O operations
- Pydantic v2 models for validation
- Dependency injection
- Modular service layer
"""

from __future__ import annotations

from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC


from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_serializer

# Import brain automation service
from amos_brain_task_automation import (
    AutomationResult,
    BrainTaskAutomator,
)

router = APIRouter(prefix="/brain-automation", tags=["brain-automation"])


# ============================================================================
# Pydantic Schemas (Following Best Practice: Excessive Pydantic usage)
# ============================================================================


class AutomationStepSchema(BaseModel):
    """Schema for automation step."""

    step_number: int
    description: str
    action_type: str
    status: str
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


class AutomationRequest(BaseModel):
    """Request for task automation.

    Uses Pydantic v2 features for validation.
    """

    request: str = Field(
        min_length=5,
        max_length=10000,
        description="Natural language task description",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional context data for the task",
    )


class AutomationResponse(BaseModel):
    """Response from task automation.

    Custom datetime serialization following best practices.
    """

    task_id: str
    original_request: str
    steps: list[AutomationStepSchema]
    final_output: str
    success: bool
    execution_time_ms: float
    timestamp: datetime

    @field_serializer("timestamp")
    def serialize_timestamp(self, value: datetime) -> str:
        """Serialize datetime to ISO format with timezone."""
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.isoformat()

    model_config = {"from_attributes": True}


class BatchAutomationRequest(BaseModel):
    """Request for batch automation."""

    requests: list[str] = Field(
        min_length=1,
        max_length=10,
        description="List of tasks to automate",
    )
    context: dict[str, Any] = Field(default_factory=dict)


class BatchAutomationResponse(BaseModel):
    """Response for batch automation."""

    results: list[AutomationResponse]
    total_success: int
    total_failed: int
    total_time_ms: float


class AutomationHistoryResponse(BaseModel):
    """Response for automation history."""

    history: list[AutomationResponse]
    total_count: int


# ============================================================================
# Dependencies (Following Best Practice: Chain Dependencies)
# ============================================================================


def get_brain_automator() -> BrainTaskAutomator:
    """Dependency to get brain automator instance.

    Following FastAPI best practice of dependency injection.
    """
    return BrainTaskAutomator()


# ============================================================================
# API Routes (Following Best Practice: Async Routes)
# ============================================================================


@router.post(
    "/automate",
    response_model=AutomationResponse,
    status_code=status.HTTP_200_OK,
    summary="Automate a complex task",
    description="""
    Automates a complex multi-step task using AMOS brain guidance.

    The task is:
    1. Analyzed by the brain
    2. Broken into executable steps
    3. Executed with brain guidance
    4. Results synthesized

    Example:
    ```json
    {
        "request": "Analyze and summarize Python dataclasses best practices",
        "context": {"detail_level": "high"}
    }
    ```
    """,
)
async def automate_task_endpoint(
    request: AutomationRequest,
    automator: BrainTaskAutomator = Depends(get_brain_automator),
) -> AutomationResponse:
    """Automate a single task through the brain."""
    try:
        result = automator.automate(request.request, request.context)
        return _convert_to_response(result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Automation failed: {str(e)}",
        )


@router.post(
    "/automate/batch",
    response_model=BatchAutomationResponse,
    status_code=status.HTTP_200_OK,
    summary="Automate multiple tasks",
    description="Automate multiple tasks concurrently with brain guidance.",
)
async def automate_batch_endpoint(
    request: BatchAutomationRequest,
    automator: BrainTaskAutomator = Depends(get_brain_automator),
) -> BatchAutomationResponse:
    """Automate multiple tasks in batch."""
    import time

    start_time = time.time()
    results: list[AutomationResponse] = []

    for req in request.requests:
        try:
            result = automator.automate(req, request.context)
            results.append(_convert_to_response(result))
        except Exception as e:
            # Create failed result
            results.append(
                AutomationResponse(
                    task_id="error",
                    original_request=req,
                    steps=[],
                    final_output=f"Error: {e}",
                    success=False,
                    execution_time_ms=0.0,
                    timestamp=datetime.now(UTC),
                )
            )

    total_time = (time.time() - start_time) * 1000

    return BatchAutomationResponse(
        results=results,
        total_success=sum(1 for r in results if r.success),
        total_failed=sum(1 for r in results if not r.success),
        total_time_ms=total_time,
    )


@router.get(
    "/history",
    response_model=AutomationHistoryResponse,
    summary="Get automation history",
    description="Retrieve history of all automation runs.",
)
async def get_automation_history(
    automator: BrainTaskAutomator = Depends(get_brain_automator),
) -> AutomationHistoryResponse:
    """Get automation history."""
    history = automator.get_history()
    return AutomationHistoryResponse(
        history=[_convert_to_response(h) for h in history],
        total_count=len(history),
    )


@router.get(
    "/health",
    summary="Brain automation health check",
    description="Check if brain automation service is operational.",
)
async def brain_automation_health() -> dict[str, Any]:
    """Health check endpoint."""
    try:
        automator = BrainTaskAutomator()
        # Quick test
        test_result = automator.automate("Health check test", {})
        return {
            "status": "healthy",
            "operational": test_result.success,
            "brain_connected": True,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "operational": False,
            "brain_connected": False,
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }


# ============================================================================
# Utility Functions
# ============================================================================


def _convert_to_response(result: AutomationResult) -> AutomationResponse:
    """Convert AutomationResult to AutomationResponse schema."""
    return AutomationResponse(
        task_id=result.task_id,
        original_request=result.original_request,
        steps=[
            AutomationStepSchema(
                step_number=s.step_number,
                description=s.description,
                action_type=s.action_type,
                status=s.status,
                error_message=s.error_message,
            )
            for s in result.steps
        ],
        final_output=result.final_output,
        success=result.success,
        execution_time_ms=result.execution_time_ms,
        timestamp=datetime.now(UTC),
    )


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    "router",
    "AutomationRequest",
    "AutomationResponse",
    "BatchAutomationRequest",
    "BatchAutomationResponse",
    "get_brain_automator",
]
