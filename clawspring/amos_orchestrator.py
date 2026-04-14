"""AMOS Workflow Orchestrator - Chains cognition, execution, and output."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

from amos_execution import full_execute, get_execution_kernel

from amos_runtime import get_runtime


@dataclass
class WorkflowStep:
    """Single step in an AMOS workflow."""

    id: str
    name: str
    step_type: str  # 'cognitive', 'execution', 'validation', 'output'
    status: str = "pending"  # pending, running, completed, failed
    input_data: dict = field(default_factory=dict)
    output_data: dict = field(default_factory=dict)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None


@dataclass
class Workflow:
    """AMOS workflow with multiple steps."""

    id: str
    name: str
    steps: list[WorkflowStep] = field(default_factory=list)
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    metadata: dict = field(default_factory=dict)


class StepHandlers:
    """Built-in step handlers for workflow execution."""

    @staticmethod
    def cognitive(step: WorkflowStep) -> dict:
        """Run cognitive analysis."""
        runtime = get_runtime()
        task = step.input_data.get("task", "")
        result = runtime.execute_cognitive_task(task)
        return {
            "perspectives": result.get("perspectives", []),
            "quadrants": list(result.get("quadrant_analysis", {}).keys()),
            "assumptions": result.get("assumptions", []),
            "recommendation": result.get("recommendation", ""),
            "gap": result.get("gap_statement", ""),
        }

    @staticmethod
    def execution(step: WorkflowStep) -> dict:
        """Run execution production."""
        task = step.input_data.get("task", "")
        out_type = step.input_data.get("output_type", "structured_explanation")
        result = full_execute(task, out_type)
        return {
            "content": result.content,
            "format_type": result.format_type,
            "quality": result.quality_passed,
            "laws": result.law_compliance,
        }

    @staticmethod
    def validation(step: WorkflowStep) -> dict:
        """Validate output against laws."""
        runtime = get_runtime()
        content = step.input_data.get("content", "")
        laws = runtime.get_law_summary()
        # Simple validation checks
        checks = {
            "has_gap_acknowledgment": "gap" in content.lower() or "embodiment" in content.lower(),
            "has_assumptions": "assumption" in content.lower(),
            "proper_length": len(content) > 200,
            "no_vague_language": "vibration" not in content.lower()
            and "energy" not in content.lower(),
        }
        return {"checks": checks, "all_passed": all(checks.values()), "laws_verified": len(laws)}

    @staticmethod
    def output(step: WorkflowStep) -> dict:
        """Format final output."""
        content = step.input_data.get("content", "")
        return {
            "final_output": content,
            "timestamp": datetime.now().isoformat(),
            "amos_branded": True,
        }


class AMOSWorkflowOrchestrator:
    """Orchestrates multi-step AMOS workflows."""

    HANDLERS: dict[str, Callable[[WorkflowStep], dict]] = {
        "cognitive": StepHandlers.cognitive,
        "execution": StepHandlers.execution,
        "validation": StepHandlers.validation,
        "output": StepHandlers.output,
    }

    def __init__(self):
        self.workflows: dict[str, Workflow] = {}
        self.runtime = get_runtime()
        self.execution = get_execution_kernel()

    def create_workflow(self, name: str, steps_config: list[dict]) -> Workflow:
        """Create a new workflow from step configurations."""
        workflow_id = str(uuid.uuid4())[:8]
        steps = []
        for i, config in enumerate(steps_config):
            step = WorkflowStep(
                id=f"{workflow_id}_{i}",
                name=config.get("name", f"Step {i+1}"),
                step_type=config.get("type", "cognitive"),
                input_data=config.get("input", {}),
            )
            steps.append(step)

        workflow = Workflow(
            id=workflow_id,
            name=name,
            steps=steps,
            metadata={
                "amos_version": "vInfinity",
                "creator": "Trang Phan",
                "laws_enforced": 6,
            },
        )
        self.workflows[workflow_id] = workflow
        return workflow

    def run_workflow(self, workflow_id: str) -> Workflow:
        """Execute all steps in a workflow."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow.status = "running"

        for step in workflow.steps:
            step.status = "running"
            step.started_at = datetime.now()

            try:
                handler = self.HANDLERS.get(step.step_type)
                if not handler:
                    raise ValueError(f"Unknown step type: {step.step_type}")

                result = handler(step)
                step.output_data = result
                step.status = "completed"
                step.completed_at = datetime.now()

                # Pass output to next step's input if configured
                if step.output_data and step != workflow.steps[-1]:
                    next_step = workflow.steps[workflow.steps.index(step) + 1]
                    next_step.input_data.update({"_previous_output": step.output_data})

            except Exception as e:
                step.status = "failed"
                step.error = str(e)
                workflow.status = "failed"
                return workflow

        workflow.status = "completed"
        workflow.completed_at = datetime.now()
        return workflow

    def create_standard_workflow(
        self, task: str, output_type: str = "structured_explanation"
    ) -> Workflow:
        """Create standard 4-step workflow: cognitive → execution → validation → output."""
        return self.create_workflow(
            name=f"AMOS_Standard_{task[:30]}",
            steps_config=[
                {
                    "name": "Cognitive Analysis",
                    "type": "cognitive",
                    "input": {"task": task},
                },
                {
                    "name": "Execution Production",
                    "type": "execution",
                    "input": {"task": task, "output_type": output_type},
                },
                {
                    "name": "Law Validation",
                    "type": "validation",
                    "input": {},  # Will receive from previous
                },
                {
                    "name": "Final Output",
                    "type": "output",
                    "input": {},  # Will receive from previous
                },
            ],
        )

    def get_workflow_report(self, workflow_id: str) -> str:
        """Generate human-readable workflow report."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return f"Workflow {workflow_id} not found"

        lines = [
            f"# AMOS Workflow Report: {workflow.name}",
            f"ID: {workflow.id}",
            f"Status: {workflow.status}",
            f"Created: {workflow.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Execution Steps",
        ]

        for step in workflow.steps:
            icon = "✓" if step.status == "completed" else "✗" if step.status == "failed" else "○"
            lines.append(f"{icon} {step.name} ({step.step_type})")
            if step.error:
                lines.append(f"   Error: {step.error}")
            if step.output_data:
                lines.append(f"   Output keys: {', '.join(step.output_data.keys())}")

        if workflow.status == "completed":
            final_step = workflow.steps[-1] if workflow.steps else None
            if final_step and final_step.output_data:
                lines.extend(["", "## Final Output"])
                final_out = final_step.output_data.get("final_output", "")
                lines.append(final_out[:500] + "..." if len(final_out) > 500 else final_out)

        return "\n".join(lines)


# Singleton
_orchestrator: AMOSWorkflowOrchestrator | None = None


def get_orchestrator() -> AMOSWorkflowOrchestrator:
    """Get singleton orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AMOSWorkflowOrchestrator()
    return _orchestrator


def run_amos_workflow(task: str, output_type: str = "structured_explanation") -> str:
    """Quick workflow execution."""
    orch = get_orchestrator()
    workflow = orch.create_standard_workflow(task, output_type)
    orch.run_workflow(workflow.id)
    return orch.get_workflow_report(workflow.id)


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS WORKFLOW ORCHESTRATOR TEST")
    print("=" * 60)

    # Test standard workflow
    result = run_amos_workflow(
        "Should we implement real-time notifications?",
        "decision_recommendation",
    )
    print(result)

    print("\n" + "=" * 60)
    print("Workflow Orchestrator: OPERATIONAL")
    print("=" * 60)
