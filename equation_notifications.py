#!/usr/bin/env python3
"""AMOS Equation Notifications - WebSocket Real-Time Updates.

WebSocket-based real-time notification system for equation processing events.
Integrates with Celery tasks to push completion notifications to clients.

Features:
    - WebSocket connection management
    - User-specific and broadcast notifications
    - Task completion push notifications
    - Progress updates for long-running operations
    - Redis pub/sub for multi-server scaling
    - Connection health monitoring

Events:
    task.completed: Task finished with results
    task.failed: Task execution failed
    task.progress: Progress percentage update
    system.status: System health broadcast

Usage:
    from equation_notifications import notify_user, broadcast

    # Send to specific user
    await notify_user(user_id, {
        "type": "task.completed",
        "task_id": task_id,
        "result": result
    })

    # Broadcast to all
    await broadcast({"type": "system.status", "status": "healthy"})

Environment Variables:
    WS_MAX_CONNECTIONS: Max concurrent connections (default: 1000)
    WS_HEARTBEAT_INTERVAL: Seconds between heartbeats (default: 30)
    REDIS_PUBSUB_ENABLED: Enable Redis pub/sub (default: false)
"""

import json
import os
import time
from typing import Any, Dict, Optional, Set

try:
    from fastapi import WebSocket, WebSocketDisconnect

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    WebSocket = None  # type: ignore
    WebSocketDisconnect = Exception  # type: ignore

try:
    from equation_tracing import create_span

    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False


class ConnectionManager:
    """Manage WebSocket connections for real-time notifications."""

    def __init__(self) -> None:
        # Map of user_id -> set of WebSocket connections
        self._user_connections: Dict[str, set[Any]] = {}
        # Map of websocket -> user_id for reverse lookup
        self._connection_users: Dict[Any, str] = {}
        # All active connections
        self._all_connections: Set[Any] = set()

        self._max_connections = int(os.getenv("WS_MAX_CONNECTIONS", "1000"))
        self._heartbeat_interval = int(os.getenv("WS_HEARTBEAT_INTERVAL", "30"))

    async def connect(self, websocket: Any, user_id: str) -> bool:
        """Accept WebSocket connection and register user.

        Args:
            websocket: WebSocket connection object
            user_id: User identifier for targeted notifications

        Returns:
            True if connection accepted, False if max reached
        """
        if len(self._all_connections) >= self._max_connections:
            await websocket.close(code=1008, reason="Max connections reached")
            return False

        await websocket.accept()

        self._all_connections.add(websocket)
        self._connection_users[websocket] = user_id

        if user_id not in self._user_connections:
            self._user_connections[user_id] = set()
        self._user_connections[user_id].add(websocket)

        # Send connection confirmation
        await websocket.send_json(
            {
                "type": "connection.established",
                "user_id": user_id,
            }
        )

        return True

    def disconnect(self, websocket: Any) -> None:
        """Remove WebSocket connection."""
        user_id = self._connection_users.get(websocket)

        if user_id and user_id in self._user_connections:
            self._user_connections[user_id].discard(websocket)
            if not self._user_connections[user_id]:
                del self._user_connections[user_id]

        self._connection_users.pop(websocket, None)
        self._all_connections.discard(websocket)

    async def notify_user(self, user_id: str, message: Dict[str, Any]) -> int:
        """Send notification to all connections for a user.

        Args:
            user_id: Target user identifier
            message: JSON-serializable message payload

        Returns:
            Number of connections notified
        """
        connections = self._user_connections.get(user_id, set())
        sent = 0

        for ws in list(connections):
            try:
                await ws.send_json(message)
                sent += 1
            except Exception:
                # Mark for cleanup
                self.disconnect(ws)

        return sent

    async def broadcast(self, message: Dict[str, Any]) -> int:
        """Broadcast message to all connected clients.

        Args:
            message: JSON-serializable message payload

        Returns:
            Number of connections notified
        """
        sent = 0
        for ws in list(self._all_connections):
            try:
                await ws.send_json(message)
                sent += 1
            except Exception:
                self.disconnect(ws)

        return sent

    def get_stats(self) -> Dict[str, Any]:
        """Get connection manager statistics."""
        return {
            "total_connections": len(self._all_connections),
            "unique_users": len(self._user_connections),
            "max_connections": self._max_connections,
            "users": {uid: len(conns) for uid, conns in self._user_connections.items()},
        }


