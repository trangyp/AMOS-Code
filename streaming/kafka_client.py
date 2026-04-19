"""AMOS Equation System - Kafka Event Streaming.

Real-time event streaming with Apache Kafka for:
- Event sourcing
- Change Data Capture (CDC)
- Stream processing
- Real-time analytics

Author: AMOS Data Engineering Team
Version: 2.0.0
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer


class EventType(str, Enum):
    """Domain event types."""
    EQUATION_CREATED = "equation.created"
    EQUATION_UPDATED = "equation.updated"
    EQUATION_DELETED = "equation.deleted"
    EQUATION_VERIFIED = "equation.verified"
    USER_REGISTERED = "user.registered"
    USER_LOGIN = "user.login"
    WEBHOOK_DELIVERED = "webhook.delivered"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"


@dataclass
class DomainEvent:
    """Domain event structure."""
    event_id: str
    event_type: EventType
    aggregate_id: str  # Entity identifier (equation_id, user_id)
    aggregate_type: str  # Entity type (equation, user)
    timestamp: datetime
    version: int  # Event version for optimistic concurrency
    payload: Dict[str, Any]
    metadata: Dict[str, Any]  # Correlation_id, user_agent, ip, etc.


class KafkaEventBus:
    """Async Kafka event bus for domain events."""

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic_prefix: str = "amos",
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic_prefix = topic_prefix
        self._producer: Optional[AIOKafkaProducer] = None
        self._consumers: List[AIOKafkaConsumer] = []

    async def start(self) -> None:
        """Initialize Kafka producer."""
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            compression_type="gzip",
            max_batch_size=16384,
            linger_ms=10,
        )
        await self._producer.start()

    async def stop(self) -> None:
        """Shutdown Kafka connections."""
        if self._producer:
            await self._producer.stop()

        for consumer in self._consumers:
            await consumer.stop()

    async def publish(
        self,
        event: DomainEvent,
        partition: int  = None,
    ) -> None:
        """Publish event to Kafka."""
        if not self._producer:
            raise RuntimeError("Kafka producer not started")

        topic = f"{self.topic_prefix}.{event.aggregate_type}.events"
        key = event.aggregate_id  # Ensure events for same entity go to same partition

        message = {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "aggregate_id": event.aggregate_id,
            "aggregate_type": event.aggregate_type,
            "timestamp": event.timestamp.isoformat(),
            "version": event.version,
            "payload": event.payload,
            "metadata": event.metadata,
        }

        await self._producer.send(
            topic,
            value=message,
            key=key,
            partition=partition,
        )

    async def subscribe(
        self,
        aggregate_type: str,
        event_types: List[EventType],
        handler: Callable[[DomainEvent], None],
        consumer_group: str,
    ) -> AIOKafkaConsumer:
        """Subscribe to events."""
        topic = f"{self.topic_prefix}.{aggregate_type}.events"

        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=consumer_group,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            auto_commit_interval_ms=5000,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        )

        await consumer.start()
        self._consumers.append(consumer)

        # Start consuming in background
        asyncio.create_task(self._consume(consumer, event_types, handler))

        return consumer

    async def _consume(
        self,
        consumer: AIOKafkaConsumer,
        event_types: List[EventType],
        handler: Callable[[DomainEvent], None],
    ) -> None:
        """Consume messages."""
        allowed_types = {et.value for et in event_types}

        async for msg in consumer:
            try:
                data = msg.value

                # Filter by event type
                if data["event_type"] not in allowed_types:
                    continue

                event = DomainEvent(
                    event_id=data["event_id"],
                    event_type=EventType(data["event_type"]),
                    aggregate_id=data["aggregate_id"],
                    aggregate_type=data["aggregate_type"],
                    timestamp=datetime.fromisoformat(data["timestamp"]),
                    version=data["version"],
                    payload=data["payload"],
                    metadata=data["metadata"],
                )

                await handler(event)
            except Exception as e:
                # Log error but continue consuming
                print(f"Error processing message: {e}")


class StreamProcessor:
    """Stream processing patterns."""

    def __init__(self, kafka_bus: KafkaEventBus):
        self.kafka_bus = kafka_bus
        self._handlers: Dict[EventType, list[Callable]] = {}

    def on(self, event_type: EventType) -> Callable:
        """Decorator to register event handler."""
        def decorator(func: Callable) -> Callable:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(func)
            return func
        return decorator

    async def process(self, event: DomainEvent) -> None:
        """Process event through registered handlers."""
        handlers = self._handlers.get(event.event_type, [])

        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                print(f"Handler error: {e}")


class EventSourcingRepository:
    """Event sourcing repository for aggregates."""

    def __init__(
        self,
        kafka_bus: KafkaEventBus,
        aggregate_type: str,
    ):
        self.kafka_bus = kafka_bus
        self.aggregate_type = aggregate_type
        self._event_store: Dict[str, list[DomainEvent]] = {}  # In-memory for demo

    async def save(self, aggregate_id: str, events: List[DomainEvent]) -> None:
        """Save events to event store and publish to Kafka."""
        # Store in event store
        if aggregate_id not in self._event_store:
            self._event_store[aggregate_id] = []
        self._event_store[aggregate_id].extend(events)

        # Publish to Kafka
        for event in events:
            await self.kafka_bus.publish(event)

    async def get_events(
        self,
        aggregate_id: str,
        from_version: int = 0,
    ) -> List[DomainEvent]:
        """Get events for aggregate."""
        events = self._event_store.get(aggregate_id, [])
        return [e for e in events if e.version > from_version]

    async def get_all_events(
        self,
        after_position: int = 0,
        limit: int = 100,
    ) -> List[DomainEvent]:
        """Get all events (for projections)."""
        all_events = []
        for events in self._event_store.values():
            all_events.extend(events)

        all_events.sort(key=lambda e: e.timestamp)
        return all_events[after_position:after_position + limit]


# CDC (Change Data Capture) handler
class CDCProcessor:
    """Process CDC events from PostgreSQL Debezium."""

    def __init__(self, kafka_bus: KafkaEventBus):
        self.kafka_bus = kafka_bus

    async def handle_cdc_event(self, cdc_message: dict) -> None:
        """Process Debezium CDC message."""
        # Debezium message format
        before = cdc_message.get("before")
        after = cdc_message.get("after")
        op = cdc_message.get("op")  # c=create, u=update, d=delete
        table = cdc_message.get("source", {}).get("table")

        event_type = self._map_operation(op, table)
        if not event_type:
            return

        aggregate_id = after.get("id") if after else before.get("id")

        event = DomainEvent(
            event_id=f"{aggregate_id}-{datetime.now(timezone.utc).timestamp()}",
            event_type=event_type,
            aggregate_id=str(aggregate_id),
            aggregate_type=table,
            timestamp=datetime.now(timezone.utc),
            version=1,
            payload={"before": before, "after": after},
            metadata={
                "source": "cdc",
                "operation": op,
                "lsn": cdc_message.get("source", {}).get("lsn"),
            },
        )

        await self.kafka_bus.publish(event)

    def _map_operation(self, op: str, table: str) -> Optional[EventType]:
        """Map CDC operation to event type."""
        mapping = {
            ("c", "equations"): EventType.EQUATION_CREATED,
            ("u", "equations"): EventType.EQUATION_UPDATED,
            ("d", "equations"): EventType.EQUATION_DELETED,
            ("c", "users"): EventType.USER_REGISTERED,
        }
        return mapping.get((op, table))


# Real-time analytics streaming
class RealtimeAnalytics:
    """Real-time analytics from event stream."""

    def __init__(self, kafka_bus: KafkaEventBus):
        self.kafka_bus = kafka_bus
        self._metrics: Dict[str, Any] = {
            "events_per_second": 0,
            "equation_creates": 0,
            "active_users": set(),
        }

    async def start(self) -> None:
        """Start real-time analytics stream."""
        await self.kafka_bus.subscribe(
            aggregate_type="equations",
            event_types=[EventType.EQUATION_CREATED],
            handler=self._handle_equation_created,
            consumer_group="realtime-analytics",
        )

        await self.kafka_bus.subscribe(
            aggregate_type="users",
            event_types=[EventType.USER_LOGIN],
            handler=self._handle_user_login,
            consumer_group="realtime-analytics",
        )

    async def _handle_equation_created(self, event: DomainEvent) -> None:
        """Update real-time metrics."""
        self._metrics["equation_creates"] += 1
        print(f"Real-time: {self._metrics['equation_creates']} equations created")

    async def _handle_user_login(self, event: DomainEvent) -> None:
        """Track active users."""
        user_id = event.aggregate_id
        self._metrics["active_users"].add(user_id)
        print(f"Real-time: {len(self._metrics['active_users'])} active users")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics."""
        return {
            "equation_creates": self._metrics["equation_creates"],
            "active_users_count": len(self._metrics["active_users"]),
        }


