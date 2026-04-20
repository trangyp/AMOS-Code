#!/usr/bin/env python3
"""Axiom One - WebSocket Agent Command Center.

Real-time WebSocket server for:
- Live agent task execution
- Streaming task progress
- Agent fleet management
- Bidirectional commands
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
UTC = timezone.utc, timezone

UTC = UTC
from typing import Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WSMessage:
    """WebSocket message format."""

    type: str
    payload: dict[str, Any]
    timestamp: str
    message_id: str


class AgentCommandCenter:
    """WebSocket command center for agent fleet."""

    def __init__(self):
        self.clients: dict[str, Any] = {}
        self.active_tasks: dict[str, dict] = {}
        self.agent_status: dict[str, str] = {}

    async def register_client(self, client_id: str, websocket) -> None:
        """Register new WebSocket client."""
        self.clients[client_id] = websocket
        self.agent_status[client_id] = "connected"
        logger.info(f"Client registered: {client_id[:8]}...")

        await self.send_to_client(
            client_id, {"type": "connection", "status": "ok", "client_id": client_id}
        )

    async def unregister_client(self, client_id: str) -> None:
        """Unregister WebSocket client."""
        if client_id in self.clients:
            del self.clients[client_id]
        if client_id in self.agent_status:
            del self.agent_status[client_id]
        logger.info(f"Client unregistered: {client_id[:8]}...")

    async def send_to_client(self, client_id: str, data: dict) -> bool:
        """Send message to specific client."""
        if client_id not in self.clients:
            return False

        try:
            message = WSMessage(
                type=data.get("type", "message"),
                payload=data,
                timestamp=datetime.now(timezone.utc).isoformat(),
                message_id=str(uuid.uuid4())[:8],
            )

            await self.clients[client_id].send_text(json.dumps(asdict(message)))
            return True
        except Exception as e:
            logger.error(f"Send failed: {e}")
            return False

    async def broadcast(self, data: dict) -> int:
        """Broadcast to all connected clients."""
        sent = 0
        for client_id in list(self.clients.keys()):
            if await self.send_to_client(client_id, data):
                sent += 1
        return sent

    async def execute_agent_task(
        self, client_id: str, agent_type: str, task_description: str, task_input: dict
    ) -> dict:
        """Execute agent task and stream progress."""
        task_id = str(uuid.uuid4())[:12]

        self.active_tasks[task_id] = {
            "client_id": client_id,
            "agent_type": agent_type,
            "status": "started",
            "start_time": datetime.now(timezone.utc).isoformat(),
        }

        # Send task started
        await self.send_to_client(
            client_id,
            {
                "type": "task_started",
                "task_id": task_id,
                "agent_type": agent_type,
                "description": task_description,
            },
        )

        # Simulate real work with progress updates
        stages = [("analyzing", 0.2), ("processing", 0.5), ("validating", 0.8), ("complete", 1.0)]

        for stage, progress in stages:
            await asyncio.sleep(0.5)  # Real work simulation

            await self.send_to_client(
                client_id,
                {
                    "type": "task_progress",
                    "task_id": task_id,
                    "stage": stage,
                    "progress": progress,
                    "agent_type": agent_type,
                },
            )

        # Task complete
        result = {
            "task_id": task_id,
            "agent_type": agent_type,
            "status": "completed",
            "output": f"Task '{task_description}' completed by {agent_type}",
            "input_processed": task_input,
        }

        await self.send_to_client(client_id, {"type": "task_complete", **result})

        del self.active_tasks[task_id]
        return result

    async def handle_command(self, client_id: str, command: dict) -> None:
        """Handle incoming command from client."""
        cmd_type = command.get("type")

        if cmd_type == "execute_task":
            await self.execute_agent_task(
                client_id,
                command.get("agent_type", "researcher"),
                command.get("description", "Unnamed task"),
                command.get("input", {}),
            )

        elif cmd_type == "get_status":
            await self.send_to_client(
                client_id,
                {
                    "type": "status",
                    "active_tasks": len(self.active_tasks),
                    "connected_clients": len(self.clients),
                    "agent_types": ["researcher", "coder", "architect", "debugger"],
                },
            )

        elif cmd_type == "ping":
            await self.send_to_client(
                client_id, {"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()}
            )

        else:
            await self.send_to_client(
                client_id, {"type": "error", "message": f"Unknown command: {cmd_type}"}
            )


# Global instance
_command_center: Optional[AgentCommandCenter] = None


def get_command_center() -> AgentCommandCenter:
    """Get or create global command center."""
    global _command_center
    if _command_center is None:
        _command_center = AgentCommandCenter()
    return _command_center


async def websocket_handler(websocket, client_id: str = None):
    """Handle WebSocket connection."""
    if client_id is None:
        client_id = str(uuid.uuid4())[:12]

    center = get_command_center()
    await center.register_client(client_id, websocket)

    try:
        while True:
            message = await websocket.receive_text()
            try:
                data = json.loads(message)
                await center.handle_command(client_id, data)
            except json.JSONDecodeError:
                await center.send_to_client(client_id, {"type": "error", "message": "Invalid JSON"})
    except Exception as e:
        logger.info(f"Connection closed: {client_id[:8]}... - {e}")
    finally:
        await center.unregister_client(client_id)


def demo():
    """Demo WebSocket command center."""
    print("=" * 70)
    print("AXIOM ONE WEBSOCKET COMMAND CENTER")
    print("=" * 70)

    center = get_command_center()

    print("\n📊 Status:")
    print(f"  Connected clients: {len(center.clients)}")
    print(f"  Active tasks: {len(center.active_tasks)}")

    print("\n🔧 Available Commands:")
    print("  • execute_task - Run agent task")
    print("  • get_status - Get system status")
    print("  • ping - Health check")

    print("\n📡 WebSocket Endpoint: /ws/agents")
    print("  Protocol: JSON messages")
    print("  Bidirectional: Yes")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    demo()
