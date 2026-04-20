"""Event bus for AMOS Platform using Redis Streams.

Provides async cross-repo event communication.
"""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import AsyncIterator, Callable
from datetime import datetime, timezone
from typing import Any

UTC = timezone.utc

import redis.asyncio as redis


class EventBus:
    """Async event bus using Redis Streams for 6-repo ecosystem."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self._redis_url = redis_url
        self._redis: redis.Optional[Redis] = None
        self._subscribers: dict[str, list[Callable]] = {}
        self._connected = False

    async def connect(self):
        """Connect to Redis."""
        self._redis = redis.from_url(self._redis_url)
        self._connected = True

    async def disconnect(self):
        """Disconnect from Redis."""
        if self._redis:
            await self._redis.close()
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected and self._redis is not None

    async def publish(self, event_type: str, payload: dict[str, Any]):
        """Publish event to the bus."""
        if not self._redis:
            return

        event_data = {
            "event_type": event_type,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_id": f"evt_{os.urandom(8).hex()}",
        }

        await self._redis.xadd(event_type, {"data": json.dumps(event_data)}, maxlen=10000)

        # Notify local subscribers
        for callback in self._subscribers.get(event_type, []):
            asyncio.create_task(callback(event_data))

    async def subscribe(self, event_type: str, callback: Callable[[dict], Any]):
        """Subscribe to specific event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    async def listen(self) -> AsyncIterator[dict[str, Any]]:
        """Listen for all events."""
        if not self._redis:
            return

        # Subscribe to common event patterns
        patterns = [
            "claws.*",
            "mailinh.*",
            "invest.*",
            "repo.*",
            "model.*",
            "workflow.*",
            "universe.*",
            "system.*",
        ]

        while True:
            try:
                # Check each pattern for new messages
                for pattern in patterns:
                    streams = await self._redis.keys(pattern.replace("*", "*"))
                    for stream in streams:
                        if isinstance(stream, bytes):
                            stream = stream.decode()

                        messages = await self._redis.xread({stream: "0"}, count=10, block=100)
                        for stream_name, msgs in messages:
                            for msg_id, fields in msgs:
                                data = json.loads(fields.get("data", "{}"))
                                yield data
                                # Acknowledge by deleting (simplified)
                                await self._redis.xdel(stream_name, msg_id)

                await asyncio.sleep(0.1)
            except Exception:
                await asyncio.sleep(1)
