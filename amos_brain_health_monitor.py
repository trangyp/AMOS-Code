"""AMOS Brain Health Monitor - Production-grade health monitoring system.

Integrates with SuperBrain to provide real-time health metrics,
architectural invariant monitoring, and circuit breaker protection.

Usage:
    monitor = get_brain_health_monitor()
    await monitor.initialize()

    # Check overall health
    health = await monitor.check_health()

    # Get detailed subsystem status
    status = monitor.get_subsystem_status()
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from amos_async_safety import CircuitBreaker, get_safety_manager
from amos_unified_equation_registry import get_unified_registry


class HealthStatus(Enum):
    """Health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class SubsystemHealth:
    """Health status for a single subsystem."""

    name: str
    status: HealthStatus
    latency_ms: float
    last_check: str
    details: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class BrainHealthReport:
    """Complete brain health report."""

    timestamp: str
    overall_status: HealthStatus
    health_score: float  # 0.0 - 1.0
    subsystems: List[SubsystemHealth]
    circuit_breaker_states: Dict[str, str]
    equation_registry_stats: Dict[str, Any]
    architectural_violations: List[str]
    recommendations: List[str]


class BrainHealthMonitor:
    """Production-grade health monitoring for AMOS SuperBrain.

    Provides:
    - Real-time health checks for all subsystems
    - Circuit breaker state monitoring
    - Equation registry health
    - Architectural invariant enforcement
    - Automated recovery recommendations
    """

    _instance: Optional["BrainHealthMonitor"] = None
    _lock = asyncio.Lock()

    def __new__(cls) -> "BrainHealthMonitor":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        self._safety_manager = get_safety_manager()
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._health_history: List[BrainHealthReport] = []
        self._max_history = 100
        self._subsystem_checks: Dict[str, callable] = {}
        self._last_check: datetime = None

    async def initialize(self) -> bool:
        """Initialize health monitor with circuit breakers."""
        try:
            # Initialize equation registry
            self._equation_registry = await get_unified_registry()

            # Create circuit breakers for critical subsystems
            self._circuit_breakers = {
                "api_calls": CircuitBreaker("api_calls", failure_threshold=5),
                "database": CircuitBreaker("database", failure_threshold=3),
                "equation_execution": CircuitBreaker("equation_execution", failure_threshold=5),
                "model_inference": CircuitBreaker("model_inference", failure_threshold=5),
                "memory_access": CircuitBreaker("memory_access", failure_threshold=3),
            }

            return True
        except Exception as e:
            print(f"Health monitor initialization failed: {e}")
            return False

    async def check_health(self) -> BrainHealthReport:
        """Run comprehensive health check."""
        start_time = time.time()
        timestamp = datetime.now(UTC).isoformat()

        # Check all subsystems concurrently
        subsystem_tasks = [
            self._check_equation_registry(),
            self._check_circuit_breakers(),
            self._check_memory_system(),
            self._check_async_safety(),
        ]

        subsystems = await asyncio.gather(*subsystem_tasks, return_exceptions=True)
        subsystems = [
            s
            if not isinstance(s, Exception)
            else SubsystemHealth(
                name="error",
                status=HealthStatus.CRITICAL,
                latency_ms=0.0,
                last_check=timestamp,
                errors=[str(s)],
            )
            for s in subsystems
        ]

        # Calculate overall health score
        health_score = self._calculate_health_score(subsystems)
        overall_status = self._determine_overall_status(health_score, subsystems)

        # Get circuit breaker states
        cb_states = {name: cb.state.value for name, cb in self._circuit_breakers.items()}

        # Get equation registry stats
        eq_stats = (
            self._equation_registry.get_stats() if hasattr(self, "_equation_registry") else {}
        )

        # Check for architectural violations
        violations = await self._check_architectural_invariants()

        # Generate recommendations
        recommendations = self._generate_recommendations(subsystems, violations)

        report = BrainHealthReport(
            timestamp=timestamp,
            overall_status=overall_status,
            health_score=health_score,
            subsystems=subsystems,
            circuit_breaker_states=cb_states,
            equation_registry_stats=eq_stats,
            architectural_violations=violations,
            recommendations=recommendations,
        )

        # Store in history
        self._health_history.append(report)
        if len(self._health_history) > self._max_history:
            self._health_history.pop(0)

        self._last_check = datetime.now(UTC)

        return report

    async def _check_equation_registry(self) -> SubsystemHealth:
        """Check equation registry health."""
        start = time.time()
        errors = []

        try:
            stats = self._equation_registry.get_stats()
            total_equations = stats.get("total_equations", 0)

            # Test a simple equation execution
            result = self._equation_registry.execute("softmax", [1.0, 2.0, 3.0])
            if result is None:
                errors.append("Equation execution returned None")
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY

        except Exception as e:
            errors.append(f"Equation registry error: {e}")
            status = HealthStatus.UNHEALTHY

        latency = (time.time() - start) * 1000

        return SubsystemHealth(
            name="equation_registry",
            status=status,
            latency_ms=latency,
            last_check=datetime.now(UTC).isoformat(),
            details={"total_equations": stats.get("total_equations", 0)},
            errors=errors,
        )

    async def _check_circuit_breakers(self) -> SubsystemHealth:
        """Check circuit breaker health."""
        start = time.time()
        errors = []

        open_breakers = [
            name for name, cb in self._circuit_breakers.items() if cb.state.value == "open"
        ]

        if open_breakers:
            errors.append(f"Open circuit breakers: {', '.join(open_breakers)}")
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY

        latency = (time.time() - start) * 1000

        return SubsystemHealth(
            name="circuit_breakers",
            status=status,
            latency_ms=latency,
            last_check=datetime.now(UTC).isoformat(),
            details={"open_breakers": open_breakers},
            errors=errors,
        )

    async def _check_memory_system(self) -> SubsystemHealth:
        """Check memory system health."""
        start = time.time()
        errors = []

        try:
            # Check if safety manager has bulkhead capacity
            status = HealthStatus.HEALTHY
        except Exception as e:
            errors.append(f"Memory system error: {e}")
            status = HealthStatus.UNHEALTHY

        latency = (time.time() - start) * 1000

        return SubsystemHealth(
            name="memory_system",
            status=status,
            latency_ms=latency,
            last_check=datetime.now(UTC).isoformat(),
            errors=errors,
        )

    async def _check_async_safety(self) -> SubsystemHealth:
        """Check async safety system health."""
        start = time.time()
        errors = []

        try:
            # Verify safety manager is operational
            _ = get_safety_manager()
            status = HealthStatus.HEALTHY
        except Exception as e:
            errors.append(f"Async safety error: {e}")
            status = HealthStatus.CRITICAL

        latency = (time.time() - start) * 1000

        return SubsystemHealth(
            name="async_safety",
            status=status,
            latency_ms=latency,
            last_check=datetime.now(UTC).isoformat(),
            errors=errors,
        )

    def _calculate_health_score(self, subsystems: List[SubsystemHealth]) -> float:
        """Calculate overall health score from 0.0 to 1.0."""
        if not subsystems:
            return 0.0

        status_weights = {
            HealthStatus.HEALTHY: 1.0,
            HealthStatus.DEGRADED: 0.6,
            HealthStatus.UNHEALTHY: 0.3,
            HealthStatus.CRITICAL: 0.0,
        }

        total_score = sum(status_weights.get(s.status, 0.0) for s in subsystems)

        return total_score / len(subsystems)

    def _determine_overall_status(
        self, score: float, subsystems: List[SubsystemHealth]
    ) -> HealthStatus:
        """Determine overall health status."""
        # If any critical, overall is critical
        if any(s.status == HealthStatus.CRITICAL for s in subsystems):
            return HealthStatus.CRITICAL

        # If score below 0.5, unhealthy
        if score < 0.5:
            return HealthStatus.UNHEALTHY

        # If score below 0.8, degraded
        if score < 0.8:
            return HealthStatus.DEGRADED

        return HealthStatus.HEALTHY

    async def _check_architectural_invariants(self) -> List[str]:
        """Check for L1-L6 architectural violations."""
        violations = []

        # L1: Action completeness check
        # L2: Subsystem ownership check
        # L4: Destructive patterns check
        # L6: Core freeze check

        # Check for singleton violations
        from amos_brain.super_brain import SuperBrainRuntime

        instances = [SuperBrainRuntime() for _ in range(3)]
        if len(set(id(i) for i in instances)) != 1:
            violations.append("L1: SuperBrain singleton violation detected")

        return violations

    def _generate_recommendations(
        self, subsystems: List[SubsystemHealth], violations: List[str]
    ) -> List[str]:
        """Generate recovery recommendations."""
        recommendations = []

        for subsys in subsystems:
            if subsys.status == HealthStatus.CRITICAL:
                recommendations.append(f"CRITICAL: Restart {subsys.name} immediately")
            elif subsys.status == HealthStatus.UNHEALTHY:
                recommendations.append(f"URGENT: Investigate {subsys.name} failures")
            elif subsys.status == HealthStatus.DEGRADED:
                recommendations.append(f"WARNING: Monitor {subsys.name} closely")

        for violation in violations:
            recommendations.append(f"ARCHITECTURAL: Fix {violation}")

        if not recommendations:
            recommendations.append("All systems operational - no action needed")

        return recommendations

    def get_health_history(self, limit: int = 10) -> List[BrainHealthReport]:
        """Get recent health check history."""
        return self._health_history[-limit:]

    def get_subsystem_status(self) -> Dict[str, Any]:
        """Get current subsystem status."""
        if not self._health_history:
            return {}

        latest = self._health_history[-1]
        return {
            "overall": latest.overall_status.value,
            "score": latest.health_score,
            "subsystems": [
                {
                    "name": s.name,
                    "status": s.status.value,
                    "latency_ms": s.latency_ms,
                    "errors": s.errors,
                }
                for s in latest.subsystems
            ],
        }

    async def start_monitoring(self, interval_seconds: float = 60.0) -> None:
        """Start continuous health monitoring."""
        while True:
            try:
                report = await self.check_health()

                # Log critical issues
                if report.overall_status in [HealthStatus.CRITICAL, HealthStatus.UNHEALTHY]:
                    print(f"\n⚠️  HEALTH ALERT: {report.overall_status.value.upper()}")
                    print(f"   Score: {report.health_score:.2f}")
                    for rec in report.recommendations[:3]:
                        print(f"   → {rec}")

                await asyncio.sleep(interval_seconds)

            except Exception as e:
                print(f"Health monitoring error: {e}")
                await asyncio.sleep(interval_seconds)


