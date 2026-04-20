"""
AMOS Agents API

REST API endpoints for agent task management.
Create, monitor, and control background agent tasks.

Creator: Trang Phan
Version: 3.0.0
"""

import uuid
from datetime import datetime, timezone
UTC = timezone.utc, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException

UTC = UTC

from .schemas import AgentTaskRequest, AgentTaskResponse, TaskListResponse

try:
    from ..real_orchestrator_bridge import get_real_orchestrator_bridge
except ImportError:
    get_real_orchestrator_bridge = None

router = APIRouter()

# In-memory task store (replace with Redis/database in production)
_task_store: dict = {}


def _create_task(task_id: str, request: AgentTaskRequest) -> AgentTaskResponse:
    """Create a new task record."""
    now = datetime.now(timezone.utc)
    return AgentTaskResponse(
        id=task_id,
        name=request.name,
        description=request.description,
        status="pending",
        progress=0,
        agent_type=request.agent_type,
        priority=request.priority,
        created_at=now,
        updated_at=now,
    )


async def _execute_task_real(task_id: str):
    """Execute a background task using real AMOS orchestrator."""
    if task_id not in _task_store:
        return

    task = _task_store[task_id]
    task["status"] = "running"
    task["updated_at"] = datetime.now(timezone.utc)

    # Get real orchestrator bridge
    bridge = get_real_orchestrator_bridge()
    await bridge.initialize()

    # Execute through real orchestrator
    result = await bridge.execute_task(
        task_description=task.get("description", ""),
        priority=task.get("priority", "MEDIUM"),
        context={"task_id": task_id, "name": task.get("name")},
    )

    # Update task with real results
    task["status"] = "completed" if result.success else "failed"
    task["result"] = {
        "output": result.output,
        "error": result.error,
        "domain": result.domain,
        "engines_used": result.engines_used,
        "duration_ms": result.duration_ms,
    }
    task["progress"] = 100
    task["updated_at"] = datetime.now(timezone.utc)


@router.post("/tasks", response_model=AgentTaskResponse)
async def create_task(request: AgentTaskRequest, background_tasks: BackgroundTasks):
    """Create a new agent task and queue it for execution."""
    task_id = str(uuid.uuid4())
    task = _create_task(task_id, request)

    # Store task
    _task_store[task_id] = task.model_dump()

    # Queue for background execution via real orchestrator
    background_tasks.add_task(_execute_task_real, task_id)

    return task


@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(status: str = None, agent_type: str = None, limit: int = 50):
    """List agent tasks with optional filtering."""
    tasks = list(_task_store.values())

    if status:
        tasks = [t for t in tasks if t["status"] == status]

    if agent_type:
        tasks = [t for t in tasks if t["agent_type"] == agent_type]

    # Sort by created_at desc
    tasks.sort(key=lambda x: x["created_at"], reverse=True)
    tasks = tasks[:limit]

    return TaskListResponse(
        tasks=[AgentTaskResponse(**t) for t in tasks],
        total=len(_task_store),
        running=len([t for t in _task_store.values() if t["status"] == "running"]),
        pending=len([t for t in _task_store.values() if t["status"] == "pending"]),
    )


@router.get("/tasks/{task_id}", response_model=AgentTaskResponse)
async def get_task(task_id: str):
    """Get detailed information about a specific task."""
    if task_id not in _task_store:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return AgentTaskResponse(**_task_store[task_id])


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancel a pending or running task."""
    if task_id not in _task_store:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    task = _task_store[task_id]
    if task["status"] not in ("pending", "running"):
        raise HTTPException(
            status_code=400, detail=f"Cannot cancel task with status {task['status']}"
        )

    task["status"] = "failed"
    task["error"] = "Cancelled by user"
    task["updated_at"] = datetime.now(timezone.utc)

    return {"message": f"Task {task_id} cancelled"}


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a completed or failed task."""
    if task_id not in _task_store:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    task = _task_store[task_id]
    if task["status"] in ("pending", "running"):
        raise HTTPException(status_code=400, detail="Cannot delete active task")

    del _task_store[task_id]
    return {"message": f"Task {task_id} deleted"}
