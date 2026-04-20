"""Database Layer for AMOS Brain API

Supports SQLite (development) and PostgreSQL (production).
"""

import os
import sqlite3
from contextlib import contextmanager

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///app/data/amos.db")


class Database:
    """Database connection manager."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_URL.replace("sqlite:///", "")
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Query history table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS query_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_key_hash TEXT,
                    endpoint TEXT NOT NULL,
                    query TEXT,
                    domain TEXT,
                    response_summary TEXT,
                    confidence TEXT,
                    law_compliant BOOLEAN,
                    processing_time_ms INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # API usage stats table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_key_hash TEXT,
                    endpoint TEXT,
                    status_code INTEGER,
                    response_time_ms INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Rate limit tracking
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS rate_limits (
                    api_key_hash TEXT PRIMARY KEY,
                    request_count INTEGER DEFAULT 0,
                    window_start TIMESTAMP,
                    reset_at TIMESTAMP
                )
            """
            )

            conn.commit()

    @contextmanager
    def get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def log_query(
        self,
        api_key_hash: str,
        endpoint: str,
        query: str,
        domain: str,
        response_summary: str,
        confidence: str,
        law_compliant: bool,
        processing_time_ms: int,
    ):
        """Log a query to history."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO query_history
                (api_key_hash, endpoint, query, domain, response_summary,
                 confidence, law_compliant, processing_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    api_key_hash,
                    endpoint,
                    query,
                    domain,
                    response_summary[:500],  # Truncate
                    confidence,
                    law_compliant,
                    processing_time_ms,
                ),
            )
            conn.commit()

    def log_api_usage(
        self, api_key_hash: str, endpoint: str, status_code: int, response_time_ms: int
    ):
        """Log API usage statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO api_usage
                (api_key_hash, endpoint, status_code, response_time_ms)
                VALUES (?, ?, ?, ?)
            """,
                (api_key_hash, endpoint, status_code, response_time_ms),
            )
            conn.commit()

    def get_query_history(
        self, api_key_hash: str = None, limit: int = 100, offset: int = 0
    ) -> list[dict]:
        """Get query history for an API key."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if api_key_hash:
                cursor.execute(
                    """
                    SELECT * FROM query_history
                    WHERE api_key_hash = ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """,
                    (api_key_hash, limit, offset),
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM query_history
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """,
                    (limit, offset),
                )

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_usage_stats(self, days: int = 7) -> dict:
        """Get usage statistics for the last N days."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Total requests
            cursor.execute(
                """
                SELECT COUNT(*) as total FROM api_usage
                WHERE created_at >= datetime('now', ?)
            """,
                (f"-{days} days",),
            )
            total = cursor.fetchone()["total"]

            # Average response time
            cursor.execute(
                """
                SELECT AVG(response_time_ms) as avg_time FROM api_usage
                WHERE created_at >= datetime('now', ?)
            """,
                (f"-{days} days",),
            )
            avg_time = cursor.fetchone()["avg_time"] or 0

            # Success rate
            cursor.execute(
                """
                SELECT
                    COUNT(CASE WHEN status_code = 200 THEN 1 END) * 100.0 / COUNT(*)
                as success_rate
                FROM api_usage
                WHERE created_at >= datetime('now', ?)
            """,
                (f"-{days} days",),
            )
            success_rate = cursor.fetchone()["success_rate"] or 0

            return {
                "total_requests": total,
                "avg_response_time_ms": round(avg_time, 2),
                "success_rate_percent": round(success_rate, 2),
                "period_days": days,
            }

    def cleanup_old_data(self, days: int = 30):
        """Clean up data older than specified days."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM query_history
                WHERE created_at < datetime('now', ?)
            """,
                (f"-{days} days",),
            )

            cursor.execute(
                """
                DELETE FROM api_usage
                WHERE created_at < datetime('now', ?)
            """,
                (f"-{days} days",),
            )

            conn.commit()


# Global database instance
db = Database()
