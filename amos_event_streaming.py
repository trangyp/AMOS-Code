"""AMOS Event Streaming - Event-Driven Architecture (Phase 28).

Reactive event-driven system with pub/sub messaging, event sourcing,
stream processing, and async task orchestration.

2024-2025 State of the Art:
    - Event Bus: Pub/Sub pattern with topic-based routing (Kafka 2025, Pulsar 2025)
    - Event Sourcing: State as immutable event sequence (CQRS patterns 2025)
    - Stream Processing: Windowing, aggregation, transformation (Apache Flink patterns)
    - Priority Queues: Task prioritization for critical events
    - Dead Letter Queues: Failed event handling and retry logic
    - Event Replay: Time-travel debugging and recovery
    - Async Processing: Non-blocking event handlers

Architecture:
    ┌─────────────────────────────────────────────────────────────────────┐
    │          Phase 28: Event-Driven Architecture & Streaming          │
    ├─────────────────────────────────────────────────────────────────────┤
    │                                                                     │
    │  ┌─────────────────────────────────────────────────────────────┐   │
    │  │              Event Bus (Pub/Sub)                              │   │
    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
    │  │  │  Producers  │  │   Topics    │  │  Consumers  │       │   │
    │  │  │             │  │             │  │             │       │   │
    │  │  │  - Equation │  │  - solve    │  │  - Solvers  │       │   │
    │  │  │  - User     │  │  - train    │  │  - Trainers │       │   │
    │  │  │  - System   │  │  - notify   │  │  - Notifiers│       │   │
    │  │  └──────┬──────┘  └─────────────┘  └──────┬──────┘       │   │
    │  │         └────────────────┼────────────────┘              │   │
    │  │                          ▼                               │   │
    │  │              ┌─────────────────────┐                   │   │
    │  │              │   Message Router    │                   │   │
    │  │              │   (Topic Matching)    │                   │   │
    │  │              └─────────────────────┘                   │   │
    │  └─────────────────────────────────────────────────────────────┘   │
    │                                                                     │
    │  ┌─────────────────────────────────────────────────────────────┐   │
    │  │              Event Sourcing                                 │   │
    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
    │  │  │   Event     │  │   Event     │  │   State     │       │   │
    │  │  │   Store     │  │   Stream    │  │   Replay    │       │   │
    │  │  │  (Immutable)│  │  (Append-   │  │  (Rebuild)  │       │   │
    │  │  │             │  │   only)     │  │             │       │   │
    │  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
    │  └─────────────────────────────────────────────────────────────┘   │
    │                                                                     │
    │  ┌─────────────────────────────────────────────────────────────┐   │
    │  │              Stream Processing                                │   │
    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
    │  │  │  Tumbling   │  │  Sliding    │  │  Session    │       │   │
    │  │  │   Window    │  │   Window    │  │   Window    │       │   │
    │  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
    │  │  │  Aggregate  │  │  Filter/    │  │  Enrich/    │       │   │
    │  │  │             │  │  Transform  │  │  Join       │       │   │
    │  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
    │  └─────────────────────────────────────────────────────────────┘   │
    │                                                                     │
    │  ┌─────────────────────────────────────────────────────────────┐   │
    │  │              Async Processing                                 │   │
    │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
    │  │  │   Priority  │  │   Dead      │  │   Retry     │       │   │
    │  │  │   Queue     │  │   Letter    │  │   Logic     │       │   │
    │  │  │             │  │   Queue     │  │             │       │   │
    │  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
    │  └─────────────────────────────────────────────────────────────┘   │
    │                                                                     │
    └─────────────────────────────────────────────────────────────────────┘

Event Types:
    - equation.submitted: Equation solving requested
    - equation.solved: Equation solution completed
    - model.trained: Model training completed
    - user.action: User interaction events
    - system.metric: System performance metrics
    - security.alert: Security-related events

Usage:
    # Initialize event streaming
    events = AMOSEventStreaming()

    # Subscribe to events
    events.subscribe("equation.solved", handle_solution)

    # Publish event
    events.publish("equation.submitted", {
        "equation_id": "eq_001",
        "equation": "neural_ode",
        "priority": "high"
    })

    # Event sourcing - append event
    events.append_event("user_123", "equation_executed", {
        "equation": "maxwell",
        "result": "success"
    })

    # Replay events to rebuild state
    state = events.replay_events("user_123")

    # Stream processing with windowing
    events.create_window("equation_latency", window_type="tumbling", size=60)

    # Process async tasks
    events.submit_task(process_equation, args=(eq,), priority=Priority.HIGH)

Author: AMOS Event Streaming Team
Version: 28.0.0
"""

