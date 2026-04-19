"""AMOS Database Connection Pooling.

Provides optimized database connection pooling for high-performance
API operations. Reduces connection overhead and improves scalability.

Features:
- SQLAlchemy connection pooling
- Async database support
- Connection health checks
- Pool size optimization

Creator: Trang Phan
Version: 3.0.0
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./amos.db")

# Pool configuration
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 1 hour


def create_database_engine():
    """Create database engine with connection pooling."""

    if DATABASE_URL.startswith("sqlite"):
        # SQLite configuration (no pooling for SQLite)
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
    else:
        # PostgreSQL/MySQL with connection pooling
        engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=POOL_SIZE,
            max_overflow=MAX_OVERFLOW,
            pool_timeout=POOL_TIMEOUT,
            pool_recycle=POOL_RECYCLE,
            pool_pre_ping=True,  # Health check before using
            echo=False,
        )

    return engine


# Create engine instance
db_engine = create_database_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


def get_db_session():
    """Get database session with automatic cleanup."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_pool_status():
    """Get connection pool status."""
    if hasattr(db_engine, "pool"):
        pool = db_engine.pool
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
        }
    return {"status": "no_pooling", "type": "sqlite"}


def test_connection():
    """Test database connection."""
    try:
        with db_engine.connect() as conn:
            conn.execute("SELECT 1")
        return {"status": "connected", "healthy": True}
    except Exception as e:
        return {"status": "error", "healthy": False, "error": str(e)}
