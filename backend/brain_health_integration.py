from __future__ import annotations

from typing import Any, Optional

"""Brain Health Integration - Real-time brain system health monitoring.

Integrates clawspring/amos_brain health reporting with FastAPI health endpoints.
Provides production-ready health checks for Kubernetes/Docker.
"""


from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timezone

UTC = UTC

# Import alias modules to set up paths
import clawspring  # noqa: F401
import clawspring.amos_brain  # noqa: F401


@dataclass
class BrainHealthStatus:
    """Brain system health status."""

    overall: str  # healthy, degraded, unhealthy
    master_orchestrator: str
    organism_bridge: str
    task_queue: str
    components_ready: int
    components_total: int
    timestamp: str
    details: dict[str, Any]


class BrainHealthChecker:
    """Production health checker for AMOS brain ecosystem."""

    def __init__(self) -> None:
        self._reporter: Optional[Any] = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize brain health connections."""
        try:
            from brain_status import BrainStatusReporter

            self._reporter = BrainStatusReporter()
            self._initialized = True
            return True
        except Exception as e:
            print(f"[BrainHealth] Init failed: {e}")
            return False

    async def get_health(self) -> BrainHealthStatus:
        """Get comprehensive brain health status."""
        if not self._initialized:
            await self.initialize()

        if not self._reporter:
            return BrainHealthStatus(
                overall="unhealthy",
                master_orchestrator="unavailable",
                organism_bridge="unavailable",
                task_queue="unavailable",
                components_ready=0,
                components_total=3,
                timestamp=datetime.now(timezone.utc).isoformat(),
                details={"error": "BrainStatusReporter not available"},
            )

        try:
            # Check individual components
            master_status = await self._reporter.check_master_orchestrator()
            organism_status = await self._reporter.check_organism_bridge()
            task_queue_status = await self._reporter.check_task_queue()

            components = [master_status, organism_status, task_queue_status]
            ready_count = sum(1 for c in components if c.status == "operational")

            # Determine overall health
            if all(c.status == "operational" for c in components):
                overall = "healthy"
            elif any(c.status == "failed" for c in components):
                overall = "unhealthy"
            else:
                overall = "degraded"

            return BrainHealthStatus(
                overall=overall,
                master_orchestrator=master_status.status,
                organism_bridge=organism_status.status,
                task_queue=task_queue_status.status,
                components_ready=ready_count,
                components_total=len(components),
                timestamp=datetime.now(timezone.utc).isoformat(),
                details={
                    "master_orchestrator": asdict(master_status),
                    "organism_bridge": asdict(organism_status),
                    "task_queue": asdict(task_queue_status),
                },
            )

        except Exception as e:
            return BrainHealthStatus(
                overall="unhealthy",
                master_orchestrator="error",
                organism_bridge="error",
                task_queue="error",
                components_ready=0,
                components_total=3,
                timestamp=datetime.now(timezone.utc).isoformat(),
                details={"error": str(e)},
            )

    async def liveness_check(self) -> dict[str, Any]:
        """Kubernetes liveness probe - is the process running?"""
        return {
            "status": "alive",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "amos-brain",
        }

    async def readiness_check(self) -> dict[str, Any]:
        """Kubernetes readiness probe - is it ready to accept traffic?"""
        health = await self.get_health()

        return {
            "status": health.overall,
            "timestamp": health.timestamp,
            "ready": health.overall == "healthy",
            "components": {
                "ready": health.components_ready,
                "total": health.components_total,
            },
            "checks": {
                "master_orchestrator": health.master_orchestrator,
                "organism_bridge": health.organism_bridge,
                "task_queue": health.task_queue,
            },
        }


# Singleton
_health_checker: Optional[BrainHealthChecker] = None


async def get_brain_health_checker() -> BrainHealthChecker:
    """Get or create singleton health checker."""
    global _health_checker
    if _health_checker is None:
        _health_checker = BrainHealthChecker()
        await _health_checker.initialize()
    return _health_checker


async def get_brain_health() -> BrainHealthStatus:
    """Convenience function to get brain health."""
    checker = await get_brain_health_checker()
    return await checker.get_health()


if __name__ == "__main__":
    import asyncio

    async def main():
        print("=" * 60)
        print("BRAIN HEALTH CHECK")
        print("=" * 60)

        health = await get_brain_health()
        print(f"\nOverall: {health.overall}")
        print(f"Master Orchestrator: {health.master_orchestrator}")
        print(f"Organism Bridge: {health.organism_bridge}")
        print(f"Task Queue: {health.task_queue}")
        print(f"Components: {health.components_ready}/{health.components_total}")
        print(f"\nTimestamp: {health.timestamp}")

        print("\n" + "=" * 60)

    asyncio.run(main())
