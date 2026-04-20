#!/usr/bin/env python3
"""AMOS Equation Database - SQLAlchemy 2.0 Async Database Layer.

Production-grade database integration using SQLAlchemy 2.0 with:
- Async engine and session management
- Repository pattern for data access
- Connection pooling and transaction management
- Entity models for equations, executions, users
- Migration-ready structure (Alembic)
- Automatic retry with exponential backoff
- Database health checks

Architecture Pattern: Repository + Unit of Work
SQLAlchemy 2.0 Features:
    - New async API with asyncpg
    - DeclarativeBase with type hints
    - select() / insert() / update() / delete() syntax
    - Session.scalars() / Session.scalar() methods
    - Connection pooling with QueuePool

Entity Models:
    - Equation: Equation metadata and configuration
    - EquationExecution: Execution history and results
    - User: User accounts and authentication
    - Domain: Domain categories for equations
    - ApiKey: API key management for external access

Usage:
    # Dependency injection in FastAPI
    from equation_database import get_db_session, EquationRepository

    @app.post("/equations")
    async def create_equation(
        data: EquationCreate,
        session: AsyncSession = Depends(get_db_session)
    ):
        repo = EquationRepository(session)
        equation = await repo.create(data)
        return equation

Environment Variables:
    DATABASE_URL: PostgreSQL connection URL
    DB_POOL_SIZE: Connection pool size (default: 5)
    DB_MAX_OVERFLOW: Max overflow connections (default: 10)
    DB_ECHO: Echo SQL queries (default: false in production)
"""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from decimal import Decimal
from enum import Enum as PyEnum
from functools import wraps
from typing import Any

# SQLAlchemy 2.0 imports
try:
    from sqlalchemy import (
        JSON,
        Boolean,
        DateTime,
        Float,
        ForeignKey,
        Integer,
        String,
        Text,
        and_,
        delete,
        func,
        insert,
        not_,
        or_,
        select,
        update,
    )
    from sqlalchemy.ext.asyncio import (
        AsyncAttrs,
        AsyncEngine,
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )
    from sqlalchemy.orm import (
        DeclarativeBase,
        Mapped,
        joinedload,
        mapped_column,
        relationship,
        selectinload,
    )
    from sqlalchemy.pool import NullPool, QueuePool

    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    # Stubs for type checking
    DeclarativeBase = object
    Mapped = lambda **kwargs: None
    mapped_column = lambda **kwargs: None
    AsyncSession = None
    AsyncEngine = None

# Import our configuration
try:
    from equation_config import Settings, get_settings

    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

logger = logging.getLogger("amos_equation_database")


# ============================================================================
# Base Model with Common Fields
# ============================================================================


class Base(DeclarativeBase, AsyncAttrs):
    """Base model with common fields and utilities."""

    # Common fields for all models
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Soft delete support
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    def soft_delete(self) -> None:
        """Soft delete the record."""
        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)

    def to_dict(self, exclude: set[str] = None) -> dict[str, Any]:
        """Convert model to dictionary."""
        exclude = exclude or set()
        result = {}
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                elif isinstance(value, Decimal):
                    value = str(value)
                result[column.name] = value
        return result


# ============================================================================
# Entity Models
# ============================================================================


