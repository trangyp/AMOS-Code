#!/usr/bin/env python3
"""AMOS Async Task Processor - Modern Python 3.12+ async task system.

Uses state-of-the-art patterns:
- Task groups (Python 3.11+)
- Exception groups
- Async generators
- Type hints with | None syntax
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents an async task."""

    id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    result: Any = None
    error: str | None = None


@dataclass
class TaskResult:
    """Result of task execution."""

    task_id: str
    success: bool
    result: Any = None
    error: str | None = None
    duration_ms: float = 0.0


class AsyncTaskProcessor:
    """Modern async task processor using Python 3.12+ features."""

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.tasks: dict[str, Task] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._shutdown = False

    async def submit(
        self,
        task_id: str,
        name: str,
        coro: Awaitable[Any],
    ) -> TaskResult:
        """Submit a task for execution."""
        task = Task(id=task_id, name=name)
        self.tasks[task_id] = task

        start_time = asyncio.get_event_loop().time()

        async with self._semaphore:
            if self._shutdown:
                task.status = TaskStatus.CANCELLED
                return TaskResult(
                    task_id=task_id,
                    success=False,
                    error="Processor shutdown",
                )

            task.status = TaskStatus.RUNNING
            try:
                result = await coro
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.completed_at = datetime.now(timezone.utc)

                return TaskResult(
                    task_id=task_id,
                    success=True,
                    result=result,
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                )
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task.completed_at = datetime.now(timezone.utc)

                return TaskResult(
                    task_id=task_id,
                    success=False,
                    error=str(e),
                    duration_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
                )

    async def submit_many(
        self,
        tasks: list[tuple[str, str, Awaitable[Any]]],
    ) -> AsyncGenerator[TaskResult, None]:
        """Submit multiple tasks and yield results as they complete."""
        async with asyncio.TaskGroup() as tg:
            task_map: dict[asyncio.Task, tuple[str, str]] = {}

            for task_id, name, coro in tasks:
                asyncio_task = tg.create_task(self.submit(task_id, name, coro))
                task_map[asyncio_task] = (task_id, name)

            # Yield results as they complete
            for asyncio_task in asyncio.as_completed(task_map.keys()):
                try:
                    result = await asyncio_task
                    yield result
                except Exception as e:
                    task_id, name = task_map.get(asyncio_task, ("unknown", "unknown"))
                    yield TaskResult(
                        task_id=task_id,
                        success=False,
                        error=str(e),
                    )

    async def shutdown(self):
        """Graceful shutdown."""
        self._shutdown = True
        # Wait for running tasks to complete
        await asyncio.sleep(0.1)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks."""
        return list(self.tasks.values())


async def example():
    """Example usage."""
    processor = AsyncTaskProcessor(max_concurrent=5)

    async def sample_task(name: str) -> str:
        await asyncio.sleep(0.1)
        return f"Result: {name}"

    # Submit single task
    result = await processor.submit("1", "test", sample_task("hello"))
    print(f"Task {result.task_id}: success={result.success}")

    # Submit multiple tasks
    tasks = [
        (f"task-{i}", f"Task {i}", sample_task(f"item {i}"))
        for i in range(5)
    ]

    async for result in processor.submit_many(tasks):
        print(f"Completed: {result.task_id} - {result.duration_ms:.2f}ms")

    await processor.shutdown()


if __name__ == "__main__":
    asyncio.run(example())
