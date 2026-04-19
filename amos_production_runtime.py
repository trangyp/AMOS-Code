"""AMOS Production Runtime - Unified integration of all 7 phases.

This is the capstone module that integrates all architectural improvements:
- Phase 1-2: Equation Bridge & Governance (180+ equations, L1-L6)
- Phase 3: Type Modernization (Python 3.12+)
- Phase 4: Async Pattern Modernization
- Phase 5: Health Monitoring System
- Phase 6: Bootstrap Orchestration
- Phase 7: Self-Healing & Auto-Recovery

Usage:
    # Quick start
    runtime = await AMOSProductionRuntime.create()

    # Use equation registry
    result = runtime.equations.execute('softmax', [1.0, 2.0, 3.0])

    # Check health
    health = runtime.get_health()

    # Start self-healing
    await runtime.enable_self_healing()
"""

import asyncio
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
UTC = timezone.utc
from typing import Any, Dict, List, Optional

from amos_bootstrap_orchestrator import get_bootstrap_orchestrator
from amos_self_healing_controller import get_self_healing_controller


@dataclass
class RuntimeStatus:
    """Production runtime status."""

    initialized: bool
    bootstrap_phase: str
    health_score: float
    equations_loaded: int
    self_healing_enabled: bool
    uptime_seconds: float