class ExecutionStatus(str, PyEnum):
    """Equation execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Equation(Base):
    """Equation metadata and configuration."""

    __tablename__ = "equations"

    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    domain: Mapped[str] = mapped_column(String(64), index=True)
    pattern: Mapped[str] = mapped_column(String(64), nullable=True)
    formula: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Configuration
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    default_inputs: Mapped[dict] = mapped_column(JSON, default=dict)
    constraints: Mapped[dict] = mapped_column(JSON, default=dict)

    # Metadata
    version: Mapped[str] = mapped_column(String(16), default="1.0.0")
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)

    # Relationships
    executions: Mapped[list["EquationExecution"]] = relationship(
        back_populates="equation", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Equation(id={self.id}, name='{self.name}', domain='{self.domain}')>"


class EquationExecution(Base):
    """Equation execution history and results."""

    __tablename__ = "equation_executions"

    equation_id: Mapped[int] = mapped_column(
        ForeignKey("equations.id", ondelete="CASCADE"), index=True
    )

    # Execution details
    inputs: Mapped[dict] = mapped_column(JSON)
    status: Mapped[ExecutionStatus] = mapped_column(String(20), default=ExecutionStatus.PENDING)

    # Results
    result: Mapped[dict] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    error_details: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Performance metrics
    execution_time_ms: Mapped[float] = mapped_column(Float, nullable=True)
    memory_usage_mb: Mapped[float] = mapped_column(Float, nullable=True)

    # Metadata
    request_id: Mapped[str] = mapped_column(String(64), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    api_key_id: Mapped[int] = mapped_column(
        ForeignKey("api_keys.id", ondelete="SET NULL"), nullable=True
    )
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    equation: Mapped["Equation"] = relationship(back_populates="executions")
    user: Mapped["User"] = relationship(back_populates="executions")

    def __repr__(self) -> str:
        return f"<EquationExecution(id={self.id}, equation_id={self.equation_id}, status='{self.status}')>"


class User(Base):
    """User accounts and authentication."""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    # Profile
    full_name: Mapped[str] = mapped_column(String(128), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    # Rate limiting
    rate_limit_tier: Mapped[str] = mapped_column(String(20), default="default")

    # Metadata
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    executions: Mapped[list["EquationExecution"]] = relationship(
        back_populates="user", lazy="selectin"
    )
    api_keys: Mapped[list["ApiKey"]] = relationship(back_populates="user", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"


class ApiKey(Base):
    """API key management for external access."""

    __tablename__ = "api_keys"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    key_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))

    # Permissions
    scopes: Mapped[list] = mapped_column(JSON, default=list)
    rate_limit_tier: Mapped[str] = mapped_column(String(20), default="default")

    # Usage tracking
    last_used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    usage_count: Mapped[int] = mapped_column(default=0)

    # Expiration
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_revoked: Mapped[bool] = mapped_column(default=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="api_keys")

    def __repr__(self) -> str:
        return f"<ApiKey(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class Domain(Base):
    """Domain categories for equations."""

    __tablename__ = "domains"

    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    icon: Mapped[str] = mapped_column(String(64), nullable=True)
    color: Mapped[str] = mapped_column(String(7), nullable=True)  # Hex color

    # Statistics
    equation_count: Mapped[int] = mapped_column(default=0)

    def __repr__(self) -> str:
        return f"<Domain(id={self.id}, name='{self.name}')>"


# ============================================================================
# Database Engine and Session Management
# ============================================================================


class DatabaseManager:
    """Manages database engine and session lifecycle."""

    def __init__(self) -> None:
        self.engine: AsyncEngine = None
        self.session_maker: async_sessionmaker = None
        self._initialized = False

    async def initialize(self, settings: Settings = None) -> None:
        """Initialize database engine and session maker."""
        if self._initialized:
            return

        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy 2.0+ required")

        if settings is None:
            if not CONFIG_AVAILABLE:
                raise ImportError("equation_config required for default settings")
            settings = get_settings()

        # Get database URL
        db_url = settings.database.get_async_url()

        # Create async engine
        self.engine = create_async_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            pool_timeout=settings.database.pool_timeout,
            pool_pre_ping=True,  # Verify connections before use
            echo=settings.app_debug,  # Log SQL in debug mode
            future=True,  # SQLAlchemy 2.0 style
        )

        # Create session maker
        self.session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Better for async
            autocommit=False,
            autoflush=False,
        )

        self._initialized = True
        logger.info(f"Database initialized: {settings.database.host}:{settings.database.port}")

    async def close(self) -> None:
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_maker = None
            self._initialized = False
            logger.info("Database connections closed")

    async def create_tables(self) -> None:
        """Create all tables (for development/testing)."""
        if not self.engine:
            raise RuntimeError("Database not initialized")

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")

    async def drop_tables(self) -> None:
        """Drop all tables (for testing)."""
        if not self.engine:
            raise RuntimeError("Database not initialized")

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped")

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session context manager."""
        if not self.session_maker:
            raise RuntimeError("Database not initialized")

        async with self.session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# Global database manager instance
_db_manager = DatabaseManager()


async def initialize_database(settings: Settings = None) -> None:
    """Initialize the database system."""
    await _db_manager.initialize(settings)


