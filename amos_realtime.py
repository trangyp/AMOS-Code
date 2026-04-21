#!/usr/bin/env python3
"""AMOS Real-Time Event Streaming - SSE & WebSocket

Production-grade real-time infrastructure with:
- Server-Sent Events (SSE) for one-way streaming
- WebSocket for bidirectional communication
- Connection management
- Room-based broadcasting
- Auto-reconnection support

Based on FastAPI 2024+ real-time patterns.
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterable, Optional

sys.path.insert(0, str(Path(__file__).parent))

# FastAPI imports
try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import StreamingResponse
    from sse_starlette.sse import EventSourceResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("⚠️  FastAPI or sse-starlette not installed. Run: pip install fastapi sse-starlette")

# AMOS brain integration
try:
    from amos_brain import think, get_cognitive_runtime
    AMOS_AVAILABLE = True
except ImportError:
    AMOS_AVAILABLE = False


class ConnectionManager:
    """Manage WebSocket connections with room support."""
    
    def __init__(self):
        # Active connections: {websocket: {"client_id": str, "rooms": set}}
        self.active_connections: dict[WebSocket, dict] = {}
        # Room membership: {room_name: set(websockets)}
        self.rooms: dict[str, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None) -> str:
        """Accept connection and register client."""
        await websocket.accept()
        client_id = client_id or str(uuid.uuid4())
        
        async with self._lock:
            self.active_connections[websocket] = {
                "client_id": client_id,
                "rooms": set(),
                "connected_at": datetime.now(timezone.utc).isoformat(),
            }
        
        print(f"✅ Client connected: {client_id}")
        return client_id
    
    def disconnect(self, websocket: WebSocket) -> None:
        """Remove connection and clean up rooms."""
        client_info = self.active_connections.pop(websocket, None)
        if client_info:
            # Remove from all rooms
            for room in list(client_info["rooms"]):
                self.rooms[room].discard(websocket)
                if not self.rooms[room]:
                    del self.rooms[room]
            print(f"🚫 Client disconnected: {client_info['client_id']}")
    
    async def join_room(self, websocket: WebSocket, room: str) -> None:
        """Add connection to room."""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections[websocket]["rooms"].add(room)
                self.rooms[room].add(websocket)
                print(f"📌 Client joined room: {room}")
    
    async def leave_room(self, websocket: WebSocket, room: str) -> None:
        """Remove connection from room."""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections[websocket]["rooms"].discard(room)
                self.rooms[room].discard(websocket)
    
    async def broadcast_to_room(self, room: str, message: dict) -> None:
        """Send message to all clients in room."""
        if room not in self.rooms:
            return
        
        disconnected = []
        for websocket in list(self.rooms[room]):
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def send_to_client(self, websocket: WebSocket, message: dict) -> bool:
        """Send message to specific client."""
        try:
            await websocket.send_json(message)
            return True
        except Exception:
            self.disconnect(websocket)
            return False
    
    def get_stats(self) -> dict:
        """Get connection statistics."""
        return {
            "total_connections": len(self.active_connections),
            "total_rooms": len(self.rooms),
            "room_members": {room: len(members) for room, members in self.rooms.items()},
        }


# Global connection manager
_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """Get or create global connection manager."""
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager


# SSE Event Generator
async def sse_event_generator(event_type: str = "heartbeat") -> AsyncIterable[dict]:
    """Generate SSE events for streaming."""
    counter = 0
    while True:
        counter += 1
        event_data = {
            "event": event_type,
            "id": counter,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "message": f"Event {counter}",
                "amos_status": "operational" if AMOS_AVAILABLE else "limited",
            }
        }
        
        # Add brain insight if available
        if AMOS_AVAILABLE and counter % 10 == 0:
            try:
                result = think(f"System status check #{counter}")
                event_data["data"]["brain_insight"] = result.content[:100]
            except Exception:
                pass
        
        yield event_data
        await asyncio.sleep(5)  # Send every 5 seconds


async def metrics_sse_generator() -> AsyncIterable[dict]:
    """Generate metrics events."""
    from amos_metrics import get_metrics_summary
    
    while True:
        yield {
            "event": "metrics",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": get_metrics_summary()
        }
        await asyncio.sleep(30)  # Metrics every 30 seconds


# FastAPI routes (if available)
if FASTAPI_AVAILABLE:
    from fastapi import APIRouter
    
    router = APIRouter(prefix="/realtime", tags=["realtime"])
    
    @router.get("/sse")
    async def sse_endpoint():
        """Server-Sent Events endpoint for real-time updates."""
        return EventSourceResponse(sse_event_generator())
    
    @router.get("/sse/metrics")
    async def sse_metrics():
        """SSE endpoint for metrics streaming."""
        return EventSourceResponse(metrics_sse_generator())
    
    @router.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for bidirectional communication."""
        manager = get_connection_manager()
        client_id = await manager.connect(websocket)
        
        try:
            # Send welcome message
            await websocket.send_json({
                "type": "welcome",
                "client_id": client_id,
                "amos_available": AMOS_AVAILABLE,
            })
            
            while True:
                # Receive message
                data = await websocket.receive_json()
                
                # Handle commands
                if data.get("action") == "join_room":
                    room = data.get("room", "general")
                    await manager.join_room(websocket, room)
                    await websocket.send_json({
                        "type": "joined",
                        "room": room,
                    })
                
                elif data.get("action") == "think":
                    if AMOS_AVAILABLE:
                        query = data.get("query", "Hello")
                        result = think(query)
                        await websocket.send_json({
                            "type": "think_result",
                            "query": query,
                            "result": result.content[:200],
                            "confidence": result.confidence,
                        })
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "message": "AMOS brain not available",
                        })
                
                elif data.get("action") == "broadcast":
                    room = data.get("room", "general")
                    message = data.get("message", {})
                    await manager.broadcast_to_room(room, {
                        "type": "broadcast",
                        "sender": client_id,
                        "data": message,
                    })
                    
                elif data.get("action") == "status":
                    await websocket.send_json({
                        "type": "status",
                        "client_id": client_id,
                        "stats": manager.get_stats(),
                    })
                
                else:
                    # Echo back
                    await websocket.send_json({
                        "type": "echo",
                        "received": data,
                    })
                    
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    
    @router.get("/stats")
    async def realtime_stats():
        """Get real-time connection statistics."""
        return get_connection_manager().get_stats()


def main():
    """Run standalone real-time server."""
    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI not available")
        return
    
    import uvicorn
    from fastapi import FastAPI
    
    app = FastAPI(title="AMOS Real-Time Server")
    app.include_router(router)
    
    @app.get("/")
    async def root():
        return {
            "service": "AMOS Real-Time",
            "features": ["sse", "websocket", "broadcast"],
            "amos_available": AMOS_AVAILABLE,
        }
    
    print("🚀 Starting AMOS Real-Time Server")
    print("📊 SSE: http://localhost:8001/realtime/sse")
    print("🔌 WebSocket: ws://localhost:8001/realtime/ws")
    uvicorn.run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    main()