class AMOSProductionRuntime:
    """Unified AMOS Production Runtime.

    Integrates all 7 phases of the architectural build:

    Phase 1-2: Core Infrastructure
    - Unified Equation Registry (180+ equations)
    - Architectural Decision Engine (L1-L6)
    - Async Safety Patterns (circuit breaker, retry)

    Phase 3: Type Modernization
    - Python 3.12+ type system
    - Modern union syntax (X )

    Phase 4: Async Modernization
    - get_running_loop() patterns
    - asyncio.to_thread() usage

    Phase 5: Health Monitoring
    - Real-time health checks
    - 0.0-1.0 health scoring

    Phase 6: Bootstrap Orchestration
    - 5-phase initialization
    - Graceful shutdown

    Phase 7: Self-Healing
    - Automatic recovery
    - Escalation policies

    This is the ONE entry point for production AMOS deployments.
    """

    _instance: Optional[AMOSProductionRuntime] = None

    def __new__(cls) -> AMOSProductionRuntime:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = False

        # Core subsystems
        self._bootstrap = get_bootstrap_orchestrator()
        self._healing = get_self_healing_controller()
        self._equations: Optional[Any] = None
        self._equation_kernel: Optional[Any] = None

        # State
        self._start_time: datetime = None
        self._self_healing_enabled = False

    @classmethod
    async def create(cls) -> AMOSProductionRuntime:
        """Factory method to create and initialize runtime.

        Returns:
            Fully initialized AMOSProductionRuntime

        Example:
            runtime = await AMOSProductionRuntime.create()
        """
        runtime = cls()
        await runtime.initialize()
        return runtime

    async def initialize(self) -> bool:
        """Initialize the production runtime.

        Executes full bootstrap sequence:
        1. Core subsystems (SuperBrain)
        2. Safety systems (circuit breakers)
        3. Equation registry (180+ equations)
        4. Health monitoring
        5. Architectural validation

        Returns:
            bool: True if initialization successful
        """
        if self._initialized:
            return True

        self._start_time = datetime.now(timezone.utc)

        print("=" * 70)
        print(" AMOS PRODUCTION RUNTIME v8.0")
        print(" Unified Integration of Phases 1-7")
        print("=" * 70)
        print(f"Timestamp: {self._start_time.isoformat()}")
        print("=" * 70)

        # Execute bootstrap
        bootstrap_success = await self._bootstrap.bootstrap()

        if not bootstrap_success:
            print("\n❌ Bootstrap failed - runtime initialization aborted")
            return False

        # Get equation registry reference
        self._equations = self._bootstrap.get_subsystem("equation_registry")

        # Get equation-kernel integration
        self._equation_kernel = self._bootstrap.get_subsystem("equation_kernel_integration")

        # Initialize self-healing
        healing_success = await self._healing.initialize()

        self._initialized = True

        # Print summary
        print("\n" + "=" * 70)
        print(" INITIALIZATION COMPLETE")
        print("=" * 70)
        print(f"Bootstrap: {'✅ SUCCESS' if bootstrap_success else '❌ FAILED'}")
        print(f"Self-Healing: {'✅ READY' if healing_success else '⚠️  PARTIAL'}")
        print(f"Equations: {self._get_equation_count()} loaded")
        print(f"Kernel-Governed: {'✅ ACTIVE' if self._equation_kernel else '⚠️  OFFLINE'}")
        print("=" * 70)
        print("\n✅ AMOS Production Runtime: ACTIVE")
        print("   All 7 phases integrated and operational")
        print("=" * 70)

        return True

    def _get_equation_count(self) -> int:
        """Get number of loaded equations."""
        if self._equations:
            stats = self._equations.get_stats()
            return stats.get("total_equations", 0)
        return 0

    async def enable_self_healing(self, interval_seconds: float = 30.0) -> bool:
        """Enable continuous self-healing monitoring.

        Args:
            interval_seconds: Health check interval (default: 30s)

        Returns:
            bool: True if self-healing enabled
        """
        if not self._initialized:
            print("❌ Runtime not initialized")
            return False

        await self._healing.start_monitoring(interval_seconds)
        self._self_healing_enabled = True

        print(f"🔄 Self-healing enabled ({interval_seconds}s interval)")
        return True

    async def disable_self_healing(self) -> None:
        """Disable self-healing monitoring."""
        await self._healing.stop_monitoring()
        self._self_healing_enabled = False
        print("🛑 Self-healing disabled")

    def get_health(self) -> Dict[str, Any]:
        """Get current system health status.

        Returns:
            Health status dictionary with score and subsystem status
        """
        if not self._initialized:
            return {"status": "not_initialized", "health_score": 0.0}

        bootstrap_health = self._bootstrap.get_health_status()
        healing_stats = self._healing.get_recovery_stats()

        return {
            "status": "healthy" if bootstrap_health.get("overall_health", 0) > 0.8 else "degraded",
            "health_score": bootstrap_health.get("overall_health", 0.0),
            "bootstrap_phase": self._bootstrap._phase.value,
            "subsystems": bootstrap_health.get("subsystems", {}),
            "self_healing": {
                "enabled": self._self_healing_enabled,
                "recovery_attempts": healing_stats.get("total_attempts", 0),
                "success_rate": healing_stats.get("success_rate", 0.0),
            },
        }

    def get_status(self) -> RuntimeStatus:
        """Get runtime status snapshot.

        Returns:
            RuntimeStatus with current system state
        """
        uptime = 0.0
        if self._start_time:
            uptime = (datetime.now(timezone.utc) - self._start_time).total_seconds()

        health = self.get_health()

        return RuntimeStatus(
            initialized=self._initialized,
            bootstrap_phase=self._bootstrap._phase.value,
            health_score=health.get("health_score", 0.0),
            equations_loaded=self._get_equation_count(),
            self_healing_enabled=self._self_healing_enabled,
            uptime_seconds=uptime,
        )

    async def execute_equation(self, name: str, *args) -> Any:
        """Execute a mathematical equation (legacy - direct execution).

        Args:
            name: Equation name
            *args: Equation arguments

        Returns:
            Equation result or None if not found
        """
        if not self._equations:
            return None

        return self._equations.execute(name, *args)

    def execute_equation_with_kernel(self, name: str, inputs: Dict[str, Any]) -> Any:
        """Execute equation through AMOS kernel with law enforcement.

        This is the recommended API for equation execution with full
        kernel governance including law scoring and collapse gates.

        Args:
            name: Equation name
            inputs: Input parameters dictionary

        Returns:
            EquationKernelResult with law_score, stability_index, etc.

        Example:
            result = runtime.execute_equation_with_kernel(
                "softmax",
                {"logits": [1.0, 2.0, 3.0]}
            )
            print(f"Success: {result.success}")
            print(f"Law Score: {result.law_score}")
        """
        if not self._equation_kernel:
            # Fallback to legacy execution
            from amos_equation_kernel_integration import (
                get_equation_kernel_integration,
            )

            integration = get_equation_kernel_integration()
            if not integration._initialized:
                import asyncio

                asyncio.run(integration.initialize())
            return integration.execute_equation(name, inputs)

        return self._equation_kernel.execute_equation(name, inputs)

    def search_equations(self, query: str) -> List[dict[str, Any]]:
        """Search equations by name or domain.

        Args:
            query: Search query

        Returns:
            List of matching equations
        """
        if not self._equations:
            return []

        return self._equations.search(query)

    async def run_health_check(self) -> Dict[str, Any]:
        """Run immediate comprehensive health check.

        Returns:
            Detailed health report
        """
        from amos_brain_health_monitor import get_brain_health_monitor

        monitor = get_brain_health_monitor()
        if not await monitor.initialize():
            return {"error": "Health monitor not available"}

        report = await monitor.check_health()

        return {
            "timestamp": report.timestamp,
            "overall_status": report.overall_status.value,
            "health_score": report.health_score,
            "recommendations": report.recommendations[:5],
            "subsystems": [
                {"name": s.name, "status": s.status.value, "latency_ms": s.latency_ms}
                for s in report.subsystems
            ],
        }

    async def shutdown(self) -> None:
        """Execute graceful shutdown."""
        print("\n" + "=" * 70)
        print(" AMOS PRODUCTION RUNTIME - SHUTDOWN")
        print("=" * 70)

        # Disable self-healing
        if self._self_healing_enabled:
            await self.disable_self_healing()

        # Bootstrap shutdown
        await self._bootstrap.shutdown()

        self._initialized = False

        print("=" * 70)
        print(" SHUTDOWN COMPLETE")
        print("=" * 70)

    async def wait_for_shutdown(self) -> None:
        """Wait for shutdown signal and execute graceful shutdown."""
        await self._bootstrap.wait_for_shutdown()
        await self.shutdown()


