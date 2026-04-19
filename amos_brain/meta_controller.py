"""AMOS Brain Meta-Cognitive Controller - Self-directed orchestration."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List

from .laws import GlobalLaws
from .loader import get_brain
from .state_manager import get_state_manager
from .task_processor import BrainTaskProcessor


class TaskStatus(Enum):
    """Status of a sub-task in workflow."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class SubTask:
    """Individual sub-task in a workflow."""

    task_id: str
    description: str
    dependencies: List[str]
    status: TaskStatus
    created_at: str
    completed_at: str  = None
    result: Any = None
    law_violations: List[dict] = field(default_factory=list)
    retry_count: int = 0


@dataclass
class WorkflowPlan:
    """Planned workflow for achieving a goal."""

    plan_id: str
    goal: str
    domain: str
    subtasks: List[SubTask]
    created_at: str
    status: str = "active"
    current_step: int = 0


class MetaCognitiveController:
    """AMOS Brain Meta-Cognitive Controller.

    Provides self-directed cognitive orchestration:
    1. Goal decomposition into executable sub-tasks
    2. Dynamic workflow planning with rollback
    3. Quality monitoring with auto re-evaluation
    4. Strategy adaptation based on results
    5. Self-correction when laws violated
    """

    def __init__(self):
        self.brain = get_brain()
        self.processor = BrainTaskProcessor()
        self.laws = GlobalLaws()
        self.state_manager = get_state_manager()
        self._active_plans: Dict[str, WorkflowPlan] = {}
        self._max_retries = 3

    def orchestrate(
        self, goal: str, domain: str = "general", auto_execute: bool = False
    ) -> WorkflowPlan:
        """Orchestrate achievement of a complex goal.

        Args:
            goal: The high-level objective
            domain: Domain context
            auto_execute: Whether to auto-execute sub-tasks

        Returns:
            WorkflowPlan with decomposed sub-tasks
        """
        # Create workflow plan
        plan = self._create_plan(goal, domain)

        # Start state manager session
        session_id = self.state_manager.start_session(
            goal=goal,
            domain=domain,
            metadata={"plan_id": plan.plan_id, "auto_execute": auto_execute},
        )

        # Store plan
        self._active_plans[plan.plan_id] = plan

        if auto_execute:
            self._execute_workflow(plan.plan_id)

        return plan

    def _create_plan(self, goal: str, domain: str) -> WorkflowPlan:
        """Decompose goal into sub-tasks using brain reasoning."""
        # Process goal through brain to get reasoning structure
        result = self.processor.process(f"Decompose into steps: {goal}")

        # Generate sub-tasks based on reasoning chain
        subtasks = []

        # Use reasoning steps as basis for sub-tasks
        for i, step in enumerate(result.reasoning_steps[:5], 1):
            task_id = f"T{i:03d}"

            # Determine dependencies
            dependencies = []
            if i > 1:
                dependencies = [f"T{i - 1:03d}"]

            subtask = SubTask(
                task_id=task_id,
                description=step[:100] if len(step) > 100 else step,
                dependencies=dependencies,
                status=TaskStatus.PENDING,
                created_at=datetime.now().isoformat(),
            )
            subtasks.append(subtask)

        # Add final synthesis task
        subtasks.append(
            SubTask(
                task_id=f"T{len(subtasks) + 1:03d}",
                description=f"Synthesize results to achieve: {goal[:50]}...",
                dependencies=[t.task_id for t in subtasks],
                status=TaskStatus.PENDING,
                created_at=datetime.now().isoformat(),
            )
        )

        plan = WorkflowPlan(
            plan_id=f"PLAN-{uuid.uuid4().hex[:8].upper()}",
            goal=goal,
            domain=domain,
            subtasks=subtasks,
            created_at=datetime.now().isoformat(),
        )

        return plan

    def _execute_workflow(self, plan_id: str) -> dict:
        """Execute workflow plan with monitoring."""
        plan = self._active_plans.get(plan_id)
        if not plan:
            return {"error": "Plan not found"}

        results = {"plan_id": plan_id, "completed": 0, "failed": 0, "retried": 0, "steps": []}

        for i, subtask in enumerate(plan.subtasks):
            plan.current_step = i

            # Check if dependencies satisfied
            deps_satisfied = all(
                self._get_task_status(plan_id, dep) == TaskStatus.COMPLETED
                for dep in subtask.dependencies
            )

            if not deps_satisfied:
                subtask.status = TaskStatus.BLOCKED
                results["steps"].append(
                    {
                        "task_id": subtask.task_id,
                        "status": "blocked",
                        "reason": "Dependencies not satisfied",
                    }
                )
                continue

            # Execute sub-task with law validation
            subtask.status = TaskStatus.IN_PROGRESS

            task_result = None
            while True:
                task_result = self.processor.process(subtask.description)

                if not task_result.law_violations:
                    subtask.law_violations = []
                    subtask.status = TaskStatus.COMPLETED
                    subtask.completed_at = datetime.now().isoformat()
                    subtask.result = task_result.output[:200]
                    results["completed"] += 1
                    break

                subtask.law_violations = task_result.law_violations

                if subtask.retry_count >= self._max_retries:
                    subtask.status = TaskStatus.FAILED
                    results["failed"] += 1
                    break

                subtask.retry_count += 1
                results["retried"] += 1
                subtask.description = f"[Retry {subtask.retry_count}] {subtask.description}"
                subtask.status = TaskStatus.IN_PROGRESS

            # Record in state manager
            self.state_manager.record_reasoning_step(
                description=subtask.description,
                perspective="Meta-Cognitive Orchestration",
                law_compliance={
                    "L1": not any(v["law"] == "L1" for v in subtask.law_violations),
                    "L2": not any(v["law"] == "L2" for v in subtask.law_violations),
                    "L3": not any(v["law"] == "L3" for v in subtask.law_violations),
                    "L4": not any(v["law"] == "L4" for v in subtask.law_violations),
                    "L5": not any(v["law"] == "L5" for v in subtask.law_violations),
                    "L6": not any(v["law"] == "L6" for v in subtask.law_violations),
                },
                kernel_activations=task_result.kernels_used,
                input_context={
                    "task": subtask.description,
                    "plan_id": plan_id,
                    "quadrants_checked": task_result.rule_of_four_check.get(
                        "quadrants_checked", []
                    ),
                },
                output_result=subtask.result or "Failed",
                confidence=task_result.confidence,
            )

            results["steps"].append(
                {
                    "task_id": subtask.task_id,
                    "status": subtask.status.value,
                    "retries": subtask.retry_count,
                    "violations": len(subtask.law_violations),
                }
            )

        # Set terminal plan status
        if all(t.status == TaskStatus.COMPLETED for t in plan.subtasks):
            plan.status = "completed"
        elif any(t.status == TaskStatus.FAILED for t in plan.subtasks):
            plan.status = "failed"
        else:
            plan.status = "active"

        # Close state session
        self.state_manager.close_session()

        return results

    def _get_task_status(self, plan_id: str, task_id: str) -> TaskStatus:
        """Get status of a sub-task."""
        plan = self._active_plans.get(plan_id)
        if not plan:
            return TaskStatus.FAILED

        for subtask in plan.subtasks:
            if subtask.task_id == task_id:
                return subtask.status

        return TaskStatus.FAILED

    def get_plan_status(self, plan_id: str) -> dict:
        """Get current status of a workflow plan."""
        plan = self._active_plans.get(plan_id)
        if not plan:
            return {"error": "Plan not found"}

        total = len(plan.subtasks)
        completed = sum(1 for t in plan.subtasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in plan.subtasks if t.status == TaskStatus.FAILED)
        blocked = sum(1 for t in plan.subtasks if t.status == TaskStatus.BLOCKED)
        in_progress = sum(1 for t in plan.subtasks if t.status == TaskStatus.IN_PROGRESS)

        return {
            "plan_id": plan_id,
            "goal": plan.goal,
            "progress": f"{completed}/{total}",
            "percentage": (completed / total * 100) if total > 0 else 0,
            "completed": completed,
            "failed": failed,
            "blocked": blocked,
            "in_progress": in_progress,
            "current_step": plan.current_step,
            "subtasks": [
                {
                    "id": t.task_id,
                    "description": t.description[:50],
                    "status": t.status.value,
                    "retries": t.retry_count,
                }
                for t in plan.subtasks
            ],
        }

    def adapt_strategy(self, plan_id: str, failed_task_id: str) -> Optional[SubTask]:
        """Adapt strategy when a task fails.

        Returns:
            New sub-task with alternative approach, or None
        """
        plan = self._active_plans.get(plan_id)
        if not plan:
            return None

        # Find failed task
        failed_task = None
        for subtask in plan.subtasks:
            if subtask.task_id == failed_task_id:
                failed_task = subtask
                break

        if not failed_task:
            return None

        # Create alternative approach
        alt_task = SubTask(
            task_id=f"{failed_task_id}-ALT",
            description=f"Alternative approach: {failed_task.description}",
            dependencies=failed_task.dependencies,
            status=TaskStatus.PENDING,
            created_at=datetime.now().isoformat(),
        )

        # Insert after failed task
        failed_index = plan.subtasks.index(failed_task)
        plan.subtasks.insert(failed_index + 1, alt_task)

        return alt_task

    def get_execution_summary(self) -> dict:
        """Get summary of all orchestrated workflows."""
        total_plans = len(self._active_plans)
        completed_plans = sum(1 for p in self._active_plans.values() if p.status == "completed")

        return {
            "total_plans": total_plans,
            "completed_plans": completed_plans,
            "active_plans": [
                {
                    "plan_id": p.plan_id,
                    "goal": p.goal[:50],
                    "status": self.get_plan_status(p.plan_id),
                }
                for p in list(self._active_plans.values())[:5]
            ],
        }


def orchestrate_goal(
    goal: str, domain: str = "general", auto_execute: bool = False
) -> WorkflowPlan:
    """Convenience function to orchestrate a goal."""
    controller = MetaCognitiveController()
    return controller.orchestrate(goal, domain, auto_execute)


@lru_cache(maxsize=1)
def get_meta_controller() -> MetaCognitiveController:
    """Get or create global meta-cognitive controller (singleton)."""
    return MetaCognitiveController()
