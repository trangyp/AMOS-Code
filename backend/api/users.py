"""
Users API - Service Layer Integration Example

Demonstrates FastAPI dependency injection with the AMOS Service Layer.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr

from amos_services import UnitOfWork, get_unit_of_work
from backend.services.user_service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


# ============================================================================
# Pydantic Models
# ============================================================================


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: str = None
    is_active: bool = None


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


# ============================================================================
# Dependency Injection
# ============================================================================


async def get_user_service(uow: UnitOfWork = Depends(get_unit_of_work)) -> UserService:
    """
    FastAPI dependency that injects UserService with UnitOfWork.

    Usage:
        @router.post("/")
        async def create(
            service: UserService = Depends(get_user_service)
        ):
            return await service.create_user(...)
    """
    return UserService(uow)


# ============================================================================
# API Endpoints
# ============================================================================


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(data: UserCreate, service: UserService = Depends(get_user_service)):
    """
    Create a new user using the service layer.

    Demonstrates:
    - Pydantic model validation
    - Service layer business logic
    - Transaction management via UnitOfWork
    """
    try:
        user = await service.create_user(
            email=data.email, username=data.username, password=data.password
        )

        # Commit transaction
        await service.repository.session.commit()

        return user
    except Exception as e:
        # Transaction automatically rolls back on exception
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, service: UserService = Depends(get_user_service)):
    """Get user by ID."""
    user = await service.get_optional(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: UserService = Depends(get_user_service),
):
    """List all active users with pagination."""
    return await service.list_active_users(skip=skip, limit=limit)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str, data: UserUpdate, service: UserService = Depends(get_user_service)
):
    """Update user."""
    try:
        user = await service.update_user(
            user_id=user_id, email=data.email, username=data.username, is_active=data.is_active
        )
        await service.repository.session.commit()
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: str, service: UserService = Depends(get_user_service)):
    """Deactivate (soft-delete) user."""
    try:
        await service.deactivate_user(user_id)
        await service.repository.session.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
