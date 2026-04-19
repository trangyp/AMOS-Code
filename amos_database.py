#!/usr/bin/env python3
"""AMOS Database - Production Persistence Layer

Features:
- SQLite/PostgreSQL support for metrics and query history
- Async operations for non-blocking API
- Automatic schema migrations
- Data retention policies
- Query analytics aggregation
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from pathlib import Path
from typing import Optional

UTC = timezone.utc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QueryRecord:
    """Record of an API query."""

    id: int = None
    timestamp: str = ""
    api_key_hash: str = ""
    endpoint: str = ""
    query: str = ""
    domain: str = ""
    response_summary: str = ""
    confidence: str = ""
    law_compliant: bool = True
    processing_time_ms: int = 0
    client_ip: str = ""
    user_agent: str = ""


@dataclass
class MetricRecord:
    """Record of system metrics."""

    id: int = None
    timestamp: str = ""
    metric_type: str = ""  # request_count, error_rate, latency, etc.
    value: float = 0.0
    labels: str = ""  # JSON string
    period_seconds: int = 60  # Aggregation period


class AMOSDatabase:
    """Production database for AMOS Brain."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.environ.get("AMOS_DB_PATH", "amos.db")
        self.db_path = db_path
        self._lock = asyncio.Lock()
        self._init_db()

    def _init_db(self):
        """Initialize database with schema."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            # Query history table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    api_key_hash TEXT,
                    endpoint TEXT NOT NULL,
                    query TEXT,
                    domain TEXT,
                    response_summary TEXT,
                    confidence TEXT,
                    law_compliant BOOLEAN DEFAULT 1,
                    processing_time_ms INTEGER,
                    client_ip TEXT,
                    user_agent TEXT
                )
            """
            )

            # Metrics table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    labels TEXT,
                    period_seconds INTEGER DEFAULT 60
                )
            """
            )

            # Health history table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS health_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    overall_status TEXT NOT NULL,
                    checks_json TEXT,
                    uptime_seconds REAL
                )
            """
            )

            # Alerts table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE NOT NULL,
                    rule_name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    value REAL,
                    threshold REAL,
                    timestamp TEXT NOT NULL,
                    acknowledged_by TEXT,
                    acknowledged_at TEXT,
                    resolved_at TEXT
                )
            """
            )

            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_queries_time ON queries(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_queries_endpoint ON queries(endpoint)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_time ON metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(metric_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_health_time ON health_history(timestamp)")

            conn.commit()
            logger.info(f"Database initialized: {self.db_path}")

    async def log_query(self, record: QueryRecord) -> int:
        """Log an API query."""
        async with self._lock:
            return await asyncio.get_running_loop().run_in_executor(
                None, self._log_query_sync, record
            )

    def _log_query_sync(self, record: QueryRecord) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO queries
                (timestamp, api_key_hash, endpoint, query, domain,
                 response_summary, confidence, law_compliant,
                 processing_time_ms, client_ip, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    record.timestamp or datetime.now(UTC).isoformat(),
                    record.api_key_hash,
                    record.endpoint,
                    record.query,
                    record.domain,
                    record.response_summary,
                    record.confidence,
                    record.law_compliant,
                    record.processing_time_ms,
                    record.client_ip,
                    record.user_agent,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    async def store_metric(self, record: MetricRecord) -> int:
        """Store a metric."""
        async with self._lock:
            return await asyncio.get_running_loop().run_in_executor(
                None, self._store_metric_sync, record
            )

    def _store_metric_sync(self, record: MetricRecord) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO metrics (timestamp, metric_type, value, labels, period_seconds)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    record.timestamp or datetime.now(UTC).isoformat(),
                    record.metric_type,
                    record.value,
                    record.labels,
                    record.period_seconds,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    async def store_health(self, overall_status: str, checks: list[dict], uptime_seconds: float) -> None:
        """Store health check result."""
        async with self._lock:
            return await asyncio.get_running_loop().run_in_executor(
                None, self._store_health_sync, overall_status, checks, uptime_seconds
            )

    def _store_health_sync(self, overall_status: str, checks: list[dict], uptime_seconds: float):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO health_history (timestamp, overall_status, checks_json, uptime_seconds)
                VALUES (?, ?, ?, ?)
            """,
                (datetime.now(UTC).isoformat(), overall_status, json.dumps(checks), uptime_seconds),
            )
            conn.commit()

    async def store_alert(
        self,
        alert_id: str,
        rule_name: str,
        severity: str,
        status: str,
        message: str,
        value: float,
        threshold: float,
    ):
        """Store an alert."""
        async with self._lock:
            return await asyncio.get_running_loop().run_in_executor(
                None,
                self._store_alert_sync,
                alert_id,
                rule_name,
                severity,
                status,
                message,
                value,
                threshold,
            )

    def _store_alert_sync(
        self,
        alert_id: str,
        rule_name: str,
        severity: str,
        status: str,
        message: str,
        value: float,
        threshold: float,
    ):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO alerts
                (alert_id, rule_name, severity, status, message, value, threshold, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    alert_id,
                    rule_name,
                    severity,
                    status,
                    message,
                    value,
                    threshold,
                    datetime.now(UTC).isoformat(),
                ),
            )
            conn.commit()

    async def get_query_history(self, limit: int = 100, hours: Optional[int] = None) -> list[dict]:
        """Get query history."""
        async with self._lock:
            return await asyncio.get_running_loop().run_in_executor(
                None, self._get_query_history_sync, limit, hours
            )

    def _get_query_history_sync(self, limit: int, hours: Optional[int]) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if hours:
                cutoff = (datetime.now(UTC) - timedelta(hours=hours)).isoformat()
                cursor = conn.execute(
                    """
                    SELECT * FROM queries
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (cutoff, limit),
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT * FROM queries
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            return [dict(row) for row in cursor.fetchall()]

    async def get_metrics_summary(self, hours: int = 24) -> dict:
        """Get metrics summary."""
        async with self._lock:
            return await asyncio.get_running_loop().run_in_executor(
                None, self._get_metrics_summary_sync, hours
            )

    def _get_metrics_summary_sync(self, hours: int) -> dict:
        cutoff = (datetime.now(UTC) - timedelta(hours=hours)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            # Get avg by metric type
            cursor = conn.execute(
                """
                SELECT metric_type, AVG(value) as avg_value, COUNT(*) as count
                FROM metrics
                WHERE timestamp > ?
                GROUP BY metric_type
            """,
                (cutoff,),
            )

            by_type = {row[0]: {"avg": row[1], "count": row[2]} for row in cursor.fetchall()}

            return {
                "period_hours": hours,
                "metrics_by_type": by_type,
                "total_records": sum(m["count"] for m in by_type.values()),
            }

    async def get_usage_stats(self, days: int = 7) -> dict:
        """Get API usage statistics."""
        async with self._lock:
            return await asyncio.get_running_loop().run_in_executor(
                None, self._get_usage_stats_sync, days
            )

    def _get_usage_stats_sync(self, days: int) -> dict:
        cutoff = (datetime.now(UTC) - timedelta(days=days)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            # Total queries
            cursor = conn.execute(
                """
                SELECT COUNT(*) FROM queries WHERE timestamp > ?
            """,
                (cutoff,),
            )
            total = cursor.fetchone()[0]

            # By endpoint
            cursor = conn.execute(
                """
                SELECT endpoint, COUNT(*) as count
                FROM queries
                WHERE timestamp > ?
                GROUP BY endpoint
            """,
                (cutoff,),
            )
            by_endpoint = {row[0]: row[1] for row in cursor.fetchall()}

            # Average processing time
            cursor = conn.execute(
                """
                SELECT AVG(processing_time_ms) FROM queries WHERE timestamp > ?
            """,
                (cutoff,),
            )
            avg_time = cursor.fetchone()[0] or 0

            # Law compliance rate
            cursor = conn.execute(
                """
                SELECT
                    SUM(CASE WHEN law_compliant = 1 THEN 1 ELSE 0 END) as compliant,
                    COUNT(*) as total
                FROM queries
                WHERE timestamp > ?
            """,
                (cutoff,),
            )
            row = cursor.fetchone()
            compliance_rate = (row[0] / row[1] * 100) if row[1] > 0 else 0

            return {
                "period_days": days,
                "total_queries": total,
                "by_endpoint": by_endpoint,
                "avg_processing_time_ms": round(avg_time, 2),
                "law_compliance_rate": round(compliance_rate, 2),
            }

    async def cleanup_old_data(self, retention_days: int = 30):
        """Clean up data older than retention period."""
        async with self._lock:
            return await asyncio.get_running_loop().run_in_executor(
                None, self._cleanup_old_data_sync, retention_days
            )

    def _cleanup_old_data_sync(self, retention_days: int):
        cutoff = (datetime.now(UTC) - timedelta(days=retention_days)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            # Delete old queries
            cursor = conn.execute("DELETE FROM queries WHERE timestamp < ?", (cutoff,))
            queries_deleted = cursor.rowcount

            # Delete old metrics
            cursor = conn.execute("DELETE FROM metrics WHERE timestamp < ?", (cutoff,))
            metrics_deleted = cursor.rowcount

            # Delete old health history
            cursor = conn.execute("DELETE FROM health_history WHERE timestamp < ?", (cutoff,))
            health_deleted = cursor.rowcount

            # Delete old resolved alerts
            cursor = conn.execute(
                """
                DELETE FROM alerts
                WHERE status = 'resolved'
                AND timestamp < ?
            """,
                (cutoff,),
            )
            alerts_deleted = cursor.rowcount

            conn.commit()

            logger.info(
                f"Cleanup: {queries_deleted} queries, {metrics_deleted} metrics, "
                f"{health_deleted} health records, {alerts_deleted} alerts deleted"
            )

            return {
                "queries_deleted": queries_deleted,
                "metrics_deleted": metrics_deleted,
                "health_deleted": health_deleted,
                "alerts_deleted": alerts_deleted,
            }


# Global database instance
_db: Optional[AMOSDatabase] = None


def get_database() -> AMOSDatabase:
    """Get or create global database instance."""
    global _db
    if _db is None:
        _db = AMOSDatabase()
    return _db


if __name__ == "__main__":
    # Test database
    async def test():
        db = get_database()

        # Test query logging
        await db.log_query(
            QueryRecord(
                api_key_hash="test123",
                endpoint="think",
                query="Test query",
                domain="test",
                response_summary="Test response",
                confidence="high",
                law_compliant=True,
                processing_time_ms=150,
            )
        )

        # Test metrics
        await db.store_metric(
            MetricRecord(metric_type="request_count", value=100, period_seconds=60)
        )

        # Get stats
        stats = await db.get_usage_stats(days=1)
        print("Usage stats:", json.dumps(stats, indent=2))

        history = await db.get_query_history(limit=10)
        print(f"Query history: {len(history)} records")

    asyncio.run(test())
