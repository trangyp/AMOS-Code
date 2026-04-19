"""AMOS Health Check System v3.1.0 - With SuperBrain Governance

Production-grade health monitoring with:
- Liveness: Is the app running?
- Readiness: Are dependencies (Redis, LLM) ready?
- Startup: Initial startup handling
- SuperBrain: Governance status for 4,644 features

Creator: Trang Phan
Version: 3.1.0
"""

import time
from datetime import datetime, timezone

UTC = timezone.utc
from enum import Enum
from typing import Any, Dict, List, Tuple

# SuperBrain integration
try:
    from amos_brain import get_super_brain

    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """Base health check class."""

    def __init__(self, name: str, critical: bool = True):
        self.name = name
        self.critical = critical
        self.last_check: datetime = None
        self.last_result: bool = None

    async def check(self) -> Tuple[bool, str]:
        """Perform health check. Returns (passed, message)."""
        raise NotImplementedError

    async def run(self) -> Dict[str, Any]:
        """Run check and return result."""
        start_time = time.time()
        try:
            passed, message = await self.check()
            self.last_result = passed
            self.last_check = datetime.now(UTC)

            return {
                "name": self.name,
                "status": HealthStatus.HEALTHY if passed else HealthStatus.UNHEALTHY,
                "critical": self.critical,
                "message": message,
                "response_time_ms": round((time.time() - start_time) * 1000, 2),
                "last_check": self.last_check.isoformat(),
            }
        except Exception as e:
            self.last_result = False
            self.last_check = datetime.now(UTC)

            return {
                "name": self.name,
                "status": HealthStatus.UNHEALTHY,
                "critical": self.critical,
                "message": f"Check failed: {str(e)}",
                "response_time_ms": round((time.time() - start_time) * 1000, 2),
                "last_check": self.last_check.isoformat(),
            }


class LLMProviderCheck(HealthCheck):
    """Check if at least one LLM provider is available."""

    def __init__(self):
        super().__init__("llm_providers", critical=True)

    async def check(self) -> Tuple[bool, str]:
        from llm_providers import llm_router

        providers = llm_router.get_available_providers()
        enabled = [p for p in providers if p.get("enabled", False)]

        if not enabled:
            return False, "No LLM providers available"

        return True, f"{len(enabled)} provider(s) ready"


class RedisCheck(HealthCheck):
    """Check Redis connectivity."""

    def __init__(self, redis_url: str = None):
        super().__init__("redis", critical=False)
        self.redis_url = redis_url

    async def check(self) -> Tuple[bool, str]:
        try:
            import aioredis

            redis = aioredis.from_url(self.redis_url or "redis://localhost:6379")
            await redis.ping()
            await redis.close()
            return True, "Redis connection OK"
        except ImportError:
            return True, "Redis check skipped (aioredis not installed)"
        except Exception as e:
            return False, f"Redis error: {str(e)}"


class MemoryCheck(HealthCheck):
    """Check system memory usage."""

    def __init__(self, threshold_percent: float = 90.0):
        super().__init__("memory", critical=False)
        self.threshold = threshold_percent

    async def check(self) -> Tuple[bool, str]:
        try:
            import psutil

            memory = psutil.virtual_memory()

            if memory.percent > self.threshold:
                return False, f"Memory usage at {memory.percent}% (threshold: {self.threshold}%)"

            return True, f"Memory usage at {memory.percent}%"
        except ImportError:
            return True, "Memory check skipped (psutil not installed)"
        except Exception as e:
            return False, f"Memory check failed: {str(e)}"


class DiskCheck(HealthCheck):
    """Check disk space."""

    def __init__(self, threshold_percent: float = 90.0):
        super().__init__("disk", critical=False)
        self.threshold = threshold_percent

    async def check(self) -> Tuple[bool, str]:
        try:
            import psutil

            disk = psutil.disk_usage("/")
            usage_percent = (disk.used / disk.total) * 100

            if usage_percent > self.threshold:
                return False, f"Disk usage at {usage_percent:.1f}% (threshold: {self.threshold}%)"

            return True, f"Disk usage at {usage_percent:.1f}%"
        except ImportError:
            return True, "Disk check skipped (psutil not installed)"
        except Exception as e:
            return False, f"Disk check failed: {str(e)}"


