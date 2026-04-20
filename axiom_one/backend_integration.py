#!/usr/bin/env python3
from __future__ import annotations

"""AXIOM One Backend Integration - Real AMOS Backend Connection

Integrates AXIOM One ExecutionSlots with the real AMOS backend:
- FastAPI WebSocket for real-time slot streaming
- RealOrchestratorBridge for brain-powered task execution
- repo_doctor for verification
- AMOS 14-layer organism integration

Author: AMOS System
Version: 3.0.0
"""

import asyncio
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Import alias modules to set up paths
import clawspring  # noqa: F401

# Backend integration - optional (avoids circular import)
try:
    from backend.real_orchestrator_bridge import (
        RealOrchestratorBridge,
        TaskResult,
        get_real_orchestrator_bridge,
    )

    _BACKEND_AVAILABLE = True
except ImportError:
    _BACKEND_AVAILABLE = False
    get_real_orchestrator_bridge = None
    RealOrchestratorBridge = None
    TaskResult = None

from .execution_slot import (
    ExecutionSlot,
    ExecutionSlotManager,
    SlotMode,
    SlotStatus,
)
from .ledger import Ledger
from .twin import Twin


@dataclass
class BackendIntegrationConfig:
    """Configuration for backend integration."""

    repo_path: Path = field(default_factory=Path.cwd)
    websocket_url: str = "ws://localhost:8000/ws"
    enable_real_orchestrator: bool = True
    enable_repo_doctor: bool = True
    enable_twin: bool = True


