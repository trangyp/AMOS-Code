from typing import Any, Dict, Optional

"""Resilient WebSocket handling with error recovery.

Production-grade WebSocket management with heartbeat, reconnection, and error handling.
"""

import asyncio
import json

import structlog
from fastapi import WebSocket, WebSocketDisconnect

logger = structlog.get_logger("amos.websocket")


class WebSocketConnectionManager:
    """Manage WebSocket connections with resilience features."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """Accept and track a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connection_metadata[client_id] = {
            "connected_at": asyncio.get_event_loop().time(),
            "last_heartbeat": asyncio.get_event_loop().time(),
            "message_count": 0,
        }
        logger.info("websocket_client_connected", client_id=client_id)

    def disconnect(self, client_id: str) -> None:
        """Remove a disconnected client."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            if client_id in self.connection_metadata:
                duration = (
                    asyncio.get_event_loop().time()
                    - self.connection_metadata[client_id]["connected_at"]
                )
                logger.info(
                    "websocket_client_disconnected",
                    client_id=client_id,
                    duration_seconds=duration,
                    message_count=self.connection_metadata[client_id]["message_count"],
                )
                del self.connection_metadata[client_id]

    async def send_personal_message(self, message: Dict[str, Any], client_id: str) -> bool:
        """Send message to specific client with error handling."""
        if client_id not in self.active_connections:
            return False

        try:
            websocket = self.active_connections[client_id]
            await websocket.send_text(json.dumps(message))
            self.connection_metadata[client_id]["message_count"] += 1
            return True
        except Exception as e:
            logger.error("websocket_send_failed", client_id=client_id, error=str(e))
            self.disconnect(client_id)
            return False

    async def broadcast(self, message: Dict[str, Any]) -> int:
        """Broadcast message to all connected clients.

        Returns number of successful deliveries.
        """
        disconnected = []
        success_count = 0

        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
                self.connection_metadata[client_id]["message_count"] += 1
                success_count += 1
            except Exception as e:
                logger.error("websocket_broadcast_failed", client_id=client_id, error=str(e))
                disconnected.append(client_id)

        # Clean up failed connections
        for client_id in disconnected:
            self.disconnect(client_id)

        return success_count

    async def heartbeat(self, client_id: str) -> bool:
        """Send ping to check connection health."""
        if client_id not in self.active_connections:
            return False

        try:
            websocket = self.active_connections[client_id]
            await websocket.send_json(
                {"type": "ping", "timestamp": asyncio.get_event_loop().time()}
            )
            self.connection_metadata[client_id]["last_heartbeat"] = asyncio.get_event_loop().time()
            return True
        except Exception:
            self.disconnect(client_id)
            return False

    async def check_stale_connections(self, max_idle_seconds: float = 60.0) -> int:
        """Disconnect clients that haven't responded to heartbeats."""
        now = asyncio.get_event_loop().time()
        stale_clients = [
            client_id
            for client_id, meta in self.connection_metadata.items()
            if now - meta["last_heartbeat"] > max_idle_seconds
        ]

        for client_id in stale_clients:
            logger.warning("websocket_stale_connection", client_id=client_id)
            self.disconnect(client_id)

        return len(stale_clients)

    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics."""
        return {
            "active_connections": len(self.active_connections),
            "total_messages": sum(
                meta["message_count"] for meta in self.connection_metadata.values()
            ),
            "connections": {
                client_id: {
                    "duration_seconds": (asyncio.get_event_loop().time() - meta["connected_at"]),
                    "message_count": meta["message_count"],
                }
                for client_id, meta in self.connection_metadata.items()
            },
        }


async def handle_websocket_with_resilience(
    websocket: WebSocket,
    client_id: str,
    message_handler: callable,
    manager: Optional[WebSocketConnectionManager] = None,
) -> None:
    """Handle WebSocket connection with full error resilience.

    Args:
        websocket: The WebSocket connection
        client_id: Unique client identifier
        message_handler: Async function to process messages
        manager: Optional connection manager for tracking
    """
    if manager:
        await manager.connect(websocket, client_id)
    else:
        await websocket.accept()

    try:
        while True:
            # Receive with timeout to enable heartbeat checks
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except TimeoutError:
                # Send heartbeat ping
                try:
                    await websocket.send_json({"type": "ping"})
                    continue
                except Exception:
                    break

            # Parse and handle message
            try:
                message = json.loads(data)

                # Handle ping/pong
                if message.get("type") == "pong":
                    if manager and client_id in manager.connection_metadata:
                        manager.connection_metadata[client_id]["last_heartbeat"] = (
                            asyncio.get_event_loop().time()
                        )
                    continue

                # Process message
                await message_handler(websocket, message, client_id)

                if manager and client_id in manager.connection_metadata:
                    manager.connection_metadata[client_id]["message_count"] += 1

            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
            except Exception as e:
                logger.error("websocket_message_error", client_id=client_id, error=str(e))
                await websocket.send_json({"type": "error", "message": "Processing failed"})

    except WebSocketDisconnect:
        logger.info("websocket_client_disconnected_cleanly", client_id=client_id)
    except Exception as e:
        logger.error("websocket_unexpected_error", client_id=client_id, error=str(e))
    finally:
        if manager:
            manager.disconnect(client_id)
