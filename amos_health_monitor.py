"""AMOS Health Monitor - Production system health monitoring.

This module provides real-time health checks for all AMOS subsystems,
API endpoints, and critical infrastructure components.
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class HealthStatus:
    """Health status for a component."""

    component: str
    status: str  # healthy, degraded, unhealthy
    last_check: datetime
    response_time_ms: float
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealth:
    """Overall system health snapshot."""

    timestamp: datetime
    overall_status: str
    components: list[HealthStatus]
    uptime_seconds: float
    version: str = "1.0.0"


class HealthMonitor:
    """Monitors health of AMOS production systems."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("AMOS_ORGANISM_OS/system_registry.json")
        self.checks: dict[str, callable] = {}
        self._last_health: Optional[SystemHealth] = None
        self._start_time = time.time()
        self._register_default_checks()

    def _register_default_checks(self):
        """Register default health checks."""
        self.checks["brain"] = self._check_brain
        self.checks["organism"] = self._check_organism
        self.checks["memory"] = self._check_memory
        self.checks["database"] = self._check_database
        self.checks["api"] = self._check_api

    async def check_all(self) -> SystemHealth:
        """Run all health checks."""
        components = []

        for name, check_func in self.checks.items():
            start = time.time()
            try:
                status = await check_func()
                status.response_time_ms = (time.time() - start) * 1000
            except Exception as e:
                status = HealthStatus(
                    component=name,
                    status="unhealthy",
                    last_check=datetime.now(),
                    response_time_ms=(time.time() - start) * 1000,
                    message=f"Check failed: {str(e)}",
                )
            components.append(status)

        # Determine overall status
        unhealthy = sum(1 for c in components if c.status == "unhealthy")
        degraded = sum(1 for c in components if c.status == "degraded")

        if unhealthy > 0:
            overall = "unhealthy"
        elif degraded > 0:
            overall = "degraded"
        else:
            overall = "healthy"

        health = SystemHealth(
            timestamp=datetime.now(),
            overall_status=overall,
            components=components,
            uptime_seconds=time.time() - self._start_time,
        )

        self._last_health = health
        return health

    async def _check_brain(self) -> HealthStatus:
        """Check BRAIN subsystem health."""
        try:
            from amos_brain import get_brain

            brain = get_brain()
            return HealthStatus(
                component="brain",
                status="healthy",
                last_check=datetime.now(),
                response_time_ms=0,
                message="BRAIN subsystem operational",
                details={"loaded": brain is not None},
            )
        except Exception as e:
            return HealthStatus(
                component="brain",
                status="degraded",
                last_check=datetime.now(),
                response_time_ms=0,
                message=f"BRAIN check failed: {e}",
            )

    async def _check_organism(self) -> HealthStatus:
        """Check Organism OS health."""
        try:
            organism_path = Path("AMOS_ORGANISM_OS/system_registry.json")
            if organism_path.exists():
                with open(organism_path) as f:
                    registry = json.load(f)
                return HealthStatus(
                    component="organism",
                    status="healthy",
                    last_check=datetime.now(),
                    response_time_ms=0,
                    message="Organism OS operational",
                    details={"subsystems": len(registry.get("subsystems", []))},
                )
            else:
                return HealthStatus(
                    component="organism",
                    status="unhealthy",
                    last_check=datetime.now(),
                    response_time_ms=0,
                    message="Registry not found",
                )
        except Exception as e:
            return HealthStatus(
                component="organism",
                status="degraded",
                last_check=datetime.now(),
                response_time_ms=0,
                message=f"Organism check failed: {e}",
            )

    async def _check_memory(self) -> HealthStatus:
        """Check memory subsystem health."""
        try:
            from memory import load_index

            entries = load_index()
            return HealthStatus(
                component="memory",
                status="healthy",
                last_check=datetime.now(),
                response_time_ms=0,
                message="Memory subsystem operational",
                details={"entries": len(entries)},
            )
        except Exception as e:
            return HealthStatus(
                component="memory",
                status="degraded",
                last_check=datetime.now(),
                response_time_ms=0,
                message=f"Memory check failed: {e}",
            )

    async def _check_database(self) -> HealthStatus:
        """Check database health."""
        try:
            import sqlite3

            conn = sqlite3.connect("amos.db")
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return HealthStatus(
                component="database",
                status="healthy",
                last_check=datetime.now(),
                response_time_ms=0,
                message="Database connection operational",
            )
        except Exception as e:
            return HealthStatus(
                component="database",
                status="unhealthy",
                last_check=datetime.now(),
                response_time_ms=0,
                message=f"Database check failed: {e}",
            )

    async def _check_api(self) -> HealthStatus:
        """Check API health."""
        # Placeholder for API health check
        return HealthStatus(
            component="api",
            status="healthy",
            last_check=datetime.now(),
            response_time_ms=0,
            message="API endpoint check placeholder",
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert last health check to dictionary."""
        if not self._last_health:
            return {"error": "No health check performed yet"}

        return {
            "timestamp": self._last_health.timestamp.isoformat(),
            "overall_status": self._last_health.overall_status,
            "uptime_seconds": self._last_health.uptime_seconds,
            "version": self._last_health.version,
            "components": [
                {
                    "component": c.component,
                    "status": c.status,
                    "response_time_ms": c.response_time_ms,
                    "message": c.message,
                    "details": c.details,
                }
                for c in self._last_health.components
            ],
        }

    def save_report(self, path: Optional[Path] = None):
        """Save health report to file."""
        path = path or Path("AMOS_ORGANISM_OS/system_health_report.json")
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


# Global health monitor instance
_health_monitor: Optional[HealthMonitor] = None


def get_health_monitor() -> HealthMonitor:
    """Get global health monitor instance."""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor


async def check_health() -> SystemHealth:
    """Quick health check function."""
    monitor = get_health_monitor()
    return await monitor.check_all()


def init_default_health_checks() -> HealthMonitor:
    """Initialize health monitor with default checks."""
    monitor = get_health_monitor()
    return monitor


if __name__ == "__main__":
    # Run health check
    health = asyncio.run(check_health())
    print(f"Overall Status: {health.overall_status}")
    print(f"Uptime: {health.uptime_seconds:.2f}s")
    print("\nComponents:")
    for comp in health.components:
        status_emoji = (
            "🟢" if comp.status == "healthy" else "🟡" if comp.status == "degraded" else "🔴"
        )
        print(f"  {status_emoji} {comp.component}: {comp.status} ({comp.response_time_ms:.2f}ms)")
        if comp.message:
            print(f"     {comp.message}")
