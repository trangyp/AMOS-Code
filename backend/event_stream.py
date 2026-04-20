from __future__ import annotations

from typing import Any, Optional

"""AMOS Event Stream - Real-time event streaming for WebSocket.

Production-grade event streaming with:
- Async event queue
- Connection management
- Event persistence
- Backpressure handling
"""


import asyncio
import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

UTC = UTC

from fastapi import WebSocket, WebSocketDisconnect


@dataclass
class Event:
    """Event message."""

    id: str
    type: str
    payload: dict[str, Any]
    timestamp: str
    source: str


class EventStreamManager:
    """Manage WebSocket event streaming."""

    def __init__(self):
        self._connections: dict[str, WebSocket] = {}
        self._event_queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=1000)
        self._running = False
        self._task: asyncio.Task = None

    async def start(self) -> None:
        """Start the event stream manager."""
        self._running = True
        self._task = asyncio.create_task(self._broadcast_loop())

    async def stop(self) -> None:
        """Stop the event stream manager."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def connect(self, client_id: str, websocket: WebSocket) -> None:
        """Register new WebSocket connection."""
        await websocket.accept()
        self._connections[client_id] = websocket

    async def disconnect(self, client_id: str) -> None:
        """Remove WebSocket connection."""
        if client_id in self._connections:
            del self._connections[client_id]

    def emit(self, event_type: str, payload: dict[str, Any], source: str = "system") -> None:
        """Emit an event to all connected clients."""
        event = Event(
            id=str(uuid.uuid4()),
            type=event_type,
            payload=payload,
            timestamp=datetime.now(UTC).isoformat(),
            source=source,
        )
        try:
            self._event_queue.put_nowait(event)
        except asyncio.QueueFull:
            # Drop oldest event if queue is full
            try:
                self._event_queue.get_nowait()
                self._event_queue.put_nowait(event)
            except asyncio.QueueEmpty:
                pass

    async def _broadcast_loop(self) -> None:
        """Background task to broadcast events."""
        while self._running:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._broadcast(event)
            except TimeoutError:
                continue
            except Exception:
                pass

    async def _broadcast(self, event: Event) -> None:
        """Broadcast event to all connected clients."""
        message = {
            "id": event.id,
            "type": event.type,
            "payload": event.payload,
            "timestamp": event.timestamp,
            "source": event.source,
        }

        disconnected = []
        for client_id, websocket in self._connections.items():
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            await self.disconnect(client_id)

    async def stream_events(self, websocket: WebSocket) -> None:
        """Handle WebSocket connection for event streaming."""
        client_id = str(uuid.uuid4())
        await self.connect(client_id, websocket)

        try:
            while True:
                # Keep connection alive and handle client messages
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    # Handle ping/pong
                    if message.get("type") == "ping":
                        await websocket.send_json(
                            {
                                "type": "pong",
                                "timestamp": datetime.now(UTC).isoformat(),
                            }
                        )
                except json.JSONDecodeError:
                    pass
        except WebSocketDisconnect:
            await self.disconnect(client_id)


# Global event stream manager instance
_event_stream_manager: Optional[EventStreamManager] = None


def get_event_stream_manager() -> EventStreamManager:
    """Get or create global event stream manager."""
    global _event_stream_manager
    if _event_stream_manager is None:
        _event_stream_manager = EventStreamManager()
    return _event_stream_manager


def emit_event(event_type: str, payload: dict[str, Any], source: str = "system") -> None:
    """Emit an event to all connected clients."""
    manager = get_event_stream_manager()
    manager.emit(event_type, payload, source)


# Convenience event emitters
def emit_task_created(task_id: str, name: str, agent_type: str) -> None:
    """Emit task creation event."""
    emit_event("task.created", {"task_id": task_id, "name": name, "agent_type": agent_type})


def emit_task_completed(task_id: str, result: dict[str, Any]) -> None:
    """Emit task completion event."""
    emit_event("task.completed", {"task_id": task_id, "result": result})


def emit_system_alert(level: str, message: str) -> None:
    """Emit system alert."""
    emit_event("system.alert", {"level": level, "message": message})
