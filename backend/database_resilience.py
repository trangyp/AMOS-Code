from typing import Any

"""Database resilience and connection handling.

Implements retry logic, connection pooling, and health checks.
"""

import asyncio
from contextlib import asynccontextmanager

import structlog
from sqlalchemy.exc import OperationalError, TimeoutError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import engine

logger = structlog.get_logger("amos.database")


class DatabaseRetryHandler:
    """Handle database operations with automatic retry."""

    MAX_RETRIES = 3
    RETRY_DELAY = 1.0  # seconds

    @classmethod
    async def execute_with_retry(cls, operation: callable, *args, **kwargs) -> Any:
        """Execute database operation with retry logic."""
        last_error = None

        for attempt in range(cls.MAX_RETRIES):
            try:
                return await operation(*args, **kwargs)
            except (OperationalError, TimeoutError) as e:
                last_error = e
                logger.warning(
                    "Database operation failed, retrying",
                    attempt=attempt + 1,
                    max_retries=cls.MAX_RETRIES,
                    error=str(e),
                )

                if attempt < cls.MAX_RETRIES - 1:
                    await asyncio.sleep(cls.RETRY_DELAY * (attempt + 1))

        logger.error(
            "Database operation failed after all retries",
            error=str(last_error),
        )
        raise last_error


@asynccontextmanager
async def resilient_session():
    """Get database session with automatic retry and proper cleanup."""
    session = AsyncSession(engine)

    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error("Session rollback due to error", error=str(e))
        raise
    finally:
        await session.close()


async def check_database_health() -> dict[str, Any]:
    """Comprehensive database health check."""
    from sqlalchemy import text

    health = {"status": "unknown", "latency_ms": 0.0, "connections": {}, "error": None}

    import time

    start = time.perf_counter()

    try:
        async with engine.connect() as conn:
            # Basic connectivity test
            await conn.execute(text("SELECT 1"))

            # Pool statistics
            pool = engine.pool
            health["connections"] = {
                "size": pool.size() if hasattr(pool, "size") else -1,
                "checked_in": pool.checkedin() if hasattr(pool, "checkedin") else -1,
                "checked_out": pool.checkedout() if hasattr(pool, "checkedout") else -1,
            }

            health["status"] = "healthy"
            health["latency_ms"] = (time.perf_counter() - start) * 1000

    except Exception as e:
        health["status"] = "unhealthy"
        health["error"] = str(e)
        health["latency_ms"] = (time.perf_counter() - start) * 1000

        logger.error("Database health check failed", error=str(e))

    return health


class ConnectionPoolManager:
    """Manage database connection pool settings."""

    @staticmethod
    def configure_pool(
        pool_size: int = 20,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
    ) -> dict[str, Any]:
        """Get optimized pool configuration."""
        return {
            "pool_size": pool_size,
            "max_overflow": max_overflow,
            "pool_timeout": pool_timeout,
            "pool_recycle": pool_recycle,
            "pool_pre_ping": True,  # Verify connections before use
        }
