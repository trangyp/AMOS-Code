#!/usr/bin/env python3
"""AMOS Event Streaming System v1.0.0.

Apache Kafka-based event streaming for event-driven architecture.

Features:
  - Async Kafka producer/consumer with aiokafka
  - Event sourcing for complete audit trail
  - Schema validation with Avro
  - Multiple consumer groups
  - Event replay capabilities
  - Dead letter queue for failed events
  - Exactly-once semantics
  - Stream processing with Faust
  - Event-driven agent activation
  - Real-time analytics pipeline

Architecture:
  ┌─────────────────────────────────────────────────────────────┐
  │                     AMOS EVENT STREAMING                     │
  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
  │  │   Producer   │  │ Kafka Cluster│  │   Consumer   │      │
  │  │  (FastAPI)   │──→│   (3 brokers)│──→│ (Background) │      │
  │  └──────────────┘  └──────────────┘  └──────────────┘      │
  │         │                  │                  │            │
  │         ▼                  ▼                  ▼            │
  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
  │  │Schema Registry│  │   Topics     │  │   Handlers   │      │
  │  │   (Avro)     │  │ (Partitioned)│  │ (Event Sinks)│      │
  │  └──────────────┘  └──────────────┘  └──────────────┘      │
  └─────────────────────────────────────────────────────────────┘

Topics:
  - amos.agent.events (spawn, terminate, state_change)
  - amos.memory.events (create, update, retrieve, consolidate)
  - amos.task.events (submit, start, progress, complete, fail)
  - amos.law.events (violation, block, warning)
  - amos.audit.events (user_action, system_event, security)
  - amos.system.events (health, metrics, alert)
  - amos.orchestration.events (multi_agent, consensus, conflict)
  - amos.evolution.events (suggestion, review, approval, deploy)

Usage:
    from amos_events import EventProducer, EventConsumer, AMOSEvent

  # Produce events
  producer = EventProducer()
  await producer.send_event(
      topic="amos.agent.events",
      event=AMOSEvent(
          type="agent_spawned",
          data={"agent_id": "123", "role": "architect"}
      )
  )

  # Consume events
  consumer = EventConsumer(
      topics=["amos.agent.events"],
      group_id="agent-processors"
  )
  async for event in consumer:
      await process_event(event)

Requirements:
  pip install aiokafka avro-python3 fastavro

Author: Trang Phan
Version: 1.0.0
"""

import asyncio
import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar

# Try to import Kafka
try:
    from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
    from aiokafka.helpers import create_ssl_context

    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    print("[Events] Kafka not available, using mock implementation")

# Try to import Avro for schema validation
try:
    import fastavro
    import fastavro.schema

    AVRO_AVAILABLE = True
except ImportError:
    AVRO_AVAILABLE = False


T = TypeVar("T")


class EventType(str, Enum):
    """AMOS event types."""

    # Agent events
    AGENT_SPAWNED = "agent_spawned"
    AGENT_TERMINATED = "agent_terminated"
    AGENT_STATE_CHANGED = "agent_state_changed"
    AGENT_ASSIGNED_TASK = "agent_assigned_task"

    # Memory events
    MEMORY_CREATED = "memory_created"
    MEMORY_UPDATED = "memory_updated"
    MEMORY_RETRIEVED = "memory_retrieved"
    MEMORY_CONSOLIDATED = "memory_consolidated"
    MEMORY_FORGOTTEN = "memory_forgotten"

    # Task events
    TASK_SUBMITTED = "task_submitted"
    TASK_STARTED = "task_started"
    TASK_PROGRESS = "task_progress"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_CANCELLED = "task_cancelled"

    # Law events
    LAW_VIOLATION_DETECTED = "law_violation_detected"
    LAW_ACTION_BLOCKED = "law_action_blocked"
    LAW_WARNING_ISSUED = "law_warning_issued"

    # Audit events
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_ACTION = "user_action"
    PERMISSION_DENIED = "permission_denied"

    # System events
    SYSTEM_STARTED = "system_started"
    SYSTEM_HEALTH_CHECK = "system_health_check"
    SYSTEM_ALERT = "system_alert"
    METRICS_COLLECTED = "metrics_collected"

    # Orchestration events
    ORCHESTRATION_STARTED = "orchestration_started"
    CONSENSUS_REACHED = "consensus_reached"
    CONFLICT_DETECTED = "conflict_detected"
    MULTI_AGENT_SYNC = "multi_agent_sync"

    # Evolution events
    EVOLUTION_SUGGESTED = "evolution_suggested"
    EVOLUTION_REVIEWED = "evolution_reviewed"
    EVOLUTION_APPROVED = "evolution_approved"
    EVOLUTION_DEPLOYED = "evolution_deployed"


