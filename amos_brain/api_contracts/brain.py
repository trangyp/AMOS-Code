"""Brain execution API contracts for AMOS cognitive operations."""

from datetime import datetime, timezone
UTC = timezone.utc
from typing import Any, Optional

from pydantic import Field

from amos_brain.api_contracts.base import BaseAMOSModel


class StateGraphInput(BaseAMOSModel):
    """Input for brain state graph execution."""
    
    variables: dict[str, Any] = Field(
        default_factory=dict,
        description="State variables (Ω, K, Φ, I, S, etc)"
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Execution context"
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="Legality constraints to enforce"
    )
    goal: Optional[str] = Field(
        None,
        description="Target goal for branch generation"
    )


class BranchResult(BaseAMOSModel):
    """Result from a single branch generation."""
    
    branch_id: str = Field(..., description="Unique branch identifier")
    state_delta: dict[str, Any] = Field(
        ...,
        description="Changes to state variables"
    )
    metrics: dict[str, float] = Field(
        default_factory=dict,
        description="Branch metrics (goal_fit, risk, cost, etc)"
    )
    legality_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Legality assessment (L = I × S)"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in this branch"
    )


class MorphExecution(BaseAMOSModel):
    """Result from a morph execution."""
    
    morph_id: str = Field(..., description="Morph identifier")
    status: str = Field(
        ...,
        description="Execution status: pending, running, completed, failed, rolled_back"
    )
    changes: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Changes made by the morph"
    )
    verification_passed: Optional[bool] = Field(
        None,
        description="Whether verification passed"
    )
    rollback_available: bool = Field(
        default=True,
        description="Whether rollback is possible"
    )
    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When execution started"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="When execution completed"
    )
    execution_time_ms: Optional[int] = Field(
        None,
        ge=0,
        description="Execution time in milliseconds"
    )


class BrainRunRequest(BaseAMOSModel):
    """Request to run the AMOS brain.
    
    Example:
        {
            "input": {
                "variables": {"Ω": 0.8, "K": 0.9},
                "goal": "Optimize system performance"
            },
            "max_branches": 5,
            "collapse_strategy": "best",
            "session_id": "sess_123"
        }
    """
    
    input: StateGraphInput = Field(..., description="State graph input")
    max_branches: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum branches to generate"
    )
    collapse_strategy: str = Field(
        default="best",
        description="Branch selection strategy: best, diverse, safe"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session identifier for continuity"
    )
    workspace_id: Optional[str] = Field(
        None,
        description="Workspace context"
    )
    execute_morph: bool = Field(
        default=True,
        description="Whether to execute the selected morph"
    )


class BrainRunResponse(BaseAMOSModel):
    """Response from brain execution.
    
    Example:
        {
            "run_id": "run_xyz789",
            "status": "completed",
            "branches": [...],
            "selected_branch": {...},
            "morph": {...},
            "final_state": {...}
        }
    """
    
    run_id: str = Field(..., description="Unique run identifier")
    status: str = Field(
        ...,
        description="Run status: pending, running, completed, failed"
    )
    branches: list[BranchResult] = Field(
        default_factory=list,
        description="Generated branches"
    )
    selected_branch: Optional[BranchResult] = Field(
        None,
        description="Branch selected by collapse function"
    )
    morph: Optional[MorphExecution] = Field(
        None,
        description="Morph execution result"
    )
    final_state: Optional[dict[str, Any]] = Field(
        None,
        description="Final state after execution"
    )
    started_at: datetime = Field(..., description="When run started")
    completed_at: Optional[datetime] = Field(
        None,
        description="When run completed"
    )
    execution_time_ms: Optional[int] = Field(
        None,
        ge=0,
        description="Total execution time"
    )
    metrics: dict[str, Any] = Field(
        default_factory=dict,
        description="Execution metrics"
    )
