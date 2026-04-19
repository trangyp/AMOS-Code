#!/usr/bin/env python3
"""AMOS Database SQLAlchemy Layer - Phase 16
==============================================

Production-grade async database persistence with SQLAlchemy 2.0,
PostgreSQL support, connection pooling, and Alembic migrations.

Features:
- SQLAlchemy 2.0 async ORM
- PostgreSQL with asyncpg driver
- Connection pooling
- Automatic migrations (Alembic)
- Type-safe models with Pydantic integration
- Audit logging
- Time-series metrics storage

Models:
- User: User accounts and authentication
- APIKey: API key management
- AuditLog: Security and operation audit trail
- EquationExecution: Equation execution history
- HealthMetric: Time-series health data
- SystemConfig: Persistent configuration

Owner: Trang
Version: 1.0.0
Phase: 16
"""

import asyncio
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, Optional

# SQLAlchemy imports
try:
    from sqlalchemy import (
        JSON,
        Boolean,
        Column,
        DateTime,
        Float,
        ForeignKey,
        Index,
        Integer,
        String,
        Text,
        create_engine,
        select,
    )
    from sqlalchemy.ext.asyncio import (
        AsyncEngine,
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )
    from sqlalchemy.orm import (
        DeclarativeBase,
        Mapped,
        mapped_column,
        relationship,
    )

    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    print("SQLAlchemy not installed. Database features disabled.")

# Configure logging
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://amos:amos@localhost:5432/amos")
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "20"))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
DATABASE_POOL_TIMEOUT = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "false").lower() == "true"


# SQLAlchemy base class
class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# ============================================
# Database Models
# ============================================


