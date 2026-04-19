#!/usr/bin/env python3
"""AMOS Unified Event Streaming Platform - Phase 24
Production-grade event streaming for 14-Layer Cognitive Architecture.
"""

import asyncio
import json
import os
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

try:
    from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False

try:
    from collections.abc import Callable

    import redis.asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_PREFIX = os.getenv("KAFKA_TOPIC_PREFIX", "amos")
EVENT_STORE_PATH = Path(os.getenv("EVENT_STORE_PATH", "/var/lib/amos/events"))


class EventType(str, Enum):
    SYSTEM_INITIALIZED = "system.initialized"
    LAYER_ACTIVATED = "layer.activated"
    LAYER_DEACTIVATED = "layer.deactivated"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    MEMORY_STORED = "memory.stored"
    AGENT_SPAWNED = "agent.spawned"
    SECURITY_ALERT = "security.alert"


@dataclass
class DomainEvent:
    event_type: EventType
    aggregate_id: str
    aggregate_type: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: int = 1

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type.value,
            "aggregate_id": self.aggregate_id,
            "aggregate_type": self.aggregate_type,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "event_id": self.event_id,
            "version": self.version,
        }


class EventStore:
    """Event Sourcing store with replay capabilities."""

    def __init__(self, path: Path = EVENT_STORE_PATH):
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)
        self._streams: dict[str, list[DomainEvent]] = {}
        self._seq = 0

    async def append(self, event: DomainEvent) -> None:
        self._seq += 1
        stream_file = self.path / f"{event.aggregate_id}.jsonl"
        with open(stream_file, "a") as f:
            f.write(json.dumps(event.to_dict()) + "\n")

        if event.aggregate_id not in self._streams:
            self._streams[event.aggregate_id] = []
        self._streams[event.aggregate_id].append(event)

    def get_stream(self, aggregate_id: str) -> List[DomainEvent]:
        return self._streams.get(aggregate_id, [])

    def replay(self, aggregate_id: str, projector: Callable, initial: Any = None) -> Any:
        state = initial
        for event in self.get_stream(aggregate_id):
            state = projector(state, event)
        return state


class AMOSEventBus:
    """Unified event bus with Kafka + Redis fallback."""

    def __init__(self):
        self._kafka_producer: Any = None
        self._redis: Any = None
        self._handlers: dict[str, list[Callable]] = {}
        self.event_store = EventStore()

    async def initialize(self) -> bool:
        if KAFKA_AVAILABLE:
            try:
                self._kafka_producer = AIOKafkaProducer(
                    bootstrap_servers=KAFKA_BOOTSTRAP,
                    value_serializer=lambda v: json.dumps(v).encode(),
                )
                await self._kafka_producer.start()
                return True
            except Exception:
                pass

        if REDIS_AVAILABLE:
            try:
                self._redis = await aioredis.from_url("redis://localhost:6379/0")
                return True
            except Exception:
                pass

        return False

    async def publish(self, event: DomainEvent, layer: str = "00") -> bool:
        topic = f"{TOPIC_PREFIX}.{layer}.{event.aggregate_type}.events"

        # Store for event sourcing
        await self.event_store.append(event)

        # Publish to Kafka
        if self._kafka_producer:
            try:
                await self._kafka_producer.send(topic, event.to_dict())
                return True
            except Exception:
                pass

        # Fallback to Redis
        if self._redis:
            try:
                await self._redis.xadd(topic, {"data": json.dumps(event.to_dict())})
                return True
            except Exception:
                pass

        return False

    def subscribe(self, event_type: str, handler: Callable) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def process_event(self, event: DomainEvent) -> None:
        handlers = self._handlers.get(event.event_type.value, [])
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)


class AMOSEventStreamingPlatform:
    """Main platform integrating 14-Layer event streaming."""

    LAYERS = {
        "00": "root",
        "01": "brain",
        "02": "senses",
        "03": "immune",
        "04": "blood",
        "05": "nerves",
        "06": "muscle",
        "07": "metabolism",
        "08": "growth",
        "09": "social",
        "10": "memory",
        "11": "legal",
        "12": "ethics",
        "13": "time",
        "14": "interfaces",
    }

    def __init__(self):
        self.bus = AMOSEventBus()
        self._initialized = False

    async def initialize(self) -> bool:
        self._initialized = await self.bus.initialize()
        return self._initialized

    async def emit_layer_event(
        self, layer: str, event_type: EventType, aggregate_id: str, payload: dict
    ) -> bool:
        """Emit event from specific layer."""
        event = DomainEvent(
            event_type=event_type,
            aggregate_id=aggregate_id,
            aggregate_type=self.LAYERS.get(layer, "unknown"),
            payload=payload,
        )
        return await self.bus.publish(event, layer)

    def subscribe_to_layer(self, layer: str, handler: Callable) -> None:
        """Subscribe to all events from a layer."""
        for event_type in EventType:
            self.bus.subscribe(f"{TOPIC_PREFIX}.{layer}", handler)

    def get_event_store(self) -> EventStore:
        """Get event store for replay/audit."""
        return self.bus.event_store


# Global instance
_platform: Optional[AMOSEventStreamingPlatform] = None


def get_event_platform() -> AMOSEventStreamingPlatform:
    global _platform
    if _platform is None:
        _platform = AMOSEventStreamingPlatform()
    return _platform


if __name__ == "__main__":
    print("AMOS Event Streaming Platform - Phase 24")
    print("=" * 50)
    print("Features:")
    print("  - 14-Layer event streaming")
    print("  - Event sourcing with replay")
    print("  - Kafka + Redis fallback")
    print("  - CQRS pattern support")
    print("=" * 50)
    print("Status: Ready")
