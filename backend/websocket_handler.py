"""
AMOS WebSocket Handler

Real-time bidirectional communication for:
- LLM streaming responses
- Agent task updates
- System status notifications
- Dashboard live data

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime

from fastapi import WebSocket, WebSocketDisconnect

UTC = UTC

# Active connections store
active_connections: dict[str, set[WebSocket]] = {
    "dashboard": set(),
    "agents": set(),
    "system": set(),
}


class ConnectionManager:
    """Manage WebSocket connections by channel."""

    def __init__(self):
        self.connections = active_connections

    async def connect(self, websocket: WebSocket, channel: str):
        """Accept and store new connection."""
        await websocket.accept()
        if channel not in self.connections:
            self.connections[channel] = set()
        self.connections[channel].add(websocket)

    def disconnect(self, websocket: WebSocket, channel: str):
        """Remove disconnected client."""
        if channel in self.connections:
            self.connections[channel].discard(websocket)

    async def broadcast(self, channel: str, message: dict):
        """Send message to all clients in channel."""
        if channel not in self.connections:
            return

        disconnected = set()
        for conn in self.connections[channel]:
            try:
                await conn.send_json(message)
            except Exception:
                disconnected.add(conn)

        # Clean up dead connections
        for conn in disconnected:
            self.connections[channel].discard(conn)

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to specific client."""
        try:
            await websocket.send_json(message)
        except Exception:
            pass


manager = ConnectionManager()


async def websocket_dashboard(websocket: WebSocket):
    """
    Dashboard WebSocket endpoint.

    Streams:
    - System metrics (CPU, memory, tasks)
    - LLM responses
    - Agent updates
    - Governance events
    """
    await manager.connect(websocket, "dashboard")

    try:
        # Send initial connection confirmation
        await manager.send_personal(
            websocket,
            {
                "type": "connection",
                "status": "connected",
                "channel": "dashboard",
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

        while True:
            # Receive client messages
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            msg_type = message.get("type")

            if msg_type == "ping":
                await manager.send_personal(
                    websocket, {"type": "pong", "timestamp": datetime.now(UTC).isoformat()}
                )

            elif msg_type == "subscribe":
                channel = message.get("channel", "dashboard")
                await manager.send_personal(websocket, {"type": "subscribed", "channel": channel})

            elif msg_type == "chat":
                # Handle chat messages from dashboard
                await manager.broadcast(
                    "dashboard",
                    {
                        "type": "chat_echo",
                        "content": message.get("content"),
                        "timestamp": datetime.now(UTC).isoformat(),
                    },
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, "dashboard")


async def websocket_agents(websocket: WebSocket):
    """
    Agent task WebSocket endpoint.

    Streams real-time agent task updates.
    """
    await manager.connect(websocket, "agents")

    try:
        await manager.send_personal(
            websocket, {"type": "connection", "status": "connected", "channel": "agents"}
        )

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Echo back for now (will integrate with actual agent system)
            await manager.send_personal(websocket, {"type": "agent_echo", "received": message})

    except WebSocketDisconnect:
        manager.disconnect(websocket, "agents")


async def notify_task_update(task_id: str, status: str, progress: int):
    """Broadcast task update to all dashboard clients."""
    await manager.broadcast(
        "dashboard",
        {
            "type": "task_update",
            "task_id": task_id,
            "status": status,
            "progress": progress,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


async def notify_llm_response(provider: str, model: str, latency_ms: float):
    """Broadcast LLM completion notification."""
    await manager.broadcast(
        "dashboard",
        {
            "type": "llm_response",
            "provider": provider,
            "model": model,
            "latency_ms": latency_ms,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


async def notify_system_alert(level: str, message: str):
    """Broadcast system alert."""
    await manager.broadcast(
        "dashboard",
        {
            "type": "system_alert",
            "level": level,  # info, warning, error
            "message": message,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


# Background task to broadcast periodic updates
async def broadcast_system_metrics():
    """Periodically broadcast system metrics to dashboard."""

    import psutil

    while True:
        try:
            await manager.broadcast(
                "dashboard",
                {
                    "type": "metrics",
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )
        except Exception:
            pass

        await asyncio.sleep(5)  # Update every 5 seconds
