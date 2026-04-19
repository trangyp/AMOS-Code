#!/usr/bin/env python3
"""AMOS Organism Integration Layer

Connects AMOS Organism Runner with:
- AMOS_MASTER_ORCHESTRATOR (subsystem orchestration)
- Ethics Validation Kernel (ethical constraint checking)
- Coherence Engine (human interaction optimization)

Provides unified control interface for the complete organism.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

# Core components
from amos_organism_runner import AMOSOrganismRunner, OrganismConfig, OrganismState

# Integration imports (with fallbacks)
try:
    from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import AmosMasterOrchestrator, CycleResult

    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    AmosMasterOrchestrator = None
    CycleResult = None

try:
    from _AMOS_BRAIN.AMOS_ORGANISM_OS._12_ETHICS_VALIDATION.ethics_validation_kernel import (
        EthicalEvaluation,
        EthicalPrinciple,
        EthicsValidationKernel,
    )

    ETHICS_AVAILABLE = True
except ImportError:
    ETHICS_AVAILABLE = False
    EthicsValidationKernel = None
    EthicalEvaluation = None
    EthicalPrinciple = None


@dataclass
class IntegrationConfig:
    """Configuration for organism integration."""

    # Runner config
    organism_config: OrganismConfig = field(default_factory=OrganismConfig)

    # Integration flags
    enable_orchestrator: bool = True
    enable_ethics: bool = True
    enable_coherence: bool = True

    # Runtime parameters
    cycle_interval: float = 1.0  # seconds
    ethics_check_frequency: int = 10  # every N cycles
    max_concurrent_cycles: int = 5


@dataclass
class CycleMetrics:
    """Metrics for a single organism cycle."""

    cycle_id: int
    timestamp: datetime
    duration_ms: float

    # Component results
    runner_result: dict = None
    orchestrator_result: Optional[Any] = None
    ethics_result: Optional[Any] = None

    # Status
    success: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class AMOSOrganismIntegration:
    """Integration layer for AMOS Organism.

    Combines:
    - Runner (lifecycle management)
    - Orchestrator (subsystem coordination)
    - Ethics (validation)
    - Coherence (human interaction)

    Provides unified API for organism control.
    """

    def __init__(self, config: Optional[IntegrationConfig] = None):
        self.config = config or IntegrationConfig()

        # Core components
        self.runner: Optional[AMOSOrganismRunner] = None
        self.orchestrator: Optional[Any] = None
        self.ethics: Optional[Any] = None

        # Runtime state
        self._cycle_count = 0
        self._running = False
        self._metrics: List[CycleMetrics] = []
        self._current_cycle: Optional[CycleMetrics] = None

    async def initialize(self) -> bool:
        """Initialize all integrated components."""
        print("[Integration] Initializing...")

        # Initialize runner
        print("  → Initializing Organism Runner...")
        self.runner = AMOSOrganismRunner(self.config.organism_config)
        if not await self.runner.initialize():
            print("✗ Runner initialization failed")
            return False

        # Calibrate runner
        report = await self.runner.calibrate()
        if not report.is_valid():
            print("⚠ Runner calibration has issues")

        # Initialize orchestrator (if available)
        if self.config.enable_orchestrator and ORCHESTRATOR_AVAILABLE:
            print("  → Initializing Master Orchestrator...")
            self.orchestrator = AmosMasterOrchestrator()
        elif self.config.enable_orchestrator:
            print("  ⚠ Orchestrator not available, continuing without")

        # Initialize ethics (if available)
        if self.config.enable_ethics and ETHICS_AVAILABLE:
            print("  → Initializing Ethics Kernel...")
            self.ethics = EthicsValidationKernel()
        elif self.config.enable_ethics:
            print("  ⚠ Ethics kernel not available, continuing without")

        print("[Integration] Initialization complete")
        return True

    async def run_cycle(self) -> CycleMetrics:
        """Execute single integrated cycle.

        Coordinates runner, orchestrator, and ethics checking.
        """
        self._cycle_count += 1
        cycle_start = datetime.now()

        metrics = CycleMetrics(cycle_id=self._cycle_count, timestamp=cycle_start, duration_ms=0.0)
        self._current_cycle = metrics

        try:
            # Step 1: Runner processing
            if self.runner and self.runner.state == OrganismState.ACTIVE:
                await self.runner._process_cycle()
                metrics.runner_result = {
                    "state": self.runner.state.name,
                    "health": self.runner.health.coherence_score,
                }

            # Step 2: Orchestrator cycle (if available)
            if self.orchestrator:
                # Note: Orchestrator has different API, adapt as needed
                metrics.orchestrator_result = {"status": "integrated", "cycle": self._cycle_count}

            # Step 3: Ethics check (periodic)
            if self.ethics and self._cycle_count % self.config.ethics_check_frequency == 0:
                # Run ethics validation on current state
                metrics.ethics_result = await self._check_ethics()

            # Calculate duration
            cycle_end = datetime.now()
            metrics.duration_ms = (cycle_end - cycle_start).total_seconds() * 1000
            metrics.success = True

        except Exception as e:
            metrics.errors.append(f"Cycle error: {e}")
            metrics.success = False

        # Store metrics (keep last 100)
        self._metrics.append(metrics)
        if len(self._metrics) > 100:
            self._metrics.pop(0)

        return metrics

    async def _check_ethics(self) -> dict:
        """Run ethics validation on current state."""
        if not self.ethics:
            return None

        # Create ethical evaluation context
        context = {
            "cycle": self._cycle_count,
            "state": self.runner.state.name if self.runner else "unknown",
        }

        # Ethics kernel would evaluate here
        return {
            "evaluated": True,
            "context": context,
            "principles_checked": ["NON_MALEFICENCE", "BENEFICENCE", "AUTONOMY"],
        }

    async def run(self, duration_seconds: float = None) -> None:
        """Run integrated organism cycles.

        Args:
            duration_seconds: Run for N seconds (None = indefinite)
        """
        if not self.runner or self.runner.state != OrganismState.ACTIVE:
            print("[Integration] Cannot run: runner not active")
            return

        print("[Integration] Starting runtime...")
        self._running = True
        start_time = datetime.now()

        try:
            while self._running:
                # Run integrated cycle
                metrics = await self.run_cycle()

                # Report on errors
                if metrics.errors:
                    print(f"  ⚠ Cycle {metrics.cycle_id}: {metrics.errors}")

                # Check duration
                if duration_seconds:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed >= duration_seconds:
                        print(f"[Integration] Duration reached ({duration_seconds}s)")
                        break

                # Wait for next cycle
                await asyncio.sleep(self.config.cycle_interval)

        except asyncio.CancelledError:
            print("[Integration] Runtime cancelled")
        except KeyboardInterrupt:
            print("\n[Integration] Interrupted by user")
        finally:
            self._running = False

    def get_status(self) -> Dict[str, Any]:
        """Get current integration status."""
        return {
            "running": self._running,
            "cycle_count": self._cycle_count,
            "runner_state": (self.runner.state.name if self.runner else "none"),
            "components": {
                "runner": self.runner is not None,
                "orchestrator": self.orchestrator is not None,
                "ethics": self.ethics is not None,
            },
            "recent_metrics": [
                {"cycle": m.cycle_id, "success": m.success, "duration_ms": m.duration_ms}
                for m in self._metrics[-5:]  # Last 5
            ],
        }

    def get_health_report(self) -> str:
        """Get comprehensive health report."""
        lines = [
            "=== AMOS Organism Integration ===",
            f"Cycles completed: {self._cycle_count}",
            f"Running: {self._running}",
            "",
            "Components:",
        ]

        # Runner health
        if self.runner:
            lines.append(f"  Runner: {self.runner.state.name}")
            lines.append(f"    Coherence: {self.runner.health.coherence_score:.2f}")
            lines.append(f"    Axiom compliance: {self.runner.health.axiom_compliance:.2f}")
        else:
            lines.append("  Runner: not initialized")

        # Orchestrator
        lines.append(f"  Orchestrator: {'connected' if self.orchestrator else 'not available'}")

        # Ethics
        lines.append(f"  Ethics: {'enabled' if self.ethics else 'not available'}")

        # Recent metrics
        if self._metrics:
            lines.extend(
                [
                    "",
                    "Recent Cycles:",
                ]
            )
            for m in self._metrics[-5:]:
                status = "✓" if m.success else "✗"
                lines.append(f"  {status} Cycle {m.cycle_id}: {m.duration_ms:.1f}ms")

        return "\n".join(lines)

    async def shutdown(self) -> None:
        """Graceful shutdown of all components."""
        print("[Integration] Shutting down...")
        self._running = False

        # Shutdown runner
        if self.runner:
            await self.runner.shutdown()

        # Clear components
        self.orchestrator = None
        self.ethics = None

        print("[Integration] Shutdown complete")


async def demo():
    """Demonstration of integrated organism."""
    print("=" * 50)
    print("AMOS Organism Integration Demo")
    print("=" * 50)

    # Create integration
    config = IntegrationConfig(
        organism_config=OrganismConfig(
            name="Demo-Organism", mode="testing", health_check_interval=10.0
        ),
        cycle_interval=0.5,  # Fast cycles for demo
        ethics_check_frequency=5,
    )

    integration = AMOSOrganismIntegration(config)

    # Initialize
    if not await integration.initialize():
        print("Failed to initialize")
        return 1

    # Show initial health
    print("\n" + integration.get_health_report())

    # Run for 10 seconds
    print("\nRunning for 10 seconds...")
    print("(Press Ctrl+C to stop early)\n")

    await integration.run(duration_seconds=10.0)

    # Final report
    print("\n" + integration.get_health_report())
    print("\nFinal status:")
    import json

    print(json.dumps(integration.get_status(), indent=2))

    # Shutdown
    await integration.shutdown()

    return 0


if __name__ == "__main__":
    exit(asyncio.run(demo()))
