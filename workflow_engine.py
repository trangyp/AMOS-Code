"""
AMOS Workflow Engine - Production Implementation v2.0.0

Real saga-pattern workflow orchestration with:
- Durable execution
- Compensation management
- State machine workflows
- Event sourcing audit trails

Owner: Trang Phan
Version: 2.0.0
"""

from collections.abc import Callable
from typing import Any, Dict, List

try:
    from backend.workflow.workflow_service import (
        ActivityStatus,
        CompensationManager,
        SagaOrchestrator,
        WorkflowActivity,
        WorkflowInstance,
        WorkflowService,
        WorkflowStatus,
        compensate_activity,
        execute_activity,
        start_workflow,
        workflow_service,
    )
except ImportError:
    from backend.workflow import (
        ActivityStatus,
        CompensationManager,
        SagaOrchestrator,
        WorkflowActivity,
        WorkflowInstance,
        WorkflowService,
        WorkflowStatus,
        compensate_activity,
        execute_activity,
        start_workflow,
        workflow_service,
    )


# Backward compatibility classes
class Workflow:
    """Represents a workflow (backward compatible)."""

    def __init__(self, name: str):
        self.name = name
        self.steps: List[dict[str, Any]] = []
        self._activities: List[Any] = []

    def add_step(self, func: Callable, args: Dict[str, Any] = None) -> None:
        """Add step to workflow."""
        self.steps.append({"func": func, "args": args or {}})

        # Convert to new Activity format
        import asyncio
        import uuid

        async def wrapper(**kwargs: Any) -> Any:
            ctx: Dict[str, Any] = kwargs.pop("context", {})
            merged = {**(args or {}), **kwargs, **ctx}
            if asyncio.iscoroutinefunction(func):
                return await func(**merged)
            return func(**merged)

        self._activities.append(
            WorkflowActivity(
                activity_id=f"act_{uuid.uuid4().hex[:8]}",
                name=f"step_{len(self.steps)}",
                handler=wrapper,
                input_data=args or {},
            )
        )


class WorkflowEngine:
    """Engine for workflow execution (backward compatible)."""

    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self._service: Any = workflow_service

    def create_workflow(self, name: str) -> Workflow:
        """Create new workflow."""
        workflow = Workflow(name)
        self.workflows[name] = workflow
        return workflow

    async def execute(self, workflow_name: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute workflow."""

        workflow = self.workflows.get(workflow_name)
        if not workflow:
            return {"status": "error", "error": f"Workflow {workflow_name} not found"}

        # Register workflow definition
        if workflow._activities:
            self._service._workflow_definitions[workflow_name] = workflow._activities

        # Start via new service
        try:
            workflow_id = await self._service.start_workflow(
                workflow_type=workflow_name, input_data=context or {}
            )
            return {"status": "completed", "workflow": workflow_name, "workflow_id": workflow_id}
        except Exception as e:
            return {"status": "error", "error": str(e)}


__all__ = [
    # New implementation
    "WorkflowService",
    "WorkflowInstance",
    "WorkflowActivity",
    "SagaOrchestrator",
    "CompensationManager",
    "WorkflowStatus",
    "ActivityStatus",
    "start_workflow",
    "execute_activity",
    "compensate_activity",
    "workflow_service",
    # Backward compatibility
    "Workflow",
    "WorkflowEngine",
]
