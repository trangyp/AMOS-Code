from typing import Any

"""AMOS Real-Time Streaming Service
======================================
State-of-the-art async streaming with WebSocket and SSE support.
Integrates with AMOS brain for intelligent stream processing.

Based on:
- FastAPI WebSocket best practices (github.com/fastapi/fastapi)
- Async generator patterns for streaming
- aiofiles for async file operations
"""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum

UTC = UTC
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)


class StreamType(Enum):
    """Types of streams supported."""

    WEBSOCKET = "websocket"
    SSE = "sse"  # Server-Sent Events
    HTTP_CHUNKED = "http_chunked"


@dataclass
class StreamMessage:
    """A message in the stream."""

    timestamp: str
    data: Any
    message_type: str = "data"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, data: Any, message_type: str = "data") -> StreamMessage:
        return cls(
            timestamp=datetime.now(UTC).isoformat(),
            data=data,
            message_type=message_type,
        )

    def to_json(self) -> str:
        return json.dumps(
            {
                "timestamp": self.timestamp,
                "type": self.message_type,
                "data": self.data,
                "metadata": self.metadata,
            }
        )

    def to_sse(self) -> str:
        """Format as Server-Sent Event."""
        return f"event: {self.message_type}\ndata: {self.to_json()}\n\n"


@dataclass
class StreamConfig:
    """Configuration for a stream."""

    stream_type: StreamType
    heartbeat_interval: float = 30.0  # seconds
    max_message_size: int = 1024 * 1024  # 1MB
    batch_size: int = 100
    compression: bool = True


