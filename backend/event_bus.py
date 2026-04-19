"""
AMOS Event Bus

Event-driven architecture using Redis Pub/Sub for distributed communication
between AMOS components. Bridges existing Python infrastructure with FastAPI.

Creator: Trang Phan
Version: 3.0.0
"""

import asyncio
import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import redis.asyncio as redis

# Redis connection configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


@dataclass
class AMOSEvent:
    """Standard AMOS event structure."""

    event_type: str
    source: str
    payload: dict[str, Any]
    timestamp: str
    correlation_id: str = None
    priority: str = "normal"  # low, normal, high, critical

    def to_json(self) -> str:
        """Serialize event to JSON."""
        return json.dumps(
            {
                "event_type": self.event_type,
                "source": self.source,
                "payload": self.payload,
                "timestamp": self.timestamp,
                "correlation_id": self.correlation_id,
                "priority": self.priority,
            }
        )

    @classmethod
    def from_json(cls, data: str) -> "AMOSEvent":
        """Deserialize event from JSON."""
        parsed = json.loads(data)
        return cls(**parsed)


class EventBus:
    """
    Distributed event bus using Redis Pub/Sub.
    Enables communication between AMOS components.
    """

    def __init__(self, redis_url: str = REDIS_URL):
        self.redis_url = redis_url
        self._redis: redis.Redis = None
        self._pubsub = None
        self._handlers: dict[str, list[Callable]] = {}
        self._running = False
        self._listener_task = None

    async def connect(self):
        """Connect to Redis."""
        self._redis = await redis.from_url(self.redis_url, decode_responses=True)
        self._pubsub = self._redis.pubsub()
        print(f"[EventBus] Connected to Redis at {self.redis_url}")

    async def disconnect(self):
        """Disconnect from Redis."""
        self._running = False
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
        if self._pubsub:
            await self._pubsub.close()
        if self._redis:
            await self._redis.close()
        print("[EventBus] Disconnected from Redis")

    async def publish(self, event: AMOSEvent, channel: str = None) -> bool:
        """
        Publish an event to the bus.

        Args:
            event: The event to publish
            channel: Optional specific channel, defaults to event_type

        Returns:
            True if published successfully
        """
        if not self._redis:
            raise RuntimeError("EventBus not connected. Call connect() first.")

        target_channel = channel or f"amos:{event.event_type}"
        await self._redis.publish(target_channel, event.to_json())

        # Also publish to general channel for monitoring
        await self._redis.publish("amos:all", event.to_json())

        print(f"[EventBus] Published {event.event_type} to {target_channel}")
        return True

    def subscribe(self, event_type: str, handler: Callable[[AMOSEvent], None]):
        """
        Subscribe to a specific event type.

        Args:
            event_type: Type of event to subscribe to
            handler: Callback function for events
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        print(f"[EventBus] Subscribed handler to {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable[[AMOSEvent], None]):
        """Unsubscribe a handler from an event type."""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)

    async def start_listening(self):
        """Start listening for events from Redis."""
        if not self._pubsub:
            raise RuntimeError("EventBus not connected. Call connect() first.")

        # Subscribe to all channels we have handlers for
        channels = [f"amos:{event_type}" for event_type in self._handlers.keys()]
        channels.append("amos:all")

        if channels:
            await self._pubsub.subscribe(*channels)

        self._running = True
        self._listener_task = asyncio.create_task(self._listen_loop())
        print(f"[EventBus] Started listening on channels: {channels}")

    async def _listen_loop(self):
        """Main listening loop for events."""
        try:
            async for message in self._pubsub.listen():
                if not self._running:
                    break

                if message["type"] == "message":
                    try:
                        event = AMOSEvent.from_json(message["data"])
                        await self._dispatch_event(event)
                    except json.JSONDecodeError as e:
                        print(f"[EventBus] Failed to parse event: {e}")
                    except Exception as e:
                        print(f"[EventBus] Error handling event: {e}")
        except asyncio.CancelledError:
            print("[EventBus] Listener cancelled")
        except Exception as e:
            print(f"[EventBus] Listener error: {e}")

    async def _dispatch_event(self, event: AMOSEvent):
        """Dispatch event to all registered handlers."""
        handlers = self._handlers.get(event.event_type, [])

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                print(f"[EventBus] Handler error for {event.event_type}: {e}")

    # Convenience methods for common event types

    async def emit_evolution(
        self, evolution_type: str, description: str, impact: str = "medium", metadata: dict = None
    ):
        """Emit an evolution event."""
        event = AMOSEvent(
            event_type="evolution",
            source="evolution_engine",
            payload={
                "evolution_type": evolution_type,
                "description": description,
                "impact": impact,
                "metadata": metadata or {},
            },
            timestamp=datetime.now(UTC).isoformat(),
            priority="high" if impact == "high" else "normal",
        )
        await self.publish(event)

    async def emit_agent_task(
        self, task_id: str, task_name: str, status: str, progress: int = 0, agent_id: str = None
    ):
        """Emit an agent task event."""
        event = AMOSEvent(
            event_type="agent_task_updated",
            source="agent_orchestra",
            payload={
                "task_id": task_id,
                "task_name": task_name,
                "status": status,
                "progress": progress,
                "agent_id": agent_id,
            },
            timestamp=datetime.now(UTC).isoformat(),
        )
        await self.publish(event)

    async def emit_governance_action(
        self, rule_id: str, rule_name: str, action: str, triggered_by: str, approved: bool = True
    ):
        """Emit a governance action event."""
        event = AMOSEvent(
            event_type="governance_action",
            source="governance_engine",
            payload={
                "rule_id": rule_id,
                "rule_name": rule_name,
                "action": action,
                "triggered_by": triggered_by,
                "approved": approved,
            },
            timestamp=datetime.now(UTC).isoformat(),
            priority="high",
        )
        await self.publish(event)

    async def emit_system_metric(
        self, metric_name: str, value: float, unit: str = "", tags: dict = None
    ):
        """Emit a system metric event."""
        event = AMOSEvent(
            event_type="system_metrics_updated",
            source="monitoring",
            payload={
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                "tags": tags or {},
            },
            timestamp=datetime.now(UTC).isoformat(),
        )
        await self.publish(event)

    async def emit_memory_event(
        self, memory_system: str, operation: str, entry_id: str = None, content_preview: str = None
    ):
        """Emit a memory system event."""
        event = AMOSEvent(
            event_type="memory_entry_created",
            source=f"memory_{memory_system}",
            payload={
                "memory_system": memory_system,
                "operation": operation,
                "entry_id": entry_id,
                "content_preview": content_preview,
            },
            timestamp=datetime.now(UTC).isoformat(),
        )
        await self.publish(event)


# Global event bus instance
event_bus = EventBus()


async def initialize_event_bus():
    """Initialize the global event bus."""
    await event_bus.connect()
    await event_bus.start_listening()


async def shutdown_event_bus():
    """Shutdown the global event bus."""
    await event_bus.disconnect()