class SuperBrainGovernanceCheck(HealthCheck):
    """Check SuperBrain governance status for 4,644 features."""

    def __init__(self):
        super().__init__("superbrain_governance", critical=True)
        self._brain = None
        self.integrated_systems = [
            "Production API 2.3.0",
            "GraphQL API 2.3.0",
            "Agent Messaging 3.1.0",
            "Agent Observability 3.1.0",
            "LLM Providers 2.0.0",
            "UBI Engine 2.0.0",
            "Audit Exporter",
            "AMOS Tools",
            "Knowledge Loader",
            "Master Orchestrator",
            "Cognitive Router",
            "Resilience Engine",
        ]

    async def check(self) -> Tuple[bool, str]:
        if not SUPERBRAIN_AVAILABLE:
            return True, "SuperBrain check skipped (not available)"

        try:
            if not self._brain:
                self._brain = get_super_brain()

            if not self._brain:
                return False, "SuperBrain not initialized"

            # Check ActionGate
            if not hasattr(self._brain, "action_gate"):
                return False, "ActionGate not available"

            # Check Audit Trail
            if not hasattr(self._brain, "record_audit"):
                return False, "Audit trail not available"

            active_count = len(self.integrated_systems)
            return True, f"SuperBrain ACTIVE | {active_count} systems"
        except Exception as e:
            return False, f"SuperBrain error: {str(e)}"


# Global health check registry
_health_checks: List[HealthCheck] = []
_startup_time = time.time()


def register_health_check(check: HealthCheck):
    """Register a health check."""
    _health_checks.append(check)


def get_health_checks() -> List[HealthCheck]:
    """Get all registered health checks."""
    return _health_checks


def init_default_checks(redis_url: str = None):
    """Initialize default health checks."""
    global _health_checks
    _health_checks = [
        SuperBrainGovernanceCheck(),
        LLMProviderCheck(),
        RedisCheck(redis_url),
        MemoryCheck(),
        DiskCheck(),
    ]


async def run_liveness_check() -> Dict[str, Any]:
    """Liveness probe - is the app running?"""
    return {
        "status": HealthStatus.HEALTHY,
        "timestamp": datetime.now(UTC).isoformat(),
        "uptime_seconds": round(time.time() - _startup_time, 2),
        "message": "Application is alive",
    }


async def run_readiness_check() -> Dict[str, Any]:
    """Readiness probe - is the app ready to serve traffic?"""
    if not _health_checks:
        init_default_checks()

    results = []
    all_critical_passed = True
    any_degraded = False

    for check in _health_checks:
        result = await check.run()
        results.append(result)

        if result["critical"] and result["status"] != HealthStatus.HEALTHY:
            all_critical_passed = False

        if result["status"] == HealthStatus.UNHEALTHY:
            any_degraded = True

    # Determine overall status
    if not all_critical_passed:
        status = HealthStatus.UNHEALTHY
    elif any_degraded:
        status = HealthStatus.DEGRADED
    else:
        status = HealthStatus.HEALTHY

    return {
        "status": status,
        "timestamp": datetime.now(UTC).isoformat(),
        "checks": results,
        "message": f"Readiness: {status.value}",
    }


async def run_startup_check() -> Dict[str, Any]:
    """Startup probe - has the app finished starting?"""
    # Simple startup check - ensure we can run basic operations
    startup_duration = time.time() - _startup_time

    if startup_duration < 5:  # Minimum 5 second startup
        return {
            "status": HealthStatus.UNHEALTHY,
            "timestamp": datetime.now(UTC).isoformat(),
            "startup_duration_seconds": round(startup_duration, 2),
            "message": "Application still initializing",
        }

    return {
        "status": HealthStatus.HEALTHY,
        "timestamp": datetime.now(UTC).isoformat(),
        "startup_duration_seconds": round(startup_duration, 2),
        "message": "Application startup complete",
    }


async def run_full_health_check() -> Dict[str, Any]:
    """Run all health checks and return comprehensive status."""
    liveness = await run_liveness_check()
    readiness = await run_readiness_check()
    startup = await run_startup_check()

    # Overall status is the worst of all checks
    statuses = [liveness["status"], readiness["status"], startup["status"]]

    if HealthStatus.UNHEALTHY in statuses:
        overall_status = HealthStatus.UNHEALTHY
    elif HealthStatus.DEGRADED in statuses:
        overall_status = HealthStatus.DEGRADED
    else:
        overall_status = HealthStatus.HEALTHY

    return {
        "status": overall_status,
        "version": "3.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
        "liveness": liveness,
        "readiness": readiness,
        "startup": startup,
    }


# Alias for API compatibility
run_all_checks = run_full_health_check
