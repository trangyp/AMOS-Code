"""AMOS Task Queue - Production task queue with brain integration.

Features:
- Async task queue with priority
- Brain-powered task analysis
- Real-time status tracking
- Result persistence

Owner: Trang Phan
"""

from __future__ import annotations


import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

try:
    from .cognitive_task_processor import TaskRequest, process_cognitive_task
except ImportError:
    from cognitive_task_processor import TaskRequest, process_cognitive_task


class TaskStatus(Enum):
    """Task status states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class QueuedTask:
    """Task in the queue."""

    id: str
    request: TaskRequest
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: str | None = None
    completed_at: str | None = None
    result: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class TaskQueue:
    """Production task queue with brain integration."""

    def __init__(self, max_workers: int = 3):
        self._queue: asyncio.Queue[QueuedTask] = asyncio.Queue()
        self._tasks: dict[str, QueuedTask] = {}
        self._max_workers = max_workers
        self._workers: list[asyncio.Task] = []
        self._running = False

    async def start(self) -> None:
        """Start queue workers."""
        self._running = True
        for i in range(self._max_workers):
            worker = asyncio.create_task(self._worker_loop(i))
            self._workers.append(worker)
        print(f"[TaskQueue] Started {self._max_workers} workers")

    async def stop(self) -> None:
        """Stop queue workers."""
        self._running = False
        for worker in self._workers:
            worker.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        print("[TaskQueue] Stopped")

    async def _worker_loop(self, worker_id: int) -> None:
        """Worker loop processing tasks."""
        while self._running:
            try:
                task = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self._process_task(task)
                self._queue.task_done()
            except TimeoutError:
                continue
            except Exception as e:
                print(f"[Worker {worker_id}] Error: {e}")

    async def _process_task(self, task: QueuedTask) -> None:
        """Process a single task using brain."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(timezone.utc).isoformat()

        try:
            # Run brain-powered processing
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: process_cognitive_task(task.request.description, task.request.priority),
            )

            task.result = {
                "success": response.success,
                "domain": response.domain,
                "engines": response.engines_used,
                "duration_ms": response.duration_ms,
            }
            task.status = TaskStatus.COMPLETED

        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED

        task.completed_at = datetime.now(timezone.utc).isoformat()

    async def submit(self, description: str, priority: str = "MEDIUM") -> str:
        """Submit a task to the queue."""
        task_id = f"queue-{uuid.uuid4().hex[:8]}"
        request = TaskRequest(description=description, priority=priority)
        task = QueuedTask(id=task_id, request=request)

        self._tasks[task_id] = task
        await self._queue.put(task)

        return task_id

    def get_status(self, task_id: str) -> QueuedTask | None:
        """Get task status."""
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[QueuedTask]:
        """List all tasks."""
        return list(self._tasks.values())


# Singleton
_queue_instance: TaskQueue | None = None


async def get_task_queue() -> TaskQueue:
    """Get or create singleton queue."""
    global _queue_instance
    if _queue_instance is None:
        _queue_instance = TaskQueue()
        await _queue_instance.start()
    return _queue_instance


async def submit_task(description: str, priority: str = "MEDIUM") -> str:
    """Convenience function to submit a task."""
    queue = await get_task_queue()
    return await queue.submit(description, priority)


async def get_task_status(task_id: str) -> QueuedTask | None:
    """Get task status."""
    queue = await get_task_queue()
    return queue.get_status(task_id)


if __name__ == "__main__":

    async def main():
        print("=" * 60)
        print("AMOS TASK QUEUE")
        print("=" * 60)

        queue = await get_task_queue()

        # Submit tasks
        tasks = [
            "Design authentication system",
            "Optimize database queries",
            "Create API documentation",
        ]

        task_ids = []
        for desc in tasks:
            tid = await submit_task(desc, "HIGH")
            task_ids.append(tid)
            print(f"Submitted: {tid} - {desc[:40]}...")

        # Wait for completion
        print("\nWaiting for tasks...")
        await asyncio.sleep(3)

        # Check results
        print("\nResults:")
        for tid in task_ids:
            task = await get_task_status(tid)
            if task:
                print(f"  {tid}: {task.status.value}")
                if task.result:
                    print(f"    Domain: {task.result.get('domain')}")
                    print(f"    Duration: {task.result.get('duration_ms', 0):.1f}ms")

        await queue.stop()
        print("\n" + "=" * 60)

    asyncio.run(main())
