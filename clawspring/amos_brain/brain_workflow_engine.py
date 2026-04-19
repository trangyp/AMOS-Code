from typing import Any

"""AMOS Brain Workflow Engine - Workflow steps powered by brain.

Integrates workflow system with cognitive processing:
- Brain-powered task analysis per workflow step
- Cognitive routing for workflow decisions
- Real-time status via task queue

Owner: Trang Phan
"""
from __future__ import annotations


import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

try:
    from .api_integration import brain_get_result, brain_process_sync, brain_submit_task
except ImportError:
    from api_integration import brain_process_sync


@dataclass
class WorkflowStep:
    """Single workflow step with brain processing."""

    id: str
    name: str
    description: str
    status: str = "pending"
    brain_task_id: str | None = None
    result: dict[str, Any] = field(default_factory=dict)
    started_at: str | None = None
    completed_at: str | None = None


@dataclass
class WorkflowInstance:
    """Running workflow instance."""

    id: str
    name: str
    steps: list[WorkflowStep]
    current_step: int = 0
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str | None = None


class BrainWorkflowEngine:
    """Workflow engine using brain for cognitive step processing."""

    def __init__(self):
        self._workflows: dict[str, WorkflowInstance] = {}

    async def create_workflow(self, name: str, step_descriptions: list[str]) -> str:
        """Create new workflow with brain-powered steps."""
        workflow_id = f"wf-{uuid.uuid4().hex[:8]}"

        steps = [
            WorkflowStep(
                id=f"step-{i}-{uuid.uuid4().hex[:4]}",
                name=f"Step {i + 1}",
                description=desc,
            )
            for i, desc in enumerate(step_descriptions)
        ]

        workflow = WorkflowInstance(
            id=workflow_id,
            name=name,
            steps=steps,
        )

        self._workflows[workflow_id] = workflow
        return workflow_id

    async def execute_step(self, workflow_id: str, step_index: int) -> dict[str, Any]:
        """Execute single workflow step using brain."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}

        if step_index >= len(workflow.steps):
            return {"error": "Step index out of range"}

        step = workflow.steps[step_index]
        step.status = "running"
        step.started_at = datetime.now(timezone.utc).isoformat()

        # Process via brain
        result = await brain_process_sync(step.description, "HIGH")

        step.result = {
            "domain": result.get("domain"),
            "success": result.get("success"),
            "duration_ms": result.get("duration_ms"),
            "engines": result.get("engines_used", []),
        }
        step.status = "completed" if result.get("success") else "failed"
        step.completed_at = datetime.now(timezone.utc).isoformat()

        return step.result

    async def execute_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Execute all workflow steps sequentially."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}

        workflow.status = "running"
        results = []

        for i, step in enumerate(workflow.steps):
            workflow.current_step = i
            result = await self.execute_step(workflow_id, i)
            results.append(result)

            if not result.get("success"):
                workflow.status = "failed"
                return {
                    "workflow_id": workflow_id,
                    "status": "failed",
                    "failed_at_step": i,
                    "step_results": results,
                }

        workflow.status = "completed"
        workflow.completed_at = datetime.now(timezone.utc).isoformat()

        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "total_steps": len(workflow.steps),
            "step_results": results,
        }

    def get_workflow(self, workflow_id: str) -> WorkflowInstance | None:
        """Get workflow instance."""
        return self._workflows.get(workflow_id)

    def list_workflows(self) -> list[WorkflowInstance]:
        """List all workflows."""
        return list(self._workflows.values())


# Singleton
_engine: BrainWorkflowEngine | None = None


def get_workflow_engine() -> BrainWorkflowEngine:
    """Get or create singleton workflow engine."""
    global _engine
    if _engine is None:
        _engine = BrainWorkflowEngine()
    return _engine


async def create_brain_workflow(name: str, steps: list[str]) -> str:
    """Convenience function to create workflow."""
    engine = get_workflow_engine()
    return await engine.create_workflow(name, steps)


async def run_brain_workflow(workflow_id: str) -> dict[str, Any]:
    """Convenience function to run workflow."""
    engine = get_workflow_engine()
    return await engine.execute_workflow(workflow_id)


if __name__ == "__main__":

    async def main():
        print("=" * 60)
        print("AMOS BRAIN WORKFLOW ENGINE")
        print("=" * 60)

        # Create workflow
        steps = [
            "Analyze system requirements",
            "Design microservices architecture",
            "Create API specifications",
            "Implement authentication system",
        ]

        workflow_id = await create_brain_workflow("System Design", steps)
        print(f"\nCreated workflow: {workflow_id}")
        print(f"Steps: {len(steps)}")

        # Execute workflow
        print("\nExecuting workflow...")
        result = await run_brain_workflow(workflow_id)

        print(f"\nResult: {result['status']}")
        if result["status"] == "completed":
            print(f"Completed all {result['total_steps']} steps")
            for i, step_result in enumerate(result["step_results"]):
                domain = step_result.get("domain", "unknown")
                duration = step_result.get("duration_ms", 0)
                print(f"  Step {i + 1}: {domain} ({duration:.1f}ms)")
        else:
            print(f"Failed at step {result.get('failed_at_step')}")

        print("\n" + "=" * 60)

    asyncio.run(main())
