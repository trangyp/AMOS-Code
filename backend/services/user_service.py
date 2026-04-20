"""
User Service - Backend Service Layer Integration Example

Demonstrates how to implement a service using the AMOS BaseService pattern
for user management operations.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Optional

from sqlalchemy import select

from amos_db_sqlalchemy import User
from amos_error_handling import ValidationError
from amos_services import BaseService, UnitOfWork


class UserService(BaseService[User, str]):
    """
    User management service with business logic.

    Usage:
        async with UnitOfWork() as uow:
            service = UserService(uow)
            user = await service.create_user(
                email="user@example.com",
                username="johndoe"
            )
    """

    def __init__(self, uow: UnitOfWork):
        super().__init__(User, uow)

    async def create_user(
        self, email: str, username: str, password: str = None, is_active: bool = True
    ) -> User:
        """Create a new user with validation."""
        # Validate email format
        if "@" not in email:
            raise ValidationError("Invalid email format")

        # Check for existing user
        existing = await self.get_by_email(email)
        if existing:
            raise ValidationError(f"User with email {email} already exists")

        # Create user data
        data = {
            "id": str(uuid.uuid4()),
            "email": email,
            "username": username,
            "is_active": is_active,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }

        return await self.create(data)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        # Query by email using repository
        query = select(User).where(User.email == email)
        result = await self.repository.session.execute(query)
        return result.scalar_one_or_none()

    async def update_user(
        self, user_id: str, email: str = None, username: str = None, is_active: bool = None
    ) -> User:
        """Update user with partial data."""
        data: dict[str, Any] = {}

        if email is not None:
            data["email"] = email
        if username is not None:
            data["username"] = username
        if is_active is not None:
            data["is_active"] = is_active

        return await self.update(user_id, data)

    async def deactivate_user(self, user_id: str) -> User:
        """Soft-delete user by deactivating."""
        return await self.update(user_id, {"is_active": False})

    async def list_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """List all active users."""
        query = select(User).where(User.is_active == True).offset(skip).limit(limit)
        result = await self.repository.session.execute(query)
        return list(result.scalars().all())
