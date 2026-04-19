"""AMOS Database Initialization and Management

Database initialization, migrations, and session management for AMOS backend.

Usage:
    python -m backend.database init     # Initialize database tables
    python -m backend.database migrate  # Run migrations
    python -m backend.database reset    # Reset all tables

Creator: Trang Phan
Version: 1.0.0
"""


import asyncio
import os
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://amos:amos@localhost:5432/amos")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session as async context manager."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database() -> None:
    """Initialize database tables."""
    print("Initializing database...")

    # Import all models to ensure they're registered
    try:
        from backend.api import schemas  # noqa: F401

        print("✅ Models imported")
    except ImportError as e:
        print(f"⚠️ Could not import models: {e}")

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Database tables created")


async def reset_database() -> None:
    """Reset database - drop all tables."""
    print("Resetting database...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    print("✅ Database tables dropped")


async def migrate_database() -> None:
    """Run database migrations."""
    print("Running migrations...")

    # For now, just ensure tables exist
    await init_database()

    print("✅ Migrations complete")


async def check_connection() -> bool:
    """Check database connectivity."""
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m backend.database <init|migrate|reset|check>")
        return 1

    command = sys.argv[1]

    async def run():
        if command == "init":
            await init_database()
        elif command == "reset":
            await reset_database()
        elif command == "migrate":
            await migrate_database()
        elif command == "check":
            ok = await check_connection()
            if ok:
                print("✅ Database connection OK")
            else:
                print("❌ Database connection failed")
                sys.exit(1)
        else:
            print(f"Unknown command: {command}")
            print("Usage: python -m backend.database <init|migrate|reset|check>")
            sys.exit(1)

    asyncio.run(run())
    return 0


if __name__ == "__main__":
    sys.exit(main())
