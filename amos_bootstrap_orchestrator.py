"""AMOS Bootstrap Orchestrator - Unified system initialization.

Integrates SuperBrain with new architectural modules:
- Unified Equation Registry (180+ equations)
- Brain Health Monitor (real-time health tracking)
- Async Safety Manager (circuit breakers, retry, bulkhead)
- Architectural Decision Engine (L1-L6 enforcement)

Usage:
    orchestrator = get_bootstrap_orchestrator()
    await orchestrator.bootstrap()

    # Get health status
    health = orchestrator.get_health_status()

    # Graceful shutdown
    await orchestrator.shutdown()
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc, timezone

UTC = UTC
from enum import Enum
from typing import Any, Optional

from amos_async_safety import get_safety_manager
from amos_brain_health_monitor import get_brain_health_monitor
from amos_unified_equation_registry import get_unified_registry

# Configure module logger
logger = logging.getLogger(__name__)


class BootstrapPhase(Enum):
    """Bootstrap phases."""

    IDLE = "idle"
    INITIALIZING = "initializing"
    CANON_INTEGRATION = "canon_integration"
    CORE_SUBSYSTEMS = "core_subsystems"
    SAFETY_SYSTEMS = "safety_systems"
    EQUATION_REGISTRY = "equation_registry"
    HEALTH_MONITORING = "health_monitoring"
    ARCHITECTURAL_VALIDATION = "architectural_validation"
    EQUATION_KERNEL_INTEGRATION = "equation_kernel_integration"
    READY = "ready"
    SHUTTING_DOWN = "shutting_down"
    SHUTDOWN = "shutdown"


@dataclass
class BootstrapStatus:
    """Bootstrap status snapshot."""

    phase: BootstrapPhase
    timestamp: str
    progress_pct: float
    subsystems_ready: list[str]
    subsystems_failed: list[str]
    health_score: float
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class BootstrapOrchestrator:
    """Unified bootstrap orchestrator for AMOS system.

    Manages the initialization sequence:
    1. Core subsystems (SuperBrain)
    2. Safety systems (circuit breakers, retry)
    3. Equation registry (180+ equations)
    4. Health monitoring
    5. Architectural validation (L1-L6)

    Provides:
    - Ordered initialization with dependencies
    - Graceful shutdown handling
    - Health status aggregation
    - Signal handling (SIGTERM, SIGINT)
    """

    _instance: Optional[BootstrapOrchestrator] = None
    _lock = asyncio.Lock()

    def __new__(cls) -> BootstrapOrchestrator:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        self._phase = BootstrapPhase.IDLE
        self._status_history: list[BootstrapStatus] = []
        self._subsystems: dict[str, Any] = {}
        self._shutdown_event = asyncio.Event()
        self._health_monitor: Optional[Any] = None
        self._safety_manager: Optional[Any] = None
        self._equation_registry: Optional[Any] = None

        # Register signal handlers
        self._register_signal_handlers()

    def _register_signal_handlers(self) -> None:
        """Register graceful shutdown signal handlers."""
        try:
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, self._signal_handler)
        except RuntimeError:
            # No running loop, will register on bootstrap
            pass

    def _signal_handler(self) -> None:
        """Handle shutdown signals."""
        print("\n⚠️  Shutdown signal received, initiating graceful shutdown...")
        self._shutdown_event.set()

    async def bootstrap(self) -> bool:
        """Execute full bootstrap sequence.

        Returns:
            bool: True if bootstrap successful
        """
        print("=" * 70)
        print(" AMOS BOOTSTRAP ORCHESTRATOR")
        print("=" * 70)
        print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print("=" * 70)

        start_time = datetime.now(timezone.utc)
        errors = []
        warnings = []

        try:
            # Phase 0: Canon Integration (load canonical definitions)
            await self._update_phase(BootstrapPhase.CANON_INTEGRATION)
            canon_ready = await self._bootstrap_canon_integration()
            if not canon_ready:
                warnings.append("Canon integration partially initialized")

            # Phase 1: Core Subsystems (SuperBrain)
            await self._update_phase(BootstrapPhase.CORE_SUBSYSTEMS)
            core_ready = await self._bootstrap_core_subsystems()
            if not core_ready:
                errors.append("Core subsystems failed to initialize")

            # Phase 2: Safety Systems
            await self._update_phase(BootstrapPhase.SAFETY_SYSTEMS)
            safety_ready = await self._bootstrap_safety_systems()
            if not safety_ready:
                warnings.append("Safety systems partially initialized")

            # Phase 3: Equation Registry
            await self._update_phase(BootstrapPhase.EQUATION_REGISTRY)
            eq_ready = await self._bootstrap_equation_registry()
            if not eq_ready:
                warnings.append("Equation registry partially initialized")

            # Phase 4: Health Monitoring
            await self._update_phase(BootstrapPhase.HEALTH_MONITORING)
            health_ready = await self._bootstrap_health_monitoring()
            if not health_ready:
                warnings.append("Health monitoring partially initialized")

            # Phase 5: Architectural Validation
            await self._update_phase(BootstrapPhase.ARCHITECTURAL_VALIDATION)
            arch_ready = await self._bootstrap_architectural_validation()
            if not arch_ready:
                warnings.append("Architectural validation partially complete")

            # Phase 6: Equation-Kernel Integration (CRITICAL)
            await self._update_phase(BootstrapPhase.EQUATION_KERNEL_INTEGRATION)
            eq_kernel_ready = await self._bootstrap_equation_kernel_integration()
            if not eq_kernel_ready:
                warnings.append("Equation-kernel integration partially initialized")

            # Calculate final status
            all_ready = core_ready and eq_kernel_ready  # Core + eq-kernel must be ready
            progress = self._calculate_progress()

            await self._update_phase(BootstrapPhase.READY if all_ready else BootstrapPhase.IDLE)

            # Record status
            status = BootstrapStatus(
                phase=self._phase,
                timestamp=datetime.now(timezone.utc).isoformat(),
                progress_pct=progress,
                subsystems_ready=list(self._subsystems.keys()),
                subsystems_failed=[],
                health_score=progress,
                errors=errors,
                warnings=warnings,
            )
            self._status_history.append(status)

            # Print summary
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            print("\n" + "=" * 70)
            print(f" BOOTSTRAP {'COMPLETE' if all_ready else 'PARTIAL'} ({elapsed:.2f}s)")
            print("=" * 70)
            print(f"Status: {self._phase.value}")
            print(f"Progress: {progress:.1%}")
            print(f"Subsystems Ready: {len(self._subsystems)}")

            if errors:
                print(f"\n❌ Errors ({len(errors)}):")
                for e in errors[:3]:
                    print(f"   - {e}")

            if warnings:
                print(f"\n⚠️  Warnings ({len(warnings)}):")
                for w in warnings[:3]:
                    print(f"   - {w}")

            print("=" * 70)

            return all_ready

        except Exception as e:
            errors.append(f"Bootstrap failed: {e}")
            await self._update_phase(BootstrapPhase.IDLE)

            status = BootstrapStatus(
                phase=self._phase,
                timestamp=datetime.now(timezone.utc).isoformat(),
                progress_pct=0.0,
                subsystems_ready=[],
                subsystems_failed=list(self._subsystems.keys()),
                health_score=0.0,
                errors=errors,
                warnings=warnings,
            )
            self._status_history.append(status)

            print(f"\n❌ Bootstrap failed: {e}")
            return False

    async def _bootstrap_canon_integration(self) -> bool:
        """Initialize AMOS Canon integration."""
        print("\n[Phase 0/6] Canon Integration (Canonical Definitions)")
        print("-" * 50)

        try:
            from amos_canon_integration import initialize_canon

            canon_ready = await initialize_canon()

            if canon_ready:
                from amos_canon_integration import get_canon_loader

                loader = get_canon_loader()
                status = loader.get_status()

                if status:
                    print("  ✅ Canon Integration: ACTIVE")
                    print(f"     Terms: {status.total_terms}")
                    print(f"     Agents: {status.total_agents}")
                    print(f"     Engines: {status.total_engines}")

                self._subsystems["canon_loader"] = loader
                return True
            else:
                print("  ⚠️  Canon Integration: PARTIAL")
                return False

        except Exception as e:
            print(f"  ⚠️  Canon integration error: {e}")
            return False

    async def _bootstrap_core_subsystems(self) -> bool:
        """Initialize core SuperBrain subsystems."""
        print("\n[Phase 1/6] Core Subsystems (SuperBrain)")
        print("-" * 50)

        try:
            # Initialize SuperBrain
            from amos_brain import get_super_brain, initialize_super_brain

            super_brain = get_super_brain()

            if initialize_super_brain():
                self._subsystems["super_brain"] = super_brain
                print("  ✅ SuperBrain Runtime: ACTIVE")
                print(f"     Brain ID: {super_brain.brain_id}")
                print(f"     Status: {super_brain.status}")
                return True
            else:
                print("  ❌ SuperBrain Runtime: FAILED")
                return False

        except Exception as e:
            print(f"  ❌ Core subsystems error: {e}")
            return False

    async def _bootstrap_safety_systems(self) -> bool:
        """Initialize async safety systems."""
        print("\n[Phase 2/6] Safety Systems (Circuit Breakers, Retry)")
        print("-" * 50)

        try:
            # Initialize safety manager
            self._safety_manager = get_safety_manager()

            # Create default circuit breakers
            from amos_async_safety import CircuitBreaker

            breakers = {
                "api_calls": CircuitBreaker("api_calls", failure_threshold=5),
                "database": CircuitBreaker("database", failure_threshold=3),
                "equation_execution": CircuitBreaker("equation_execution", failure_threshold=5),
                "model_inference": CircuitBreaker("model_inference", failure_threshold=5),
                "external_services": CircuitBreaker("external_services", failure_threshold=3),
            }

            for name, cb in breakers.items():
                self._safety_manager.register_circuit_breaker(cb)
                print(f"  ✅ Circuit Breaker '{name}': CLOSED")

            self._subsystems["safety_manager"] = self._safety_manager
            return True

        except Exception as e:
            print(f"  ⚠️  Safety systems error: {e}")
            return False

    async def _bootstrap_equation_registry(self) -> bool:
        """Initialize unified equation registry."""
        print("\n[Phase 3/6] Equation Registry (180+ equations)")
        print("-" * 50)

        try:
            # Initialize equation registry
            self._equation_registry = await get_unified_registry()

            stats = self._equation_registry.get_stats()
            total = stats.get("total_equations", 0)

            self._subsystems["equation_registry"] = self._equation_registry

            print("  ✅ Equation Registry: ACTIVE")
            print(f"     Total Equations: {total}")
            print(f"     Phases: {len(stats.get('by_phase', {}))}")

            # Test a simple equation
            result = self._equation_registry.execute("softmax", [1.0, 2.0, 3.0])
            if result is not None:
                print("     Test Execution: PASS")

            return True

        except Exception as e:
            print(f"  ⚠️  Equation registry error: {e}")
            return False

    async def _bootstrap_health_monitoring(self) -> bool:
        """Initialize health monitoring system."""
        print("\n[Phase 4/6] Health Monitoring")
        print("-" * 50)

        try:
            # Initialize health monitor
            self._health_monitor = get_brain_health_monitor()

            if await self._health_monitor.initialize():
                self._subsystems["health_monitor"] = self._health_monitor

                # Run initial health check
                report = await self._health_monitor.check_health()

                print("  ✅ Health Monitor: ACTIVE")
                print(f"     Overall Status: {report.overall_status.value}")
                print(f"     Health Score: {report.health_score:.2f}/1.0")

                if report.recommendations:
                    print(f"     Recommendations: {len(report.recommendations)}")

                return True
            else:
                print("  ⚠️  Health Monitor: PARTIAL")
                return False

        except Exception as e:
            print(f"  ⚠️  Health monitoring error: {e}")
            return False

    async def _bootstrap_architectural_validation(self) -> bool:
        """Initialize architectural validation (L1-L6)."""
        print("\n[Phase 5/6] Architectural Validation (L1-L6)")
        print("-" * 50)

        try:
            # Run architectural decision engine
            from amos_architectural_decision_engine import (
                Severity,
                get_architectural_decision_engine,
            )

            engine = get_architectural_decision_engine()
            violations = engine.analyze()

            critical = [v for v in violations if v.severity == Severity.CRITICAL]
            high = [v for v in violations if v.severity == Severity.HIGH]

            if critical:
                print(f"  ⚠️  {len(critical)} CRITICAL violations detected")
            if high:
                print(f"  ⚠️  {len(high)} HIGH severity violations")

            if not critical and not high:
                print("  ✅ Architecture: COMPLIANT (L1-L6)")
            else:
                print(f"  ⚠️  Architecture: {len(critical + high)} violations")

            self._subsystems["architectural_engine"] = engine
            return True

        except Exception as e:
            print(f"  ⚠️  Architectural validation error: {e}")
            return False

    async def _bootstrap_equation_kernel_integration(self) -> bool:
        """Initialize equation-kernel integration layer."""
        print("\n[Phase 6/6] Equation-Kernel Integration (Law Enforcement)")
        print("-" * 50)

        try:
            # Initialize equation-kernel integration
            from amos_equation_kernel_integration import (
                get_equation_kernel_integration,
            )

            integration = get_equation_kernel_integration()
            success = await integration.initialize()

            if success:
                self._subsystems["equation_kernel_integration"] = integration

                stats = integration.get_stats()
                print("  ✅ Equation-Kernel Integration: ACTIVE")
                print(f"     Total Executions: {stats.get('total_executions', 0)}")
                print("     Law Enforcement: ENABLED (L = I × S)")
                print("     Collapse Gates: ENABLED (σ = Ω/K)")

                # Test kernel-governed execution
                result = integration.execute_equation(
                    equation_name="softmax",
                    inputs={"logits": [1.0, 2.0, 3.0]},
                    mode=integration.EquationExecutionMode.KERNEL_GOVERNED,
                )
                if result.success:
                    print("     Test Kernel Execution: PASS")
                    print(f"     Law Score: {result.law_score:.4f}")

                return True
            else:
                print("  ⚠️  Equation-Kernel Integration: PARTIAL")
                return False

        except Exception as e:
            print(f"  ⚠️  Equation-kernel integration error: {e}")
            return False

    async def _update_phase(self, phase: BootstrapPhase) -> None:
        """Update bootstrap phase."""
        self._phase = phase
        print(f"\n  → Phase: {phase.value}")

    def _calculate_progress(self) -> float:
        """Calculate bootstrap progress percentage."""
        expected_subsystems = 7  # canon, core, safety, equations, health, architecture, eq-kernel
        actual = len(self._subsystems)
        return min(actual / expected_subsystems, 1.0)

    def get_health_status(self) -> dict[str, Any]:
        """Get current health status from all subsystems."""
        status = {"phase": self._phase.value, "subsystems": {}, "overall_health": 0.0}

        # Get health from health monitor if available
        if self._health_monitor:
            try:
                subsystem_status = self._health_monitor.get_subsystem_status()
                status["subsystems"] = subsystem_status
                status["overall_health"] = subsystem_status.get("score", 0.0)
            except Exception:
                pass

        return status

    async def shutdown(self) -> None:
        """Execute graceful shutdown."""
        print("\n" + "=" * 70)
        print(" GRACEFUL SHUTDOWN INITIATED")
        print("=" * 70)

        await self._update_phase(BootstrapPhase.SHUTTING_DOWN)

        # Shutdown in reverse order
        shutdown_order = [
            "health_monitor",
            "equation_registry",
            "safety_manager",
            "architectural_engine",
            "super_brain",
            "canon_loader",
        ]

        for name in shutdown_order:
            if name in self._subsystems:
                try:
                    subsystem = self._subsystems[name]

                    # Check if subsystem has shutdown method
                    if hasattr(subsystem, "shutdown"):
                        if asyncio.iscoroutinefunction(subsystem.shutdown):
                            await subsystem.shutdown()
                        else:
                            subsystem.shutdown()

                    print(f"  ✅ {name}: shutdown complete")

                except Exception as e:
                    print(f"  ⚠️  {name}: shutdown error ({e})")

        self._subsystems.clear()
        await self._update_phase(BootstrapPhase.SHUTDOWN)

        print("=" * 70)
        print(" SHUTDOWN COMPLETE")
        print("=" * 70)

    async def wait_for_shutdown(self) -> None:
        """Wait for shutdown signal."""
        await self._shutdown_event.wait()
        await self.shutdown()

    def get_subsystem(self, name: str) -> Optional[Any]:
        """Get initialized subsystem by name."""
        return self._subsystems.get(name)


def get_bootstrap_orchestrator() -> BootstrapOrchestrator:
    """Get or create global bootstrap orchestrator instance (singleton)."""
    return BootstrapOrchestrator()


async def demo():
    """Demonstrate bootstrap orchestration."""
    print("=" * 70)
    print(" AMOS BOOTSTRAP ORCHESTRATOR - DEMO")
    print("=" * 70)

    orchestrator = get_bootstrap_orchestrator()

    # Bootstrap the system
    success = await orchestrator.bootstrap()

    if success:
        print("\n✅ Bootstrap successful!")

        # Get health status
        health = orchestrator.get_health_status()
        print("\nHealth Status:")
        print(f"  Phase: {health['phase']}")
        print(f"  Overall Health: {health['overall_health']:.2f}")

        # Keep running for a moment
        print("\n⏳ Running for 2 seconds...")
        await asyncio.sleep(2)

        # Graceful shutdown
        await orchestrator.shutdown()
    else:
        print("\n❌ Bootstrap failed!")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(demo())
    sys.exit(exit_code)