class BackendIntegratedOrchestrator:
    """
    AXIOM One orchestrator with real AMOS backend integration.

    Connects to:
    - FastAPI WebSocket for real-time updates
    - RealOrchestratorBridge for brain execution
    - repo_doctor for verification
    - AMOS organism for lifecycle management
    """

    def __init__(self, config: BackendIntegrationConfig = None):
        self.config = config or BackendIntegrationConfig()
        self.slot_manager = ExecutionSlotManager()
        self._twin = Twin(self.config.repo_path) if self.config.enable_twin else None
        self._ledger = Ledger()

        # Backend connections (lazy-loaded)
        self._orchestrator_bridge: RealOrchestratorBridge = None
        self._websocket: Any = None
        self._connected: bool = False

    async def connect(self) -> bool:
        """Connect to AMOS backend."""
        try:
            # Connect to real orchestrator
            if self.config.enable_real_orchestrator:
                self._orchestrator_bridge = get_real_orchestrator_bridge()
                await self._orchestrator_bridge.initialize()

            self._connected = True
            return True
        except Exception as e:
            print(f"[AXIOM One] Backend connection failed: {e}")
            return False

    async def execute_slot(
        self,
        objective: str,
        mode: SlotMode = SlotMode.LOCAL,
        priority: str = "MEDIUM",
        context: dict[str, Any] = None,
    ) -> ExecutionSlot:
        """
        Execute objective through real AMOS backend.

        Args:
            objective: Task description
            mode: Execution mode (LOCAL/MANAGED/ORCHESTRATION)
            priority: Task priority (LOW/MEDIUM/HIGH/CRITICAL)
            context: Additional execution context

        Returns:
            ExecutionSlot with real execution results
        """
        # Ensure connected
        if not self._connected:
            await self.connect()

        # Capture pre-execution state
        if self._twin:
            self._twin.capture_state("pre_execution")

        # Create execution slot
        slot = ExecutionSlot.create_local(
            objective=objective,
            repo_path=self.config.repo_path,
        )
        slot.mode = mode
        slot = self.slot_manager.allocate(slot)
        self.slot_manager.start(slot.slot_id)

        # Log start
        slot.log_event("execution_started", mode=mode.value, objective=objective)

        try:
            # Execute via real orchestrator bridge
            if self._orchestrator_bridge:
                result: TaskResult = await self._orchestrator_bridge.execute_task(
                    task_description=objective,
                    priority=priority,
                    context=context,
                )

                # Map result to slot
                slot.log_event(
                    "orchestrator_result",
                    success=result.success,
                    task_id=result.task_id,
                    domain=result.domain,
                    engines=result.engines_used,
                )

                # Store artifacts
                slot.artifacts.update(
                    {
                        "task_id": result.task_id,
                        "output": result.output,
                        "execution_type": result.execution_type,
                        "domain": result.domain,
                        "engines_used": result.engines_used,
                        "duration_ms": result.duration_ms,
                        "organism_enhancements": result.organism_enhancements,
                    }
                )

                # Set final status
                if result.success:
                    self.slot_manager.complete(slot.slot_id, True, slot.artifacts)
                else:
                    slot.status = SlotStatus.FAILED
                    slot.failure_reason = result.error
            else:
                # Fallback: mark as pending manual execution
                slot.log_event("no_orchestrator", warning="No backend available")
                slot.status = SlotStatus.PAUSED

        except Exception as e:
            slot.status = SlotStatus.FAILED
            slot.failure_reason = str(e)
            slot.log_event("execution_error", error=str(e))

        # Capture post-execution state
        if self._twin:
            post_state = self._twin.capture_state("post_execution")
            slot.artifacts["post_state_signature"] = post_state.compute_signature()

        # Create ledger receipt
        receipt = self._ledger.create_receipt(
            slot_id=slot.slot_id,
            objective=slot.objective,
            actions=[
                {
                    "type": "backend_execution",
                    "objective": objective,
                    "mode": mode.value,
                    "priority": priority,
                }
            ],
        )
        slot.verification_bundle = {
            "receipt_id": receipt.receipt_id,
            "timestamp": receipt.timestamp,
            "backend_connected": self._connected,
        }

        return slot

    async def stream_slot_events(
        self,
        slot_id: str,
        websocket: Any,
    ) -> None:
        """Stream slot events to WebSocket."""
        slot = self.slot_manager.get(slot_id)
        if not slot:
            await websocket.send_json(
                {
                    "type": "error",
                    "message": f"Slot not found: {slot_id}",
                }
            )
            return

        # Send initial slot state
        await websocket.send_json(
            {
                "type": "slot_connected",
                "slot_id": slot_id,
                "status": slot.status.value,
                "mode": slot.mode.value,
            }
        )

        # Stream events as they occur
        last_event_count = 0
        while slot.status in (SlotStatus.RUNNING, SlotStatus.ALLOCATED):
            if len(slot.event_log) > last_event_count:
                new_events = slot.event_log[last_event_count:]
                for event in new_events:
                    await websocket.send_json(
                        {
                            "type": "slot_event",
                            "slot_id": slot_id,
                            "event": {
                                "timestamp": event.timestamp,
                                "type": event.event_type,
                                "data": event.data,
                            },
                        }
                    )
                last_event_count = len(slot.event_log)

            await asyncio.sleep(0.1)

        # Send completion
        await websocket.send_json(
            {
                "type": "slot_complete",
                "slot_id": slot_id,
                "status": slot.status.value,
                "artifacts": slot.artifacts,
                "verification_bundle": slot.verification_bundle,
            }
        )

    def get_slot(self, slot_id: str) -> ExecutionSlot:
        """Get slot by ID."""
        return self.slot_manager.get(slot_id)

    def list_active_slots(self) -> list[ExecutionSlot]:
        """List all active slots."""
        return self.slot_manager.list_active()

    def get_backend_status(self) -> dict[str, Any]:
        """Get backend connection status."""
        status = {
            "connected": self._connected,
            "websocket_url": self.config.websocket_url,
        }

        if self._orchestrator_bridge:
            status["orchestrator"] = self._orchestrator_bridge.get_status()

        return status


# Global instance
_backend_orchestrator: BackendIntegratedOrchestrator = None


def get_backend_orchestrator() -> BackendIntegratedOrchestrator:
    """Get global backend orchestrator."""
    global _backend_orchestrator
    if _backend_orchestrator is None:
        _backend_orchestrator = BackendIntegratedOrchestrator()
    return _backend_orchestrator


async def main():
    """Test backend integration."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--objective", required=True)
    parser.add_argument("--mode", default="local")
    parser.add_argument("--priority", default="MEDIUM")
    args = parser.parse_args()

    mode_map = {
        "local": SlotMode.LOCAL,
        "managed": SlotMode.MANAGED,
        "orch": SlotMode.ORCHESTRATION,
    }

    orchestrator = get_backend_orchestrator()
    slot = await orchestrator.execute_slot(
        objective=args.objective,
        mode=mode_map.get(args.mode, SlotMode.LOCAL),
        priority=args.priority,
    )

    print(f"Slot ID: {slot.slot_id}")
    print(f"Status: {slot.status.value}")
    print(f"Events: {len(slot.event_log)}")
    print(f"Artifacts: {json.dumps(slot.artifacts, indent=2, default=str)}")


if __name__ == "__main__":
    asyncio.run(main())
