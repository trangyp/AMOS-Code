"""Workflow Engine — Orchestrate multi-step workflows.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional


class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """A single step in a workflow."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    action: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: str = ""
    start_time: str = ""
    end_time: str = ""
    depends_on: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "status": self.status.value}


@dataclass
class Workflow:
    """A workflow definition."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    steps: list[WorkflowStep] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "draft"  # draft, running, completed, failed
    context: dict[str, Any] = field(default_factory=dict)

    def add_step(
        self,
        name: str,
        action: str,
        params: dict[str, Any] = None,
        depends_on: list[str] = None,
    ) -> WorkflowStep:
        """Add a step to the workflow."""
        step = WorkflowStep(
            name=name,
            action=action,
            params=params or {},
            depends_on=depends_on or [],
        )
        self.steps.append(step)
        return step

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "steps": [s.to_dict() for s in self.steps],
        }


class WorkflowEngine:
    """Orchestrate multi-step workflows with dependency management."""

    WORKFLOW_DIR = Path(__file__).parent / "workflows"

    def __init__(self):
        self._workflows: dict[str, Workflow] = {}
        self._handlers: dict[str, Callable] = {}
        self.WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)

    def register_handler(self, action: str, handler: Callable):
        """Register a handler for an action type."""
        self._handlers[action] = handler

    def create_workflow(self, name: str, description: str = "") -> Workflow:
        """Create a new workflow."""
        workflow = Workflow(name=name, description=description)
        self._workflows[workflow.id] = workflow
        return workflow

    def run_workflow(self, workflow_id: str) -> Workflow:
        """Execute a workflow."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow.status = "running"
        completed = set()

        for step in workflow.steps:
            # Check dependencies
            if step.depends_on and not all(d in completed for d in step.depends_on):
                step.status = StepStatus.SKIPPED
                step.error = "Dependencies not met"
                continue

            # Run step
            step.start_time = datetime.utcnow().isoformat()
            step.status = StepStatus.RUNNING

            handler = self._handlers.get(step.action)
            if not handler:
                step.status = StepStatus.FAILED
                step.error = f"No handler for action: {step.action}"
            else:
                try:
                    step.result = handler(step.params, workflow.context)
                    step.status = StepStatus.SUCCESS
                    completed.add(step.id)
                except Exception as e:
                    step.status = StepStatus.FAILED
                    step.error = str(e)

            step.end_time = datetime.utcnow().isoformat()

        # Update workflow status
        failed = [s for s in workflow.steps if s.status == StepStatus.FAILED]
        workflow.status = "failed" if failed else "completed"

        # Save
        self._save_workflow(workflow)
        return workflow

    def _save_workflow(self, workflow: Workflow):
        """Persist workflow."""
        filepath = self.WORKFLOW_DIR / f"{workflow.id}.json"
        filepath.write_text(json.dumps(workflow.to_dict(), indent=2))

    def load_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Load workflow from disk."""
        filepath = self.WORKFLOW_DIR / f"{workflow_id}.json"
        if not filepath.exists():
            return None
        data = json.loads(filepath.read_text())
        # Reconstruct workflow (simplified)
        workflow = Workflow(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            created_at=data["created_at"],
            status=data["status"],
            context=data.get("context", {}),
        )
        for s in data.get("steps", []):
            step = WorkflowStep(
                id=s["id"],
                name=s["name"],
                action=s["action"],
                params=s.get("params", {}),
                status=StepStatus(s["status"]),
                result=s.get("result"),
                error=s.get("error", ""),
                start_time=s.get("start_time", ""),
                end_time=s.get("end_time", ""),
                depends_on=s.get("depends_on", []),
            )
            workflow.steps.append(step)
        self._workflows[workflow_id] = workflow
        return workflow

    def list_workflows(self) -> list[Workflow]:
        """List all workflows."""
        return list(self._workflows.values())
