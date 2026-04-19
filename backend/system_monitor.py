from typing import Any, Dict, Optional

"""Production System Monitor for AMOS.

Collects metrics, tracks performance, and exposes Prometheus-compatible metrics.
"""

import asyncio
import time

try:
    import psutil

    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False


import structlog
from fastapi import APIRouter, Response
from prometheus_client import CollectorRegistry, Gauge, generate_latest

from backend.database import engine

logger = structlog.get_logger("amos.monitor")
router = APIRouter(prefix="/metrics", tags=["monitoring"])


class SystemMonitor:
    """Monitor system resources and AMOS performance."""

    def __init__(self):
        self.registry = CollectorRegistry()
        self._init_metrics()
        self._running = False
        self._api_times: Dict[str, list[float]] = {}

    def _init_metrics(self) -> None:
        """Initialize Prometheus metrics."""
        # System metrics
        self.cpu_usage = Gauge(
            "amos_cpu_usage_percent", "Current CPU usage percentage", registry=self.registry
        )
        self.memory_usage = Gauge(
            "amos_memory_usage_bytes", "Current memory usage in bytes", registry=self.registry
        )
        self.memory_total = Gauge(
            "amos_memory_total_bytes", "Total system memory in bytes", registry=self.registry
        )
        self.disk_usage = Gauge(
            "amos_disk_usage_percent", "Current disk usage percentage", registry=self.registry
        )

        # API metrics
        self.api_requests_total = Gauge(
            "amos_api_requests_total",
            "Total API requests",
            ["method", "endpoint"],
            registry=self.registry,
        )
        self.api_response_time = Gauge(
            "amos_api_response_time_seconds",
            "API response time",
            ["endpoint"],
            registry=self.registry,
        )

        # Database metrics
        self.db_pool_size = Gauge(
            "amos_db_pool_size", "Database connection pool size", registry=self.registry
        )
        self.db_active_connections = Gauge(
            "amos_db_active_connections", "Active database connections", registry=self.registry
        )

        # AMOS specific
        self.brain_available = Gauge(
            "amos_brain_available",
            "Brain availability status (1=available, 0=unavailable)",
            registry=self.registry,
        )
        self.active_websockets = Gauge(
            "amos_active_websockets",
            "Number of active WebSocket connections",
            registry=self.registry,
        )

    async def collect_system_metrics(self) -> None:
        """Continuously collect system metrics."""
        if not _PSUTIL_AVAILABLE:
            logger.warning("psutil not available, system metrics disabled")
            return

        while self._running:
            try:
                # CPU usage
                self.cpu_usage.set(psutil.cpu_percent(interval=1))

                # Memory usage
                memory = psutil.virtual_memory()
                self.memory_usage.set(memory.used)
                self.memory_total.set(memory.total)

                # Disk usage
                disk = psutil.disk_usage("/")
                self.disk_usage.set(disk.percent)

                logger.debug("system_metrics_collected")

            except Exception as e:
                logger.error("system_metrics_error", error=str(e))

            await asyncio.sleep(5)

    async def collect_database_metrics(self) -> None:
        """Collect database connection pool metrics."""
        while self._running:
            try:
                pool = engine.pool
                self.db_pool_size.set(pool.size())
                self.db_active_connections.set(pool.checkedout())

                logger.debug("db_metrics_collected")

            except Exception as e:
                logger.error("db_metrics_error", error=str(e))

            await asyncio.sleep(10)

    def record_api_request(self, method: str, endpoint: str, duration_seconds: float) -> None:
        """Record API request metrics."""
        self.api_requests_total.labels(method=method, endpoint=endpoint).inc()

        self.api_response_time.labels(endpoint=endpoint).set(duration_seconds)

    def set_brain_availability(self, available: bool) -> None:
        """Update brain availability metric."""
        self.brain_available.set(1 if available else 0)

    def set_active_websockets(self, count: int) -> None:
        """Update active WebSocket count."""
        self.active_websockets.set(count)

    async def get_prometheus_metrics(self) -> bytes:
        """Get metrics in Prometheus format."""
        return generate_latest(self.registry)

    async def get_health_summary(self) -> Dict[str, Any]:
        """Get summary of system health."""
        health = {"timestamp": time.time(), "system": {}, "database": {}, "amos": {}}

        if _PSUTIL_AVAILABLE:
            health["system"] = {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent,
            }

        try:
            pool = engine.pool
            health["database"] = {"pool_size": pool.size(), "active_connections": pool.checkedout()}
        except Exception:
            health["database"] = {"error": "unable to get pool stats"}

        return health

    def start(self) -> None:
        """Start monitoring loops."""
        self._running = True
        asyncio.create_task(self.collect_system_metrics())
        asyncio.create_task(self.collect_database_metrics())
        logger.info("system_monitor_started")

    def stop(self) -> None:
        """Stop monitoring."""
        self._running = False
        logger.info("system_monitor_stopped")


# Global monitor instance
_monitor: Optional[SystemMonitor] = None


def get_monitor() -> SystemMonitor:
    """Get or create global monitor instance."""
    global _monitor
    if _monitor is None:
        _monitor = SystemMonitor()
    return _monitor


@router.get("/prometheus")
async def prometheus_metrics() -> Response:
    """Prometheus-compatible metrics endpoint."""
    monitor = get_monitor()
    metrics = await monitor.get_prometheus_metrics()
    return Response(content=metrics, media_type="text/plain")


@router.get("/health")
async def health_summary() -> Dict[str, Any]:
    """JSON health summary endpoint."""
    monitor = get_monitor()
    return await monitor.get_health_summary()
