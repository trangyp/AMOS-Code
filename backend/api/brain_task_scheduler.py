"""AMOS Brain-Powered Task Scheduler

Intelligent task scheduling with brain analysis for priority,
dependencies, and optimal execution timing.

Creator: Trang Phan
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import heapq
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

UTC = UTC

# Import BrainClient facade
try:
    from clawspring.agents.amos_brain.facade import BrainClient
    from clawspring.agents.amos_brain.master_orchestrator import MasterOrchestrator

    _BRAIN_AVAILABLE = True
except ImportError:
    _BRAIN_AVAILABLE = False

router = APIRouter(prefix="/api/v1/brain/scheduler", tags=["Brain Task Scheduler"])


class TaskScheduleRequest(BaseModel):
    """Request to schedule a task."""

    task: str
    priority: int = Field(default=5, ge=1, le=10)
    context: dict[str, Any] = Field(default_factory=dict)
    dependencies: list[str] = Field(default_factory=list)
    deadline: Optional[str] = None
    use_brain_optimization: bool = True


class ScheduledTask(BaseModel):
    """A scheduled task with brain analysis."""

    task_id: str
    task: str
    priority: int
    scheduled_time: str
    estimated_duration_ms: int
    brain_confidence: float
    recommended_parallel: bool
    resource_requirements: dict[str, Any]
    execution_order: int


class TaskExecutionResult(BaseModel):
    """Result of executing a scheduled task."""

    task_id: str
    status: str
    result: dict[str, Any]
    execution_time_ms: float
    started_at: str
    completed_at: str


@dataclass(order=True)
class PrioritizedTask:
    """Task with priority for heap queue."""

    priority_score: float
    scheduled_time: float = field(compare=False)
    task_id: str = field(compare=False)
    task: str = field(compare=False)
    original_priority: int = field(compare=False)
    context: dict[str, Any] = field(compare=False, default_factory=dict)
    dependencies: list[str] = field(compare=False, default_factory=list)
    brain_analysis: dict[str, Any] = field(compare=False, default_factory=dict)


class BrainTaskScheduler:
    """Brain-powered intelligent task scheduler."""

    def __init__(self):
        self._task_queue: list[PrioritizedTask] = []
        self._completed_tasks: dict[str, TaskExecutionResult] = {}
        self._running_tasks: set[str] = set()
        self._lock = asyncio.Lock()
        self._execution_order = 0

    async def schedule_task(
        self,
        request: TaskScheduleRequest,
    ) -> ScheduledTask:
        """Schedule a task with brain optimization."""
        task_id = str(uuid4())
        scheduled_time = datetime.now(UTC)

        brain_confidence = 0.8
        estimated_duration_ms = 1000
        recommended_parallel = True
        resource_requirements: dict[str, Any] = {"cpu": "low", "memory": "low"}

        if _BRAIN_AVAILABLE and request.use_brain_optimization:
            try:
                client = BrainClient()

                # Brain analysis for scheduling optimization
                analysis = await client.think(
                    thought=f"Optimize scheduling for task: {request.task}",
                    context={
                        "task": request.task,
                        "priority": request.priority,
                        "dependencies": request.dependencies,
                        "deadline": request.deadline,
                        "analysis_type": "scheduling",
                    },
                )

                brain_confidence = analysis.get("confidence", 0.8)
                estimated_duration_ms = analysis.get("estimated_duration_ms", 1000)
                recommended_parallel = analysis.get("recommended_parallel", True)
                resource_requirements = analysis.get("resources", {"cpu": "low", "memory": "low"})

            except Exception:
                pass

        # Calculate priority score (lower = higher priority for heapq)
        priority_score = 10 - request.priority
        if brain_confidence > 0.9:
            priority_score -= 1  # Boost high-confidence tasks

        async with self._lock:
            self._execution_order += 1
            current_order = self._execution_order

        # Create prioritized task
        prioritized = PrioritizedTask(
            priority_score=float(priority_score),
            scheduled_time=scheduled_time.timestamp(),
            task_id=task_id,
            task=request.task,
            original_priority=request.priority,
            context=request.context,
            dependencies=request.dependencies,
            brain_analysis={
                "confidence": brain_confidence,
                "estimated_duration_ms": estimated_duration_ms,
            },
        )

        # Add to queue
        async with self._lock:
            heapq.heappush(self._task_queue, prioritized)

        return ScheduledTask(
            task_id=task_id,
            task=request.task,
            priority=request.priority,
            scheduled_time=scheduled_time.isoformat(),
            estimated_duration_ms=estimated_duration_ms,
            brain_confidence=brain_confidence,
            recommended_parallel=recommended_parallel,
            resource_requirements=resource_requirements,
            execution_order=current_order,
        )

    async def schedule_batch(
        self,
        requests: list[TaskScheduleRequest],
    ) -> list[ScheduledTask]:
        """Schedule multiple tasks with brain-optimized ordering."""
        scheduled = []
        for request in requests:
            task = await self.schedule_task(request)
            scheduled.append(task)

        # If brain available, re-optimize batch
        if _BRAIN_AVAILABLE and len(requests) > 1:
            try:
                client = BrainClient()

                task_list = [
                    {"id": s.task_id, "task": s.task, "priority": s.priority} for s in scheduled
                ]
                batch_analysis = await client.think(
                    thought="Optimize batch task execution order",
                    context={
                        "tasks": task_list,
                        "analysis_type": "batch_scheduling",
                    },
                )

                # Get optimized order from brain
                optimized_order = batch_analysis.get("optimized_order", [])
                if optimized_order:
                    # Reorder based on brain recommendation
                    order_map = {task_id: idx for idx, task_id in enumerate(optimized_order)}
                    scheduled.sort(key=lambda s: order_map.get(s.task_id, s.execution_order))

            except Exception:
                pass

        return scheduled

    async def execute_next(self) -> Optional[TaskExecutionResult]:
        """Execute the next task in the queue."""
        async with self._lock:
            if not self._task_queue:
                return None

            # Get next task
            next_task = heapq.heappop(self._task_queue)

            # Check dependencies
            pending_deps = [d for d in next_task.dependencies if d not in self._completed_tasks]
            if pending_deps:
                # Put back in queue if dependencies not ready
                heapq.heappush(self._task_queue, next_task)
                return None

            self._running_tasks.add(next_task.task_id)

        # Execute task
        start_time = time.time()
        started_at = datetime.now(UTC)

        try:
            if _BRAIN_AVAILABLE:
                client = BrainClient()
                orchestrator = MasterOrchestrator()

                # Brain evaluation before execution
                eval_result = await client.think(
                    thought=f"Execute scheduled task: {next_task.task}",
                    context=next_task.context,
                    use_legality=True,
                )

                if eval_result.get("legality_score", 1.0) < 0.5:
                    raise ValueError("Task failed legality check")

                # Execute via orchestrator
                exec_result = await orchestrator.orchestrate_cognitive_task(
                    task_type="scheduled_task",
                    inputs={
                        "task": next_task.task,
                        "context": next_task.context,
                        **next_task.context,
                    },
                )

                result = {
                    "status": "completed",
                    "brain_evaluation": eval_result,
                    "orchestration": exec_result,
                }
            else:
                result = {"status": "completed", "message": "Executed without brain"}

            execution_time_ms = (time.time() - start_time) * 1000

            exec_result = TaskExecutionResult(
                task_id=next_task.task_id,
                status="completed",
                result=result,
                execution_time_ms=execution_time_ms,
                started_at=started_at.isoformat(),
                completed_at=datetime.now(UTC).isoformat(),
            )

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            exec_result = TaskExecutionResult(
                task_id=next_task.task_id,
                status="failed",
                result={"error": str(e)},
                execution_time_ms=execution_time_ms,
                started_at=started_at.isoformat(),
                completed_at=datetime.now(UTC).isoformat(),
            )

        finally:
            async with self._lock:
                self._running_tasks.discard(next_task.task_id)
                self._completed_tasks[next_task.task_id] = exec_result

        return exec_result

    def get_queue_status(self) -> dict[str, Any]:
        """Get current queue status."""
        return {
            "queued_tasks": len(self._task_queue),
            "running_tasks": len(self._running_tasks),
            "completed_tasks": len(self._completed_tasks),
            "brain_available": _BRAIN_AVAILABLE,
        }

    def get_result(self, task_id: str) -> Optional[TaskExecutionResult]:
        """Get execution result for a task."""
        return self._completed_tasks.get(task_id)


# Global scheduler instance
scheduler = BrainTaskScheduler()


@router.post("/schedule", response_model=ScheduledTask)
async def schedule_task_endpoint(request: TaskScheduleRequest) -> ScheduledTask:
    """Schedule a single task with brain optimization."""
    return await scheduler.schedule_task(request)


@router.post("/schedule-batch")
async def schedule_batch_endpoint(requests: list[TaskScheduleRequest]) -> list[ScheduledTask]:
    """Schedule multiple tasks with batch optimization."""
    return await scheduler.schedule_batch(requests)


@router.post("/execute-next")
async def execute_next_task() -> TaskExecutionResult | dict[str, str]:
    """Execute the next task in the queue."""
    result = await scheduler.execute_next()
    if result is None:
        return {"status": "no_tasks_available"}
    return result


@router.get("/queue-status")
async def get_queue_status() -> dict[str, Any]:
    """Get current queue status."""
    return scheduler.get_queue_status()


@router.get("/result/{task_id}")
async def get_task_result(task_id: str) -> TaskExecutionResult:
    """Get execution result for a task."""
    result = scheduler.get_result(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Task result not found")
    return result