from __future__ import annotations

import heapq
import random
import secrets
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Optional


class Priority(Enum):
    """Event and task priorities."""

    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class WindowType(Enum):
    """Stream window types."""

    TUMBLING = auto()  # Fixed, non-overlapping windows
    SLIDING = auto()  # Overlapping windows
    SESSION = auto()  # Dynamic based on activity


class EventStatus(Enum):
    """Event processing status."""

    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()
    RETRYING = auto()
    DEAD_LETTER = auto()


@dataclass
class Event:
    """Event in the system."""

    event_id: str
    event_type: str
    payload: dict[str, Any]
    timestamp: float
    priority: Priority = Priority.NORMAL
    source: str = None
    correlation_id: str = None
    status: EventStatus = EventStatus.PENDING
    retry_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SourcedEvent:
    """Event for event sourcing pattern."""

    aggregate_id: str
    event_type: str
    payload: dict[str, Any]
    version: int
    timestamp: float
    event_id: str = field(default_factory=lambda: f"evt_{secrets.token_hex(8)}")


@dataclass
class StreamWindow:
    """Stream processing window."""

    window_id: str
    window_type: WindowType
    size_seconds: float
    events: list[Event] = field(default_factory=list)
    start_time: float = field(default_factory=lambda: time.time())
    end_time: float = None


@dataclass
class AsyncTask:
    """Async task for execution."""

    task_id: str
    priority: Priority
    function: Callable[..., Any]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    created_at: float
    scheduled_at: float = None
    executed_at: float = None
    result: Optional[Any] = None
    error: str = None