async def close_database() -> None:
    """Close database connections."""
    await _db_manager.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions.

    Usage:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_db_session)):
            ...
    """
    if not _db_manager.session_maker:
        await _db_manager.initialize()

    async with _db_manager.session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ============================================================================
# Repository Pattern
# ============================================================================


class BaseRepository:
    """Base repository with common CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, model: type, id: int) -> Any:
        """Get record by ID."""
        result = await self.session.execute(
            select(model).where(and_(model.id == id, not_(model.is_deleted)))
        )
        return result.scalar_one_or_none()

    async def get_all(self, model: type, skip: int = 0, limit: int = 100, **filters) -> list[Any]:
        """Get all records with pagination and filters."""
        query = select(model).where(not_(model.is_deleted))

        # Apply filters
        for key, value in filters.items():
            if hasattr(model, key) and value is not None:
                query = query.where(getattr(model, key) == value)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(self, model: type, **filters) -> int:
        """Count records."""
        query = select(func.count(model.id)).where(not_(model.is_deleted))

        for key, value in filters.items():
            if hasattr(model, key) and value is not None:
                query = query.where(getattr(model, key) == value)

        result = await self.session.execute(query)
        return result.scalar() or 0


class EquationRepository(BaseRepository):
    """Repository for Equation operations."""

    async def get_by_name(self, name: str) -> Equation:
        """Get equation by name."""
        result = await self.session.execute(
            select(Equation).where(
                and_(Equation.name == name, not_(Equation.is_deleted), Equation.is_active == True)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_domain(self, domain: str, skip: int = 0, limit: int = 100) -> list[Equation]:
        """Get equations by domain."""
        result = await self.session.execute(
            select(Equation)
            .where(
                and_(
                    Equation.domain == domain, not_(Equation.is_deleted), Equation.is_active == True
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, **data) -> Equation:
        """Create a new equation."""
        equation = Equation(**data)
        self.session.add(equation)
        await self.session.flush()
        await self.session.refresh(equation)
        return equation

    async def update(self, equation: Equation, **data) -> Equation:
        """Update an equation."""
        for key, value in data.items():
            if hasattr(equation, key):
                setattr(equation, key, value)

        await self.session.flush()
        await self.session.refresh(equation)
        return equation

    async def soft_delete_equation(self, equation: Equation) -> None:
        """Soft delete an equation."""
        equation.soft_delete()
        await self.session.flush()

    async def search(
        self, query: str, domain: str = None, skip: int = 0, limit: int = 100
    ) -> list[Equation]:
        """Search equations by name or description."""
        search_pattern = f"%{query}%"

        stmt = select(Equation).where(
            and_(
                not_(Equation.is_deleted),
                Equation.is_active == True,
                or_(
                    Equation.name.ilike(search_pattern), Equation.description.ilike(search_pattern)
                ),
            )
        )

        if domain:
            stmt = stmt.where(Equation.domain == domain)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class ExecutionRepository(BaseRepository):
    """Repository for EquationExecution operations."""

    async def create(self, **data) -> EquationExecution:
        """Create a new execution record."""
        execution = EquationExecution(**data)
        self.session.add(execution)
        await self.session.flush()
        await self.session.refresh(execution)
        return execution

    async def update_status(
        self, execution: EquationExecution, status: ExecutionStatus, **kwargs
    ) -> EquationExecution:
        """Update execution status and optional fields."""
        execution.status = status

        for key, value in kwargs.items():
            if hasattr(execution, key):
                setattr(execution, key, value)

        await self.session.flush()
        await self.session.refresh(execution)
        return execution

    async def get_by_request_id(self, request_id: str) -> EquationExecution:
        """Get execution by request ID."""
        result = await self.session.execute(
            select(EquationExecution).where(EquationExecution.request_id == request_id)
        )
        return result.scalar_one_or_none()

    async def get_recent_by_equation(
        self, equation_id: int, limit: int = 10
    ) -> list[EquationExecution]:
        """Get recent executions for an equation."""
        result = await self.session.execute(
            select(EquationExecution)
            .where(EquationExecution.equation_id == equation_id)
            .order_by(EquationExecution.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_statistics(
        self, equation_id: int = None, start_date: datetime = None, end_date: datetime = None
    ) -> dict[str, Any]:
        """Get execution statistics."""
        query = select(EquationExecution)

        if equation_id:
            query = query.where(EquationExecution.equation_id == equation_id)
        if start_date:
            query = query.where(EquationExecution.created_at >= start_date)
        if end_date:
            query = query.where(EquationExecution.created_at <= end_date)

        result = await self.session.execute(query)
        executions = result.scalars().all()

        total = len(executions)
        completed = sum(1 for e in executions if e.status == ExecutionStatus.COMPLETED)
        failed = sum(1 for e in executions if e.status == ExecutionStatus.FAILED)
        avg_time = sum((e.execution_time_ms or 0) for e in executions) / total if total > 0 else 0

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "success_rate": completed / total if total > 0 else 0,
            "average_execution_time_ms": avg_time,
        }


class UserRepository(BaseRepository):
    """Repository for User operations."""

    async def get_by_username(self, username: str) -> User:
        """Get user by username."""
        result = await self.session.execute(
            select(User).where(and_(User.username == username, not_(User.is_deleted)))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User:
        """Get user by email."""
        result = await self.session.execute(
            select(User).where(and_(User.email == email, not_(User.is_deleted)))
        )
        return result.scalar_one_or_none()

    async def create(self, **data) -> User:
        """Create a new user."""
        user = User(**data)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update_last_login(self, user: User) -> None:
        """Update user's last login timestamp."""
        user.last_login = datetime.now(UTC)
        await self.session.flush()


class ApiKeyRepository(BaseRepository):
    """Repository for ApiKey operations."""

    async def get_by_key_hash(self, key_hash: str) -> ApiKey:
        """Get API key by hash."""
        result = await self.session.execute(
            select(ApiKey).where(
                and_(ApiKey.key_hash == key_hash, not_(ApiKey.is_deleted), not_(ApiKey.is_revoked))
            )
        )
        return result.scalar_one_or_none()

    async def increment_usage(self, api_key: ApiKey) -> None:
        """Increment API key usage count."""
        api_key.usage_count += 1
        api_key.last_used_at = datetime.now(UTC)
        await self.session.flush()

    async def revoke(self, api_key: ApiKey) -> None:
        """Revoke an API key."""
        api_key.is_revoked = True
        await self.session.flush()


# ============================================================================
# Database Health Check
# ============================================================================


async def check_database_health() -> dict[str, Any]:
    """Check database connectivity and health.

    Returns:
        Health status dictionary
    """
    if not _db_manager.engine:
        return {"status": "unhealthy", "error": "Database not initialized"}

    try:
        async with _db_manager.engine.connect() as conn:
            result = await conn.execute(select(func.now()))
            db_time = result.scalar()

        return {
            "status": "healthy",
            "database_time": db_time.isoformat() if db_time else None,
            "initialized": _db_manager._initialized,
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


# ============================================================================
# Retry Decorator for Database Operations
# ============================================================================


def with_retry(max_retries: int = 3, delay: float = 0.1):
    """Decorator for retrying database operations with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (doubles each attempt)
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Database operation failed (attempt {attempt + 1}/{max_retries}): {e}"
                    )

                    if attempt < max_retries - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= 2  # Exponential backoff

            raise last_exception

        return wrapper

    return decorator


# ============================================================================
# Migration Helpers (Alembic-ready)
# ============================================================================


def get_alembic_config() -> dict[str, Any]:
    """Get Alembic configuration dictionary.

    Usage in alembic.ini:
        [alembic]
        sqlalchemy.url = %(DATABASE_URL)s

    Usage in alembic/env.py:
        from equation_database import get_alembic_config
        config.set_main_option("sqlalchemy.url", get_alembic_config()["url"])
    """
    if not CONFIG_AVAILABLE:
        raise ImportError("equation_config required")

    settings = get_settings()
    return {"url": settings.database.get_async_url(), "async": True}


# ============================================================================
# Example Usage and Testing
# ============================================================================


async def example_usage():
    """Example usage of the database layer."""
    # Initialize database
    await initialize_database()

    # Create tables (for development)
    await _db_manager.create_tables()

    # Use repository pattern
    async with _db_manager.session() as session:
        # Create equation
        eq_repo = EquationRepository(session)
        equation = await eq_repo.create(
            name="sigmoid",
            domain="machine_learning",
            formula="1 / (1 + exp(-x))",
            description="Sigmoid activation function",
        )
        print(f"Created equation: {equation}")

        # Search equations
        results = await eq_repo.search("sigmoid")
        print(f"Search results: {results}")

    # Cleanup
    await _db_manager.drop_tables()
    await close_database()


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