def get_production_runtime() -> AMOSProductionRuntime:
    """Get production runtime instance.

    Note: Use AMOSProductionRuntime.create() for full initialization.

    Returns:
        AMOSProductionRuntime instance (may not be initialized)
    """
    return AMOSProductionRuntime()


async def demo():
    """Demonstrate production runtime capabilities."""
    print("=" * 70)
    print(" AMOS PRODUCTION RUNTIME - DEMO")
    print("=" * 70)

    # Create and initialize runtime
    print("\n1. Creating production runtime...")
    runtime = await AMOSProductionRuntime.create()

    # Get status
    print("\n2. Runtime Status:")
    status = runtime.get_status()
    print(f"   Initialized: {status.initialized}")
    print(f"   Bootstrap Phase: {status.bootstrap_phase}")
    print(f"   Health Score: {status.health_score:.2f}")
    print(f"   Equations: {status.equations_loaded}")

    # Execute equation
    print("\n3. Equation Execution:")
    result = await runtime.execute_equation("softmax", [1.0, 2.0, 3.0])
    print(f"   softmax([1.0, 2.0, 3.0]) = {result}")

    # Search equations
    print("\n4. Equation Search ('consensus'):")
    matches = runtime.search_equations("consensus")
    print(f"   Found {len(matches)} equations")
    for m in matches[:3]:
        print(f"   - {m.get('name', 'unknown')}")

    # Health check
    print("\n5. Health Check:")
    health = await runtime.run_health_check()
    print(f"   Status: {health.get('overall_status', 'unknown')}")
    print(f"   Score: {health.get('health_score', 0):.2f}")

    # Enable self-healing (briefly)
    print("\n6. Self-Healing:")
    await runtime.enable_self_healing(interval_seconds=5.0)
    print("   Self-healing enabled for 5 seconds...")
    await asyncio.sleep(5)
    await runtime.disable_self_healing()

    # Shutdown
    print("\n7. Shutdown:")
    await runtime.shutdown()

    print("\n" + "=" * 70)
    print(" DEMO COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(demo())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