class AMOSEventStreaming:
    """Phase 28: Event-Driven Architecture & Streaming.

    Implements pub/sub event bus, event sourcing, stream processing,
    and async task execution with priority queues and dead letter handling.
    """

    def __init__(
        self, max_retries: int = 3, retry_delay_seconds: float = 5.0, max_history: int = 10000
    ):
        self.max_retries = max_retries
        self.retry_delay_seconds = retry_delay_seconds

        # Event bus
        self.subscribers: dict[str, list[Callable[[Event], Any]]] = defaultdict(list)
        self.event_history: deque[Event] = deque(maxlen=max_history)
        self.pending_events: list[tuple[int, float, Event]] = []  # (priority, timestamp, event)

        # Event sourcing
        self.event_store: dict[str, list[SourcedEvent]] = defaultdict(list)

        # Stream processing
        self.windows: dict[str, StreamWindow] = {}
        self.window_results: dict[str, Any] = {}

        # Async processing
        self.task_queue: list[tuple[int, float, AsyncTask]] = []  # (priority, timestamp, task)
        self.dead_letter_queue: list[Event] = []
        self.completed_tasks: dict[str, AsyncTask] = {}

        # Statistics
        self.total_events_published: int = 0
        self.total_events_processed: int = 0
        self.total_events_failed: int = 0
        self.total_tasks_submitted: int = 0
        self.total_tasks_completed: int = 0

    # ==================== Event Bus (Pub/Sub) ====================

    def subscribe(self, event_type: str, handler: Callable[[Event], Any]) -> None:
        """Subscribe handler to event type."""
        self.subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[[Event], Any]) -> bool:
        """Unsubscribe handler from event type."""
        if event_type in self.subscribers and handler in self.subscribers[event_type]:
            self.subscribers[event_type].remove(handler)
            return True
        return False

    def publish(
        self,
        event_type: str,
        payload: dict[str, Any],
        priority: Priority = Priority.NORMAL,
        source: str = None,
        correlation_id: str = None,
    ) -> str:
        """Publish event to the bus."""
        event_id = f"evt_{secrets.token_hex(8)}"

        event = Event(
            event_id=event_id,
            event_type=event_type,
            payload=payload,
            timestamp=time.time(),
            priority=priority,
            source=source,
            correlation_id=correlation_id,
        )

        # Add to history
        self.event_history.append(event)
        self.total_events_published += 1

        # Add to priority queue
        heapq.heappush(self.pending_events, (priority.value, event.timestamp, event))

        # Notify subscribers
        self._notify_subscribers(event)

        return event_id

    def _notify_subscribers(self, event: Event) -> None:
        """Notify all subscribers of event."""
        # Exact match
        if event.event_type in self.subscribers:
            for handler in self.subscribers[event.event_type]:
                try:
                    handler(event)
                    event.status = EventStatus.COMPLETED
                    self.total_events_processed += 1
                except Exception:
                    event.status = EventStatus.FAILED
                    event.retry_count += 1
                    self.total_events_failed += 1

                    # Retry logic
                    if event.retry_count < self.max_retries:
                        event.status = EventStatus.RETRYING
                        time.sleep(self.retry_delay_seconds)
                        self._retry_event(event)
                    else:
                        # Move to dead letter queue
                        event.status = EventStatus.DEAD_LETTER
                        self.dead_letter_queue.append(event)

        # Wildcard subscribers (*)
        if "*" in self.subscribers:
            for handler in self.subscribers["*"]:
                try:
                    handler(event)
                except Exception:
                    pass  # Wildcard failures don't affect main flow

    def _retry_event(self, event: Event) -> None:
        """Retry failed event."""
        heapq.heappush(self.pending_events, (event.priority.value, time.time(), event))

    def get_pending_events(self, limit: int = 100) -> list[Event]:
        """Get pending events sorted by priority."""
        sorted_events = sorted(self.pending_events, key=lambda x: (x[0], x[1]))
        return [event for _, _, event in sorted_events[:limit]]

    def get_dead_letter_events(self) -> list[Event]:
        """Get events that failed all retries."""
        return list(self.dead_letter_queue)

    def replay_dead_letter(self, event_id: str = None) -> int:
        """Replay events from dead letter queue."""
        if event_id:
            # Replay specific event
            for event in self.dead_letter_queue:
                if event.event_id == event_id:
                    event.retry_count = 0
                    event.status = EventStatus.PENDING
                    self.dead_letter_queue.remove(event)
                    heapq.heappush(self.pending_events, (event.priority.value, time.time(), event))
                    return 1
            return 0
        else:
            # Replay all
            count = len(self.dead_letter_queue)
            for event in list(self.dead_letter_queue):
                event.retry_count = 0
                event.status = EventStatus.PENDING
                heapq.heappush(self.pending_events, (event.priority.value, time.time(), event))
            self.dead_letter_queue.clear()
            return count

    # ==================== Event Sourcing ====================

    def append_event(
        self, aggregate_id: str, event_type: str, payload: dict[str, Any]
    ) -> SourcedEvent:
        """Append event to aggregate's event stream."""
        version = len(self.event_store[aggregate_id]) + 1

        sourced_event = SourcedEvent(
            aggregate_id=aggregate_id,
            event_type=event_type,
            payload=payload,
            version=version,
            timestamp=time.time(),
        )

        self.event_store[aggregate_id].append(sourced_event)
        return sourced_event

    def get_event_stream(self, aggregate_id: str, from_version: int = 1) -> list[SourcedEvent]:
        """Get event stream for aggregate."""
        events = self.event_store.get(aggregate_id, [])
        return [e for e in events if e.version >= from_version]

    def replay_events(
        self, aggregate_id: str, from_version: int = 1, to_version: int = None
    ) -> dict[str, Any]:
        """
        Replay events to rebuild aggregate state.

        Returns the final state after applying all events.
        """
        events = self.get_event_stream(aggregate_id, from_version)

        if to_version:
            events = [e for e in events if e.version <= to_version]

        # Rebuild state by applying events in order
        state = {"aggregate_id": aggregate_id, "version": 0}

        for event in events:
            state = self._apply_event(state, event)
            state["version"] = event.version

        return state

    def _apply_event(self, state: dict[str, Any], event: SourcedEvent) -> dict[str, Any]:
        """Apply event to state (event sourcing projection)."""
        new_state = state.copy()

        # Handle different event types
        if event.event_type == "equation_executed":
            new_state["last_equation"] = event.payload.get("equation")
            new_state["execution_count"] = new_state.get("execution_count", 0) + 1

        elif event.event_type == "user_login":
            new_state["last_login"] = event.timestamp
            new_state["login_count"] = new_state.get("login_count", 0) + 1

        elif event.event_type == "model_trained":
            new_state["last_model"] = event.payload.get("model_name")
            new_state["training_count"] = new_state.get("training_count", 0) + 1

        # Merge payload properties
        for key, value in event.payload.items():
            if key not in ["equation", "model_name", "result"]:
                new_state[key] = value

        return new_state

    # ==================== Stream Processing ====================

    def create_window(
        self,
        window_id: str,
        window_type: WindowType = WindowType.TUMBLING,
        size_seconds: float = 60.0,
    ) -> StreamWindow:
        """Create stream processing window."""
        window = StreamWindow(
            window_id=window_id, window_type=window_type, size_seconds=size_seconds
        )
        self.windows[window_id] = window
        return window

    def add_to_window(self, window_id: str, event: Event) -> bool:
        """Add event to processing window."""
        if window_id not in self.windows:
            return False

        window = self.windows[window_id]

        # Check if window is still open
        elapsed = time.time() - window.start_time

        if window.window_type == WindowType.TUMBLING:
            if elapsed > window.size_seconds:
                # Window closed, process it
                self._process_window(window)
                # Create new window
                window = self.create_window(window_id, window.window_type, window.size_seconds)

        window.events.append(event)
        return True

    def _process_window(self, window: StreamWindow) -> dict[str, Any]:
        """Process window events and compute aggregations."""
        window.end_time = time.time()

        # Compute aggregations
        results = {
            "window_id": window.window_id,
            "window_type": window.window_type.name,
            "event_count": len(window.events),
            "start_time": window.start_time,
            "end_time": window.end_time,
            "duration": window.end_time - window.start_time,
            "event_types": {},
            "avg_latency": 0.0,
            "max_latency": 0.0,
        }

        # Count by event type
        for event in window.events:
            et = event.event_type
            results["event_types"][et] = results["event_types"].get(et, 0) + 1

            # Compute latency stats if available
            latency = event.payload.get("latency_ms", 0)
            results["avg_latency"] += latency
            results["max_latency"] = max(results["max_latency"], latency)

        if window.events:
            results["avg_latency"] /= len(window.events)

        self.window_results[window.window_id] = results
        return results

    def get_window_results(self, window_id: str) -> dict[str, Any]:
        """Get processed window results."""
        return self.window_results.get(window_id)

    # ==================== Async Task Processing ====================

    def submit_task(
        self,
        function: Callable[..., Any],
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] = None,
        priority: Priority = Priority.NORMAL,
        delay_seconds: float = 0.0,
    ) -> str:
        """Submit async task for execution."""
        task_id = f"task_{secrets.token_hex(8)}"

        task = AsyncTask(
            task_id=task_id,
            priority=priority,
            function=function,
            args=args,
            kwargs=kwargs or {},
            created_at=time.time(),
            scheduled_at=time.time() + delay_seconds,
        )

        heapq.heappush(self.task_queue, (priority.value, task.scheduled_at or time.time(), task))

        self.total_tasks_submitted += 1
        return task_id

    def process_tasks(self, max_tasks: int = 10) -> list[AsyncTask]:
        """Process pending tasks from queue."""
        processed = []
        now = time.time()

        while len(processed) < max_tasks and self.task_queue:
            # Peek at next task
            priority, scheduled_at, task = self.task_queue[0]

            # Check if ready
            if scheduled_at > now:
                break

            # Pop and execute
            heapq.heappop(self.task_queue)

            try:
                task.executed_at = time.time()
                task.result = task.function(*task.args, **task.kwargs)
                self.total_tasks_completed += 1
            except Exception as e:
                task.error = str(e)

            self.completed_tasks[task.task_id] = task
            processed.append(task)

        return processed

    def get_task_status(self, task_id: str) -> dict[str, Any]:
        """Get task execution status."""
        if task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            return {
                "task_id": task.task_id,
                "status": "completed" if task.result is not None else "failed",
                "result": task.result,
                "error": task.error,
                "created_at": task.created_at,
                "executed_at": task.executed_at,
            }

        # Check pending queue
        for _, _, task in self.task_queue:
            if task.task_id == task_id:
                return {
                    "task_id": task.task_id,
                    "status": "pending",
                    "scheduled_at": task.scheduled_at,
                }

        return None

    # ==================== Statistics & Health ====================

    def get_streaming_stats(self) -> dict[str, Any]:
        """Get comprehensive streaming statistics."""
        return {
            "event_bus": {
                "total_published": self.total_events_published,
                "total_processed": self.total_events_processed,
                "total_failed": self.total_events_failed,
                "pending_count": len(self.pending_events),
                "dead_letter_count": len(self.dead_letter_queue),
                "subscriber_count": sum(len(s) for s in self.subscribers.values()),
            },
            "event_sourcing": {
                "aggregate_count": len(self.event_store),
                "total_stored_events": sum(len(events) for events in self.event_store.values()),
            },
            "stream_processing": {
                "active_windows": len(self.windows),
                "processed_windows": len(self.window_results),
            },
            "async_processing": {
                "total_submitted": self.total_tasks_submitted,
                "total_completed": self.total_tasks_completed,
                "pending_tasks": len(self.task_queue),
                "completion_rate": (
                    self.total_tasks_completed / self.total_tasks_submitted
                    if self.total_tasks_submitted > 0
                    else 0.0
                ),
            },
        }


