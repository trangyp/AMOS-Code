"""AMOS Brain Task Queue - Async task processing system.

Provides background task execution for brain operations with
proper queue management and result storage.
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc


from enum import Enum
from typing import Any


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BrainTask:
    """A brain task to be executed."""

    id: str
    type: str
    payload: dict[str, Any]
    status: TaskStatus = field(default=TaskStatus.PENDING)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: str = None
    completed_at: str = None
    result: Any = None
    error: str = None


class BrainTaskQueue:
    """Async task queue for brain operations."""

    def __init__(self, max_workers: int = 4) -> None:
        self.max_workers = max_workers
        self._queue: asyncio.Queue[BrainTask] = asyncio.Queue()
        self._tasks: dict[str, BrainTask] = {}
        self._workers: list[asyncio.Task] = []
        self._running = False
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        """Start the task queue workers."""
        if self._running:
            return

        self._running = True
        for _ in range(self.max_workers):
            worker = asyncio.create_task(self._worker_loop())
            self._workers.append(worker)

    async def stop(self) -> None:
        """Stop the task queue workers."""
        self._running = False

        # Cancel all workers
        for worker in self._workers:
            worker.cancel()

        # Wait for workers to finish
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()

    async def submit(
        self,
        task_type: str,
        payload: dict[str, Any],
        processor: Callable[[dict[str, Any]], Any] = None,
    ) -> str:
        """Submit a task to the queue.

        Args:
            task_type: Type of task (think, validate, decide)
            payload: Task parameters
            processor: Optional custom processor function

        Returns:
            Task ID for tracking
        """
        task_id = f"bt_{uuid.uuid4().hex[:12]}"
        task = BrainTask(id=task_id, type=task_type, payload=payload, processor=processor)

        async with self._lock:
            self._tasks[task_id] = task

        await self._queue.put(task)
        return task_id

    async def get_status(self, task_id: str) -> BrainTask:
        """Get task status by ID."""
        async with self._lock:
            return self._tasks.get(task_id)

    async def _worker_loop(self) -> None:
        """Worker loop that processes tasks."""
        while self._running:
            try:
                task = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self._process_task(task)
            except TimeoutError:
                continue
            except Exception as e:
                print(f"[TaskQueue] Worker error: {e}")

    async def _process_task(self, task: BrainTask) -> None:
        """Process a single task."""
        from .facade import BrainClient

        # Update status
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(timezone.utc).isoformat()

        try:
            client = BrainClient()

            if task.type == "think":
                query = task.payload.get("query", "")
                domain = task.payload.get("domain", "general")
                response = client.think(query, domain=domain)
                task.result = {
                    "content": response.content,
                    "confidence": response.confidence,
                    "law_compliant": response.law_compliant,
                }
            elif task.type == "validate":
                query = task.payload.get("query", "")
                # Use the client's validation
                decision = client.decide(query, [])
                task.result = {"valid": decision.confidence > 0.5}
            else:
                task.result = {"message": f"Unknown task type: {task.type}"}

            task.status = TaskStatus.COMPLETED

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)

        task.completed_at = datetime.now(timezone.utc).isoformat()


# Global queue instance
_queue_instance: BrainTaskQueue = None


async def get_task_queue() -> BrainTaskQueue:
    """Get or create global task queue."""
    global _queue_instance
    if _queue_instance is None:
        _queue_instance = BrainTaskQueue()
        await _queue_instance.start()
    return _queue_instance


async def submit_task(task_type: str, payload: dict[str, Any]) -> str:
    """Submit a task to the global queue."""
    queue = await get_task_queue()
    return await queue.submit(task_type, payload)


async def get_task_status(task_id: str) -> BrainTask:
    """Get task status from global queue."""
    queue = await get_task_queue()
    return await queue.get_status(task_id)
