from typing import Any

"""AMOS Brain Streaming API

Real-time WebSocket streaming for brain processing with ReAct steps.
Based on research: Streaming agent outputs for responsive UX.
"""
from __future__ import annotations


import json
import sys
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

# Add clawspring to path
CLAWSPRING_PATH = Path(__file__).parent.parent.parent / "clawspring"
if str(CLAWSPRING_PATH) not in sys.path:
    sys.path.insert(0, str(CLAWSPRING_PATH))


try:
    from amos_brain.brain_event_integration import (
        BrainEventProcessor,
        get_brain_event_processor,
    )

    BRAIN_STREAMING_AVAILABLE = True
except ImportError as e:
    BRAIN_STREAMING_AVAILABLE = False
    print(f"[BrainStreaming] Not available: {e}")

router = APIRouter(prefix="/brain-stream", tags=["brain-streaming"])


class BrainStreamRequest(BaseModel):
    """Request for brain streaming."""

    query: str
    mode: str = "auto"
    context: dict[str, Any] = {}


class BrainStreamManager:
    """Manage WebSocket connections for brain streaming."""

    def __init__(self):
        self.connections: dict[str, WebSocket] = {}
        self.processor: BrainEventProcessor | None = None
        if BRAIN_STREAMING_AVAILABLE:
            self.processor = get_brain_event_processor()

    async def connect(self, client_id: str, websocket: WebSocket) -> None:
        """Accept new WebSocket connection."""
        await websocket.accept()
        self.connections[client_id] = websocket

        # Send welcome message
        await websocket.send_json(
            {
                "type": "connected",
                "client_id": client_id,
                "brain_available": BRAIN_STREAMING_AVAILABLE,
            }
        )

    def disconnect(self, client_id: str) -> None:
        """Remove WebSocket connection."""
        if client_id in self.connections:
            del self.connections[client_id]

    async def stream_brain_processing(
        self,
        client_id: str,
        query: str,
        mode: str = "auto",
        context: dict[str, Any] = None,
    ) -> None:
        """
        Stream brain processing steps to client.

        Args:
            client_id: WebSocket client ID
            query: User query to process
            mode: Processing mode (fast/react/reflect/auto)
            context: Additional context
        """
        if client_id not in self.connections:
            return

        websocket = self.connections[client_id]

        if not BRAIN_STREAMING_AVAILABLE or not self.processor:
            await websocket.send_json(
                {
                    "type": "error",
                    "error": "Brain streaming not available",
                }
            )
            return

        try:
            # Send start event
            await websocket.send_json(
                {
                    "type": "processing_started",
                    "query": query[:100],
                    "mode": mode,
                }
            )

            # Stream ReAct steps
            async for event in self.processor.stream_react_steps(query):
                await websocket.send_json(
                    {
                        "type": "step",
                        "step": event.step,
                        "iteration": event.iteration,
                        "thought": event.thought,
                        "action": event.action,
                        "observation": event.observation,
                        "latency_ms": event.latency_ms,
                        "timestamp": event.timestamp,
                    }
                )

            # Send final result
            result = await self.processor.process_with_events(query, mode, context)

            await websocket.send_json(
                {
                    "type": "complete",
                    "response": result.response,
                    "confidence": result.confidence,
                    "latency_ms": result.latency_ms,
                    "components_used": result.components_used,
                }
            )

        except Exception as e:
            await websocket.send_json(
                {
                    "type": "error",
                    "error": str(e),
                }
            )


# Global stream manager
_stream_manager = BrainStreamManager()


@router.websocket("/ws/{client_id}")
async def brain_websocket(websocket: WebSocket, client_id: str) -> None:
    """
    WebSocket endpoint for real-time brain processing.

    Streams:
    - processing_started: When processing begins
    - step: Each ReAct step (thought/action/observation)
    - complete: Final result
    - error: If something goes wrong

    Usage:
        ws = new WebSocket("ws://localhost:8000/brain-stream/ws/client-123")
        ws.onmessage = (e) => console.log(JSON.parse(e.data))
        ws.send(JSON.stringify({query: "What is AI?", mode: "auto"}))
    """
    await _stream_manager.connect(client_id, websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                request = json.loads(data)
                query = request.get("query", "")
                mode = request.get("mode", "auto")
                context = request.get("context", {})

                # Stream processing
                await _stream_manager.stream_brain_processing(client_id, query, mode, context)

            except json.JSONDecodeError:
                await websocket.send_json(
                    {
                        "type": "error",
                        "error": "Invalid JSON",
                    }
                )

    except WebSocketDisconnect:
        _stream_manager.disconnect(client_id)


@router.get("/status")
async def brain_streaming_status() -> dict[str, Any]:
    """Get brain streaming status."""

    # Check fast thinking availability
    fast_thinking = False
    try:
        fast_thinking = True
    except Exception:
        pass

    return {
        "available": BRAIN_STREAMING_AVAILABLE,
        "fast_thinking": fast_thinking,
        "active_connections": len(_stream_manager.connections),
        "processor_ready": _stream_manager.processor is not None,
    }


if __name__ == "__main__":
    print("Brain Streaming API Test")
    print("=" * 60)
    print(f"Brain Streaming Available: {BRAIN_STREAMING_AVAILABLE}")
    print(f"Stream Manager Ready: {_stream_manager.processor is not None}")
    print("=" * 60)