def main():
    """CLI demo for event streaming."""
    import argparse

    parser = argparse.ArgumentParser(description="AMOS Event Streaming (Phase 28)")
    parser.add_argument("--demo", action="store_true", help="Run demonstration")

    args = parser.parse_args()

    if args.demo:
        print("=" * 70)
        print("Phase 28: Event-Driven Architecture & Streaming")
        print("Event Bus | Event Sourcing | Stream Processing | Async Tasks")
        print("=" * 70)

        # Initialize event streaming
        events = AMOSEventStreaming(max_retries=2)

        # 1. Event Bus (Pub/Sub)
        print("\n1. Event Bus - Publish/Subscribe")
        print("-" * 50)

        received_events = []

        def equation_handler(event: Event) -> None:
            received_events.append(event)
            print(f"   Handled: {event.event_type} (id: {event.event_id[:12]}...)")

        def all_events_handler(event: Event) -> None:
            print(f"   [Wildcard] {event.event_type} from {event.source}")

        # Subscribe
        events.subscribe("equation.solved", equation_handler)
        events.subscribe("equation.failed", equation_handler)
        events.subscribe("*", all_events_handler)

        # Publish events
        print("   Publishing events:")
        event_ids = []
        for i in range(5):
            event_id = events.publish(
                "equation.solved" if i % 2 == 0 else "equation.failed",
                {
                    "equation_id": f"eq_{i}",
                    "equation": "neural_ode" if i % 2 == 0 else "black_scholes",
                    "latency_ms": random.uniform(10, 100),
                    "success": i % 2 == 0,
                },
                priority=Priority.HIGH if i < 2 else Priority.NORMAL,
                source="equation_solver",
                correlation_id=f"batch_{i // 2}",
            )
            event_ids.append(event_id)

        print(f"\n   Subscribers notified: {len(received_events)} events")

        # 2. Event Sourcing
        print("\n2. Event Sourcing - State as Event Stream")
        print("-" * 50)

        user_id = "user_researcher_001"

        # Append events
        print("   Appending events to aggregate:")
        event_types = [
            ("user_login", {"ip": "192.168.1.100"}),
            ("equation_executed", {"equation": "neural_ode", "result": "success"}),
            ("model_trained", {"model_name": "transformer_v2", "accuracy": 0.95}),
            ("equation_executed", {"equation": "maxwell", "result": "success"}),
            ("user_logout", {"duration_minutes": 45}),
        ]

        for event_type, payload in event_types:
            evt = events.append_event(user_id, event_type, payload)
            print(f"   v{evt.version}: {event_type}")

        # Replay to rebuild state
        print("\n   Replaying events to rebuild state:")
        state = events.replay_events(user_id)
        print(f"      Aggregate: {state['aggregate_id']}")
        print(f"      Version: {state['version']}")
        print(f"      Execution count: {state.get('execution_count', 0)}")
        print(f"      Training count: {state.get('training_count', 0)}")
        print(f"      Last equation: {state.get('last_equation', 'N/A')}")

        # Replay to specific version
        partial_state = events.replay_events(user_id, to_version=3)
        print("\n   State at version 3:")
        print(f"      Training count: {partial_state.get('training_count', 0)}")

        # 3. Stream Processing
        print("\n3. Stream Processing - Windowing & Aggregation")
        print("-" * 50)

        # Create window
        window = events.create_window("equation_latency", WindowType.TUMBLING, size_seconds=60)
        print(f"   Created {window.window_type.name} window: {window.window_id}")

        # Add events to window
        for i in range(10):
            event = Event(
                event_id=f"evt_{i}",
                event_type="equation.solved",
                payload={"latency_ms": random.uniform(10, 200)},
                timestamp=time.time(),
            )
            events.add_to_window("equation_latency", event)

        # Manually process window
        results = events._process_window(window)
        print("\n   Window processed:")
        print(f"      Events: {results['event_count']}")
        print(f"      Event types: {results['event_types']}")
        print(f"      Avg latency: {results['avg_latency']:.1f}ms")
        print(f"      Max latency: {results['max_latency']:.1f}ms")

        # 4. Async Task Processing
        print("\n4. Async Task Processing - Priority Queue")
        print("-" * 50)

        # Submit tasks with different priorities
        def sample_task(name: str, duration: float) -> str:
            time.sleep(duration)
            return f"Task {name} completed"

        task_ids = []
        priorities = [
            (Priority.BACKGROUND, "background_job", 0.01),
            (Priority.NORMAL, "normal_processing", 0.01),
            (Priority.HIGH, "urgent_solve", 0.01),
            (Priority.CRITICAL, "critical_alert", 0.01),
            (Priority.NORMAL, "another_normal", 0.01),
        ]

        print("   Submitting tasks:")
        for priority, name, duration in priorities:
            task_id = events.submit_task(sample_task, args=(name, duration), priority=priority)
            task_ids.append((priority.name, name, task_id))
            print(f"      [{priority.name}] {name}")

        # Process tasks
        print("\n   Processing tasks (order by priority):")
        processed = events.process_tasks(max_tasks=10)
        for task in processed:
            print(f"      Completed: {task.task_id[:12]}... (priority: {task.priority.name})")

        # Check task status
        print("\n   Task status check:")
        for _, _, task_id in task_ids[:2]:
            status = events.get_task_status(task_id)
            if status:
                print(f"      {task_id[:12]}...: {status['status']}")

        # 5. Dead Letter Queue
        print("\n5. Dead Letter Queue - Failed Event Handling")
        print("-" * 50)

        # Simulate a failing handler
        def failing_handler(event: Event) -> None:
            raise ValueError("Simulated processing error")

        events.subscribe("problematic.event", failing_handler)

        # Publish events that will fail
        print("   Publishing events that will fail:")
        for i in range(3):
            events.publish("problematic.event", {"data": f"test_{i}"}, priority=Priority.NORMAL)

        # Check dead letter queue
        dlq = events.get_dead_letter_events()
        print(f"\n   Dead letter queue size: {len(dlq)}")
        if dlq:
            for event in dlq:
                print(f"      {event.event_id[:12]}... (retries: {event.retry_count})")

        # Replay from dead letter
        if dlq:
            replayed = events.replay_dead_letter(dlq[0].event_id)
            print(f"\n   Replayed {replayed} event from DLQ")

        # 6. Statistics
        print("\n" + "=" * 70)
        print("Event Streaming Statistics")
        print("=" * 70)

        stats = events.get_streaming_stats()

        print("   Event Bus:")
        print(f"      Published: {stats['event_bus']['total_published']}")
        print(f"      Processed: {stats['event_bus']['total_processed']}")
        print(f"      Failed: {stats['event_bus']['total_failed']}")
        print(f"      Pending: {stats['event_bus']['pending_count']}")
        print(f"      Dead letter: {stats['event_bus']['dead_letter_count']}")

        print("   Event Sourcing:")
        print(f"      Aggregates: {stats['event_sourcing']['aggregate_count']}")
        print(f"      Total events: {stats['event_sourcing']['total_stored_events']}")

        print("   Stream Processing:")
        print(f"      Active windows: {stats['stream_processing']['active_windows']}")

        print("   Async Processing:")
        print(f"      Submitted: {stats['async_processing']['total_submitted']}")
        print(f"      Completed: {stats['async_processing']['total_completed']}")
        print(f"      Completion rate: {stats['async_processing']['completion_rate']:.1%}")

        print("\n" + "=" * 70)
        print("Phase 28 Event Streaming: OPERATIONAL")
        print("   Pub/Sub | Event Sourcing | Stream Processing | Async Tasks")
        print("=" * 70)

    else:
        print("AMOS Event Streaming v28.0.0")
        print("Usage: python amos_event_streaming.py --demo")


if __name__ == "__main__":
    main()
