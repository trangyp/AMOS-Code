#!/usr/bin/env python3
"""AMOS Organism Runner — Unified Execution System

Integrates:
- Layer 8 (∞): AMOS Infinite (hyperbundles, sheaves)
- Layer 7 (Ω): Ω Axiomatic (32 axioms, validation)
- Layer 6 (Λ): Integration (Brain, Organism, ClawSpring)
- Layer 5 (Λ): Code Intelligence
- Layer 4 (Λ): Meta-cognition (Coherence Engine)
- Layer 3 (Λ): Memory Systems
- Layer 2 (Λ): Core Cognitive (Time, Energy)
- Layer 1 (Λ): Economic Organism
- Layer 0 (X): Executable Reality (CLI, Interfaces)

Provides:
- Unified organism lifecycle management
- Ethics validation integration
- Health monitoring and diagnostics
- CLI interface for operator control
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from amos_axiom_validator import AxiomValidator, ValidationReport
from amos_coherence_engine import SignalExtractionEngine
from amos_energy import EnergyBudget

# Layer imports
from amos_infinite import AMOSInfinite
from amos_memory import AMOSMemory, MemoryEntry
from amos_time import AMOSTimeEngine


class OrganismState(Enum):
    """Lifecycle states for the AMOS Organism."""

    DORMANT = auto()  # Not initialized
    INITIALIZING = auto()  # Starting up
    CALIBRATING = auto()  # Self-checks, validation
    ACTIVE = auto()  # Fully operational
    DEGRADED = auto()  # Reduced capacity, errors present
    STANDBY = auto()  # Paused, ready to resume
    SHUTDOWN = auto()  # Graceful termination


@dataclass
class OrganismHealth:
    """Health metrics for organism monitoring."""

    timestamp: datetime = field(default_factory=datetime.now)
    state: OrganismState = OrganismState.DORMANT

    # Layer health (0-1 scores)
    layer_health: Dict[int, float] = field(default_factory=dict)

    # System metrics
    coherence_score: float = 0.0
    axiom_compliance: float = 0.0
    memory_utilization: float = 0.0
    energy_efficiency: float = 0.0

    # Active components
    active_processes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


@dataclass
class OrganismConfig:
    """Configuration for organism initialization."""

    name: str = "AMOS-Organism"
    mode: str = "production"  # development, testing, production

    # Layer activation
    enable_layer_8: bool = True  #  Infinite
    enable_layer_7: bool = True  # Omega axioms
    enable_layer_6: bool = True  # Integration
    enable_layer_5: bool = True  # Code intelligence
    enable_layer_4: bool = True  # Meta-cognition
    enable_layer_3: bool = True  # Memory
    enable_layer_2: bool = True  # Core cognitive
    enable_layer_1: bool = True  # Economic
    enable_layer_0: bool = True  # Executable reality

    # Ethics and validation
    ethics_strict: bool = True
    axiom_validation: bool = True

    # Runtime parameters
    health_check_interval: float = 30.0  # seconds
    max_memory_mb: int = 1024
    log_level: str = "INFO"


class AMOSOrganismRunner:
    """Unified runner for the AMOS 8-layer organism.

    Manages lifecycle, health monitoring, and integration
    across all architectural layers.
    """

    def __init__(self, config: Optional[OrganismConfig] = None):
        self.config = config or OrganismConfig()
        self.state = OrganismState.DORMANT
        self.health = OrganismHealth()

        # Layer components (initialized on demand)
        self.layer_8_infinite: Optional[AMOSInfinite] = None
        self.layer_7_validator: Optional[AxiomValidator] = None
        self.layer_4_coherence: Optional[SignalExtractionEngine] = None
        self.layer_3_memory: Optional[AMOSMemory] = None
        self.layer_2_time: Optional[AMOSTimeEngine] = None
        self.layer_2_energy: Optional[EnergyBudget] = None

        # Runtime state
        self._running = False
        self._health_task: asyncio.Task = None
        self._start_time: datetime = None

    async def initialize(self) -> bool:
        """Initialize the organism across all enabled layers.

        Returns True if initialization successful.
        """
        self.state = OrganismState.INITIALIZING
        print(f"[{self.config.name}] Initializing...")

        try:
            # Layer 8: Infinite (hyperbundles)
            if self.config.enable_layer_8:
                print("  → Layer 8 (∞): AMOS Infinite...")
                self.layer_8_infinite = AMOSInfinite()

            # Layer 7: Omega axioms
            if self.config.enable_layer_7:
                print("  → Layer 7 (Ω): Axiom Validator...")
                self.layer_7_validator = AxiomValidator(strict=self.config.axiom_validation)

            # Layer 4: Coherence
            if self.config.enable_layer_4:
                print("  → Layer 4 (Λ): Coherence Engine...")
                self.layer_4_coherence = SignalExtractionEngine()

            # Layer 3: Memory
            if self.config.enable_layer_3:
                print("  → Layer 3 (Λ): Memory Systems...")
                self.layer_3_memory = AMOSMemory()

            # Layer 2: Time and Energy
            if self.config.enable_layer_2:
                print("  → Layer 2 (Λ): Time & Energy...")
                self.layer_2_time = AMOSTimeEngine()
                self.layer_2_energy = EnergyBudget()

            self.state = OrganismState.CALIBRATING
            print(f"[{self.config.name}] Initialization complete.")
            return True

        except Exception as e:
            self.health.errors.append(f"Initialization failed: {e}")
            self.state = OrganismState.DEGRADED
            return False

    async def calibrate(self) -> ValidationReport:
        """Run self-checks and validation across all layers.

        Returns validation report with compliance status.
        """
        print(f"[{self.config.name}] Calibrating...")

        checks = []

        # Axiom validation
        if self.layer_7_validator:
            print("  → Validating axioms...")
            # Create minimal test state
            test_state = {"test": True}
            axiom_check = self.layer_7_validator.check_axiom_1_substrate(test_state)
            checks.append(axiom_check)

        # Coherence check
        if self.layer_4_coherence:
            print("  → Testing coherence...")
            test_msg = "System calibration test"
            analysis = self.layer_4_coherence.analyze(test_msg)
            self.health.coherence_score = analysis.coherence_score

        # Memory check
        if self.layer_3_memory:
            print("  → Checking memory...")
            entry = MemoryEntry(
                content="Calibration entry", entry_type="system", timestamp=time.time()
            )
            self.layer_3_memory.store(entry)
            self.health.memory_utilization = 0.1  # Placeholder

        # Build validation report
        report = ValidationReport(
            timestamp=datetime.now(),
            checks=checks,
            summary={
                "total": len(checks),
                "passed": sum(1 for c in checks if c.passed),
                "failed": sum(1 for c in checks if not c.passed),
                "critical": 0,
                "warnings": 0,
            },
        )

        passed_count = report.summary["passed"]
        total_checks = max(len(checks), 1)
        self.health.axiom_compliance = passed_count / total_checks

        if report.is_valid():
            self.state = OrganismState.ACTIVE
            print(f"[{self.config.name}] Calibration passed. ACTIVE.")
        else:
            self.state = OrganismState.DEGRADED
            print(f"[{self.config.name}] Calibration issues detected. DEGRADED.")

        return report

    async def run(self) -> None:
        """Main organism runtime loop.

        Runs health monitoring and maintains organism state
        until shutdown signal received.
        """
        if self.state != OrganismState.ACTIVE:
            print(f"[{self.config.name}] Cannot run: not in ACTIVE state")
            return

        print(f"[{self.config.name}] Starting runtime...")
        self._running = True
        self._start_time = datetime.now()

        # Start health monitoring
        self._health_task = asyncio.create_task(self._health_monitor())

        try:
            while self._running:
                # Main organism processing loop
                await self._process_cycle()
                await asyncio.sleep(1.0)  # 1 second cycle

        except asyncio.CancelledError:
            print(f"[{self.config.name}] Runtime cancelled")
        finally:
            self._running = False
            if self._health_task:
                self._health_task.cancel()
                try:
                    await self._health_task
                except asyncio.CancelledError:
                    pass

    async def _process_cycle(self) -> None:
        """Single processing cycle - override for custom behavior."""
        # Base implementation does minimal processing
        # Subclasses can override for specific organism behaviors
        pass

    async def _health_monitor(self) -> None:
        """Background health monitoring task."""
        while self._running:
            try:
                self._update_health()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.health.errors.append(f"Health monitor error: {e}")

    def _update_health(self) -> None:
        """Update health metrics."""
        self.health.timestamp = datetime.now()

        # Calculate uptime
        if self._start_time:
            uptime = (datetime.now() - self._start_time).total_seconds()
            self.health.active_processes = [f"uptime: {uptime:.0f}s"]

        # Layer health scores
        self.health.layer_health = {
            8: 1.0 if self.layer_8_infinite else 0.0,
            7: 1.0 if self.layer_7_validator else 0.0,
            4: self.health.coherence_score,
            3: 1.0 - self.health.memory_utilization,
            2: self.health.energy_efficiency,
        }

    def get_health(self) -> OrganismHealth:
        """Get current health snapshot."""
        self._update_health()
        return self.health

    def health_report(self) -> str:
        """Generate formatted health report."""
        h = self.get_health()
        lines = [
            f"=== {self.config.name} Health Report ===",
            f"State: {h.state.name}",
            f"Timestamp: {h.timestamp.isoformat()}",
            "",
            "Layer Health:",
        ]
        for layer, score in sorted(h.layer_health.items()):
            status = "✓" if score > 0.8 else "⚠" if score > 0.5 else "✗"
            lines.append(f"  {status} Layer {layer}: {score:.2f}")

        lines.extend(
            [
                "",
                f"Coherence: {h.coherence_score:.2f}",
                f"Axiom Compliance: {h.axiom_compliance:.2f}",
                f"Memory: {h.memory_utilization:.2f}",
                "",
            ]
        )

        if h.warnings:
            lines.append("Warnings:")
            for w in h.warnings:
                lines.append(f"  ⚠ {w}")

        if h.errors:
            lines.append("Errors:")
            for e in h.errors:
                lines.append(f"  ✗ {e}")

        return "\n".join(lines)

    async def shutdown(self) -> None:
        """Graceful organism shutdown."""
        print(f"[{self.config.name}] Shutting down...")
        self._running = False
        self.state = OrganismState.SHUTDOWN

        if self._health_task:
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass

        # Cleanup layers
        self.layer_8_infinite = None
        self.layer_7_validator = None
        self.layer_4_coherence = None
        self.layer_3_memory = None
        self.layer_2_time = None
        self.layer_2_energy = None

        print(f"[{self.config.name}] Shutdown complete.")

    async def status(self) -> Dict[str, Any]:
        """Get organism status as dictionary."""
        return {
            "name": self.config.name,
            "state": self.state.name,
            "mode": self.config.mode,
            "running": self._running,
            "health": {
                "coherence": self.health.coherence_score,
                "axiom_compliance": self.health.axiom_compliance,
                "memory": self.health.memory_utilization,
            },
            "layers": {
                "infinite": self.layer_8_infinite is not None,
                "omega": self.layer_7_validator is not None,
                "coherence": self.layer_4_coherence is not None,
                "memory": self.layer_3_memory is not None,
                "time_energy": self.layer_2_time is not None,
            },
        }


async def main():
    """CLI entry point for organism runner."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Organism Runner")
    parser.add_argument(
        "--mode",
        default="development",
        choices=["development", "testing", "production"],
        help="Run mode",
    )
    parser.add_argument("--config", type=str, help="JSON config file")
    parser.add_argument(
        "--health-check", type=float, default=30.0, help="Health check interval (seconds)"
    )
    parser.add_argument(
        "--no-axiom-validation", action="store_true", help="Disable axiom validation"
    )

    args = parser.parse_args()

    # Build config
    config = OrganismConfig(
        mode=args.mode,
        health_check_interval=args.health_check,
        axiom_validation=not args.no_axiom_validation,
    )

    if args.config:
        with open(args.config) as f:
            config_data = json.load(f)
            # Override config with file values
            for k, v in config_data.items():
                if hasattr(config, k):
                    setattr(config, k, v)

    # Create and run organism
    organism = AMOSOrganismRunner(config)

    # Initialize
    if not await organism.initialize():
        print("Failed to initialize organism")
        return 1

    # Calibrate
    report = await organism.calibrate()
    if not report.is_valid():
        print("Calibration failed")
        print(report.to_dict())
        return 1

    # Run
    print("\n" + organism.health_report())
    print("\nStarting runtime (Ctrl+C to stop)...\n")

    try:
        await organism.run()
    except KeyboardInterrupt:
        print("\nReceived shutdown signal")
    finally:
        await organism.shutdown()
        print("\nFinal status:")
        print(json.dumps(await organism.status(), indent=2))

    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