# Usage example and CLI
if __name__ == "__main__":
    import argparse
    import asyncio
    import uuid

    parser = argparse.ArgumentParser(description="AMOS Kafka Event Streaming")
    parser.add_argument("--produce", action="store_true", help="Produce sample events")
    parser.add_argument("--consume", action="store_true", help="Consume events")
    parser.add_argument("--bootstrap", default="localhost:9092", help="Kafka bootstrap servers")

    args = parser.parse_args()

    async def main():
        bus = KafkaEventBus(bootstrap_servers=args.bootstrap)

        if args.produce:
            await bus.start()

            # Produce sample events
            for i in range(10):
                event = DomainEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=EventType.EQUATION_CREATED,
                    aggregate_id=f"eq-{i}",
                    aggregate_type="equations",
                    timestamp=datetime.now(timezone.utc),
                    version=1,
                    payload={"name": f"Equation {i}", "formula": "x + y"},
                    metadata={"correlation_id": str(uuid.uuid4())},
                )
                await bus.publish(event)
                print(f"Published: {event.event_id}")
                await asyncio.sleep(0.1)

            await bus.stop()

        elif args.consume:
            await bus.start()

            async def handler(event: DomainEvent) -> None:
                print(f"Consumed: {event.event_type} - {event.aggregate_id}")

            consumer = await bus.subscribe(
                aggregate_type="equations",
                event_types=[EventType.EQUATION_CREATED],
                handler=handler,
                consumer_group="demo-consumer",
            )

            print("Consuming events... Press Ctrl+C to stop")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                await bus.stop()

        else:
            parser.print_help()

    asyncio.run(main())