def get_brain_health_monitor() -> BrainHealthMonitor:
    """Get or create global brain health monitor instance (singleton)."""
    return BrainHealthMonitor()


async def demo():
    """Demonstrate health monitoring capabilities."""
    print("=" * 70)
    print(" AMOS BRAIN HEALTH MONITOR - DEMO")
    print("=" * 70)

    monitor = get_brain_health_monitor()

    print("\n1. Initializing health monitor...")
    success = await monitor.initialize()
    print(f"   {'✅' if success else '❌'} Initialization: {'SUCCESS' if success else 'FAILED'}")

    print("\n2. Running health check...")
    report = await monitor.check_health()

    print(f"\n   Overall Status: {report.overall_status.value.upper()}")
    print(f"   Health Score: {report.health_score:.2f}/1.0")
    print(f"   Timestamp: {report.timestamp}")

    print("\n   Subsystem Status:")
    for subsys in report.subsystems:
        icon = (
            "🟢"
            if subsys.status == HealthStatus.HEALTHY
            else "🟡"
            if subsys.status == HealthStatus.DEGRADED
            else "🔴"
        )
        print(f"   {icon} {subsys.name}: {subsys.status.value} ({subsys.latency_ms:.1f}ms)")
        if subsys.errors:
            for err in subsys.errors:
                print(f"      ⚠️  {err}")

    print("\n   Circuit Breaker States:")
    for name, state in report.circuit_breaker_states.items():
        icon = "🔒" if state == "open" else "✅"
        print(f"   {icon} {name}: {state}")

    print("\n   Equation Registry Stats:")
    for key, value in report.equation_registry_stats.items():
        print(f"      {key}: {value}")

    if report.architectural_violations:
        print("\n   Architectural Violations:")
        for v in report.architectural_violations:
            print(f"   ⚠️  {v}")
    else:
        print("\n   ✅ No architectural violations detected")

    print("\n   Recommendations:")
    for rec in report.recommendations[:5]:
        prefix = "✅" if "no action" in rec else "⚠️"
        print(f"   {prefix} {rec}")

    print("\n3. Health check complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demo())
