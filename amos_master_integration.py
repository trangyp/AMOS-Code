#!/usr/bin/env python3
"""AMOS Master Integration - Unified interface for all AMOS components.

This module provides a single entry point to:
- AMOS Kernel (L0-L5 layers)
- AMOS Brain (cognitive functions)
- AMOS Organism (14 subsystems)
- AMOS API (backend endpoints)
- AMOS CLI (command interface)

All components are lazy-loaded and properly initialized.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypeVar


@dataclass
class AMOSCapabilities:
    """Available AMOS capabilities."""

    kernel: bool = False
    brain: bool = False
    organism: bool = False
    api: bool = False
    cli: bool = False
    event_bus: bool = False
    database: bool = False


@dataclass
class AMOSStatus:
    """Current AMOS system status."""

    initialized: bool = False
    healthy: bool = False
    capabilities: AMOSCapabilities = field(default_factory=AMOSCapabilities)
    components_loaded: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


T = TypeVar("T")


class AMOSMasterIntegration:
    """Unified interface to all AMOS components."""

    def __init__(self, root_path: Path | None = None):
        self.root_path = root_path or Path.cwd()
        self.status = AMOSStatus()
        self._kernel: Any | None = None
        self._brain: Any | None = None
        self._organism: Any | None = None
        self._event_bus: Any | None = None
        self._circuit_breaker: Any | None = None
        self._workflow_engine: Any | None = None
        self._initialized = False

    async def initialize(self) -> AMOSStatus:
        """Initialize all AMOS components."""
        if self._initialized:
            return self.status

        print("[AMOS] Initializing Master Integration...")

        # Initialize kernel
        await self._init_kernel()

        # Initialize brain
        await self._init_brain()

        # Initialize organism
        await self._init_organism()

        # Initialize supporting components
        await self._init_event_bus()
        await self._init_circuit_breaker()
        await self._init_workflow_engine()

        self._initialized = True
        self.status.initialized = True
        self.status.healthy = len(self.status.errors) == 0

        print(f"[AMOS] Initialization complete. Components: {self.status.components_loaded}")
        return self.status

    async def _init_kernel(self) -> None:
        """Initialize AMOS kernel."""
        try:
            from amos_kernel import get_unified_kernel

            self._kernel = get_unified_kernel()
            self.status.capabilities.kernel = True
            self.status.components_loaded.append("kernel")
            print("  ✓ Kernel initialized")
        except ImportError as e:
            self.status.errors.append(f"Kernel: {e}")
            print(f"  ✗ Kernel not available: {e}")

    async def _init_brain(self) -> None:
        """Initialize AMOS brain."""
        try:
            from amos_brain import get_brain

            self._brain = get_brain()
            self.status.capabilities.brain = True
            self.status.components_loaded.append("brain")
            print("  ✓ Brain initialized")
        except ImportError as e:
            self.status.errors.append(f"Brain: {e}")
            print(f"  ✗ Brain not available: {e}")

    async def _init_organism(self) -> None:
        """Initialize AMOS organism."""
        try:
            organism_path = self.root_path / "AMOS_ORGANISM_OS"
            if organism_path.exists():
                self.status.capabilities.organism = True
                self.status.components_loaded.append("organism")
                print("  ✓ Organism directory found")
        except Exception as e:
            self.status.errors.append(f"Organism: {e}")

    async def _init_event_bus(self) -> None:
        """Initialize event bus."""
        try:
            from amos_event_bus import AMOSEventBus

            self._event_bus = AMOSEventBus()
            self.status.capabilities.event_bus = True
            self.status.components_loaded.append("event_bus")
            print("  ✓ Event bus initialized")
        except ImportError as e:
            print(f"  ⚠ Event bus not available: {e}")

    async def _init_circuit_breaker(self) -> None:
        """Initialize circuit breaker."""
        try:
            from amos_circuit_breaker import get_circuit_breaker_registry

            self._circuit_breaker = get_circuit_breaker_registry()
            self.status.components_loaded.append("circuit_breaker")
            print("  ✓ Circuit breaker initialized")
        except ImportError as e:
            print(f"  ⚠ Circuit breaker not available: {e}")

    async def _init_workflow_engine(self) -> None:
        """Initialize workflow engine."""
        try:
            from amos_workflow_engine_v2 import WorkflowEngine

            self._workflow_engine = WorkflowEngine()
            self.status.components_loaded.append("workflow_engine")
            print("  ✓ Workflow engine initialized")
        except ImportError as e:
            print(f"  ⚠ Workflow engine not available: {e}")

    # Public API methods

    def get_kernel(self) -> Any | None:
        """Get AMOS kernel instance."""
        return self._kernel

    def get_brain(self) -> Any | None:
        """Get AMOS brain instance."""
        return self._brain

    def get_event_bus(self) -> Any | None:
        """Get event bus instance."""
        return self._event_bus

    def get_circuit_breaker(self, name: str) -> Any:
        """Get or create circuit breaker."""
        if self._circuit_breaker:
            from amos_circuit_breaker import CircuitBreakerConfig

            return self._circuit_breaker.get_or_create(
                name, CircuitBreakerConfig()
            )
        return None

    async def execute_workflow(
        self,
        definition_id: str,
        inputs: dict[str, Any] | None = None,
    ) -> Any | None:
        """Execute a workflow."""
        if self._workflow_engine:
            return await self._workflow_engine.start_workflow(definition_id, inputs)
        return None

    def publish_event(self, event_type: str, payload: Any) -> bool:
        """Publish event to bus."""
        if self._event_bus and hasattr(self._event_bus, "publish"):
            try:
                self._event_bus.publish(event_type, payload)
                return True
            except Exception:
                pass
        return False

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "initialized": self.status.initialized,
            "healthy": self.status.healthy,
            "capabilities": {
                k: v for k, v in self.status.capabilities.__dict__.items()
            },
            "components_loaded": self.status.components_loaded,
            "error_count": len(self.status.errors),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global instance
_master: AMOSMasterIntegration | None = None


async def get_master_integration() -> AMOSMasterIntegration:
    """Get global AMOS master integration instance."""
    global _master
    if _master is None:
        _master = AMOSMasterIntegration()
        await _master.initialize()
    return _master


def get_master_sync() -> AMOSMasterIntegration | None:
    """Get master integration (sync version, may return uninitialized)."""
    return _master


# Example usage
async def example():
    """Example of using AMOS Master Integration."""
    master = await get_master_integration()

    # Check status
    status = master.get_status()
    print(f"\nAMOS Status: {status}")

    # Access components
    kernel = master.get_kernel()
    brain = master.get_brain()

    # Publish event
    master.publish_event("test.event", {"message": "Hello AMOS"})

    # Get circuit breaker
    breaker = master.get_circuit_breaker("api_service")
    print(f"Circuit breaker: {breaker}")


if __name__ == "__main__":
    asyncio.run(example())
