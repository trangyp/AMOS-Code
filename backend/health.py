"""AMOS Production Health Checks

Comprehensive health check system for Docker/Kubernetes deployment.
Implements liveness, readiness, and startup probes.

Usage:
    from backend.health import HealthChecker, health_checker

    # In FastAPI endpoint
    @app.get("/health/live")
    async def liveness():
        return health_checker.liveness()

    @app.get("/health/ready")
    async def readiness():
        return await health_checker.readiness()

Creator: Trang Phan
Version: 1.0.0
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

UTC = timezone.utc
from typing import Any, Dict

import psutil


@dataclass
class HealthStatus:
    """Health check response."""

    status: str  # "healthy" or "unhealthy"
    timestamp: str
    version: str
    uptime_seconds: float
    checks: Dict[str, Any] = field(default_factory=dict)
    details: Dict[str, Any] = None


@dataclass
class ComponentCheck:
    """Individual component health check."""

    name: str
    status: str  # "pass", "fail", "warn"
    response_time_ms: float
    message: str = None
    metadata: Dict[str, Any] = None


class HealthChecker:
    """Production health checker for AMOS."""

    VERSION = "3.0.0"

    def __init__(self):
        self._start_time = time.time()
        self._checks: Dict[str, callable] = {}
        self._last_checks: Dict[str, ComponentCheck] = {}
        self._register_default_checks()

    def _register_default_checks(self) -> None:
        """Register default health checks."""
        self._checks["memory"] = self._check_memory
        self._checks["disk"] = self._check_disk
        self._checks["api"] = self._check_api

    def liveness(self) -> HealthStatus:
        """
        Liveness probe - is the application running?

        Kubernetes uses this to know when to restart the container.
        Should be lightweight and always return 200 if the app is alive.
        """
        return HealthStatus(
            status="healthy",
            timestamp=datetime.now(UTC).isoformat(),
            version=self.VERSION,
            uptime_seconds=time.time() - self._start_time,
            checks={"liveness": "pass"},
        )

    async def readiness(self) -> HealthStatus:
        """
        Readiness probe - is the application ready to accept traffic?

        Kubernetes uses this to know when to send traffic to the pod.
        Should check all dependencies (database, external services, etc.)
        """
        start_time = time.time()
        checks: Dict[str, Any] = {}
        all_passed = True

        # Run all registered checks
        for name, check_fn in self._checks.items():
            try:
                check_start = time.time()
                result = await check_fn() if asyncio.iscoroutinefunction(check_fn) else check_fn()
                response_time = (time.time() - check_start) * 1000

                self._last_checks[name] = result
                checks[name] = {
                    "status": result.status,
                    "response_time_ms": round(response_time, 2),
                    "message": result.message,
                }

                if result.status == "fail":
                    all_passed = False

            except Exception as e:
                checks[name] = {"status": "fail", "error": str(e)}
                all_passed = False

        total_time = time.time() - start_time

        return HealthStatus(
            status="healthy" if all_passed else "unhealthy",
            timestamp=datetime.now(UTC).isoformat(),
            version=self.VERSION,
            uptime_seconds=time.time() - self._start_time,
            checks=checks,
            details={"total_check_time_ms": round(total_time * 1000, 2)},
        )

    def _check_memory(self) -> ComponentCheck:
        """Check memory usage."""
        try:
            memory = psutil.virtual_memory()
            used_percent = memory.percent

            status = "pass"
            message = f"Memory usage: {used_percent:.1f}%"

            if used_percent > 90:
                status = "fail"
                message = f"Critical: Memory usage at {used_percent:.1f}%"
            elif used_percent > 80:
                status = "warn"
                message = f"Warning: Memory usage at {used_percent:.1f}%"

            return ComponentCheck(
                name="memory",
                status=status,
                response_time_ms=0,
                message=message,
                metadata={
                    "used_percent": used_percent,
                    "available_gb": memory.available / (1024**3),
                },
            )
        except Exception as e:
            return ComponentCheck(
                name="memory",
                status="fail",
                response_time_ms=0,
                message=f"Failed to check memory: {e}",
            )

    def _check_disk(self) -> ComponentCheck:
        """Check disk usage."""
        try:
            disk = psutil.disk_usage("/")
            used_percent = disk.percent

            status = "pass"
            message = f"Disk usage: {used_percent:.1f}%"

            if used_percent > 95:
                status = "fail"
                message = f"Critical: Disk usage at {used_percent:.1f}%"
            elif used_percent > 85:
                status = "warn"
                message = f"Warning: Disk usage at {used_percent:.1f}%"

            return ComponentCheck(
                name="disk",
                status=status,
                response_time_ms=0,
                message=message,
                metadata={"used_percent": used_percent, "free_gb": disk.free / (1024**3)},
            )
        except Exception as e:
            return ComponentCheck(
                name="disk", status="fail", response_time_ms=0, message=f"Failed to check disk: {e}"
            )

    async def _check_api(self) -> ComponentCheck:
        """Check API responsiveness."""
        # Simple self-check
        return ComponentCheck(
            name="api", status="pass", response_time_ms=0, message="API is responsive"
        )

    async def _check_database(self) -> ComponentCheck:
        """Check database connectivity."""
        start_time = time.time()

        try:
            from backend.database import check_connection

            ok = await check_connection()
            response_time = (time.time() - start_time) * 1000

            if ok:
                return ComponentCheck(
                    name="database",
                    status="pass",
                    response_time_ms=round(response_time, 2),
                    message="Database connection OK",
                )
            else:
                return ComponentCheck(
                    name="database",
                    status="fail",
                    response_time_ms=round(response_time, 2),
                    message="Database connection failed",
                )
        except Exception as e:
            return ComponentCheck(
                name="database",
                status="fail",
                response_time_ms=(time.time() - start_time) * 1000,
                message=f"Database check error: {e}",
            )

    def enable_database_check(self) -> None:
        """Enable database health check."""
        self._checks["database"] = self._check_database

    def disable_database_check(self) -> None:
        """Disable database health check."""
        self._checks.pop("database", None)

    def add_custom_check(self, name: str, check_fn: callable) -> None:
        """Add a custom health check."""
        self._checks[name] = check_fn

    def get_last_checks(self) -> Dict[str, ComponentCheck]:
        """Get results from last health check run."""
        return self._last_checks.copy()


# Global health checker instance
health_checker = HealthChecker()
