#!/usr/bin/env python3
"""AMOS Unified Orchestrator v2 - Production orchestration system.

Integrates all AMOS components:
- Circuit breaker for resilience
- Workflow engine for task orchestration  
- Async task processor for concurrent execution
- Event bus for communication
- Health monitoring
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class OrchestratorState(Enum):
    """Orchestrator lifecycle states."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class OrchestratorConfig:
    """Configuration for orchestrator."""

    max_concurrent: int = 10
    enable_circuit_breaker: bool = True
    enable_event_bus: bool = True
    enable_metrics: bool = True
    health_check_interval: float = 30.0


@dataclass
class OrchestratorStats:
    """Runtime statistics."""

    tasks_submitted: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    workflows_executed: int = 0
    circuit_breaker_trips: int = 0
    start_time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AMOSUnifiedOrchestrator:
    """Production orchestrator integrating all AMOS components."""

    def __init__(self, config: OrchestratorConfig | None = None):
        self.config = config or OrchestratorConfig()
        self.state = OrchestratorState.IDLE
        self.stats = OrchestratorStats()

        # Component instances
        self._circuit_breaker: Any | None = None
        self._workflow_engine: Any | None = None
        self._task_processor: Any | None = None
        self._event_bus: Any | None = None
        self._metrics: Any | None = None

        self._initialized = False
        self._shutdown_event = asyncio.Event()

    async def initialize(self) -> bool:
        """Initialize all components."""
        if self._initialized:
            return True

        print("[Orchestrator] Initializing...")

        # Initialize circuit breaker
        if self.config.enable_circuit_breaker:
            await self._init_circuit_breaker()

        # Initialize workflow engine
        await self._init_workflow_engine()

        # Initialize task processor
        await self._init_task_processor()

        # Initialize event bus
        if self.config.enable_event_bus:
            await self._init_event_bus()

        self._initialized = True
        self.state = OrchestratorState.RUNNING
        print("[Orchestrator] Initialized and running")
        return True

    async def _init_circuit_breaker(self) -> None:
        """Initialize circuit breaker."""
        try:
            from amos_circuit_breaker import get_circuit_breaker_registry

            self._circuit_breaker = get_circuit_breaker_registry()
            print("  ✓ Circuit breaker ready")
        except ImportError as e:
            print(f"  ⚠ Circuit breaker not available: {e}")

    async def _init_workflow_engine(self) -> None:
        """Initialize workflow engine."""
        try:
            from amos_workflow_engine_v2 import WorkflowEngine

            self._workflow_engine = WorkflowEngine(
                max_concurrent=self.config.max_concurrent
            )
            print("  ✓ Workflow engine ready")
        except ImportError as e:
            print(f"  ⚠ Workflow engine not available: {e}")

    async def _init_task_processor(self) -> None:
        """Initialize task processor."""
        try:
            from amos_async_task_processor import AsyncTaskProcessor

            self._task_processor = AsyncTaskProcessor(
                max_concurrent=self.config.max_concurrent
            )
            print("  ✓ Task processor ready")
        except ImportError as e:
            print(f"  ⚠ Task processor not available: {e}")

    async def _init_event_bus(self) -> None:
        """Initialize event bus."""
        try:
            from amos_event_bus import AMOSEventBus

            self._event_bus = AMOSEventBus()
            print("  ✓ Event bus ready")
        except ImportError as e:
            print(f"  ⚠ Event bus not available: {e}")

    async def submit_task(
        self,
        task_id: str,
        name: str,
        coro: Any,
        use_circuit_breaker: bool = False,
        circuit_name: Optional[str] = None,
    ) -> Any:
        """Submit a task for execution."""
        if not self._initialized:
            raise RuntimeError("Orchestrator not initialized")

        self.stats.tasks_submitted += 1

        if use_circuit_breaker and self._circuit_breaker and circuit_name:
            # Use circuit breaker protection
            breaker = self._circuit_breaker.get_or_create(circuit_name)
            return await breaker.call(lambda: coro)
        elif self._task_processor:
            # Use task processor
            return await self._task_processor.submit(task_id, name, coro)
        else:
            # Direct execution
            return await coro

    async def execute_workflow(
        self,
        definition_id: str,
        inputs: dict[str, Any] | None = None,
    ) -> Any | None:
        """Execute a workflow."""
        if not self._initialized or not self._workflow_engine:
            raise RuntimeError("Workflow engine not available")

        self.stats.workflows_executed += 1
        return await self._workflow_engine.start_workflow(definition_id, inputs)

    def publish_event(self, event_type: str, payload: Any) -> bool:
        """Publish event to bus."""
        if self._event_bus and hasattr(self._event_bus, "publish"):
            try:
                self._event_bus.publish(event_type, payload, source="orchestrator")
                return True
            except Exception:
                pass
        return False

    def get_status(self) -> dict[str, Any]:
        """Get orchestrator status."""
        return {
            "state": self.state.value,
            "initialized": self._initialized,
            "config": {
                "max_concurrent": self.config.max_concurrent,
                "circuit_breaker": self.config.enable_circuit_breaker,
                "event_bus": self.config.enable_event_bus,
            },
            "stats": {
                "tasks_submitted": self.stats.tasks_submitted,
                "tasks_completed": self.stats.tasks_completed,
                "tasks_failed": self.stats.tasks_failed,
                "workflows_executed": self.stats.workflows_executed,
                "circuit_breaker_trips": self.stats.circuit_breaker_trips,
            },
            "components": {
                "circuit_breaker": self._circuit_breaker is not None,
                "workflow_engine": self._workflow_engine is not None,
                "task_processor": self._task_processor is not None,
                "event_bus": self._event_bus is not None,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def shutdown(self) -> None:
        """Graceful shutdown."""
        print("[Orchestrator] Shutting down...")
        self.state = OrchestratorState.SHUTDOWN
        self._shutdown_event.set()

        # Shutdown components
        if self._task_processor:
            await self._task_processor.shutdown()

        print("[Orchestrator] Shutdown complete")


# Global instance
_orchestrator: AMOSUnifiedOrchestrator | None = None


async def get_orchestrator() -> AMOSUnifiedOrchestrator:
    """Get global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AMOSUnifiedOrchestrator()
        await _orchestrator.initialize()
    return _orchestrator


# Example usage
async def example():
    """Example orchestrator usage."""
    orchestrator = await get_orchestrator()

    # Check status
    status = orchestrator.get_status()
    print(f"\nOrchestrator Status:")
    print(json.dumps(status, indent=2))

    # Publish event
    orchestrator.publish_event("test.event", {"data": "example"})

    await orchestrator.shutdown()


if __name__ == "__main__":
    import json

    asyncio.run(example())
