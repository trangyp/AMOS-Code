"""
AMOS WebSocket Manager - Real-Time Communication Infrastructure

Production-grade WebSocket management with room support, authentication,
and Event Bus integration for distributed real-time messaging.

Author: AMOS System
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone

UTC = UTC
from typing import Any

from fastapi import WebSocket
from starlette.websockets import WebSocketState

from amos_event_bus import Event, get_event_bus

# ============================================================================
# WebSocket Connection Model
# ============================================================================


@dataclass
class WSConnection:
    """Represents an active WebSocket connection."""

    id: str
    websocket: WebSocket
    user_id: str = None
    rooms: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)
    connected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    async def send(self, message: dict[str, Any]) -> None:
        """Send message to this connection."""
        if self.websocket.client_state == WebSocketState.CONNECTED:
            await self.websocket.send_json(message)

    def touch(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)

    @property
    def is_active(self) -> bool:
        """Check if connection is still active."""
        return self.websocket.client_state == WebSocketState.CONNECTED


# ============================================================================
# WebSocket Manager
# ============================================================================


class WebSocketManager:
    """
    Central WebSocket connection manager.

    Features:
    - Multi-room support
    - User authentication tracking
    - Event Bus integration
    - Connection health monitoring
    - Broadcast and targeted messaging

    Usage:
        manager = WebSocketManager()

        @app.websocket("/ws/{room}")
        async def websocket_endpoint(websocket: WebSocket, room: str):
            await manager.connect(websocket, room)
            try:
                while True:
                    data = await websocket.receive_json()
                    await manager.broadcast(room, data)
            except WebSocketDisconnect:
                await manager.disconnect(websocket)
    """

    def __init__(self):
        self._connections: dict[str, WSConnection] = {}
        self._rooms: dict[str, set[str]] = defaultdict(set)
        self._user_connections: dict[str, set[str]] = defaultdict(set)
        self._event_bus = get_event_bus()
        self._lock = asyncio.Lock()
        self._running = False
        self._cleanup_task: asyncio.Task = None

    # ========================================================================
    # Connection Management
    # ========================================================================

    async def connect(
        self,
        websocket: WebSocket,
        room: str = None,
        user_id: str = None,
        metadata: dict[str, Any] = None,
    ) -> str:
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: The WebSocket object from FastAPI
            room: Optional room to join immediately
            user_id: Optional authenticated user ID
            metadata: Optional connection metadata

        Returns:
            Connection ID
        """
        await websocket.accept()

        conn_id = str(uuid.uuid4())
        connection = WSConnection(
            id=conn_id, websocket=websocket, user_id=user_id, metadata=metadata or {}
        )

        async with self._lock:
            self._connections[conn_id] = connection

            if user_id:
                self._user_connections[user_id].add(conn_id)

            if room:
                connection.rooms.add(room)
                self._rooms[room].add(conn_id)

        # Publish connection event
        await self._event_bus.publish(
            "websocket.connected", {"connection_id": conn_id, "user_id": user_id, "room": room}
        )

        return conn_id

    async def disconnect(self, websocket: WebSocket) -> None:
        """Disconnect and cleanup a WebSocket connection."""
        async with self._lock:
            # Find connection by websocket object
            conn_id = None
            for cid, conn in self._connections.items():
                if conn.websocket == websocket:
                    conn_id = cid
                    break

            if not conn_id:
                return

            connection = self._connections.pop(conn_id)

            # Remove from rooms
            for room in connection.rooms:
                self._rooms[room].discard(conn_id)
                if not self._rooms[room]:
                    del self._rooms[room]

            # Remove from user connections
            if connection.user_id:
                self._user_connections[connection.user_id].discard(conn_id)
                if not self._user_connections[connection.user_id]:
                    del self._user_connections[connection.user_id]

        # Publish disconnection event
        await self._event_bus.publish(
            "websocket.disconnected",
            {
                "connection_id": conn_id,
                "user_id": connection.user_id,
                "duration_seconds": (
                    datetime.now(timezone.utc) - connection.connected_at
                ).total_seconds(),
            },
        )

    # ========================================================================
    # Room Management
    # ========================================================================

    async def join_room(self, connection_id: str, room: str) -> bool:
        """Add connection to a room."""
        async with self._lock:
            if connection_id not in self._connections:
                return False

            connection = self._connections[connection_id]
            connection.rooms.add(room)
            self._rooms[room].add(connection_id)

        await self._event_bus.publish(
            "websocket.room.joined", {"connection_id": connection_id, "room": room}
        )

        return True

    async def leave_room(self, connection_id: str, room: str) -> bool:
        """Remove connection from a room."""
        async with self._lock:
            if connection_id not in self._connections:
                return False

            connection = self._connections[connection_id]
            connection.rooms.discard(room)
            self._rooms[room].discard(connection_id)

            if not self._rooms[room]:
                del self._rooms[room]

        await self._event_bus.publish(
            "websocket.room.left", {"connection_id": connection_id, "room": room}
        )

        return True

    # ========================================================================
    # Messaging
    # ========================================================================

    async def send_to_connection(self, connection_id: str, message: dict[str, Any]) -> bool:
        """Send message to a specific connection."""
        if connection_id not in self._connections:
            return False

        connection = self._connections[connection_id]
        if not connection.is_active:
            return False

        try:
            await connection.send(message)
            connection.touch()
            return True
        except Exception:
            return False

    async def send_to_user(self, user_id: str, message: dict[str, Any]) -> int:
        """Send message to all connections of a user. Returns count sent."""
        sent = 0

        if user_id not in self._user_connections:
            return sent

        for conn_id in list(self._user_connections[user_id]):
            if await self.send_to_connection(conn_id, message):
                sent += 1

        return sent

    async def broadcast(self, room: str, message: dict[str, Any], exclude: str = None) -> int:
        """
        Broadcast message to all connections in a room.

        Args:
            room: Room name
            message: Message data
            exclude: Optional connection ID to exclude

        Returns:
            Number of connections that received the message
        """
        if room not in self._rooms:
            return 0

        sent = 0
        dead_connections = []

        for conn_id in list(self._rooms[room]):
            if conn_id == exclude:
                continue

            if not await self.send_to_connection(conn_id, message):
                dead_connections.append(conn_id)
            else:
                sent += 1

        # Cleanup dead connections
        for conn_id in dead_connections:
            await self._cleanup_connection(conn_id)

        return sent

    async def broadcast_all(self, message: dict[str, Any]) -> int:
        """Broadcast message to all connected clients."""
        sent = 0
        dead_connections = []

        for conn_id, connection in list(self._connections.items()):
            if not await self.send_to_connection(conn_id, message):
                dead_connections.append(conn_id)
            else:
                sent += 1

        # Cleanup dead connections
        for conn_id in dead_connections:
            await self._cleanup_connection(conn_id)

        return sent

    # ========================================================================
    # Event Bus Integration
    # ========================================================================

    async def start_event_listener(self):
        """Start listening for Event Bus events to broadcast."""
        self._running = True

        # Subscribe to relevant events
        await self._event_bus.subscribe("broadcast", "ws_manager", self._handle_broadcast_event)
        await self._event_bus.subscribe(
            "user.notification", "ws_manager", self._handle_user_notification
        )

        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())

    async def stop(self):
        """Stop the WebSocket manager."""
        self._running = False

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Close all connections
        for connection in list(self._connections.values()):
            try:
                await connection.websocket.close()
            except Exception:
                pass

        self._connections.clear()
        self._rooms.clear()
        self._user_connections.clear()

    async def _handle_broadcast_event(self, event: Event):
        """Handle broadcast events from Event Bus."""
        room = event.payload.get("room", "default")
        message = event.payload.get("message", {})
        await self.broadcast(room, message)

    async def _handle_user_notification(self, event: Event):
        """Handle user notification events."""
        user_id = event.payload.get("user_id")
        message = event.payload.get("message", {})
        if user_id:
            await self.send_to_user(user_id, message)

    # ========================================================================
    # Maintenance
    # ========================================================================

    async def _cleanup_connection(self, connection_id: str) -> None:
        """Remove a dead connection."""
        async with self._lock:
            if connection_id not in self._connections:
                return

            connection = self._connections.pop(connection_id)

            for room in connection.rooms:
                self._rooms[room].discard(connection_id)

            if connection.user_id:
                self._user_connections[connection.user_id].discard(connection_id)

    async def _periodic_cleanup(self):
        """Periodically cleanup stale connections."""
        while self._running:
            await asyncio.sleep(60)  # Run every minute

            stale_threshold = datetime.now(timezone.utc).timestamp() - 300  # 5 minutes
            dead_connections = []

            for conn_id, connection in self._connections.items():
                if connection.last_activity.timestamp() < stale_threshold:
                    dead_connections.append(conn_id)

            for conn_id in dead_connections:
                await self._cleanup_connection(conn_id)

    # ========================================================================
    # Statistics
    # ========================================================================

    def get_stats(self) -> dict[str, Any]:
        """Get WebSocket manager statistics."""
        return {
            "total_connections": len(self._connections),
            "total_rooms": len(self._rooms),
            "connections_per_room": {room: len(conns) for room, conns in self._rooms.items()},
            "users_online": len(self._user_connections),
        }


# ============================================================================
# Global Manager Instance
# ============================================================================_manager: Optional[WebSocketManager] = None


def get_websocket_manager() -> WebSocketManager:
    """Get or create global WebSocket manager."""
    global _manager
    if _manager is None:
        _manager = WebSocketManager()
    return _manager


# ============================================================================
# FastAPI Dependency
# ============================================================================


async def get_ws_manager() -> WebSocketManager:
    """FastAPI dependency for WebSocket manager."""
    return get_websocket_manager()
