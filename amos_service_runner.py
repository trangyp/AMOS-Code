#!/usr/bin/env python3
"""AMOS Service Runner - Production service lifecycle manager.

Manages starting, stopping, and monitoring AMOS services:
- Kernel runtime
- API server
- Event bus
- Background workers
- Health monitoring
"""

from __future__ import annotations

import asyncio
import signal
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ServiceStatus(Enum):
    """Service lifecycle states."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class ServiceState:
    """Current state of a service."""

    name: str
    status: ServiceStatus
    start_time: datetime | None = None
    error_count: int = 0
    last_error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceConfig:
    """Configuration for a service."""

    name: str
    factory: Callable[[], Any]
    dependencies: list[str] = field(default_factory=list)
    restart_on_failure: bool = True
    max_restarts: int = 3
    health_check_interval: float = 30.0


class AMOSServiceRunner:
    """Production service runner for AMOS ecosystem."""

    def __init__(self):
        self.services: dict[str, ServiceConfig] = {}
        self.states: dict[str, ServiceState] = {}
        self._instances: dict[str, Any] = {}
        self._tasks: dict[str, asyncio.Task] = {}
        self._shutdown_event = asyncio.Event()
        self._health_check_task: asyncio.Task | None = None

    def register_service(self, config: ServiceConfig) -> None:
        """Register a service to be managed."""
        self.services[config.name] = config
        self.states[config.name] = ServiceState(
            name=config.name,
            status=ServiceStatus.STOPPED,
        )
        print(f"[Runner] Registered service: {config.name}")

    async def start_all(self) -> dict[str, ServiceState]:
        """Start all registered services in dependency order."""
        print("\n[Runner] Starting AMOS services...")
        print("=" * 60)

        # Resolve dependencies
        startup_order = self._resolve_dependencies()

        for service_name in startup_order:
            await self._start_service(service_name)

        # Start health monitoring
        self._health_check_task = asyncio.create_task(self._health_monitor())

        return self.states

    def _resolve_dependencies(self) -> list[str]:
        """Resolve service startup order based on dependencies."""
        resolved: list[str] = []
        visiting: set[str] = set()

        def visit(name: str) -> None:
            if name in resolved:
                return
            if name in visiting:
                raise RuntimeError(f"Circular dependency detected: {name}")

            visiting.add(name)
            config = self.services[name]
            for dep in config.dependencies:
                if dep not in self.services:
                    raise RuntimeError(f"Unknown dependency: {dep}")
                visit(dep)
            visiting.remove(name)
            resolved.append(name)

        for name in self.services:
            visit(name)

        return resolved

    async def _start_service(self, name: str) -> None:
        """Start a single service."""
        config = self.services[name]
        state = self.states[name]

        print(f"[Runner] Starting {name}...")
        state.status = ServiceStatus.STARTING
        state.start_time = datetime.now(timezone.utc)

        try:
            instance = config.factory()
            self._instances[name] = instance
            state.status = ServiceStatus.RUNNING
            print(f"  ✓ {name} started")

        except Exception as e:
            state.status = ServiceStatus.ERROR
            state.last_error = str(e)
            state.error_count += 1
            print(f"  ✗ {name} failed: {e}")

            if config.restart_on_failure and state.error_count < config.max_restarts:
                print(f"  → Restarting {name} (attempt {state.error_count + 1})")
                await asyncio.sleep(1)
                await self._start_service(name)

    async def _health_monitor(self) -> None:
        """Monitor health of all services."""
        while not self._shutdown_event.is_set():
            for name, state in self.states.items():
                if state.status == ServiceStatus.RUNNING:
                    # Perform health check
                    healthy = await self._check_service_health(name)
                    if not healthy:
                        print(f"[Health] {name} is unhealthy")
                        config = self.services[name]
                        if config.restart_on_failure:
                            await self._restart_service(name)

            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=30.0,
                )
            except TimeoutError:
                pass

    async def _check_service_health(self, name: str) -> bool:
        """Check if a service is healthy."""
        instance = self._instances.get(name)
        if instance is None:
            return False

        # Check for health method
        if hasattr(instance, "is_healthy"):
            try:
                result = instance.is_healthy()
                if asyncio.iscoroutine(result):
                    return await result
                return result
            except Exception:
                return False

        return True

    async def _restart_service(self, name: str) -> None:
        """Restart a service."""
        print(f"[Runner] Restarting {name}...")
        await self._stop_service(name)
        await asyncio.sleep(1)
        await self._start_service(name)

    async def _stop_service(self, name: str) -> None:
        """Stop a service."""
        state = self.states[name]
        state.status = ServiceStatus.STOPPING

        instance = self._instances.pop(name, None)
        if instance and hasattr(instance, "stop"):
            try:
                result = instance.stop()
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                print(f"  Error stopping {name}: {e}")

        state.status = ServiceStatus.STOPPED
        state.start_time = None
        print(f"  ✓ {name} stopped")

    async def stop_all(self) -> None:
        """Stop all services gracefully."""
        print("\n[Runner] Stopping AMOS services...")
        print("=" * 60)

        self._shutdown_event.set()

        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        # Stop in reverse dependency order
        for name in reversed(list(self.services.keys())):
            if self.states[name].status == ServiceStatus.RUNNING:
                await self._stop_service(name)

        print("=" * 60)
        print("[Runner] All services stopped")

    def get_status(self) -> dict[str, Any]:
        """Get current status of all services."""
        return {
            "services": [
                {
                    "name": s.name,
                    "status": s.status.value,
                    "start_time": s.start_time.isoformat() if s.start_time else None,
                    "error_count": s.error_count,
                    "last_error": s.last_error,
                }
                for s in self.states.values()
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Example services
def create_kernel_service() -> Any:
    """Factory for kernel service."""
    try:
        from amos_kernel import get_unified_kernel

        return get_unified_kernel()
    except ImportError:
        return None


def create_api_service() -> Any:
    """Factory for API service."""
    try:
        from fastapi import FastAPI

        app = FastAPI(title="AMOS API")
        return app
    except ImportError:
        return None


async def main():
    """Run service runner."""
    runner = AMOSServiceRunner()

    # Register services
    runner.register_service(
        ServiceConfig(
            name="kernel",
            factory=create_kernel_service,
        )
    )

    runner.register_service(
        ServiceConfig(
            name="api",
            factory=create_api_service,
            dependencies=["kernel"],
        )
    )

    # Handle shutdown signals
    def signal_handler(sig, frame):
        print("\n[Runner] Shutdown signal received")
        asyncio.create_task(runner.stop_all())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start services
    await runner.start_all()

    # Keep running
    print("\n[Runner] Services running. Press Ctrl+C to stop.")
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
