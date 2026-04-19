#!/usr/bin/env python3
"""
AMOS Enhanced Event-Driven Architecture (2025 SOTA)
=====================================================

Implements state-of-the-art event patterns:
- Event-Carried State Transfer (full state in events)
- Event Sourcing (complete event log for replay)
- CQRS (Command Query Responsibility Segregation)
- Publish/Subscribe (decoupled messaging)
- Choreography (services react to events)

Based on: Gravitee.io "Best Architectural Patterns for Event-Driven Systems"
Owner: Trang
Version: 2.0.0
"""


import json
import time
import uuid
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict
from enum import Enum
import asyncio
from pathlib import Path


class EventPattern(Enum):
    """Event-driven architecture patterns."""
    EVENT_NOTIFICATION = "notification"  # Lightweight signal
    EVENT_CARRIED_STATE = "state_transfer"  # Full state in event
    EVENT_SOURCING = "sourcing"  # Store all events
    CQRS = "cqrs"  # Separate read/write


@dataclass
class DomainEvent:
    """
    Rich domain event with Event-Carried State Transfer pattern.

    Carries complete state needed by consumers - no external lookups required.
    Improves resilience and reduces latency.
    """
    event_id: str
    event_type: str
    aggregate_id: str  # Entity this event relates to
    aggregate_type: str  # Type of entity (engine, subsystem, task)
    timestamp: float
    version: int  # Event version for schema evolution

    # Event-Carried State Transfer: Full state included
    payload: Dict[str, Any]  # Complete state needed by consumers
    metadata: Dict[str, Any] = field(default_factory=dict)  # Context

    # Source tracking
    source_service: str = ""  # Which service emitted
    source_version: str = "1.0"

    # Tracing (integrates with observability system)
    trace_id: str  = None
    correlation_id: str  = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), default=str)


@dataclass
class Command:
    """
    Command for CQRS pattern.

    Commands represent intentions to change state.
    Separated from queries (reads).
    """
    command_id: str
    command_type: str
    aggregate_id: str
    aggregate_type: str
    payload: Dict[str, Any]
    timestamp: float

    # Execution metadata
    requested_by: str = "system"
    expected_version: int  = None  # Optimistic concurrency

    def to_event(self, event_type: str, payload: Dict[str, Any]) -> DomainEvent:
        """Convert command to event (after execution)."""
        return DomainEvent(
            event_id=str(uuid.uuid4())[:16],
            event_type=event_type,
            aggregate_id=self.aggregate_id,
            aggregate_type=self.aggregate_type,
            timestamp=time.time(),
            version=1,
            payload=payload,
            metadata={"command_id": self.command_id},
            correlation_id=self.command_id
        )


@dataclass
class EventStoreEntry:
    """Entry in event store for Event Sourcing pattern."""
    sequence_number: int
    event: DomainEvent
    stored_at: float
    stream_id: str  # Event stream (aggregate_id)


