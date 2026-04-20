"""
AMOS Unified Streaming API

Real-time streaming layer unifying WebSocket, Kafka, and EventBus.
Exposes live events from all SuperBrain subsystems.

Creator: Trang Phan
Version: 3.0.0
"""

import asyncio
import json
from datetime import UTC, datetime
from typing import Any

UTC = UTC

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


# Connection managers for different stream types
class ConnectionManager:
    """Manages WebSocket connections for streaming."""

    def __init__(self):
        self.active_connections: dict[str, set] = {
            "superbrain": set(),
            "world_model": set(),
            "governance": set(),
            "workflow": set(),
            "a2a": set(),
            "knowledge": set(),
            "events": set(),
        }

    async def connect(self, websocket: WebSocket, stream_type: str):
        await websocket.accept()
        if stream_type in self.active_connections:
            self.active_connections[stream_type].add(websocket)

    def disconnect(self, websocket: WebSocket, stream_type: str):
        if stream_type in self.active_connections:
            self.active_connections[stream_type].discard(websocket)

    async def broadcast(self, stream_type: str, message: dict[str, Any]):
        """Broadcast message to all connections of a stream type."""
        if stream_type not in self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections[stream_type]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections[stream_type].discard(conn)


manager = ConnectionManager()


# ============================================================================
# UNIFIED SUPERBRAIN STREAM
# ============================================================================


@router.websocket("/ws/superbrain")
async def superbrain_stream(websocket: WebSocket):
    """
    WebSocket stream for unified SuperBrain events.

    Receives all subsystem events:
    - World Model simulations
    - Governance decisions
    - Workflow progress
    - A2A agent communications
    - Knowledge Bridge updates
    """
    await manager.connect(websocket, "superbrain")

    try:
        # Send initial connection ack
        await websocket.send_json(
            {
                "type": "connected",
                "stream": "superbrain",
                "timestamp": datetime.now(UTC).isoformat(),
                "subsystems": [
                    "world_model",
                    "constitutional_governance",
                    "workflow_orchestrator",
                    "a2a_protocol",
                    "knowledge_bridge",
                ],
            }
        )

        # Keep connection alive and handle client messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle subscription requests
                if message.get("action") == "subscribe":
                    subsystems = message.get("subsystems", [])
                    await websocket.send_json(
                        {"type": "subscription_confirmed", "subsystems": subsystems}
                    )

                elif message.get("action") == "ping":
                    await websocket.send_json(
                        {"type": "pong", "timestamp": datetime.now(UTC).isoformat()}
                    )

            except WebSocketDisconnect:
                break
            except Exception as e:
                await websocket.send_json({"type": "error", "message": str(e)})

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, "superbrain")


# ============================================================================
# SUBSYSTEM-SPECIFIC STREAMS
# ============================================================================


@router.websocket("/ws/world-model")
async def world_model_stream(websocket: WebSocket):
    """Real-time stream for World Model simulation events."""
    await manager.connect(websocket, "world_model")

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "stream": "world_model",
                "capabilities": ["simulation_start", "step_complete", "reflection", "improvement"],
            }
        )

        while True:
            data = await websocket.receive_text()
            # Handle control messages
            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, "world_model")


@router.websocket("/ws/governance")
async def governance_stream(websocket: WebSocket):
    """Real-time stream for Constitutional Governance decisions."""
    await manager.connect(websocket, "governance")

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "stream": "governance",
                "capabilities": ["decision", "violation", "drift_detected", "correction"],
            }
        )

        while True:
            await asyncio.sleep(1)  # Keep alive

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, "governance")


@router.websocket("/ws/workflow")
async def workflow_stream(websocket: WebSocket):
    """Real-time stream for Workflow Orchestrator progress."""
    await manager.connect(websocket, "workflow")

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "stream": "workflow",
                "capabilities": [
                    "workflow_started",
                    "step_completed",
                    "compensation",
                    "human_approval_needed",
                ],
            }
        )

        while True:
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, "workflow")


@router.websocket("/ws/a2a")
async def a2a_stream(websocket: WebSocket):
    """Real-time stream for A2A Protocol agent communications."""
    await manager.connect(websocket, "a2a")

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "stream": "a2a",
                "capabilities": [
                    "task_submitted",
                    "task_update",
                    "streaming_response",
                    "completion",
                ],
            }
        )

        while True:
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, "a2a")


@router.websocket("/ws/knowledge")
async def knowledge_stream(websocket: WebSocket):
    """Real-time stream for Knowledge Bridge equation updates."""
    await manager.connect(websocket, "knowledge")

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "stream": "knowledge",
                "capabilities": ["equation_added", "cache_updated", "sync_complete"],
            }
        )

        while True:
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, "knowledge")


# ============================================================================
# EVENT BROADCAST API
# ============================================================================


@router.post("/broadcast/{stream_type}")
async def broadcast_event(stream_type: str, event: dict[str, Any]):
    """
    Broadcast an event to all connected clients of a stream type.

    Used by internal systems to push events to WebSocket clients.
    """
    event["timestamp"] = datetime.now(UTC).isoformat()
    event["stream"] = stream_type

    await manager.broadcast(stream_type, event)

    return {"status": "broadcasted", "stream": stream_type, "timestamp": event["timestamp"]}


# ============================================================================
# STREAMING STATUS
# ============================================================================


@router.get("/status")
async def get_streaming_status():
    """Get current streaming system status."""
    return {
        "streams": {
            "superbrain": len(manager.active_connections["superbrain"]),
            "world_model": len(manager.active_connections["world_model"]),
            "governance": len(manager.active_connections["governance"]),
            "workflow": len(manager.active_connections["workflow"]),
            "a2a": len(manager.active_connections["a2a"]),
            "knowledge": len(manager.active_connections["knowledge"]),
        },
        "endpoints": [
            "/ws/superbrain",
            "/ws/world-model",
            "/ws/governance",
            "/ws/workflow",
            "/ws/a2a",
            "/ws/knowledge",
        ],
        "timestamp": datetime.now(UTC).isoformat(),
    }


# ============================================================================
# EVENT BRIDGE - Connect SuperBrain to Streaming
# ============================================================================


async def emit_superbrain_event(event_type: str, payload: dict[str, Any]):
    """
    Emit an event from SuperBrain to the streaming layer.

    This bridges the SuperBrain's _emit_event() method to WebSocket clients.
    """
    event = {"type": event_type, "data": payload, "timestamp": datetime.now(UTC).isoformat()}

    # Route to appropriate stream
    stream_mapping = {
        "world_model_initialized": "world_model",
        "world_model_simulation": "world_model",
        "constitutional_governance_initialized": "governance",
        "governance_decision": "governance",
        "workflow_orchestrator_initialized": "workflow",
        "workflow_progress": "workflow",
        "a2a_protocol_initialized": "a2a",
        "a2a_task_update": "a2a",
        "knowledge_bridge_initialized": "knowledge",
        "knowledge_update": "knowledge",
    }

    stream_type = stream_mapping.get(event_type, "superbrain")

    # Broadcast to specific stream
    await manager.broadcast(stream_type, event)

    # Also broadcast to unified superbrain stream
    await manager.broadcast("superbrain", event)
