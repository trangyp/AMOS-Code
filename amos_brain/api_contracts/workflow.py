"""Workflow execution API contracts."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import Field

from amos_brain.api_contracts.base import BaseAMOSModel


class WorkflowStatus(str, Enum):
    """Status of a workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskResult(BaseAMOSModel):
    """Result from a single task execution."""
    
    task_id: str = Field(..., description="Task identifier")
    task_type: str = Field(..., description="Type of task")
    status: str = Field(
        ...,
        description="Task status: success, failed, skipped"
    )
    output: Any = Field(None, description="Task output")
    error: Optional[str] = Field(None, description="Error message if failed")
    started_at: datetime = Field(..., description="When task started")
    completed_at: Optional[datetime] = Field(
        None,
        description="When task completed"
    )
    execution_time_ms: Optional[int] = Field(
        None,
        ge=0,
        description="Execution time"
    )


class WorkflowRunRequest(BaseAMOSModel):
    """Request to run a workflow.
    
    Example:
        {
            "workflow_id": "repo_analysis",
            "inputs": {
                "repo_path": "/path/to/repo",
                "scan_types": ["style", "security"]
            },
            "session_id": "sess_123"
        }
    """
    
    workflow_id: str = Field(..., description="Workflow identifier")
    inputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Workflow inputs"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session for tracking"
    )
    workspace_id: Optional[str] = Field(
        None,
        description="Workspace context"
    )
    synchronous: bool = Field(
        default=True,
        description="Whether to wait for completion"
    )
    timeout_seconds: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum execution time"
    )


class WorkflowRunResponse(BaseAMOSModel):
    """Response from workflow execution.
    
    Example:
        {
            "run_id": "run_abc123",
            "workflow_id": "repo_analysis",
            "status": "completed",
            "tasks": [...],
            "output": {...}
        }
    """
    
    run_id: str = Field(..., description="Unique run identifier")
    workflow_id: str = Field(..., description="Workflow identifier")
    status: WorkflowStatus = Field(..., description="Current status")
    tasks: list[TaskResult] = Field(
        default_factory=list,
        description="Task execution results"
    )
    output: Any = Field(None, description="Workflow output")
    error: Optional[str] = Field(
        None,
        description="Error message if failed"
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When run started"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="When run completed"
    )
    execution_time_ms: Optional[int] = Field(
        None,
        ge=0,
        description="Total execution time"
    )
    logs: list[str] = Field(
        default_factory=list,
        description="Execution logs"
    )