class EventStore:
    """
    Event Store for Event Sourcing pattern.

    Stores complete history of events for:
    - Audit trails
    - Time-travel debugging
    - State reconstruction
    - Event replay
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("/tmp/amos_event_store")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # In-memory storage (with persistence option)
        self.streams: Dict[str, list[EventStoreEntry]] = defaultdict(list)
        self.global_sequence = 0
        self._lock = asyncio.Lock()

    async def append(self, event: DomainEvent) -> EventStoreEntry:
        """Append event to store."""
        async with self._lock:
            self.global_sequence += 1

            entry = EventStoreEntry(
                sequence_number=self.global_sequence,
                event=event,
                stored_at=time.time(),
                stream_id=event.aggregate_id
            )

            # Add to stream
            self.streams[event.aggregate_id].append(entry)

            # Persist to disk (optional)
            await self._persist(entry)

            return entry

    async def _persist(self, entry: EventStoreEntry) -> None:
        """Persist entry to disk."""
        stream_file = self.storage_path / f"{entry.stream_id}.jsonl"
        with open(stream_file, "a") as f:
            f.write(json.dumps({
                "seq": entry.sequence_number,
                "event": entry.event.to_dict(),
                "stored_at": entry.stored_at
            }) + "\n")

    def get_stream(self, aggregate_id: str,
                   from_version: int = 0) -> List[DomainEvent]:
        """Get all events for an aggregate."""
        entries = self.streams.get(aggregate_id, [])
        return [
            e.event for e in entries
            if e.event.version >= from_version
        ]

    def get_all_events(self,
                       event_types: List[str ] = None,
                       since: float  = None) -> List[DomainEvent]:
        """Get all events (for replay/analysis)."""
        events = []
        for stream in self.streams.values():
            for entry in stream:
                event = entry.event
                if event_types and event.event_type not in event_types:
                    continue
                if since and event.timestamp < since:
                    continue
                events.append(event)
        return sorted(events, key=lambda e: e.timestamp)

    def replay_stream(self, aggregate_id: str,
                      projector: Callable[[Any, DomainEvent], Any],
                      initial_state: Any = None) -> Any:
        """
        Replay events to reconstruct state.

        Event Sourcing pattern: State is derived from event history.
        """
        state = initial_state
        for entry in self.streams.get(aggregate_id, []):
            state = projector(state, entry.event)
        return state


class CQRSView:
    """
    Read model for CQRS pattern.

    Optimized for queries, separate from write model.
    Updated asynchronously via events.
    """

    def __init__(self, view_name: str):
        self.view_name = view_name
        self.data: Dict[str, Any] = {}
        self.indexes: Dict[str, dict[Any, set[str]]] = defaultdict(lambda: defaultdict(set))
        self.last_update = 0.0

    def update(self, event: DomainEvent) -> None:
        """Update view based on event."""
        self.data[event.aggregate_id] = {
            "state": event.payload,
            "version": event.version,
            "last_event": event.event_type,
            "updated_at": event.timestamp
        }
        self.last_update = time.time()

        # Update indexes
        for key, value in event.payload.items():
            if isinstance(value, (str, int, float, bool)):
                self.indexes[key][value].add(event.aggregate_id)

    def query_by_id(self, aggregate_id: str) -> Dict[str, Any ]:
        """Query by aggregate ID."""
        return self.data.get(aggregate_id)

    def query_by_field(self, field: str, value: Any) -> List[dict[str, Any]]:
        """Query by indexed field."""
        ids = self.indexes[field].get(value, set())
        return [self.data[id] for id in ids if id in self.data]

    def get_all(self) -> List[dict[str, Any]]:
        """Get all entries."""
        return list(self.data.values())


class EnhancedEventBus:
    """
    Enhanced Event Bus with 2025 best practices.

    Combines:
    - Publish/Subscribe (decoupled messaging)
    - Event Sourcing (complete history)
    - CQRS (separate read models)
    - Event-Carried State Transfer (resilience)
    """

    def __init__(self):
        # Publish/Subscribe
        self.subscribers: Dict[str, list[Callable[[DomainEvent], Any]]] = defaultdict(list)
        self.subscriber_names: Dict[str, str] = {}  # id -> name

        # Event Sourcing
        self.event_store = EventStore()

        # CQRS Read Models
        self.views: Dict[str, CQRSView] = {}

        # Statistics
        self.events_published = 0
        self.events_by_type: Dict[str, int] = defaultdict(int)

        # Async processing
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._running = False

    def register_view(self, view_name: str) -> CQRSView:
        """Register a CQRS read model."""
        view = CQRSView(view_name)
        self.views[view_name] = view

        # Subscribe to all events for this view
        self.subscribe(f"view.{view_name}", ["*"], lambda e: view.update(e))

        return view

    def subscribe(self, subscriber_id: str,
                  event_types: List[str],
                  handler: Callable[[DomainEvent], Any]) -> None:
        """Subscribe to event types."""
        for event_type in event_types:
            self.subscribers[event_type].append(handler)
        self.subscriber_names[subscriber_id] = subscriber_id

    async def publish(self, event: DomainEvent) -> int:
        """
        Publish event to all subscribers.

        Also:
        - Store in event store (Event Sourcing)
        - Update CQRS views
        - Track statistics
        """
        # Store event (Event Sourcing)
        await self.event_store.append(event)

        # Update statistics
        self.events_published += 1
        self.events_by_type[event.event_type] += 1

        # Notify subscribers (Publish/Subscribe)
        notified = 0
        handlers = self.subscribers.get(event.event_type, []) + self.subscribers.get("*", [])

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
                notified += 1
            except Exception as e:
                print(f"Handler error: {e}")

        return notified

    def publish_sync(self, event_type: str, aggregate_id: str,
                     aggregate_type: str, payload: Dict[str, Any],
                     source: str = "system") -> DomainEvent:
        """Synchronous publish helper."""
        event = DomainEvent(
            event_id=str(uuid.uuid4())[:16],
            event_type=event_type,
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            timestamp=time.time(),
            version=1,
            payload=payload,
            source_service=source
        )

        # Run async publish in sync context using modern pattern
        try:
            # Check if we're in an async context
            asyncio.get_running_loop()
            # If we get here, we're in an async context - use create_task
            # This requires the caller to handle the task
            import warnings
            warnings.warn(
                "publish_sync called from async context. Use publish() directly.",
                DeprecationWarning,
                stacklevel=2
            )
        except RuntimeError:
            # No running loop - safe to use asyncio.run()
            pass

        # Use asyncio.run for clean, modern execution
        asyncio.run(self.publish(event))

        return event

    def execute_command(self, command: Command) -> Optional[DomainEvent]:
        """
        Execute command (CQRS write side).

        Command -> Business Logic -> Event -> Store -> Update Views
        """
        # Create event from command
        event = command.to_event(
            event_type=f"{command.aggregate_type}.{command.command_type}",
            payload=command.payload
        )

        # Publish (triggers storage and view updates)
        self.publish_sync(
            event.event_type,
            event.aggregate_id,
            event.aggregate_type,
            event.payload,
            "command_handler"
        )

        return event

    def get_view(self, view_name: str) -> Optional[CQRSView]:
        """Get CQRS read model."""
        return self.views.get(view_name)

    def query_aggregate(self, aggregate_id: str) -> List[DomainEvent]:
        """Query all events for aggregate (CQRS/Event Sourcing)."""
        return self.event_store.get_stream(aggregate_id)

    def replay_aggregate(self, aggregate_id: str,
                        projector: Callable[[Any, DomainEvent], Any],
                        initial_state: Any = None) -> Any:
        """Replay events to reconstruct aggregate state."""
        return self.event_store.replay_stream(aggregate_id, projector, initial_state)

    def get_stats(self) -> Dict[str, Any]:
        """Get bus statistics."""
        return {
            "events_published": self.events_published,
            "event_types": dict(self.events_by_type),
            "subscribers": len(self.subscriber_names),
            "views": list(self.views.keys()),
            "streams": len(self.event_store.streams)
        }


# AMOS-specific event factories
def create_engine_event(engine_type: str, operation: str,
                        result: Any, duration_ms: float) -> DomainEvent:
    """Create event for engine execution."""
    return DomainEvent(
        event_id=str(uuid.uuid4())[:16],
        event_type=f"engine.{engine_type}.{operation}",
        aggregate_id=f"engine:{engine_type}",
        aggregate_type="engine",
        timestamp=time.time(),
        version=1,
        payload={
            "engine_type": engine_type,
            "operation": operation,
            "result_summary": str(result)[:200],
            "duration_ms": duration_ms,
            "success": True
        },
        source_service=engine_type
    )


def create_subsystem_event(subsystem: str, state_change: str,
                           details: Dict[str, Any]) -> DomainEvent:
    """Create event for organism subsystem state change."""
    return DomainEvent(
        event_id=str(uuid.uuid4())[:16],
        event_type=f"subsystem.{subsystem}.{state_change}",
        aggregate_id=f"subsystem:{subsystem}",
        aggregate_type="subsystem",
        timestamp=time.time(),
        version=1,
        payload={
            "subsystem": subsystem,
            "state_change": state_change,
            "details": details
        },
        source_service="organism"
    )


def create_task_event(task_id: str, status: str,
                      metadata: Dict[str, Any]) -> DomainEvent:
    """Create event for task lifecycle."""
    return DomainEvent(
        event_id=str(uuid.uuid4())[:16],
        event_type=f"task.{status}",
        aggregate_id=task_id,
        aggregate_type="task",
        timestamp=time.time(),
        version=1,
        payload={
            "task_id": task_id,
            "status": status,
            **metadata
        },
        source_service="task_scheduler"
    )


# Global enhanced bus instance
_enhanced_bus: Optional[EnhancedEventBus] = None


def get_enhanced_event_bus() -> EnhancedEventBus:
    """Get global enhanced event bus."""
    global _enhanced_bus
    if _enhanced_bus is None:
        _enhanced_bus = EnhancedEventBus()
    return _enhanced_bus


def demo_enhanced_architecture():
    """Demonstrate enhanced event-driven architecture."""
    print("=" * 70)
    print("🚀 AMOS ENHANCED EVENT-DRIVEN ARCHITECTURE")
    print("   (2025 SOTA Patterns)")
    print("=" * 70)

    bus = EnhancedEventBus()

    # 1. CQRS Views
    print("\n[1] Setting up CQRS Read Models...")
    engine_view = bus.register_view("engines")
    task_view = bus.register_view("tasks")
    print("   ✓ Engine view registered")
    print("   ✓ Task view registered")

    # 2. Event Handlers (Choreography pattern)
    print("\n[2] Setting up Event Handlers...")

    def notify_on_completion(event: DomainEvent):
        if event.event_type == "task.completed":
            print(f"   [Notification] Task {event.aggregate_id} completed!")

    def audit_logger(event: DomainEvent):
        print(f"   [Audit] {event.event_type} at {event.timestamp:.2f}")

    bus.subscribe("notifier", ["task.completed"], notify_on_completion)
    bus.subscribe("auditor", ["*"], audit_logger)
    print("   ✓ Notifier subscribed to task.completed")
    print("   ✓ Auditor subscribed to all events")

    # 3. Event-Carried State Transfer
    print("\n[3] Publishing Events (Event-Carried State Transfer)...")

    # Engine event with full state
    engine_event = bus.publish_sync(
        "engine.economics.analyze",
        "engine:economics",
        "engine",
        {
            "engine": "economics",
            "query": "market_analysis",
            "result": {"findings": 5, "confidence": 0.85},
            "duration_ms": 125.5,
            "resources_used": {"cpu": 15, "memory": 32}
        },
        "economics_engine"
    )
    print(f"   ✓ Engine event published: {engine_event.event_id}")

    # Task events with full state
    task_id = f"task:{uuid.uuid4().hex[:8]}"
    bus.publish_sync("task.created", task_id, "task",
                    {"status": "created", "priority": 5}, "scheduler")
    bus.publish_sync("task.started", task_id, "task",
                    {"status": "running", "worker": "worker-1"}, "scheduler")
    bus.publish_sync("task.completed", task_id, "task",
                    {"status": "completed", "result": "success"}, "scheduler")

    # 4. Event Store (Event Sourcing)
    print("\n[4] Event Store (Event Sourcing Pattern)...")
    stream = bus.query_aggregate("engine:economics")
    print(f"   ✓ Events in stream: {len(stream)}")

    # 5. CQRS Query
    print("\n[5] CQRS Read Model Query...")
    engine_data = engine_view.query_by_id("engine:economics")
    if engine_data:
        print(f"   ✓ Engine state: {engine_data['state']['engine']}")
        print(f"   ✓ Last event: {engine_data['last_event']}")

    tasks = task_view.get_all()
    print(f"   ✓ Tasks in view: {len(tasks)}")

    # 6. Statistics
    print("\n[6] Architecture Statistics...")
    stats = bus.get_stats()
    for key, value in stats.items():
        print(f"   • {key}: {value}")

    print("\n" + "=" * 70)
    print("✅ Enhanced Event-Driven Architecture Active")
    print("=" * 70)
    print("\n📊 Patterns Implemented:")
    print("   ✓ Event-Carried State Transfer (full state in events)")
    print("   ✓ Event Sourcing (complete history stored)")
    print("   ✓ CQRS (separate read/write models)")
    print("   ✓ Publish/Subscribe (decoupled messaging)")
    print("   ✓ Choreography (services react to events)")
    print("\n🎯 Benefits:")
    print("   • 22 engines can communicate asynchronously")
    print("   • Complete audit trail for all operations")
    print("   • Read-optimized views for queries")
    print("   • No service coupling (decoupled)")
    print("   • Time-travel debugging enabled")
    print("=" * 70)


if __name__ == "__main__":
    demo_enhanced_architecture()
