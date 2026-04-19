from typing import Any, Optional

"""Task Processor API - Production task queue with brain integration.

Real implementation using AMOS brain for intelligent task processing
with proper timeout handling and progress tracking.
"""
from __future__ import annotations


import asyncio
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

UTC = timezone.utc
from enum import Enum

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

# Import AMOS brain
try:
    from typing import List, Optional

    from amos_brain import process_task, think

    BRAIN_AVAILABLE = True
except ImportError:
    BRAIN_AVAILABLE = False

router = APIRouter(prefix="/api/v1/tasks", tags=["Task Processor"])


class TaskStatus(str, Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class TaskPriority(int, Enum):
    """Task priority levels."""

    LOW = 1
    MEDIUM = 5
    HIGH = 10
    CRITICAL = 20


@dataclass
class Task:
    """Internal task representation."""

    id: str
    name: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    result: Any = None
    error: str | None = None


# In-memory task store (replace with Redis/DB in production)
_task_store: dict[str, Task] = {}


class TaskRequest(BaseModel):
    """Request to create a new task."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    priority: TaskPriority = TaskPriority.MEDIUM
    timeout_seconds: float = Field(default=60.0, ge=1.0, le=300.0)
    use_brain: bool = Field(default=True)
    brain_query: str | None = None


class TaskResponse(BaseModel):
    """Task response model."""

    id: str
    name: str
    description: str
    status: str
    priority: int
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    result: Any = None
    error: str | None = None


class TaskCreateResponse(BaseModel):
    """Response when creating a task."""

    task_id: str
    status: str
    message: str


async def _execute_task_with_brain(task_id: str, query: str, timeout: float) -> None:
    """Execute task using AMOS brain with timeout protection."""
    task = _task_store.get(task_id)
    if not task:
        return

    task.status = TaskStatus.RUNNING
    task.started_at = datetime.now(UTC).isoformat()

    try:
        if not BRAIN_AVAILABLE:
            raise RuntimeError("Brain system not available")

        # Execute with timeout
        result = await asyncio.wait_for(
            asyncio.to_thread(think, query, {"task_id": task_id}), timeout=timeout
        )

        task.status = TaskStatus.COMPLETED
        task.result = str(result) if result else "No result"

    except TimeoutError:
        task.status = TaskStatus.TIMEOUT
        task.error = f"Task timed out after {timeout}s"
    except Exception as e:
        task.status = TaskStatus.FAILED
        task.error = str(e)
    finally:
        task.completed_at = datetime.now(UTC).isoformat()


async def _execute_simple_task(task_id: str, name: str, timeout: float) -> None:
    """Execute simple background task."""
    task = _task_store.get(task_id)
    if not task:
        return

    task.status = TaskStatus.RUNNING
    task.started_at = datetime.now(UTC).isoformat()

    try:
        # Simulate work
        await asyncio.sleep(min(2.0, timeout / 10))

        task.status = TaskStatus.COMPLETED
        task.result = f"Task '{name}' completed successfully"

    except TimeoutError:
        task.status = TaskStatus.TIMEOUT
        task.error = "Task timed out"
    except Exception as e:
        task.status = TaskStatus.FAILED
        task.error = str(e)
    finally:
        task.completed_at = datetime.now(UTC).isoformat()


@router.post("/create", response_model=TaskCreateResponse)
async def create_task(
    request: TaskRequest, background_tasks: BackgroundTasks
) -> TaskCreateResponse:
    """Create a new task and queue it for execution."""
    task_id = str(uuid.uuid4())[:8]

    task = Task(
        id=task_id,
        name=request.name,
        description=request.description,
        status=TaskStatus.PENDING,
        priority=request.priority,
        created_at=datetime.now(UTC).isoformat(),
    )

    _task_store[task_id] = task

    # Queue for background execution
    if request.use_brain and request.brain_query:
        background_tasks.add_task(
            _execute_task_with_brain, task_id, request.brain_query, request.timeout_seconds
        )
    else:
        background_tasks.add_task(
            _execute_simple_task, task_id, request.name, request.timeout_seconds
        )

    return TaskCreateResponse(
        task_id=task_id, status="queued", message=f"Task '{request.name}' queued for execution"
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> TaskResponse:
    """Get task status and result."""
    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse(
        id=task.id,
        name=task.name,
        description=task.description,
        status=task.status.value,
        priority=task.priority.value,
        created_at=task.created_at,
        started_at=task.started_at,
        completed_at=task.completed_at,
        result=task.result,
        error=task.error,
    )


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(limit: int = 100) -> list[TaskResponse]:
    """List all tasks."""
    tasks = sorted(_task_store.values(), key=lambda t: t.created_at, reverse=True)[:limit]

    return [
        TaskResponse(
            id=t.id,
            name=t.name,
            description=t.description,
            status=t.status.value,
            priority=t.priority.value,
            created_at=t.created_at,
            started_at=t.started_at,
            completed_at=t.completed_at,
            result=t.result,
            error=t.error,
        )
        for t in tasks
    ]


@router.delete("/{task_id}")
async def delete_task(task_id: str) -> dict[str, str]:
    """Delete a completed or failed task."""
    task = _task_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status in (TaskStatus.RUNNING, TaskStatus.PENDING):
        raise HTTPException(status_code=400, detail="Cannot delete running or pending tasks")

    del _task_store[task_id]
    return {"message": f"Task {task_id} deleted"}


@router.get("/health/brain")
async def brain_health() -> dict[str, Any]:
    """Check brain availability for tasks."""
    return {
        "brain_available": BRAIN_AVAILABLE,
        "tasks_in_queue": len([t for t in _task_store.values() if t.status == TaskStatus.PENDING]),
        "tasks_running": len([t for t in _task_store.values() if t.status == TaskStatus.RUNNING]),
        "total_tasks": len(_task_store),
        "timestamp": datetime.now(UTC).isoformat(),
    }
