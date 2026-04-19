#!/usr/bin/env python3
"""AMOS SQLAlchemy Models v2.0.0
=============================

Production-grade database models using SQLAlchemy 2.0.

Features:
  - SQLAlchemy 2.0 with async support
  - PostgreSQL optimized types
  - Indexed columns for performance
  - JSONB for flexible metadata
  - Relationships and cascades
  - Audit trail support

Models:
  - User: Authentication and authorization
  - Agent: Agent instances and state
  - Session: User sessions with JWT
  - MemoryEntry: Episodic and semantic memories
  - Task: Async task tracking
  - AuditLog: Security audit trail
  - LawViolation: Compliance tracking
  - PerformanceMetric: System metrics

Usage:
    from amos_models import init_db, User, Agent

  async with async_session() as session:
      user = await session.get(User, 1)
      user.name = "Updated"
      await session.commit()

Requirements:
  pip install sqlalchemy[asyncio] asyncpg alembic

Author: Trang Phan
Version: 2.0.0
"""

import uuid
from collections.abc import AsyncGenerator
from datetime import datetime
from enum import Enum as PyEnum

# SQLAlchemy imports
try:
    from sqlalchemy import (
        JSON,
        Boolean,
        Column,
        DateTime,
        Enum,
        Float,
        ForeignKey,
        Index,
        Integer,
        String,
        Text,
        UniqueConstraint,
        create_engine,
        select,
    )
    from sqlalchemy.dialects.postgresql import JSONB, UUID
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.orm import (
        DeclarativeBase,
        Mapped,
        mapped_column,
        relationship,
        sessionmaker,
    )
    from sqlalchemy.sql import func

    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    print("[Models] SQLAlchemy not available, using mock models")


# Database configuration
if SQLALCHEMY_AVAILABLE:

    class Base(DeclarativeBase):
        """Base class for all models."""

        pass
else:

    class Base:
        pass


# Enums
class AgentRole(str, PyEnum):
    """Agent role enumeration."""

    ARCHITECT = "architect"
    REVIEWER = "reviewer"
    AUDITOR = "auditor"
    EXECUTOR = "executor"
    SYNTHESIZER = "synthesizer"


class AgentParadigm(str, PyEnum):
    """Cognitive paradigm enumeration."""

    SYMBOLIC = "symbolic"
    NEURAL = "neural"
    HYBRID = "hybrid"


