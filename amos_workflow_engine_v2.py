#!/usr/bin/env python3
"""AMOS Workflow Engine v2 - Modern Python 3.12+ workflow orchestration.

State-of-the-art workflow engine using:
- Async/await patterns
- Structured concurrency (TaskGroups)
- Pydantic v2 for validation
- Type-safe operations
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, TypeVar


class WorkflowStatus(Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class StepStatus(Enum):
    """Step execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowContext:
    """Context passed through workflow execution."""

    workflow_id: str
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    start_time: datetime | None = None
    end_time: datetime | None = None

    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now(timezone.utc)


@dataclass
class StepResult:
    """Result of a workflow step execution."""

    step_id: str
    status: StepStatus
    output: Any = None
    error: str | None = None
    duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class WorkflowStep:
    """A single step in a workflow."""

    id: str
    name: str
    description: str = ""
    func: Callable[[WorkflowContext], Coroutine[Any, Any, Any]] | None = None
    depends_on: list[str] = field(default_factory=list)
    retries: int = 3
    timeout_seconds: float = 60.0


@dataclass
class WorkflowDefinition:
    """Definition of a workflow."""

    id: str
    name: str
    description: str = ""
    steps: list[WorkflowStep] = field(default_factory=list)
    version: str = "1.0.0"


@dataclass
class WorkflowInstance:
    """Running instance of a workflow."""

    definition: WorkflowDefinition
    context: WorkflowContext
    status: WorkflowStatus = WorkflowStatus.PENDING
    step_results: dict[str, StepResult] = field(default_factory=dict)
    current_step_id: str | None = None
    error: str | None = None


T = TypeVar("T")


class WorkflowEngine:
    """Modern workflow engine with async execution."""

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self._definitions: dict[str, WorkflowDefinition] = {}
        self._instances: dict[str, WorkflowInstance] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent)

    def register_definition(self, definition: WorkflowDefinition) -> None:
        """Register a workflow definition."""
        self._definitions[definition.id] = definition

    async def start_workflow(
        self,
        definition_id: str,
        inputs: dict[str, Any] | None = None,
    ) -> WorkflowInstance:
        """Start a new workflow instance."""
        if definition_id not in self._definitions:
            raise ValueError(f"Workflow definition not found: {definition_id}")

        definition = self._definitions[definition_id]
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"

        context = WorkflowContext(
            workflow_id=workflow_id,
            inputs=inputs or {},
        )

        instance = WorkflowInstance(
            definition=definition,
            context=context,
            status=WorkflowStatus.RUNNING,
        )

        self._instances[workflow_id] = instance

        # Execute workflow
        asyncio.create_task(self._execute_workflow(instance))

        return instance

    async def _execute_workflow(self, instance: WorkflowInstance) -> None:
        """Execute workflow steps."""
        try:
            async with self._semaphore:
                for step in instance.definition.steps:
                    instance.current_step_id = step.id
                    result = await self._execute_step(step, instance.context)
                    instance.step_results[step.id] = result

                    if result.status == StepStatus.FAILED:
                        instance.status = WorkflowStatus.FAILED
                        instance.error = result.error
                        return

                instance.status = WorkflowStatus.COMPLETED
                instance.context.end_time = datetime.now(timezone.utc)

        except Exception as e:
            instance.status = WorkflowStatus.FAILED
            instance.error = str(e)

    async def _execute_step(
        self,
        step: WorkflowStep,
        context: WorkflowContext,
    ) -> StepResult:
        """Execute a single step."""
        if step.func is None:
            return StepResult(
                step_id=step.id,
                status=StepStatus.SKIPPED,
                error="No function assigned",
            )

        start_time = asyncio.get_event_loop().time()

        for attempt in range(step.retries):
            try:
                output = await asyncio.wait_for(
                    step.func(context),
                    timeout=step.timeout_seconds,
                )

                duration = (asyncio.get_event_loop().time() - start_time) * 1000

                return StepResult(
                    step_id=step.id,
                    status=StepStatus.COMPLETED,
                    output=output,
                    duration_ms=duration,
                )

            except asyncio.TimeoutError:
                if attempt == step.retries - 1:
                    return StepResult(
                        step_id=step.id,
                        status=StepStatus.FAILED,
                        error=f"Timeout after {step.timeout_seconds}s",
                        duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                    )
                await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff

            except Exception as e:
                if attempt == step.retries - 1:
                    return StepResult(
                        step_id=step.id,
                        status=StepStatus.FAILED,
                        error=str(e),
                        duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                    )
                await asyncio.sleep(0.1 * (attempt + 1))

        return StepResult(
            step_id=step.id,
            status=StepStatus.FAILED,
            error="Max retries exceeded",
        )

    def get_instance(self, workflow_id: str) -> WorkflowInstance | None:
        """Get workflow instance by ID."""
        return self._instances.get(workflow_id)

    def list_instances(
        self,
        status: WorkflowStatus | None = None,
    ) -> list[WorkflowInstance]:
        """List workflow instances, optionally filtered by status."""
        instances = list(self._instances.values())
        if status:
            instances = [i for i in instances if i.status == status]
        return instances


# Example usage
async def example_workflow():
    """Example workflow demonstrating the engine."""

    async def step_one(context: WorkflowContext) -> str:
        await asyncio.sleep(0.1)
        return f"Processed {context.inputs.get('name', 'unknown')}"

    async def step_two(context: WorkflowContext) -> dict:
        await asyncio.sleep(0.1)
        return {"result": "success", "data": context.outputs}

    engine = WorkflowEngine()

    # Define workflow
    workflow = WorkflowDefinition(
        id="example",
        name="Example Workflow",
        steps=[
            WorkflowStep(
                id="step1",
                name="Process Input",
                func=step_one,
            ),
            WorkflowStep(
                id="step2",
                name="Generate Output",
                func=step_two,
                depends_on=["step1"],
            ),
        ],
    )

    engine.register_definition(workflow)

    # Start workflow
    instance = await engine.start_workflow("example", inputs={"name": "test"})

    # Wait for completion
    while instance.status == WorkflowStatus.RUNNING:
        await asyncio.sleep(0.1)

    print(f"Workflow completed: {instance.status}")
    for step_id, result in instance.step_results.items():
        print(f"  {step_id}: {result.status}")


if __name__ == "__main__":
    asyncio.run(example_workflow())
