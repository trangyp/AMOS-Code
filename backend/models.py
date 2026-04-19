"""AMOS Database Models using SQLModel.

SQLModel combines SQLAlchemy ORM with Pydantic validation,
providing the perfect match for FastAPI applications.

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations




import json
from datetime import datetime, timezone

UTC = timezone.utc

from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import List

# Database configuration
DATABASE_URL = "sqlite:///./amos.db"


# ============================================
# Base Model with Common Fields
# ============================================


class BaseModel(SQLModel):
    """Base model with common fields."""

    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ============================================
# Agent Task Model
# ============================================


class AgentTask(BaseModel, table=True):
    """Background agent task persistence."""

    __tablename__ = "agent_tasks"

    name: str = Field(index=True)
    description: str
    agent_type: str = Field(default="general")
    status: str = Field(default="pending")  # pending, running, completed, failed
    priority: str = Field(default="normal")  # low, normal, high, critical
    payload: str = Field(default=None)  # JSON string
    result: str = Field(default=None)
    error_message: str = Field(default=None)
    started_at: datetime = Field(default=None)
    completed_at: datetime = Field(default=None)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "agent_type": self.agent_type,
            "status": self.status,
            "priority": self.priority,
            "payload": json.loads(self.payload) if self.payload else None,
            "result": self.result,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


# ============================================
# Memory Entry Model
# ============================================


class MemoryEntry(BaseModel, table=True):
    """Persistent memory storage."""

    __tablename__ = "memory_entries"

    system: str = Field(index=True)  # cognitive, execution, emotional, etc.
    content: str
    importance: str = Field(default="medium")  # low, medium, high, critical
    tags: str = Field(default=None)  # JSON array string
    embedding: str = Field(default=None)  # For vector search
    access_count: int = Field(default=0)
    last_accessed: datetime = Field(default=None)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "system": self.system,
            "content": self.content,
            "importance": self.importance,
            "tags": json.loads(self.tags) if self.tags else [],
            "access_count": self.access_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
        }


# ============================================
# Checkpoint Model
# ============================================


class Checkpoint(BaseModel, table=True):
    """System state checkpoints for /rewind."""

    __tablename__ = "checkpoints"

    label: str
    state_hash: str = Field(index=True)
    files_count: int
    metadata: str = Field(default=None)  # JSON string

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "label": self.label,
            "state_hash": self.state_hash,
            "files_count": self.files_count,
            "metadata": json.loads(self.metadata) if self.metadata else {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================
# API Request Log Model
# ============================================


class APIRequestLog(SQLModel, table=True):
    """API request logging for monitoring."""

    __tablename__ = "api_request_logs"

    id: int = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
    method: str
    path: str
    status_code: int
    response_time_ms: float
    client_ip: str = None
    user_agent: str = None
    error_message: str = None


# ============================================
# System Event Model
# ============================================


class SystemEvent(SQLModel, table=True):
    """System event logging."""

    __tablename__ = "system_events"

    id: int = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
    event_type: str = Field(index=True)  # error, warning, info
    component: str  # llm, agents, system, etc.
    message: str
    details: str = Field(default=None)  # JSON string


# ============================================
# Database Engine & Session
# ============================================

engine = create_engine(DATABASE_URL, echo=False)


# Create tables
def init_db():
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session


# ============================================
# CRUD Operations
# ============================================


class AgentTaskCRUD:
    """Agent task CRUD operations."""

    @staticmethod
    def create(session: Session, task: AgentTask) -> AgentTask:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def get(session: Session, task_id: int) -> Optional[AgentTask]:
        return session.get(AgentTask, task_id)

    @staticmethod
    def list(session: Session, status: str = None, limit: int = 100) -> List[AgentTask]:
        query = select(AgentTask)
        if status:
            query = query.where(AgentTask.status == status)
        query = query.order_by(AgentTask.created_at.desc()).limit(limit)
        return session.exec(query).all()

    @staticmethod
    def update(session: Session, task_id: int, **kwargs) -> Optional[AgentTask]:
        task = session.get(AgentTask, task_id)
        if task:
            for key, value in kwargs.items():
                setattr(task, key, value)
            task.updated_at = datetime.now(UTC)
            session.commit()
            session.refresh(task)
        return task

    @staticmethod
    def delete(session: Session, task_id: int) -> bool:
        task = session.get(AgentTask, task_id)
        if task:
            session.delete(task)
            session.commit()
            return True
        return False


class MemoryEntryCRUD:
    """Memory entry CRUD operations."""

    @staticmethod
    def create(session: Session, entry: MemoryEntry) -> MemoryEntry:
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return entry

    @staticmethod
    def get(session: Session, entry_id: int) -> Optional[MemoryEntry]:
        entry = session.get(MemoryEntry, entry_id)
        if entry:
            entry.access_count += 1
            entry.last_accessed = datetime.now(UTC)
            session.commit()
        return entry

    @staticmethod
    def search(
        session: Session, system: str = None, query: str = None, limit: int = 100
    ) -> List[MemoryEntry]:
        statement = select(MemoryEntry)
        if system:
            statement = statement.where(MemoryEntry.system == system)
        if query:
            statement = statement.where(MemoryEntry.content.contains(query))
        statement = statement.order_by(MemoryEntry.created_at.desc()).limit(limit)
        return session.exec(statement).all()

    @staticmethod
    def delete(session: Session, entry_id: int) -> bool:
        entry = session.get(MemoryEntry, entry_id)
        if entry:
            session.delete(entry)
            session.commit()
            return True
        return False


class CheckpointCRUD:
    """Checkpoint CRUD operations."""

    @staticmethod
    def create(session: Session, checkpoint: Checkpoint) -> Checkpoint:
        session.add(checkpoint)
        session.commit()
        session.refresh(checkpoint)
        return checkpoint

    @staticmethod
    def get(session: Session, checkpoint_id: int) -> Optional[Checkpoint]:
        return session.get(Checkpoint, checkpoint_id)

    @staticmethod
    def list(session: Session, limit: int = 100) -> List[Checkpoint]:
        statement = select(Checkpoint).order_by(Checkpoint.created_at.desc()).limit(limit)
        return session.exec(statement).all()

    @staticmethod
    def delete(session: Session, checkpoint_id: int) -> bool:
        checkpoint = session.get(Checkpoint, checkpoint_id)
        if checkpoint:
            session.delete(checkpoint)
            session.commit()
            return True
        return False
