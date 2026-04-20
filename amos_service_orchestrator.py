#!/usr/bin/env python3
"""AMOS Brain Service Orchestrator - 14-Layer Unified Management.

This module provides unified service orchestration for the AMOS Brain
14-Layer Cognitive OS, managing startup, monitoring, and shutdown
of all organism components.

Architecture:
- Layer 00: Orchestrator (this module)
- Layer 01: Brain (Cognitive engines)
- Layer 02: Senses (Environment scanning)
- Layer 03: Immune (Anomaly detection)
- Layer 04: Blood (Resource management)
- Layer 05: Nerves (Event bus)
- Layer 06: Muscle (Workflow execution)
- Layer 07: Metabolism (Pipeline processing)
- Layer 08: Growth (Self-evolution)
- Layer 09: Social (Multi-agent)
- Layer 10: Memory (Knowledge persistence)
- Layer 11: Legal (Compliance)
- Layer 12: Ethics (Validation)
- Layer 13: Time (Temporal)
- Layer 14: Interfaces (API/CLI)
"""

from __future__ import annotations

import asyncio
import json
import signal
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

UTC = UTC
from pathlib import Path
from typing import Any, Optional


class ServiceStatus(Enum):
    """Service lifecycle states."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    DEGRADED = "degraded"
    ERROR = "error"
    STOPPING = "stopping"


@dataclass
class ServiceState:
    """State of a single service."""

    layer: str
    name: str
    status: ServiceStatus
    pid: int = None
    start_time: float = None
    last_health_check: float = None
    health_score: float = 1.0
    error_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealth:
    """Overall system health snapshot."""

    timestamp: str
    overall_status: str
    services: dict[str, ServiceState]
    active_layers: int
    degraded_layers: int
    error_layers: int
    avg_health_score: float
    uptime_seconds: float


class AMOSServiceOrchestrator:
    """Unified service orchestrator for 14-Layer Cognitive OS."""

    LAYERS = {
        "00_ROOT": {"name": "Orchestrator", "module": None},
        "01_BRAIN": {"name": "Cognitive Brain", "module": "amos_brain.brain_os"},
        "02_SENSES": {"name": "Senses", "module": None},
        "03_IMMUNE": {"name": "Immune System", "module": None},
        "04_BLOOD": {"name": "Blood/Energy", "module": None},
        "05_NERVES": {"name": "Nerves", "module": "amos_event_bus"},
        "06_MUSCLE": {"name": "Muscle", "module": None},
        "07_METABOLISM": {"name": "Metabolism", "module": None},
        "08_GROWTH": {"name": "Growth", "module": None},
        "09_SOCIAL": {"name": "Social", "module": None},
        "10_MEMORY": {"name": "Memory", "module": None},
        "11_LEGAL": {"name": "Legal", "module": None},
        "12_ETHICS": {"name": "Ethics", "module": None},
        "13_TIME": {"name": "Time", "module": None},
        "14_INTERFACES": {"name": "Interfaces", "module": None},
    }

    def __init__(self, root_path: Optional[Path] = None) -> None:
        """Initialize orchestrator."""
        self.root = root_path or Path(__file__).parent
        self.services: dict[str, ServiceState] = {}
        self.running = False
        self.start_time: float = None
        self._shutdown_event = asyncio.Event()

        # Initialize service states
        for layer_id, config in self.LAYERS.items():
            self.services[layer_id] = ServiceState(
                layer=layer_id, name=config["name"], status=ServiceStatus.STOPPED
            )

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def _handle_shutdown(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals gracefully."""
        print(f"\n[ORCHESTRATOR] Received signal {signum}, initiating shutdown...")
        self.running = False
        self._shutdown_event.set()

    async def start_all(self) -> bool:
        """Start all services in dependency order."""
        print("=" * 70)
        print("  AMOS BRAIN SERVICE ORCHESTRATOR v14.0.0")
        print("  Starting 14-Layer Cognitive OS")
        print("=" * 70)

        self.start_time = time.time()
        self.running = True

        # Start sequence: 00, 01, 02, 03, 05, 04, 06, 07, 08, 09, 10, 11, 12, 13, 14
        start_order = [
            "00_ROOT",
            "01_BRAIN",
            "02_SENSES",
            "03_IMMUNE",
            "05_NERVES",
            "04_BLOOD",
            "06_MUSCLE",
            "07_METABOLISM",
            "08_GROWTH",
            "09_SOCIAL",
            "10_MEMORY",
            "11_LEGAL",
            "12_ETHICS",
            "13_TIME",
            "14_INTERFACES",
        ]

        for layer_id in start_order:
            await self._start_service(layer_id)
            await asyncio.sleep(0.1)  # Staggered startup

        print("\n" + "=" * 70)
        print("  STARTUP COMPLETE")
        print("=" * 70)
        self._print_status()

        return True

    async def _start_service(self, layer_id: str) -> None:
        """Start a single service."""
        service = self.services[layer_id]
        config = self.LAYERS[layer_id]

        print(f"\n[ORCHESTRATOR] Starting {layer_id}: {config['name']}")
        service.status = ServiceStatus.STARTING

        try:
            # Simulate service startup
            # In production, this would actually import and start the module
            await asyncio.sleep(0.05)

            service.status = ServiceStatus.RUNNING
            service.start_time = time.time()
            service.pid = 1000 + hash(layer_id) % 9000  # Simulated PID
            service.last_health_check = time.time()

            print(f"  ✓ {config['name']} started (PID: {service.pid})")

        except Exception as e:
            service.status = ServiceStatus.ERROR
            service.error_count += 1
            service.metadata["last_error"] = str(e)
            print(f"  ✗ {config['name']} failed: {e}")

    async def stop_all(self) -> None:
        """Stop all services gracefully."""
        print("\n" + "=" * 70)
        print("  SHUTTING DOWN SERVICES")
        print("=" * 70)

        # Stop in reverse order
        stop_order = list(self.LAYERS.keys())[::-1]

        for layer_id in stop_order:
            service = self.services[layer_id]
            if service.status == ServiceStatus.RUNNING:
                service.status = ServiceStatus.STOPPING
                print(f"[ORCHESTRATOR] Stopping {layer_id}: {service.name}")
                await asyncio.sleep(0.05)
                service.status = ServiceStatus.STOPPED
                print(f"  ✓ {service.name} stopped")

        self.running = False
        print("\n" + "=" * 70)
        print("  SHUTDOWN COMPLETE")
        print("=" * 70)

    async def health_check(self) -> SystemHealth:
        """Perform health check on all services."""
        now = time.time()
        active = degraded = error = 0
        total_health = 0.0

        for service in self.services.values():
            if service.status == ServiceStatus.RUNNING:
                active += 1
                # Simulate health degradation over time
                service.health_score = max(0.0, 1.0 - (now - (service.start_time or now)) / 3600)
                service.last_health_check = now
                total_health += service.health_score

                if service.health_score < 0.5:
                    service.status = ServiceStatus.DEGRADED
                    degraded += 1

            elif service.status == ServiceStatus.ERROR:
                error += 1

        avg_health = total_health / max(active, 1)

        # Determine overall status
        if error > 0:
            overall = "degraded" if active > error else "critical"
        elif degraded > 0:
            overall = "degraded"
        elif active == len(self.LAYERS):
            overall = "healthy"
        else:
            overall = "partial"

        uptime = now - (self.start_time or now)

        return SystemHealth(
            timestamp=datetime.now(UTC).isoformat(),
            overall_status=overall,
            services=self.services.copy(),
            active_layers=active,
            degraded_layers=degraded,
            error_layers=error,
            avg_health_score=avg_health,
            uptime_seconds=uptime,
        )

    def _print_status(self) -> None:
        """Print current system status."""
        running = sum(1 for s in self.services.values() if s.status == ServiceStatus.RUNNING)
        print(f"\nActive Services: {running}/{len(self.LAYERS)}")
        for layer_id, service in self.services.items():
            status_icon = "✓" if service.status == ServiceStatus.RUNNING else "○"
            print(f"  {status_icon} {layer_id}: {service.name} [{service.status.value}]")

    async def run(self) -> None:
        """Main orchestrator loop."""
        await self.start_all()

        # Health check loop
        while self.running:
            try:
                await asyncio.wait_for(self._shutdown_event.wait(), timeout=30.0)
                break  # Shutdown requested
            except TimeoutError:
                # Periodic health check
                health = await self.health_check()
                if health.overall_status != "healthy":
                    print(f"\n[ORCHESTRATOR] Health: {health.overall_status.upper()}")

        await self.stop_all()


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Brain Service Orchestrator")
    parser.add_argument(
        "action",
        choices=["start", "stop", "status", "health"],
        default="start",
        nargs="?",
        help="Orchestrator action",
    )
    parser.add_argument("--daemon", "-d", action="store_true", help="Run as daemon")

    args = parser.parse_args()

    orchestrator = AMOSServiceOrchestrator()

    if args.action == "start":
        try:
            asyncio.run(orchestrator.run())
        except KeyboardInterrupt:
            print("\n[ORCHESTRATOR] Interrupted by user")
            return 0

    elif args.action == "status":
        print("=" * 70)
        print("  AMOS BRAIN SERVICE STATUS")
        print("=" * 70)
        running = sum(
            1 for s in orchestrator.services.values() if s.status == ServiceStatus.RUNNING
        )
        print(f"\nActive Services: {running}/{len(orchestrator.LAYERS)}")
        for layer_id, service in orchestrator.services.items():
            icon = "✓" if service.status == ServiceStatus.RUNNING else "○"
            print(f"  {icon} {layer_id}: {service.name} [{service.status.value}]")

    elif args.action == "health":
        health = asyncio.run(orchestrator.health_check())
        print(
            json.dumps(
                {
                    "timestamp": health.timestamp,
                    "status": health.overall_status,
                    "active_layers": health.active_layers,
                    "degraded_layers": health.degraded_layers,
                    "error_layers": health.error_layers,
                    "avg_health_score": round(health.avg_health_score, 2),
                    "uptime_seconds": round(health.uptime_seconds, 2),
                },
                indent=2,
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
