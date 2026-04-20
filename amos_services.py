"""
AMOS Service Layer Architecture

Production-grade service layer with repository pattern, dependency injection,
and comprehensive business logic management.

Author: AMOS System
Version: 1.0.0
"""

from __future__ import annotations

from datetime import datetime, timezone
UTC = timezone.utc
from typing import Any, Generic, Optional, Protocol, TypeVar, runtime_checkable

UTC = UTC
# SQLAlchemy imports
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

# AMOS imports
from amos_db_sqlalchemy import AsyncSessionLocal
from amos_error_handling import NotFoundError

T = TypeVar("T")
ID = TypeVar("ID", str, int)


# ============================================================================
# Repository Protocol
# ============================================================================


@runtime_checkable
class RepositoryProtocol(Protocol[T, ID]):
    """Protocol defining repository interface."""

    async def get(self, id: ID) -> T: ...
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[T]: ...
    async def create(self, obj: T) -> T: ...
    async def update(self, id: ID, data: dict[str, Any]) -> T: ...
    async def delete(self, id: ID) -> bool: ...
    async def count(self) -> int: ...


# ============================================================================
# Base Repository
# ============================================================================


class BaseRepository(Generic[T, ID]):
    """
    Generic repository implementing standard CRUD operations.

    Usage:
        repo = BaseRepository[User, str](User)
        user = await repo.get("user-id")
        users = await repo.get_all(skip=0, limit=10)
    """

    def __init__(self, model_class: type[T], session: Optional[AsyncSession] = None):
        self.model_class = model_class
        self._session = session

    @property
    def session(self) -> AsyncSession:
        """Get current session or raise error."""
        if self._session is None:
            raise RuntimeError("Repository requires active session. Use with UnitOfWork.")
        return self._session

    async def get(self, id: ID) -> T:
        """Get entity by ID."""
        result = await self.session.get(self.model_class, id)
        return result

    async def get_all(self, skip: int = 0, limit: int = 100, order_by: str = None) -> list[T]:
        """Get all entities with pagination."""
        query = select(self.model_class)

        if order_by:
            query = query.order_by(order_by)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, obj: T) -> T:
        """Create new entity."""
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, id: ID, data: dict[str, Any]) -> T:
        """Update entity by ID."""
        # Check if entity exists
        obj = await self.get(id)
        if obj is None:
            return None

        # Apply updates
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        obj.updated_at = datetime.now(UTC)  # type: ignore
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, id: ID) -> bool:
        """Delete entity by ID."""
        obj = await self.get(id)
        if obj is None:
            return False

        await self.session.delete(obj)
        await self.session.flush()
        return True

    async def count(self) -> int:
        """Count total entities."""
        result = await self.session.execute(select(func.count()).select_from(self.model_class))
        return result.scalar() or 0

    async def exists(self, id: ID) -> bool:
        """Check if entity exists."""
        obj = await self.get(id)
        return obj is not None


# ============================================================================
# Unit of Work Pattern
# ============================================================================


class UnitOfWork:
    """
    Unit of Work pattern for transaction management.

    Ensures atomic operations across multiple repositories.

    Usage:
        async with UnitOfWork() as uow:
            user = await uow.users.create(new_user)
            await uow.commit()
    """

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session
        self._owns_session = session is None
        self._repositories: dict[type, BaseRepository] = {}

    async def __aenter__(self) -> UnitOfWork:
        if self._session is None:
            self._session = AsyncSessionLocal()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()

        if self._owns_session and self._session:
            await self._session.close()

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("No active session")
        return self._session

    def repository(self, model_class: type[T]) -> BaseRepository[T, Any]:
        """Get or create repository for model class."""
        if model_class not in self._repositories:
            self._repositories[model_class] = BaseRepository(model_class, self.session)
        return self._repositories[model_class]

    async def commit(self):
        """Commit current transaction."""
        await self.session.commit()

    async def rollback(self):
        """Rollback current transaction."""
        await self.session.rollback()

    async def flush(self):
        """Flush current session without committing."""
        await self.session.flush()


# ============================================================================
# Base Service
# ============================================================================


class BaseService(Generic[T, ID]):
    """
    Generic base service implementing business logic operations.

    Provides standard CRUD with validation, logging, and error handling.

    Usage:
        class UserService(BaseService[User, str]):
            async def create_user(self, email: str, name: str) -> User:
                # Business logic here
                return await self.create({"email": email, "name": name})
    """

    def __init__(self, model_class: type[T], uow: UnitOfWork | None = None):
        self.model_class = model_class
        self._uow = uow
        self._repo: BaseRepository[T, ID] = None

    @property
    def repository(self) -> BaseRepository[T, ID]:
        """Get repository instance."""
        if self._repo is None:
            if self._uow is None:
                raise RuntimeError("Service requires UnitOfWork")
            self._repo = self._uow.repository(self.model_class)
        return self._repo

    # CRUD Operations

    async def get(self, id: ID) -> T:
        """Get entity by ID with NotFoundError."""
        obj = await self.repository.get(id)
        if obj is None:
            raise NotFoundError(f"{self.model_class.__name__} not found: {id}")
        return obj

    async def get_optional(self, id: ID) -> T:
        """Get entity by ID, returns None if not found."""
        return await self.repository.get(id)

    async def get_all(self, skip: int = 0, limit: int = 100, order_by: str = None) -> list[T]:
        """Get all entities with pagination."""
        return await self.repository.get_all(skip, limit, order_by)

    async def create(self, data: dict[str, Any]) -> T:
        """Create new entity with validation."""
        # Validate data
        self._validate_create(data)

        # Create entity
        obj = self.model_class(**data)  # type: ignore
        return await self.repository.create(obj)

    async def update(self, id: ID, data: dict[str, Any]) -> T:
        """Update entity with validation."""
        # Validate data
        self._validate_update(data)

        # Update entity
        obj = await self.repository.update(id, data)
        if obj is None:
            raise NotFoundError(f"{self.model_class.__name__} not found: {id}")
        return obj

    async def delete(self, id: ID) -> None:
        """Delete entity."""
        success = await self.repository.delete(id)
        if not success:
            raise NotFoundError(f"{self.model_class.__name__} not found: {id}")

    async def count(self) -> int:
        """Count total entities."""
        return await self.repository.count()

    async def exists(self, id: ID) -> bool:
        """Check if entity exists."""
        return await self.repository.exists(id)

    # Validation Hooks

    def _validate_create(self, data: dict[str, Any]) -> None:
        """Override to validate create data."""
        pass

    def _validate_update(self, data: dict[str, Any]) -> None:
        """Override to validate update data."""
        pass


# ============================================================================
# Service Factory
# ============================================================================


class ServiceFactory:
    """
    Factory for creating services with dependency injection.

    Usage:
        factory = ServiceFactory()
        user_service = factory.user_service()
    """

    def __init__(self, uow: UnitOfWork | None = None):
        self._uow = uow

    def _get_uow(self) -> UnitOfWork:
        """Get or create Unit of Work."""
        if self._uow is None:
            raise RuntimeError("No UnitOfWork available")
        return self._uow


# ============================================================================
# FastAPI Dependencies
# ============================================================================


async def get_unit_of_work() -> UnitOfWork:
    """FastAPI dependency for Unit of Work."""
    async with UnitOfWork() as uow:
        yield uow


def get_service_factory(uow: UnitOfWork) -> ServiceFactory:
    """FastAPI dependency for Service Factory."""
    return ServiceFactory(uow)