class TaskStatus(str, PyEnum):
    """Async task status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MemoryType(str, PyEnum):
    """Memory tier type."""

    WORKING = "working"
    SHORT_TERM = "short_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class UserRole(str, PyEnum):
    """User role for RBAC."""

    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"
    EVOLUTION_APPROVER = "evolution_approver"


# Models
if SQLALCHEMY_AVAILABLE:

    class User(Base):
        """User model for authentication and authorization."""

        __tablename__ = "users"

        id: Mapped[int] = mapped_column(primary_key=True)
        username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
        email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
        password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
        role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.VIEWER)
        is_active: Mapped[bool] = mapped_column(Boolean, default=True)
        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now()
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
        last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

        # Relationships
        sessions: Mapped[list["Session"]] = relationship(
            back_populates="user", cascade="all, delete-orphan"
        )
        audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")

        def __repr__(self) -> str:
            return f"<User(id={self.id}, username={self.username}, role={self.role})>"

    class Session(Base):
        """Session model for JWT token tracking."""

        __tablename__ = "sessions"

        id: Mapped[int] = mapped_column(primary_key=True)
        user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
        token_jti: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)  # JWT ID
        expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
        is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now()
        )
        ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
        user_agent: Mapped[str] = mapped_column(String(255), nullable=True)

        # Relationships
        user: Mapped["User"] = relationship(back_populates="sessions")

        # Indexes
        __table_args__ = (
            Index("idx_session_token", "token_jti"),
            Index("idx_session_user", "user_id"),
        )

    class Agent(Base):
        """Agent model for tracking agent instances."""

        __tablename__ = "agents"

        id: Mapped[int] = mapped_column(primary_key=True)
        agent_id: Mapped[str] = mapped_column(
            String(36), unique=True, default=lambda: str(uuid.uuid4())
        )
        name: Mapped[str] = mapped_column(String(100), nullable=False)
        role: Mapped[AgentRole] = mapped_column(Enum(AgentRole), nullable=False)
        paradigm: Mapped[AgentParadigm] = mapped_column(
            Enum(AgentParadigm), default=AgentParadigm.HYBRID
        )
        status: Mapped[str] = mapped_column(
            String(20), default="active"
        )  # active, paused, terminated
        capabilities: Mapped[dict] = mapped_column(JSONB, default=dict)
        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now()
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )
        terminated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

        # Relationships
        tasks: Mapped[list["Task"]] = relationship(back_populates="agent")
        memories: Mapped[list["MemoryEntry"]] = relationship(back_populates="agent")

        # Indexes
        __table_args__ = (
            Index("idx_agent_agent_id", "agent_id"),
            Index("idx_agent_role", "role"),
            Index("idx_agent_status", "status"),
        )

    class MemoryEntry(Base):
        """Memory entry model for all memory tiers."""

        __tablename__ = "memory_entries"

        id: Mapped[int] = mapped_column(primary_key=True)
        memory_id: Mapped[str] = mapped_column(
            String(36), unique=True, default=lambda: str(uuid.uuid4())
        )
        agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=True)
        memory_type: Mapped[MemoryType] = mapped_column(Enum(MemoryType), nullable=False)
        content: Mapped[str] = mapped_column(Text, nullable=False)
        summary: Mapped[str] = mapped_column(Text, nullable=True)
        importance: Mapped[float] = mapped_column(Float, default=1.0)  # 0.0 to 10.0
        metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
        embedding_id: Mapped[str] = mapped_column(String(36), nullable=True)  # ChromaDB ID
        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now()
        )
        expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
        access_count: Mapped[int] = mapped_column(Integer, default=0)
        last_accessed: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

        # Relationships
        agent: Mapped["Agent"] = relationship(back_populates="memories")

        # Indexes
        __table_args__ = (
            Index("idx_memory_type", "memory_type"),
            Index("idx_memory_agent", "agent_id"),
            Index("idx_memory_created", "created_at"),
            Index("idx_memory_expires", "expires_at"),
        )

    class Task(Base):
        """Async task model for Celery task tracking."""

        __tablename__ = "tasks"

        id: Mapped[int] = mapped_column(primary_key=True)
        task_id: Mapped[str] = mapped_column(
            String(36), unique=True, default=lambda: str(uuid.uuid4())
        )
        celery_id: Mapped[str] = mapped_column(String(100), nullable=True)
        task_type: Mapped[str] = mapped_column(
            String(50), nullable=False
        )  # spawn, orchestrate, index, evolve
        status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.PENDING)
        agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=True)
        user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
        parameters: Mapped[dict] = mapped_column(JSONB, default=dict)
        result: Mapped[dict] = mapped_column(JSONB, nullable=True)
        error_message: Mapped[str] = mapped_column(Text, nullable=True)
        progress_percent: Mapped[int] = mapped_column(Integer, default=0)
        started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
        completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now()
        )

        # Relationships
        agent: Mapped["Agent"] = relationship(back_populates="tasks")

        # Indexes
        __table_args__ = (
            Index("idx_task_task_id", "task_id"),
            Index("idx_task_status", "status"),
            Index("idx_task_type", "task_type"),
            Index("idx_task_user", "user_id"),
        )

    class AuditLog(Base):
        """Security audit log model."""

        __tablename__ = "audit_logs"

        id: Mapped[int] = mapped_column(primary_key=True)
        user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
        action: Mapped[str] = mapped_column(
            String(50), nullable=False
        )  # login, logout, spawn, execute, etc.
        resource_type: Mapped[str] = mapped_column(
            String(50), nullable=False
        )  # agent, task, memory, etc.
        resource_id: Mapped[str] = mapped_column(String(36), nullable=True)
        details: Mapped[dict] = mapped_column(JSONB, default=dict)
        ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
        user_agent: Mapped[str] = mapped_column(String(255), nullable=True)
        success: Mapped[bool] = mapped_column(Boolean, default=True)
        timestamp: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now()
        )

        # Relationships
        user: Mapped["User"] = relationship(back_populates="audit_logs")

        # Indexes
        __table_args__ = (
            Index("idx_audit_user", "user_id"),
            Index("idx_audit_action", "action"),
            Index("idx_audit_timestamp", "timestamp"),
            Index("idx_audit_resource", "resource_type", "resource_id"),
        )

    class LawViolation(Base):
        """Law compliance violation tracking."""

        __tablename__ = "law_violations"

        id: Mapped[int] = mapped_column(primary_key=True)
        law_id: Mapped[str] = mapped_column(String(10), nullable=False)  # L1, L2, L3, L4, L5, L6
        action: Mapped[str] = mapped_column(Text, nullable=False)
        violation_details: Mapped[str] = mapped_column(Text, nullable=False)
        agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), nullable=True)
        task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=True)
        blocked: Mapped[bool] = mapped_column(Boolean, default=True)  # Was action blocked?
        timestamp: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now()
        )

        # Indexes
        __table_args__ = (
            Index("idx_violation_law", "law_id"),
            Index("idx_violation_timestamp", "timestamp"),
            Index("idx_violation_agent", "agent_id"),
        )

    class PerformanceMetric(Base):
        """System performance metrics."""

        __tablename__ = "performance_metrics"

        id: Mapped[int] = mapped_column(primary_key=True)
        metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
        metric_value: Mapped[float] = mapped_column(Float, nullable=False)
        labels: Mapped[dict] = mapped_column(JSONB, default=dict)  # endpoint, status, etc.
        timestamp: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now()
        )

        # Indexes
        __table_args__ = (
            Index("idx_metric_name", "metric_name"),
            Index("idx_metric_timestamp", "timestamp"),
        )


# Database engine and session management
engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None


def init_database(database_url: str = None) -> bool:
    """Initialize database connection.

    Args:
        database_url: Database URL. If None, uses SQLite.

    Returns:
        True if initialization successful
    """
    global engine, async_engine, SessionLocal, AsyncSessionLocal

    if not SQLALCHEMY_AVAILABLE:
        print("[Database] SQLAlchemy not available")
        return False

    try:
        if database_url is None:
            # Default to SQLite for development
            database_url = "sqlite:///./amos.db"

        # Create sync engine for migrations
        engine = create_engine(database_url, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Create async engine for FastAPI
        if database_url.startswith("sqlite"):
            async_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")
        elif database_url.startswith("postgresql"):
            async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            async_url = database_url

        async_engine = create_async_engine(async_url, echo=False)
        AsyncSessionLocal = async_sessionmaker(
            async_engine, class_=AsyncSession, expire_on_commit=False
        )

        print(f"  ✓ Database initialized: {database_url.split('://')[0]}")
        return True

    except Exception as e:
        print(f"  ✗ Database initialization failed: {e}")
        return False


async def create_tables() -> bool:
    """Create all database tables."""
    if not SQLALCHEMY_AVAILABLE or async_engine is None:
        return False

    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("  ✓ Database tables created")
        return True
    except Exception as e:
        print(f"  ✗ Table creation failed: {e}")
        return False


async def drop_tables() -> bool:
    """Drop all database tables (use with caution)."""
    if not SQLALCHEMY_AVAILABLE or async_engine is None:
        return False

    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("  ✓ Database tables dropped")
        return True
    except Exception as e:
        print(f"  ✗ Table drop failed: {e}")
        return False


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not initialized")

    async with AsyncSessionLocal() as session:
        yield session


def get_sync_session():
    """Get sync database session."""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized")

    with SessionLocal() as session:
        yield session


# Mock classes for when SQLAlchemy is not available
if not SQLALCHEMY_AVAILABLE:

    class MockModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    User = MockModel
    Session = MockModel
    Agent = MockModel
    MemoryEntry = MockModel
    Task = MockModel
    AuditLog = MockModel
    LawViolation = MockModel
    PerformanceMetric = MockModel


async def main():
    """Demo database functionality."""
    print("=" * 70)
    print("AMOS DATABASE MODELS v2.0.0")
    print("=" * 70)

    # Initialize database
    if not init_database():
        print("\nDatabase initialization failed!")
        return

    # Create tables
    if not await create_tables():
        print("\nTable creation failed!")
        return

    # Demo operations
    if SQLALCHEMY_AVAILABLE:
        async with AsyncSessionLocal() as session:
            # Create user
            user = User(
                username="demo_user",
                email="demo@amos.ai",
                password_hash="hashed_password",
                role=UserRole.OPERATOR,
            )
            session.add(user)
            await session.commit()
            print(f"  ✓ Created user: {user.username} (ID: {user.id})")

            # Create agent
            agent = Agent(
                name="architect_001",
                role=AgentRole.ARCHITECT,
                paradigm=AgentParadigm.HYBRID,
                capabilities={"strengths": ["design", "planning"], "constraints": []},
            )
            session.add(agent)
            await session.commit()
            print(f"  ✓ Created agent: {agent.name} (ID: {agent.agent_id})")

            # Create memory
            memory = MemoryEntry(
                memory_type=MemoryType.EPISODIC,
                content="Designed REST API for todo app",
                importance=8.5,
                agent_id=agent.id,
            )
            session.add(memory)
            await session.commit()
            print(f"  ✓ Created memory entry (ID: {memory.memory_id})")

            # Query
            result = await session.execute(select(User).where(User.username == "demo_user"))
            found_user = result.scalar_one_or_none()
            if found_user:
                print(f"  ✓ Retrieved user: {found_user.email}")

    print("\n" + "=" * 70)
    print("Database demo completed!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Run migrations: alembic upgrade head")
    print("  2. Use in FastAPI: Depends(get_async_session)")
    print("  3. For production: Use PostgreSQL")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
