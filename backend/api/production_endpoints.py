"""AMOS Production API Endpoints

Implements state-of-art FastAPI patterns:
- Pydantic validation with CustomBaseModel
- Dependency injection for validation
- Async routes with proper error handling
- Structured logging

Based on: zhanymkanov/fastapi-best-practices (GitHub)
"""

from __future__ import annotations

import logging
import time
from datetime import UTC, datetime
from typing import Any, Optional, TypeVar
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer

UTC = UTC

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/prod", tags=["production"])

T = TypeVar("T")


class CustomBaseModel(BaseModel):
    """Custom base model with datetime serialization."""

    model_config = ConfigDict(populate_by_name=True)

    @field_serializer("*", when_used="json", check_fields=False)
    def _serialize_datetimes(self, value: Any) -> Any:
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=UTC)
            return value.isoformat()
        return value


class UserCreate(CustomBaseModel):
    """User creation with validation."""

    username: str = Field(min_length=3, max_length=128, pattern="^[A-Za-z0-9_-]+$")
    email: EmailStr
    age: int = Field(ge=18, le=120)
    is_active: bool = True


class UserResponse(CustomBaseModel):
    """User response model."""

    id: UUID
    username: str
    email: str
    created_at: datetime
    is_active: bool


class TaskCreate(CustomBaseModel):
    """Task creation with validation."""

    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: int = Field(ge=1, le=5, default=3)


class TaskResponse(CustomBaseModel):
    """Task response model."""

    id: UUID
    title: str
    description: Optional[str]
    priority: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime]


# In-memory storage (replace with DB in production)
_users: dict[UUID, dict[str, Any]] = {}
_tasks: dict[UUID, dict[str, Any]] = {}


async def validate_user_id(user_id: UUID) -> dict[str, Any]:
    """Dependency: Validate user exists."""
    user = _users.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return user


async def validate_task_id(task_id: UUID) -> dict[str, Any]:
    """Dependency: Validate task exists."""
    task = _tasks.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return task


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate) -> UserResponse:
    """Create new user with validation."""
    start_time = time.time()

    # Check for duplicate email
    for existing in _users.values():
        if existing["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email {user.email} already registered",
            )

    user_id = UUID(int=len(_users) + 1)
    user_data = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "age": user.age,
        "is_active": user.is_active,
        "created_at": datetime.now(UTC),
    }
    _users[user_id] = user_data

    duration_ms = (time.time() - start_time) * 1000
    logger.info("user_created", user_id=str(user_id), duration_ms=duration_ms)

    return UserResponse(**user_data)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user: dict[str, Any] = Depends(validate_user_id)) -> UserResponse:
    """Get user by ID. Uses dependency for validation."""
    return UserResponse(**user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    update_data: UserCreate,
    user: dict[str, Any] = Depends(validate_user_id),
) -> UserResponse:
    """Update user. Uses dependency for validation."""
    user.update(
        {
            "username": update_data.username,
            "email": update_data.email,
            "age": update_data.age,
            "is_active": update_data.is_active,
        }
    )
    logger.info("user_updated", user_id=str(user["id"]))
    return UserResponse(**user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user: dict[str, Any] = Depends(validate_user_id),
) -> None:
    """Delete user."""
    user_id = user["id"]
    del _users[user_id]
    logger.info("user_deleted", user_id=str(user_id))


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    user: dict[str, Any] = Depends(validate_user_id),
) -> TaskResponse:
    """Create task for user."""
    task_id = UUID(int=len(_tasks) + 1)
    task_data = {
        "id": task_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": "pending",
        "user_id": user["id"],
        "created_at": datetime.now(UTC),
        "completed_at": None,
    }
    _tasks[task_id] = task_data

    logger.info("task_created", task_id=str(task_id), user_id=str(user["id"]))
    return TaskResponse(**task_data)


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task: dict[str, Any] = Depends(validate_task_id),
) -> TaskResponse:
    """Get task by ID."""
    return TaskResponse(**task)


@router.patch("/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task: dict[str, Any] = Depends(validate_task_id),
) -> TaskResponse:
    """Mark task as complete."""
    if task["status"] == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task already completed",
        )

    task["status"] = "completed"
    task["completed_at"] = datetime.now(UTC)

    logger.info("task_completed", task_id=str(task["id"]))
    return TaskResponse(**task)


@router.get("/users/{user_id}/tasks", response_model=list[TaskResponse])
async def list_user_tasks(
    user: dict[str, Any] = Depends(validate_user_id),
    status_filter: Optional[str] = None,
) -> list[TaskResponse]:
    """List all tasks for user with optional status filter."""
    user_id = user["id"]
    tasks = [t for t in _tasks.values() if t["user_id"] == user_id]

    if status_filter:
        tasks = [t for t in tasks if t["status"] == status_filter]

    return [TaskResponse(**t) for t in tasks]


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "users_count": len(_users),
        "tasks_count": len(_tasks),
    }
