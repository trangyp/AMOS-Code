"""AMOS Workflow API - Saga Pattern Workflow Orchestration with Brain

Production-ready workflow endpoints with durable execution,
compensation management, event sourcing, and brain validation.

Owner: Trang Phan
Version: 2.1.0
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.auth import User, get_current_user

# Brain integration
try:
    from amos_kernel_runtime import AMOSKernelRuntime  # noqa: E402

    BRAIN_AVAILABLE = True
except ImportError:
    BRAIN_AVAILABLE = False


from backend.workflow import (
    ActivityStatus,
    WorkflowInstance,
    WorkflowService,
    WorkflowStatus,
    workflow_service,
)

router = APIRouter(prefix="/workflow", tags=["workflow"])


class WorkflowCreateRequest(BaseModel):
    """Request to create a new workflow."""

    workflow_type: str = Field(..., description="Type of workflow to execute")
    input_data: dict[str, Any] = Field(default_factory=dict, description="Initial workflow input")
    correlation_id: str = Field(None, description="External correlation ID")


class WorkflowResponse(BaseModel):
    """Workflow status response."""

    workflow_id: str
    workflow_type: str
    status: str
    created_at: float
    updated_at: float
    progress_percent: int
    activity_count: int
    completed_activities: int
    failed_activities: int
    compensating_activities: int
    result: dict[str, Any] = None
    error: str = None


class ActivityResponse(BaseModel):
    """Activity status response."""

    activity_id: str
    name: str
    status: str
    started_at: float = None
    completed_at: float = None
    retry_count: int
    error: str = None
    result_preview: dict[str, Any] = None


class WorkflowListResponse(BaseModel):
    """List of workflows response."""

    workflows: list[WorkflowResponse]
    total: int
    by_status: dict[str, int]


class CompensationRequest(BaseModel):
    """Request to trigger compensation."""

    reason: str = Field(..., description="Reason for compensation")


class CompensationResponse(BaseModel):
    """Compensation result."""

    workflow_id: str
    compensation_status: str
    compensated_activities: list[str]
    failed_compensations: list[dict[str, Any]]


def get_workflow_service() -> WorkflowService:
    """Dependency injection for workflow service."""
    return workflow_service


@router.post("/start", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def start_new_workflow(
    request: WorkflowCreateRequest,
    service: WorkflowService = Depends(get_workflow_service),
    current_user: User = Depends(get_current_user),
) -> WorkflowResponse:
    """Start a new workflow execution.

    Creates a durable workflow instance with saga pattern support.
    """
    try:
        workflow_id = await service.start_workflow(
            workflow_type=request.workflow_type,
            input_data=request.input_data,
            correlation_id=request.correlation_id,
        )

        instance = service.get_workflow(workflow_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Workflow created but instance not found",
            )

        return _instance_to_response(instance)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start workflow: {str(e)}",
        )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_status(
    workflow_id: str,
    service: WorkflowService = Depends(get_workflow_service),
    current_user: User = Depends(get_current_user),
) -> WorkflowResponse:
    """Get workflow status by ID."""
    instance = service.get_workflow(workflow_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow {workflow_id} not found"
        )

    return _instance_to_response(instance)


@router.get("/{workflow_id}/activities", response_model=list[ActivityResponse])
async def get_workflow_activities(
    workflow_id: str,
    service: WorkflowService = Depends(get_workflow_service),
    current_user: User = Depends(get_current_user),
) -> list[ActivityResponse]:
    """Get all activities for a workflow."""
    instance = service.get_workflow(workflow_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow {workflow_id} not found"
        )

    return [
        ActivityResponse(
            activity_id=act.activity_id,
            name=act.name,
            status=act.status.value,
            started_at=act.started_at,
            completed_at=act.completed_at,
            retry_count=act.retry_count,
            error=act.error,
            result_preview=_preview_result(act.result),
        )
        for act in instance.activities
    ]


@router.post("/{workflow_id}/compensate", response_model=CompensationResponse)
async def compensate_workflow(
    workflow_id: str,
    request: CompensationRequest,
    service: WorkflowService = Depends(get_workflow_service),
    current_user: User = Depends(get_current_user),
) -> CompensationResponse:
    """Trigger compensation for a workflow.

    Rolls back completed activities in reverse order.
    """
    instance = service.get_workflow(workflow_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow {workflow_id} not found"
        )

    if instance.status not in [WorkflowStatus.FAILED, WorkflowStatus.COMPLETED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot compensate workflow in {instance.status.value} status",
        )

    try:
        result = await service.compensate_saga(instance)
        return CompensationResponse(
            workflow_id=workflow_id,
            compensation_status="completed" if result else "failed",
            compensated_activities=[
                act.activity_id for act in instance.activities if act.compensated
            ],
            failed_compensations=[],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compensation failed: {str(e)}",
        )


@router.get("/", response_model=WorkflowListResponse)
async def list_workflows(
    status_filter: WorkflowStatus = None,
    limit: int = 100,
    service: WorkflowService = Depends(get_workflow_service),
) -> WorkflowListResponse:
    """List all workflows with optional filtering."""
    workflows = service.list_workflows(status=status_filter, limit=limit)

    by_status: dict[str, int] = {}
    for wf in workflows:
        s = wf.status.value
        by_status[s] = by_status.get(s, 0) + 1

    return WorkflowListResponse(
        workflows=[_instance_to_response(wf) for wf in workflows],
        total=len(workflows),
        by_status=by_status,
    )


@router.post("/{workflow_id}/pause")
async def pause_workflow(
    workflow_id: str, service: WorkflowService = Depends(get_workflow_service)
) -> dict[str, Any]:
    """Pause a running workflow."""
    instance = service.get_workflow(workflow_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow {workflow_id} not found"
        )

    success = await service.pause_workflow(workflow_id)
    return {"workflow_id": workflow_id, "paused": success}


@router.post("/{workflow_id}/resume")
async def resume_workflow(
    workflow_id: str, service: WorkflowService = Depends(get_workflow_service)
) -> dict[str, Any]:
    """Resume a paused workflow."""
    instance = service.get_workflow(workflow_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Workflow {workflow_id} not found"
        )

    success = await service.resume_workflow(workflow_id)
    return {"workflow_id": workflow_id, "resumed": success}


def _instance_to_response(instance: WorkflowInstance) -> WorkflowResponse:
    """Convert workflow instance to API response."""
    completed = sum(1 for a in instance.activities if a.status == ActivityStatus.COMPLETED)
    failed = sum(1 for a in instance.activities if a.status == ActivityStatus.FAILED)
    compensating = sum(1 for a in instance.activities if a.compensating)

    total = len(instance.activities)
    progress = int(completed / total * 100) if total > 0 else 0

    return WorkflowResponse(
        workflow_id=instance.workflow_id,
        workflow_type=instance.workflow_type,
        status=instance.status.value,
        created_at=instance.created_at,
        updated_at=instance.updated_at,
        progress_percent=progress,
        activity_count=total,
        completed_activities=completed,
        failed_activities=failed,
        compensating_activities=compensating,
        result=instance.result,
        error=instance.error,
    )


def _preview_result(result: Any) -> dict[str, Any]:
    """Create a preview of result data (truncate large data)."""
    if result is None:
        return None
    if isinstance(result, dict):
        preview = {}
        for k, v in result.items():
            if isinstance(v, (str, bytes)) and len(str(v)) > 100:
                preview[k] = str(v)[:100] + "..."
            else:
                preview[k] = v
        return preview
    return {"value": str(result)[:100]}