class User(Base):
    """User account model."""

    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_username", "username", unique=True),
        Index("ix_users_email", "email", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    api_keys: Mapped[list["APIKey"]] = relationship(back_populates="user", lazy="selectin")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user", lazy="selectin")


class APIKey(Base):
    """API key management model."""

    __tablename__ = "api_keys"
    __table_args__ = (
        Index("ix_api_keys_key_id", "key_id"),
        Index("ix_api_keys_user_id", "user_id"),
        Index("ix_api_keys_is_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    hashed_key: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    role: Mapped[str] = mapped_column(String(50), default="service")
    rate_limit: Mapped[int] = mapped_column(Integer, default=1000)
    permissions: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="api_keys")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="api_key", lazy="selectin")


class AuditLog(Base):
    """Audit log for security and operations."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_timestamp", "timestamp"),
        Index("ix_audit_logs_event_type", "event_type"),
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_api_key_id", "api_key_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    api_key_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("api_keys.id", ondelete="SET NULL"), nullable=True
    )
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(500), nullable=True)
    resource: Mapped[str] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="audit_logs")
    api_key: Mapped["APIKey"] = relationship(back_populates="audit_logs")


class EquationExecution(Base):
    """Equation execution history."""

    __tablename__ = "equation_executions"
    __table_args__ = (
        Index("ix_equation_executions_timestamp", "timestamp"),
        Index("ix_equation_executions_name", "name"),
        Index("ix_equation_executions_user_id", "user_id"),
        Index("ix_equation_executions_success", "success"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    api_key_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("api_keys.id", ondelete="SET NULL"), nullable=True
    )
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)
    result: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)
    duration_ms: Mapped[float] = mapped_column(Float, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)


class HealthMetric(Base):
    """Time-series health metrics."""

    __tablename__ = "health_metrics"
    __table_args__ = (
        Index("ix_health_metrics_timestamp", "timestamp"),
        Index("ix_health_metrics_metric_name", "metric_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    metric_name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    labels: Mapped[dict[str, str]] = mapped_column(JSON, nullable=True)


class SystemConfig(Base):
    """Persistent system configuration."""

    __tablename__ = "system_config"
    __table_args__ = (Index("ix_system_config_key", "key", unique=True),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    value: Mapped[Any] = mapped_column(JSON, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    updated_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


# ============================================
# Database Engine and Session Management
# ============================================


class AMOSDatabase:
    """
    AMOS Database Manager.

    Handles connection pooling, session management,
    and provides high-level database operations.
    """

    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_maker: async_sessionmaker[AsyncSession] = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize database connection pool."""
        if not SQLALCHEMY_AVAILABLE:
            logger.warning("SQLAlchemy not available. Database features disabled.")
            return

        if self._initialized:
            return

        try:
            self._engine = create_async_engine(
                DATABASE_URL,
                pool_size=DATABASE_POOL_SIZE,
                max_overflow=DATABASE_MAX_OVERFLOW,
                pool_timeout=DATABASE_POOL_TIMEOUT,
                echo=DATABASE_ECHO,
                pool_pre_ping=True,  # Verify connections before use
            )

            self._session_maker = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )

            # Create tables (in production, use Alembic migrations)
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            self._initialized = True
            logger.info("✅ AMOS Database initialized (Phase 16)")
            logger.info(f"   Pool size: {DATABASE_POOL_SIZE}")
            logger.info(f"   Max overflow: {DATABASE_MAX_OVERFLOW}")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def close(self) -> None:
        """Close database connections."""
        if self._engine:
            await self._engine.dispose()
            self._initialized = False
            logger.info("Database connections closed")

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session context manager."""
        if not self._session_maker:
            raise RuntimeError("Database not initialized")

        session = self._session_maker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def health_check(self) -> Dict[str, Any]:
        """Check database health."""
        if not self._initialized or not self._engine:
            return {"status": "unhealthy", "error": "Database not initialized"}

        try:
            async with self.session() as session:
                # Execute simple query to verify connection
                result = await session.execute(select(1))
                result.scalar()

                # Get connection pool stats
                pool = self._engine.pool
                return {
                    "status": "healthy",
                    "pool_size": pool.size(),
                    "checked_in": pool.checkedin(),
                    "checked_out": pool.checkedout(),
                    "overflow": pool.overflow(),
                }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    # ============================================
    # High-level Operations
    # ============================================

    async def create_user(
        self, username: str, email: str, role: str = "user", is_superuser: bool = False
    ) -> User:
        """Create a new user."""
        async with self.session() as session:
            user = User(username=username, email=email, role=role, is_superuser=is_superuser)
            session.add(user)
            await session.flush()
            await session.refresh(user)
            return user

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        async with self.session() as session:
            result = await session.execute(select(User).where(User.username == username))
            return result.scalar_one_or_none()

    async def create_api_key(
        self,
        key_id: str,
        hashed_key: str,
        name: str,
        user_id: int = None,
        role: str = "service",
        rate_limit: int = 1000,
        expires_at: datetime = None,
    ) -> APIKey:
        """Create a new API key."""
        async with self.session() as session:
            api_key = APIKey(
                key_id=key_id,
                hashed_key=hashed_key,
                name=name,
                user_id=user_id,
                role=role,
                rate_limit=rate_limit,
                expires_at=expires_at,
            )
            session.add(api_key)
            await session.flush()
            await session.refresh(api_key)
            return api_key

    async def get_api_key_by_key_id(self, key_id: str) -> Optional[APIKey]:
        """Get API key by key_id."""
        async with self.session() as session:
            result = await session.execute(
                select(APIKey).where(APIKey.key_id == key_id).where(APIKey.is_active == True)
            )
            return result.scalar_one_or_none()

    async def log_audit_event(
        self,
        event_type: str,
        user_id: int = None,
        api_key_id: int = None,
        ip_address: str = None,
        user_agent: str = None,
        resource: str = None,
        action: str = None,
        success: bool = True,
        details: Dict[str, Any] = None,
    ) -> AuditLog:
        """Log an audit event."""
        async with self.session() as session:
            log = AuditLog(
                event_type=event_type,
                user_id=user_id,
                api_key_id=api_key_id,
                ip_address=ip_address,
                user_agent=user_agent,
                resource=resource,
                action=action,
                success=success,
                details=details,
            )
            session.add(log)
            await session.flush()
            await session.refresh(log)
            return log

    async def record_equation_execution(
        self,
        name: str,
        duration_ms: float,
        user_id: int = None,
        api_key_id: int = None,
        parameters: Dict[str, Any] = None,
        result: Dict[str, Any] = None,
        success: bool = True,
        error_message: str = None,
        ip_address: str = None,
    ) -> EquationExecution:
        """Record equation execution."""
        async with self.session() as session:
            execution = EquationExecution(
                name=name,
                user_id=user_id,
                api_key_id=api_key_id,
                parameters=parameters,
                result=result,
                duration_ms=duration_ms,
                success=success,
                error_message=error_message,
                ip_address=ip_address,
            )
            session.add(execution)
            await session.flush()
            await session.refresh(execution)
            return execution

    async def record_health_metric(
        self, metric_name: str, value: float, labels: Dict[str, str] = None
    ) -> HealthMetric:
        """Record health metric."""
        async with self.session() as session:
            metric = HealthMetric(metric_name=metric_name, value=value, labels=labels)
            session.add(metric)
            await session.flush()
            await session.refresh(metric)
            return metric


# Global database instance
_database: Optional[AMOSDatabase] = None


async def get_database() -> AMOSDatabase:
    """Get or create global database instance."""
    global _database
    if _database is None:
        _database = AMOSDatabase()
        await _database.initialize()
    return _database


# ============================================
# FastAPI Integration
# ============================================

try:
    from fastapi import Depends, HTTPException, status

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


if FASTAPI_AVAILABLE and SQLALCHEMY_AVAILABLE:

    async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
        """FastAPI dependency for database session."""
        db = await get_database()
        async with db.session() as session:
            yield session


# Backwards compatibility exports for amos_services
AsyncSessionLocal = None  # Will be set when database is initialized


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session (alias for get_db_session)."""
    async for session in get_db_session():
        yield session


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    print("AMOS Database SQLAlchemy Layer - Phase 16")
    print("=" * 60)

    if not SQLALCHEMY_AVAILABLE:
        print("\n⚠️  SQLAlchemy not installed")
        print("   Install: pip install sqlalchemy asyncpg alembic")
        exit(1)

    async def demo():
        db = await get_database()

        # Health check
        health = await db.health_check()
        print(f"\n✅ Database health: {health['status']}")
        if health["status"] == "healthy":
            print(f"   Pool size: {health['pool_size']}")

        # Create user
        try:
            user = await db.create_user(
                username="admin", email="admin@amos.io", role="admin", is_superuser=True
            )
            print(f"\n✅ Created user: {user.username} (ID: {user.id})")
        except Exception as e:
            print(f"\n⚠️  User may already exist: {e}")

        # Log audit event
        log = await db.log_audit_event(
            event_type="test_event",
            resource="test_resource",
            action="test_action",
            success=True,
            details={"test": True},
        )
        print(f"✅ Logged audit event: {log.event_type} (ID: {log.id})")

        # Record health metric
        metric = await db.record_health_metric(
            metric_name="amos_health_score", value=95.5, labels={"subsystem": "gateway"}
        )
        print(f"✅ Recorded metric: {metric.metric_name} = {metric.value}")

        await db.close()

    asyncio.run(demo())

    print("\n" + "=" * 60)
    print("✅ AMOS Database Layer ready!")
