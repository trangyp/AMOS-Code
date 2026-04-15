"""Workflow Engine stub for compatibility."""

from typing import Any, Callable


class Workflow:
    """Represents a workflow."""

    def __init__(self, name: str):
        self.name = name
        self.steps: list[dict[str, Any]] = []

    def add_step(self, func: Callable, args: dict[str, Any] | None = None) -> None:
        """Add step to workflow."""
        self.steps.append({"func": func, "args": args or {}})


class WorkflowEngine:
    """Engine for workflow execution."""

    def __init__(self):
        self.workflows: dict[str, Workflow] = {}

    def create_workflow(self, name: str) -> Workflow:
        """Create new workflow."""
        workflow = Workflow(name)
        self.workflows[name] = workflow
        return workflow

    def execute(self, workflow_name: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute workflow."""
        return {"status": "completed", "workflow": workflow_name}


__all__ = ["Workflow", "WorkflowEngine"]
