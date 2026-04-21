"""Agent Monitor API - Real-time agent execution monitoring.

Live monitoring of agents spawned via Agent Fabric Kernel with:
- Real-time status updates
- Budget tracking
- Action history
- Performance metrics
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# Add repo root to path
_REPO_ROOT = Path(__file__).parent.parent.parent.resolve()
try:
    from amos_brain.agent_fabric_kernel import get_agent_fabric_kernel
    from amos_brain.facade import BrainClient

    _BRAIN_AVAILABLE = True
except ImportError:
    _BRAIN_AVAILABLE = False
    BrainClient = None

router = APIRouter(prefix="/agent-monitor", tags=["Agent Monitor"])

# Active monitoring sessions
_monitor_sessions: dict[str, dict[str, Any]] = {}


@dataclass
class AgentMetrics:
    """Real-time agent metrics."""

    agent_id: str
    run_id: str
    phase: str
    actions_count: int
    budget_spent: float
    budget_remaining: float
    execution_time_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentMonitor:
    """Real-time agent monitoring with brain integration."""

    def __init__(self):
        self.subscribers: dict[str, set[WebSocket]] = {}
        self.metrics_history: dict[str, list[AgentMetrics]] = {}
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self):
        """Start monitoring loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())

    async def stop(self):
        """Stop monitoring loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def subscribe(self, run_id: str, websocket: WebSocket):
        """Subscribe to agent updates."""
        if run_id not in self.subscribers:
            self.subscribers[run_id] = set()
        self.subscribers[run_id].add(websocket)

    def unsubscribe(self, run_id: str, websocket: WebSocket):
        """Unsubscribe from agent updates."""
        if run_id in self.subscribers:
            self.subscribers[run_id].discard(websocket)

    async def _monitor_loop(self):
        """Main monitoring loop - polls agent status."""
        while self._running:
            try:
                # Check all subscribed agents
                for run_id, websockets in list(self.subscribers.items()):
                    if not websockets:
                        continue

                    # Get current status from brain
                    if _BRAIN_AVAILABLE and BrainClient:
                        client = BrainClient(repo_path=str(_REPO_ROOT))
                        status = client.get_agent_run(run_id)

                        if status:
                            # Build metrics
                            metrics = AgentMetrics(
                                agent_id=status.get("agent_class", "unknown"),
                                run_id=run_id,
                                phase=status.get("phase", "unknown"),
                                actions_count=status.get("actions_count", 0),
                                budget_spent=status.get("budget_spent", 0.0),
                                budget_remaining=status.get("budget_remaining", 0.0),
                                execution_time_ms=0.0,  # Calculate from timestamps
                            )

                            # Store history
                            if run_id not in self.metrics_history:
                                self.metrics_history[run_id] = []
                            self.metrics_history[run_id].append(metrics)

                            # Keep only last 100 data points
                            self.metrics_history[run_id] = self.metrics_history[run_id][-100:]

                            # Broadcast to subscribers
                            await self._broadcast(
                                run_id,
                                {
                                    "type": "metrics_update",
                                    "metrics": {
                                        "agent_id": metrics.agent_id,
                                        "run_id": metrics.run_id,
                                        "phase": metrics.phase,
                                        "actions_count": metrics.actions_count,
                                        "budget_spent": round(metrics.budget_spent, 4),
                                        "budget_remaining": round(metrics.budget_remaining, 4),
                                        "timestamp": metrics.timestamp,
                                    },
                                },
                            )

                            # Check if completed
                            if status.get("phase") in ("completed", "failed", "rolled_back"):
                                await self._broadcast(
                                    run_id,
                                    {
                                        "type": "execution_complete",
                                        "status": status.get("phase"),
                                        "final_metrics": {
                                            "total_actions": metrics.actions_count,
                                            "total_spent": round(metrics.budget_spent, 4),
                                            "timestamp": datetime.now(timezone.utc).isoformat(),
                                        },
                                    },
                                )

                await asyncio.sleep(2)  # Poll every 2 seconds

            except Exception:
                await asyncio.sleep(5)  # Back off on error

    async def _broadcast(self, run_id: str, message: dict):
        """Broadcast message to all subscribers."""
        if run_id not in self.subscribers:
            return

        dead_sockets = set()
        for ws in self.subscribers[run_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead_sockets.add(ws)

        # Cleanup dead connections
        for ws in dead_sockets:
            self.subscribers[run_id].discard(ws)


# Global monitor instance
_agent_monitor = AgentMonitor()


@router.on_event("startup")
async def startup():
    """Start agent monitoring on startup."""
    await _agent_monitor.start()


@router.on_event("shutdown")
async def shutdown():
    """Stop agent monitoring on shutdown."""
    await _agent_monitor.stop()


@router.websocket("/ws/{run_id}")
async def agent_monitor_websocket(websocket: WebSocket, run_id: str):
    """WebSocket for real-time agent monitoring.

    Connect to /ws/{run_id} to receive live updates about an agent run.
    """
    await websocket.accept()

    # Subscribe to updates
    await _agent_monitor.subscribe(run_id, websocket)

    # Send initial data
    if _BRAIN_AVAILABLE and BrainClient:
        client = BrainClient(repo_path=str(_REPO_ROOT))
        status = client.get_agent_run(run_id)

        if status:
            await websocket.send_json(
                {
                    "type": "connected",
                    "run_id": run_id,
                    "current_status": {
                        "phase": status.get("phase"),
                        "agent_class": status.get("agent_class"),
                        "objective": status.get("objective"),
                        "actions_count": status.get("actions_count"),
                        "budget": {
                            "spent": status.get("budget_spent"),
                            "remaining": status.get("budget_remaining"),
                        },
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
        else:
            await websocket.send_json(
                {
                    "type": "error",
                    "message": f"Agent run {run_id} not found",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            await websocket.close()
            return
    else:
        await websocket.send_json(
            {
                "type": "error",
                "message": "Brain not available",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        await websocket.close()
        return

    try:
        # Keep connection alive and handle commands
        while True:
            data = await websocket.receive_text()

            try:
                import json

                message = json.loads(data)
                msg_type = message.get("type")

                if msg_type == "get_history":
                    # Send metrics history
                    history = _agent_monitor.metrics_history.get(run_id, [])
                    await websocket.send_json(
                        {
                            "type": "history",
                            "data": [
                                {
                                    "phase": m.phase,
                                    "actions": m.actions_count,
                                    "spent": round(m.budget_spent, 4),
                                    "remaining": round(m.budget_remaining, 4),
                                    "timestamp": m.timestamp,
                                }
                                for m in history
                            ],
                        }
                    )

                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})

            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})

    except WebSocketDisconnect:
        _agent_monitor.unsubscribe(run_id, websocket)


@router.get("/runs/active")
async def get_active_runs() -> list[dict]:
    """Get list of currently active agent runs."""
    if not _BRAIN_AVAILABLE:
        return []

    client = BrainClient(repo_path=str(_REPO_ROOT))
    kernel = get_agent_fabric_kernel()

    active_runs = []
    for run_id, run in kernel._runs.items():
        if run.phase in ("spawning", "executing"):
            active_runs.append(
                {
                    "run_id": run_id,
                    "agent_class": run.agent.class_id if run.agent else "unknown",
                    "phase": run.phase,
                    "objective": run.task.objective[:50] + "..." if run.task else "",
                    "budget_remaining": round(run.budget.remaining(), 4),
                    "actions_count": len(run.actions),
                }
            )

    return active_runs


@router.get("/runs/{run_id}/metrics")
async def get_run_metrics(run_id: str) -> dict:
    """Get metrics for a specific agent run."""
    history = _agent_monitor.metrics_history.get(run_id, [])

    if not history:
        return None

    latest = history[-1]

    return {
        "run_id": run_id,
        "current": {
            "phase": latest.phase,
            "actions_count": latest.actions_count,
            "budget_spent": round(latest.budget_spent, 4),
            "budget_remaining": round(latest.budget_remaining, 4),
        },
        "history_points": len(history),
        "data_points": [
            {
                "timestamp": m.timestamp,
                "phase": m.phase,
                "actions": m.actions_count,
                "budget_spent": round(m.budget_spent, 4),
            }
            for m in history
        ],
    }