class AMOSStreamProcessor:
    """Processes streams with AMOS brain integration."""

    def __init__(self, brain_processor=None):
        self.brain_processor = brain_processor
        self._active_streams: dict[str, StreamConfig] = {}
        self._callbacks: dict[str, list[Callable]] = {}

    async def process_with_brain(self, data: Any, context: dict[str, Any] = None) -> dict[str, Any]:
        """Process data through AMOS brain before streaming."""
        if self.brain_processor is None:
            return {"data": data, "processed": False}

        try:
            # Use brain to analyze/enrich data
            result = self.brain_processor.process(str(data), context)
            return {
                "data": data,
                "brain_analysis": result.output[:500] if hasattr(result, "output") else None,
                "confidence": result.confidence if hasattr(result, "confidence") else None,
                "processed": True,
            }
        except Exception as e:
            logger.error(f"Brain processing error: {e}")
            return {"data": data, "processed": False, "error": str(e)}

    def register_callback(self, stream_id: str, callback: Callable) -> None:
        """Register a callback for stream events."""
        if stream_id not in self._callbacks:
            self._callbacks[stream_id] = []
        self._callbacks[stream_id].append(callback)

    async def emit(self, stream_id: str, message: StreamMessage) -> None:
        """Emit a message to registered callbacks."""
        callbacks = self._callbacks.get(stream_id, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
            except Exception as e:
                logger.error(f"Callback error: {e}")


class WebSocketStreamer:
    """WebSocket streaming with async generator pattern."""

    def __init__(self, processor: AMOSStreamProcessor):
        self.processor = processor
        self._connections: dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket) -> None:
        """Accept and store WebSocket connection."""
        await websocket.accept()
        self._connections[client_id] = websocket
        logger.info(f"WebSocket connected: {client_id}")

    def disconnect(self, client_id: str) -> None:
        """Remove WebSocket connection."""
        if client_id in self._connections:
            del self._connections[client_id]
            logger.info(f"WebSocket disconnected: {client_id}")

    async def send_to_client(self, client_id: str, message: StreamMessage) -> bool:
        """Send message to specific client."""
        websocket = self._connections.get(client_id)
        if websocket is None:
            return False

        try:
            await websocket.send_text(message.to_json())
            return True
        except WebSocketDisconnect:
            self.disconnect(client_id)
            return False
        except Exception as e:
            logger.error(f"Send error to {client_id}: {e}")
            return False

    async def broadcast(self, message: StreamMessage) -> int:
        """Broadcast message to all connected clients."""
        sent_count = 0
        disconnected = []

        for client_id, websocket in self._connections.items():
            try:
                await websocket.send_text(message.to_json())
                sent_count += 1
            except WebSocketDisconnect:
                disconnected.append(client_id)
            except Exception as e:
                logger.error(f"Broadcast error to {client_id}: {e}")
                disconnected.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)

        return sent_count

    async def stream_generator(
        self,
        client_id: str,
        data_source: AsyncGenerator[Any, None],
        context: dict[str, Any] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream data from async generator to WebSocket."""
        try:
            async for data in data_source:
                # Process through brain
                processed = await self.processor.process_with_brain(data, context)

                # Create message
                message = StreamMessage.create(processed, "data")

                # Send to client
                success = await self.send_to_client(client_id, message)
                if not success:
                    break

                # Yield for flow control
                yield message.to_json()

                # Small delay to prevent overwhelming
                await asyncio.sleep(0.01)

        except WebSocketDisconnect:
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Stream error: {e}")
            error_msg = StreamMessage.create({"error": str(e)}, "error")
            yield error_msg.to_json()


class SSEStreamer:
    """Server-Sent Events streaming."""

    def __init__(self, processor: AMOSStreamProcessor):
        self.processor = processor

    async def stream_response(
        self, data_source: AsyncGenerator[Any, None], context: dict[str, Any] = None
    ) -> StreamingResponse:
        """Create SSE streaming response."""

        async def sse_generator() -> AsyncGenerator[str, None]:
            try:
                async for data in data_source:
                    # Process through brain
                    processed = await self.processor.process_with_brain(data, context)

                    # Create SSE message
                    message = StreamMessage.create(processed, "data")
                    yield message.to_sse()

                    # Heartbeat every 30 seconds
                    await asyncio.sleep(0.01)

            except Exception as e:
                error_msg = StreamMessage.create({"error": str(e)}, "error")
                yield error_msg.to_sse()

        return StreamingResponse(
            sse_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )


class FileTailStreamer:
    """Stream file updates in real-time (like tail -f)."""

    def __init__(self, processor: AMOSStreamProcessor):
        self.processor = processor

    async def tail_file(
        self, file_path: Path, lines: int = 10, follow: bool = True
    ) -> AsyncGenerator[str, None]:
        """Async generator that yields file lines as they are written."""

        # First, yield last N lines
        if file_path.exists():
            try:
                # Read last N lines
                with open(file_path) as f:
                    all_lines = f.readlines()
                    last_lines = all_lines[-lines:]
                    for line in last_lines:
                        yield line.strip()
            except Exception as e:
                logger.error(f"Error reading file: {e}")

        if not follow:
            return

        # Then follow for new lines
        # Note: In production, use aiofiles for true async file I/O
        # and watchdog for file change detection
        last_size = file_path.stat().st_size if file_path.exists() else 0

        while follow:
            try:
                if not file_path.exists():
                    await asyncio.sleep(1)
                    continue

                current_size = file_path.stat().st_size

                if current_size > last_size:
                    with open(file_path) as f:
                        f.seek(last_size)
                        new_data = f.read()
                        if new_data:
                            for line in new_data.strip().split("\n"):
                                if line:
                                    yield line

                    last_size = current_size

                await asyncio.sleep(0.5)  # Poll every 500ms

            except Exception as e:
                logger.error(f"Tail error: {e}")
                await asyncio.sleep(1)


# ============================================================================
# FastAPI Integration
# ============================================================================


def create_streaming_app(brain_processor=None) -> FastAPI:
    """Create FastAPI app with streaming endpoints."""

    app = FastAPI(title="AMOS Real-Time Streaming")
    processor = AMOSStreamProcessor(brain_processor)
    ws_streamer = WebSocketStreamer(processor)
    sse_streamer = SSEStreamer(processor)

    @app.websocket("/ws/stream/{client_id}")
    async def websocket_endpoint(websocket: WebSocket, client_id: str):
        """WebSocket streaming endpoint."""
        await ws_streamer.connect(client_id, websocket)

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()

                try:
                    parsed = json.loads(data)
                    message_type = parsed.get("type", "echo")

                    if message_type == "echo":
                        # Simple echo with brain processing
                        processed = await processor.process_with_brain(
                            parsed.get("data", {}), {"client_id": client_id}
                        )
                        response = StreamMessage.create(processed, "echo_response")
                        await websocket.send_text(response.to_json())

                    elif message_type == "subscribe":
                        # Subscribe to a stream
                        stream_id = parsed.get("stream_id")
                        processor.register_callback(
                            stream_id, lambda msg: ws_streamer.send_to_client(client_id, msg)
                        )
                        await websocket.send_text(
                            StreamMessage.create({"subscribed": stream_id}, "confirm").to_json()
                        )

                except json.JSONDecodeError:
                    error = StreamMessage.create({"error": "Invalid JSON"}, "error")
                    await websocket.send_text(error.to_json())

        except WebSocketDisconnect:
            ws_streamer.disconnect(client_id)

    @app.get("/sse/stream")
    async def sse_endpoint() -> StreamingResponse:
        """SSE streaming endpoint."""

        async def dummy_data_source() -> AsyncGenerator[Any, None]:
            """Generate dummy data for demo."""
            for i in range(100):
                yield {"iteration": i, "timestamp": datetime.now(UTC).isoformat()}
                await asyncio.sleep(1)

        return await sse_streamer.stream_response(dummy_data_source())

    @app.post("/stream/broadcast")
    async def broadcast_message(data: dict[str, Any]) -> dict[str, Any]:
        """Broadcast a message to all connected WebSocket clients."""
        message = StreamMessage.create(data.get("payload", {}), data.get("type", "broadcast"))
        count = await ws_streamer.broadcast(message)
        return {"broadcast_to": count, "timestamp": message.timestamp}

    return app


# ============================================================================
# Usage Example
# ============================================================================


async def demo_streaming():
    """Demonstrate streaming capabilities."""

    from amos_brain.task_processor import BrainTaskProcessor

    # Initialize brain processor
    brain = BrainTaskProcessor()
    processor = AMOSStreamProcessor(brain)

    # Create streamers
    WebSocketStreamer(processor)
    SSEStreamer(processor)

    # Demo: Create async data source
    async def demo_data_source() -> AsyncGenerator[Any, None]:
        for i in range(5):
            yield {"value": i, "message": f"Data point {i}"}
            await asyncio.sleep(0.5)

    # Demo: Process stream
    print("=== Streaming with Brain Processing ===")
    async for data in demo_data_source():
        processed = await processor.process_with_brain(data)
        print(f"Original: {data}")
        print(f"Processed: {processed}")
        print()


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_streaming())