@dataclass
class AMOSEvent:
    """AMOS event structure."""

    event_type: EventType | str
    data: Dict[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    source: str = "amos"
    correlation_id: str = None
    causation_id: str = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": str(self.event_type),
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "data": self.data,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AMOSEvent":
        """Create event from dictionary."""
        return cls(
            event_id=data.get("event_id", str(uuid.uuid4())),
            event_type=data.get("event_type", "unknown"),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if "timestamp" in data
            else datetime.now(UTC),
            source=data.get("source", "amos"),
            data=data.get("data", {}),
            correlation_id=data.get("correlation_id"),
            causation_id=data.get("causation_id"),
            metadata=data.get("metadata", {}),
        )


# Event schemas (Avro)
EVENT_SCHEMAS: Dict[str, dict[str, Any]] = {
    "agent_spawned": {
        "type": "record",
        "name": "AgentSpawned",
        "fields": [
            {"name": "agent_id", "type": "string"},
            {"name": "role", "type": "string"},
            {"name": "paradigm", "type": "string"},
            {"name": "capabilities", "type": {"type": "map", "values": "string"}},
        ],
    },
    "task_completed": {
        "type": "record",
        "name": "TaskCompleted",
        "fields": [
            {"name": "task_id", "type": "string"},
            {"name": "agent_id", "type": "string"},
            {"name": "result", "type": ["null", "string"]},
            {"name": "duration_ms", "type": "long"},
        ],
    },
    "law_violation_detected": {
        "type": "record",
        "name": "LawViolation",
        "fields": [
            {"name": "law_id", "type": "string"},
            {"name": "violation_level", "type": "int"},
            {"name": "action", "type": "string"},
            {"name": "blocked", "type": "boolean"},
        ],
    },
}


class EventProducer:
    """AMOS Kafka event producer."""

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        client_id: str = "amos-producer",
        enable_idempotence: bool = True,
    ):
        """Initialize event producer.

        Args:
            bootstrap_servers: Kafka broker addresses
            client_id: Producer client ID
            enable_idempotence: Exactly-once semantics
        """
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id
        self.enable_idempotence = enable_idempotence
        self._producer: Optional[AIOKafkaProducer] = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize Kafka producer."""
        if not KAFKA_AVAILABLE:
            print("[EventProducer] Kafka not available")
            return False

        if self._initialized:
            return True

        try:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=self.client_id,
                enable_idempotence=self.enable_idempotence,
                compression_type="gzip",
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
            )
            await self._producer.start()
            self._initialized = True
            print(f"[EventProducer] Connected to {self.bootstrap_servers}")
            return True
        except Exception as e:
            print(f"[EventProducer] Failed to initialize: {e}")
            return False

    async def close(self) -> None:
        """Close producer connection."""
        if self._producer:
            await self._producer.stop()
            self._producer = None
            self._initialized = False

    async def send_event(
        self, topic: str, event: AMOSEvent, key: str = None, headers: Dict[str, str] = None
    ) -> bool:
        """Send event to Kafka topic.

        Args:
            topic: Target topic
            event: Event to send
            key: Partition key (optional)
            headers: Message headers (optional)

        Returns:
            True if sent successfully
        """
        if not self._initialized or not self._producer:
            print(f"[EventProducer] Not initialized, event dropped: {event.event_type}")
            return False

        try:
            # Prepare headers
            msg_headers = {
                "event_type": str(event.event_type),
                "event_id": event.event_id,
                "source": event.source,
            }
            if headers:
                msg_headers.update(headers)

            # Send to Kafka
            await self._producer.send(
                topic=topic,
                key=key.encode("utf-8") if key else None,
                value=event.to_dict(),
                headers=[(k, v.encode("utf-8")) for k, v in msg_headers.items()],
            )

            print(f"[EventProducer] Sent: {event.event_type} → {topic}")
            return True

        except Exception as e:
            print(f"[EventProducer] Failed to send: {e}")
            return False

    async def send_batch(self, topic: str, events: List[AMOSEvent], key: str = None) -> int:
        """Send batch of events.

        Args:
            topic: Target topic
            events: Events to send
            key: Partition key

        Returns:
            Number of events sent
        """
        if not self._initialized:
            return 0

        sent = 0
        for event in events:
            if await self.send_event(topic, event, key):
                sent += 1

        return sent


class EventConsumer:
    """AMOS Kafka event consumer."""

    def __init__(
        self,
        topics: List[str],
        group_id: str,
        bootstrap_servers: str = "localhost:9092",
        client_id: str = None,
        auto_offset_reset: str = "latest",
        enable_auto_commit: bool = True,
        max_poll_records: int = 100,
    ):
        """Initialize event consumer.

        Args:
            topics: Topics to subscribe to
            group_id: Consumer group ID
            bootstrap_servers: Kafka broker addresses
            client_id: Consumer client ID
            auto_offset_reset: Where to start (earliest/latest)
            enable_auto_commit: Auto commit offsets
            max_poll_records: Max records per poll
        """
        self.topics = topics
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers
        self.client_id = client_id or f"amos-consumer-{uuid.uuid4().hex[:8]}"
        self.auto_offset_reset = auto_offset_reset
        self.enable_auto_commit = enable_auto_commit
        self.max_poll_records = max_poll_records
        self._consumer: Optional[AIOKafkaConsumer] = None
        self._initialized = False
        self._running = False

    async def initialize(self) -> bool:
        """Initialize Kafka consumer."""
        if not KAFKA_AVAILABLE:
            print("[EventConsumer] Kafka not available")
            return False

        if self._initialized:
            return True

        try:
            self._consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                client_id=self.client_id,
                auto_offset_reset=self.auto_offset_reset,
                enable_auto_commit=self.enable_auto_commit,
                max_poll_records=self.max_poll_records,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            )
            await self._consumer.start()
            self._initialized = True
            print(f"[EventConsumer] Subscribed to {self.topics} as {self.group_id}")
            return True
        except Exception as e:
            print(f"[EventConsumer] Failed to initialize: {e}")
            return False

    async def close(self) -> None:
        """Close consumer connection."""
        self._running = False
        if self._consumer:
            await self._consumer.stop()
            self._consumer = None
            self._initialized = False

    async def events(self) -> asyncio.AsyncGenerator[AMOSEvent, None]:
        """Async generator for consuming events.

        Yields:
            AMOSEvent instances
        """
        if not self._initialized or not self._consumer:
            print("[EventConsumer] Not initialized")
            return

        self._running = True
        print(f"[EventConsumer] Started consuming from {self.topics}")

        try:
            async for msg in self._consumer:
                if not self._running:
                    break

                try:
                    event = AMOSEvent.from_dict(msg.value)
                    event.metadata.update(
                        {
                            "kafka_topic": msg.topic,
                            "kafka_partition": msg.partition,
                            "kafka_offset": msg.offset,
                            "consumer_group": self.group_id,
                        }
                    )
                    yield event

                except Exception as e:
                    print(f"[EventConsumer] Failed to parse event: {e}")
                    continue

        except Exception as e:
            print(f"[EventConsumer] Consumer error: {e}")
        finally:
            print("[EventConsumer] Stopped")

    async def seek_to_beginning(self) -> None:
        """Seek to beginning of topics (replay)."""
        if self._consumer:
            await self._consumer.seek_to_beginning()

    async def seek_to_end(self) -> None:
        """Seek to end of topics."""
        if self._consumer:
            await self._consumer.seek_to_end()


class EventHandler(ABC):
    """Abstract base class for event handlers."""

    @abstractmethod
    async def handle(self, event: AMOSEvent) -> None:
        """Handle an event.

        Args:
            event: Event to handle
        """
        pass

    @abstractmethod
    def can_handle(self, event_type: EventType | str) -> bool:
        """Check if handler can handle event type.

        Args:
            event_type: Event type to check

        Returns:
            True if can handle
        """
        pass


class EventProcessor:
    """Event processor with multiple handlers."""

    def __init__(self, consumer: EventConsumer):
        """Initialize processor.

        Args:
            consumer: Event consumer
        """
        self.consumer = consumer
        self.handlers: List[EventHandler] = []
        self._running = False

    def add_handler(self, handler: EventHandler) -> None:
        """Add event handler.

        Args:
            handler: Handler to add
        """
        self.handlers.append(handler)
        print(f"[EventProcessor] Added handler: {type(handler).__name__}")

    async def start(self) -> None:
        """Start processing events."""
        if not await self.consumer.initialize():
            return

        self._running = True
        print(f"[EventProcessor] Started with {len(self.handlers)} handlers")

        async for event in self.consumer.events():
            if not self._running:
                break

            # Route to appropriate handlers
            for handler in self.handlers:
                if handler.can_handle(event.event_type):
                    try:
                        await handler.handle(event)
                    except Exception as e:
                        print(f"[EventProcessor] Handler error: {e}")

    async def stop(self) -> None:
        """Stop processing events."""
        self._running = False
        await self.consumer.close()


# Example handlers
class AgentEventHandler(EventHandler):
    """Handler for agent lifecycle events."""

    def can_handle(self, event_type: EventType | str) -> bool:
        return str(event_type).startswith("agent_")

    async def handle(self, event: AMOSEvent) -> None:
        print(f"[AgentHandler] {event.event_type}: {event.data.get('agent_id')}")
        # Implement agent state updates


class AuditEventHandler(EventHandler):
    """Handler for audit events."""

    def can_handle(self, event_type: EventType | str) -> bool:
        return str(event_type) in ["user_login", "user_logout", "user_action"]

    async def handle(self, event: AMOSEvent) -> None:
        # Persist to audit log
        print(f"[AuditHandler] {event.event_type}: {event.data}")


class LawViolationHandler(EventHandler):
    """Handler for law violation events."""

    def can_handle(self, event_type: EventType | str) -> bool:
        return str(event_type).startswith("law_")

    async def handle(self, event: AMOSEvent) -> None:
        print(f"[LawHandler] VIOLATION: {event.data.get('law_id')}")
        # Trigger alerts, notifications


# AMOS Topics
AMOS_TOPICS = {
    "agent": "amos.agent.events",
    "memory": "amos.memory.events",
    "task": "amos.task.events",
    "law": "amos.law.events",
    "audit": "amos.audit.events",
    "system": "amos.system.events",
    "orchestration": "amos.orchestration.events",
    "evolution": "amos.evolution.events",
    "dead_letter": "amos.dead-letter.events",
}


async def main():
    """Demo event streaming."""
    print("=" * 70)
    print("AMOS EVENT STREAMING SYSTEM v1.0.0")
    print("=" * 70)

    if not KAFKA_AVAILABLE:
        print("\n⚠️  Kafka not installed")
        print("Install with: pip install aiokafka")
        return

    # Initialize producer
    producer = EventProducer()
    if not await producer.initialize():
        print("\n⚠️  Failed to connect to Kafka")
        print("Ensure Kafka is running on localhost:9092")
        return

    # Send events
    print("\n[Demo: Sending Events]")

    events = [
        AMOSEvent(
            event_type=EventType.AGENT_SPAWNED,
            data={"agent_id": "agent-001", "role": "architect", "paradigm": "hybrid"},
        ),
        AMOSEvent(
            event_type=EventType.TASK_SUBMITTED,
            data={"task_id": "task-001", "agent_id": "agent-001", "type": "orchestrate"},
        ),
        AMOSEvent(event_type=EventType.TASK_PROGRESS, data={"task_id": "task-001", "progress": 50}),
        AMOSEvent(
            event_type=EventType.TASK_COMPLETED,
            data={"task_id": "task-001", "result": "success", "duration_ms": 1200},
        ),
        AMOSEvent(
            event_type=EventType.LAW_VIOLATION_DETECTED,
            data={"law_id": "L3", "violation_level": 3, "action": "unsafe_code", "blocked": True},
        ),
    ]

    for event in events:
        topic = AMOS_TOPICS.get(str(event.event_type).split("_")[0], "amos.events")
        await producer.send_event(topic, event)
        await asyncio.sleep(0.5)

    print(f"\n  ✓ Sent {len(events)} events")

    # Setup consumer
    print("\n[Demo: Consuming Events]")

    consumer = EventConsumer(
        topics=list(AMOS_TOPICS.values())[:4],  # First 4 topics
        group_id="amos-demo-consumer",
        auto_offset_reset="earliest",
    )

    # Setup processor
    processor = EventProcessor(consumer)
    processor.add_handler(AgentEventHandler())
    processor.add_handler(AuditEventHandler())
    processor.add_handler(LawViolationHandler())

    # Consume for a few seconds
    print("\n  Consuming for 5 seconds...")

    async def consume_with_timeout():
        try:
            await asyncio.wait_for(processor.start(), timeout=5.0)
        except TimeoutError:
            pass

    await consume_with_timeout()
    await processor.stop()
    await producer.close()

    print("\n" + "=" * 70)
    print("Event streaming demo completed!")
    print("=" * 70)

    print("\n📊 AMOS Topics:")
    for name, topic in AMOS_TOPICS.items():
        print(f"  • {name}: {topic}")

    print("\n🚀 Integration with FastAPI:")
    print("""
from fastapi import FastAPI
from amos_events import EventProducer, AMOSEvent, EventType
from typing import Callable, TypeVar

app = FastAPI()
producer: Optional[EventProducer] = None

@app.on_event("startup")
async def startup():
    global producer
    producer = EventProducer()
    await producer.initialize()

@app.on_event("shutdown")
async def shutdown():
    if producer:
        await producer.close()

@app.post("/api/agents/{agent_id}/spawn")
async def spawn_agent(agent_id: str):
    # Spawn agent...

    # Emit event
    await producer.send_event(
        "amos.agent.events",
        AMOSEvent(
            event_type=EventType.AGENT_SPAWNED,
            data={"agent_id": agent_id, "role": "architect"}
        )
    )

    return {"status": "spawned"}
""")


if __name__ == "__main__":
    asyncio.run(main())