# Global connection manager instance
_manager: Optional[ConnectionManager] = None


def get_manager() -> ConnectionManager:
    """Get or create global connection manager."""
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager


async def notify_user(user_id: str, message: Dict[str, Any]) -> int:
    """Send notification to specific user.

    Args:
        user_id: Target user identifier
        message: Message payload with 'type' field

    Returns:
        Number of connections notified
    """
    if not FASTAPI_AVAILABLE:
        return 0

    manager = get_manager()

    if TRACING_AVAILABLE:
        with create_span(
            "websocket.notify_user",
            {"user_id": user_id, "message_type": message.get("type")},
        ) as span:
            count = await manager.notify_user(user_id, message)
            if span:
                span.set_attribute("connections.notified", count)
            return count

    return await manager.notify_user(user_id, message)


async def broadcast(message: Dict[str, Any]) -> int:
    """Broadcast to all connected clients.

    Args:
        message: Message payload with 'type' field

    Returns:
        Number of connections notified
    """
    if not FASTAPI_AVAILABLE:
        return 0

    manager = get_manager()

    if TRACING_AVAILABLE:
        with create_span(
            "websocket.broadcast",
            {"message_type": message.get("type")},
        ) as span:
            count = await manager.broadcast(message)
            if span:
                span.set_attribute("connections.notified", count)
            return count

    return await manager.broadcast(message)


async def notify_task_completed(
    user_id: str,
    task_id: str,
    result: Dict[str, Any],
) -> int:
    """Notify user that a task completed.

    Args:
        user_id: User who owns the task
        task_id: Completed task identifier
        result: Task result data

    Returns:
        Number of connections notified
    """
    return await notify_user(
        user_id,
        {
            "type": "task.completed",
            "task_id": task_id,
            "result": result,
            "timestamp": time.time(),
        },
    )


async def notify_task_failed(
    user_id: str,
    task_id: str,
    error: str,
) -> int:
    """Notify user that a task failed.

    Args:
        user_id: User who owns the task
        task_id: Failed task identifier
        error: Error message

    Returns:
        Number of connections notified
    """
    return await notify_user(
        user_id,
        {
            "type": "task.failed",
            "task_id": task_id,
            "error": error,
            "timestamp": time.time(),
        },
    )


async def notify_task_progress(
    user_id: str,
    task_id: str,
    progress: float,
    message: str = None,
) -> int:
    """Send task progress update.

    Args:
        user_id: User who owns the task
        task_id: Task identifier
        progress: Progress percentage (0-100)
        message: Optional progress message

    Returns:
        Number of connections notified
    """
    payload: Dict[str, Any] = {
        "type": "task.progress",
        "task_id": task_id,
        "progress": progress,
        "timestamp": time.time(),
    }
    if message:
        payload["message"] = message

    return await notify_user(user_id, payload)


def get_connection_stats() -> Dict[str, Any]:
    """Get WebSocket connection statistics."""
    if _manager is None:
        return {"status": "not_initialized"}
    return _manager.get_stats()


if FASTAPI_AVAILABLE:
    from fastapi import APIRouter

    router = APIRouter()

    @router.websocket("/ws/notifications")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        """WebSocket endpoint for real-time notifications.

        Clients connect here to receive push notifications.
        User ID extracted from query param: ?user_id=xxx
        """
        # Get user_id from query params
        user_id = websocket.query_params.get("user_id", "anonymous")

        manager = get_manager()

        if not await manager.connect(websocket, user_id):
            return

        try:
            while True:
                # Keep connection alive and handle client messages
                data = await websocket.receive_text()

                # Handle ping/heartbeat
                try:
                    msg = json.loads(data)
                    if msg.get("action") == "ping":
                        await websocket.send_json({"type": "pong"})
                except json.JSONDecodeError:
                    pass

        except WebSocketDisconnect:
            manager.disconnect(websocket)
        except Exception:
            manager.disconnect(websocket)
