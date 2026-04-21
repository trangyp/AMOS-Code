"""
Event-Driven Transition System (EDTS)

Replaces polling-style loops with event-driven transitions.

Instead of:
    while True:
        what_changed?
        recompute

We do:
    event -> state_delta -> invariant_gate -> transition

This is the lawful efficient form.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol

from amos_kernel.compiled_numeric_kernel import (
    CompiledConstraints,
    CompiledState,
    NumericInputs,
    TransitionResult,
    get_compiled_numeric_kernel,
)

# ============================================================================
# Event Protocols and Types
# ============================================================================


class EventHandler(Protocol):
    """Protocol for event handlers."""

    async def __call__(self, event: StateEvent) -> TransitionResult | None: ...


@dataclass(frozen=True)
class StateEvent:
    """
    Canonical state event.

    Events are immutable and carry their own hash for deduplication.
    """

    event_id: str
    event_type: str  # "signal", "control", "query", "command", "time"
    source: str
    timestamp: float

    # Event payload as compact dict
    payload: dict[str, Any] = field(default_factory=dict)

    # Canonical hash for dedup
    event_hash: str = field(default="")

    def __post_init__(self) -> None:
        if not self.event_hash:
            # Compute hash from content
            content = f"{self.event_type}:{self.source}:{json.dumps(self.payload, sort_keys=True, default=str)}"
            object.__setattr__(
                self, "event_hash", hashlib.sha256(content.encode()).hexdigest()[:16]
            )


@dataclass
class StateDelta:
    """
    Computed state change from event.

    Delta is pre-computed so transition kernel doesn't reinterpret.
    """

    delta_id: str
    source_event: StateEvent

    # Numeric changes (vectorized)
    mu_delta: list[float] = field(default_factory=list)
    nu_delta: list[float] = field(default_factory=list)
    alpha_delta: list[float] = field(default_factory=list)
    beta_delta: list[float] = field(default_factory=list)

    # Computed inputs for numeric kernel
    numeric_inputs: NumericInputs | None = None

    # Constraints (pre-checked)
    constraints: CompiledConstraints | None = None


@dataclass
class EventDrivenTransition:
    """Record of event-driven transition."""

    transition_id: str
    event: StateEvent
    delta: StateDelta
    result: TransitionResult
    timestamp: float


# ============================================================================
# Event Router
# ============================================================================


class EventRouter:
    """
    Routes events to appropriate handlers.

    No dynamic lookup - pre-registered handlers only.
    """

    def __init__(self) -> None:
        # Pre-registered handlers by event type
        self._handlers: dict[str, list[EventHandler]] = {
            "signal": [],
            "control": [],
            "query": [],
            "command": [],
            "time": [],
        }

        # Event deduplication (event_hash -> timestamp)
        self._recent_events: dict[str, float] = {}
        self._dedup_window = 1.0  # 1 second dedup window

    def register_handler(self, event_type: str, handler: EventHandler) -> None:
        """Register handler for event type."""
        if event_type in self._handlers:
            self._handlers[event_type].append(handler)

    async def route_event(self, event: StateEvent) -> list[TransitionResult]:
        """
        Route event to all registered handlers.

        Filters duplicates before routing.
        """
        # Deduplication check
        now = datetime.now(UTC).timestamp()
        if event.event_hash in self._recent_events:
            last_seen = self._recent_events[event.event_hash]
            if now - last_seen < self._dedup_window:
                return []  # Duplicate, drop

        self._recent_events[event.event_hash] = now

        # Route to handlers
        results: list[TransitionResult] = []
        handlers = self._handlers.get(event.event_type, [])

        for handler in handlers:
            try:
                result = await handler(event)
                if result:
                    results.append(result)
            except Exception:
                # Handler failed, continue with others
                pass

        return results

    def cleanup_dedup_cache(self) -> None:
        """Remove old dedup entries."""
        now = datetime.now(UTC).timestamp()
        cutoff = now - self._dedup_window
        self._recent_events = {k: v for k, v in self._recent_events.items() if v > cutoff}


# ============================================================================
# State Delta Computer
# ============================================================================


class StateDeltaComputer:
    """
    Computes state deltas from events.

    This is where semantic interpretation happens (if needed).
    Once delta is computed, numeric kernel takes over.
    """

    def __init__(self) -> None:
        # Pre-compiled delta functions
        self._delta_computers: dict[str, Callable[[StateEvent], StateDelta]] = {
            "signal": self._compute_signal_delta,
            "control": self._compute_control_delta,
            "query": self._compute_query_delta,
            "command": self._compute_command_delta,
            "time": self._compute_time_delta,
        }

    def compute_delta(self, event: StateEvent) -> StateDelta:
        """
        Compute state delta from event.

        This is the ONE place where interpretation happens.
        After this, it's all numeric.
        """
        computer = self._delta_computers.get(event.event_type, self._compute_default_delta)
        return computer(event)

    def _compute_signal_delta(self, event: StateEvent) -> StateDelta:
        """Compute delta for signal event."""
        payload = event.payload

        # Extract numeric values
        load = payload.get("load", 0.0)
        confidence = payload.get("confidence", 0.5)

        # Build numeric inputs
        inputs = NumericInputs.from_dict(
            {
                "load": load,
                "confidence": confidence,
                "type": "signal",
            }
        )

        # Build constraints
        constraints = CompiledConstraints.from_dict(
            {
                "mode_valid": True,
                "schema_valid": payload.get("schema_valid", False),
                "provenance_ok": payload.get("trusted", False),
                "complete": True,
                "permission_ok": True,
                "min": [0.0, 0.0, 0.0, 0.0],
                "max": [1.0, 1.0, 1.0, 1.0],
            }
        )

        return StateDelta(
            delta_id=event.event_hash,
            source_event=event,
            mu_delta=[load],
            nu_delta=[confidence],
            numeric_inputs=inputs,
            constraints=constraints,
        )

    def _compute_control_delta(self, event: StateEvent) -> StateDelta:
        """Compute delta for control event."""
        payload = event.payload

        urgency = payload.get("urgency", 0.5)
        priority = payload.get("priority", 0.5)

        inputs = NumericInputs.from_dict(
            {
                "urgency": urgency,
                "priority": priority,
                "type": "control",
            }
        )

        constraints = CompiledConstraints.from_dict(
            {
                "mode_valid": True,
                "schema_valid": True,
                "provenance_ok": payload.get("authorized", False),
                "complete": True,
                "permission_ok": payload.get("permission_ok", False),
            }
        )

        return StateDelta(
            delta_id=event.event_hash,
            source_event=event,
            alpha_delta=[urgency],
            beta_delta=[priority],
            numeric_inputs=inputs,
            constraints=constraints,
        )

    def _compute_query_delta(self, event: StateEvent) -> StateDelta:
        """Compute delta for query event."""
        # Queries don't change state, just read
        return StateDelta(
            delta_id=event.event_hash,
            source_event=event,
            numeric_inputs=NumericInputs.from_dict({"type": "query"}),
            constraints=CompiledConstraints.from_dict({"complete": True}),
        )

    def _compute_command_delta(self, event: StateEvent) -> StateDelta:
        """Compute delta for command event."""
        payload = event.payload

        inputs = NumericInputs.from_dict(
            {
                "signal": payload.get("intensity", 0.5),
                "type": "command",
            }
        )

        constraints = CompiledConstraints.from_dict(
            {
                "mode_valid": True,
                "schema_valid": True,
                "provenance_ok": payload.get("authenticated", False),
                "complete": payload.get("valid", False),
                "permission_ok": payload.get("authorized", False),
            }
        )

        return StateDelta(
            delta_id=event.event_hash,
            source_event=event,
            numeric_inputs=inputs,
            constraints=constraints,
        )

    def _compute_time_delta(self, event: StateEvent) -> StateDelta:
        """Compute delta for time event."""
        # Time events trigger decay
        return StateDelta(
            delta_id=event.event_hash,
            source_event=event,
            mu_delta=[-0.01],  # Slight decay
            nu_delta=[-0.01],
            numeric_inputs=NumericInputs.from_dict({"type": "time"}),
            constraints=CompiledConstraints.from_dict({"complete": True}),
        )

    def _compute_default_delta(self, event: StateEvent) -> StateDelta:
        """Default delta computation."""
        return StateDelta(
            delta_id=event.event_hash,
            source_event=event,
            numeric_inputs=NumericInputs.from_dict({"type": event.event_type}),
            constraints=CompiledConstraints.from_dict({"complete": True}),
        )


# ============================================================================
# Event-Driven Transition Engine
# ============================================================================


class EventDrivenTransitionEngine:
    """
    Event-driven state transition engine.

    Replaces polling with event-driven transitions:
        event -> delta -> invariant_gate -> transition -> commit

    No semantic work in the hot path.
    """

    _instance: EventDrivenTransitionEngine | None = None

    def __new__(cls) -> EventDrivenTransitionEngine:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        # Numeric kernel (fast path)
        self._numeric_kernel = get_compiled_numeric_kernel()

        # Event router
        self._router = EventRouter()

        # Delta computer
        self._delta_computer = StateDeltaComputer()

        # Current state
        self._current_state: CompiledState | None = None

        # Event queue
        self._event_queue: asyncio.Queue[StateEvent] = asyncio.Queue()

        # Transition history (circular buffer)
        self._history: deque[EventDrivenTransition] = deque(maxlen=1000)

        # Running flag
        self._running = False

        # Stats
        self._stats = {
            "events_processed": 0,
            "transitions": 0,
            "invariant_rejections": 0,
            "avg_latency_ms": 0.0,
        }

        self._initialized = True

    # ========================================================================
    # Public API
    # ========================================================================

    def initialize(self, initial_state: CompiledState) -> None:
        """Initialize with starting state."""
        self._current_state = initial_state

    async def emit_event(self, event: StateEvent) -> TransitionResult | None:
        """
        Emit event for processing.

        This is the entry point: events go in, transitions come out.
        """
        await self._event_queue.put(event)
        self._stats["events_processed"] += 1

        # Process immediately (async)
        return await self._process_single_event(event)

    async def emit(
        self, event_type: str, source: str, payload: dict[str, Any]
    ) -> TransitionResult | None:
        """Convenience method to emit event."""
        event = StateEvent(
            event_id=f"{source}:{datetime.now(UTC).timestamp()}",
            event_type=event_type,
            source=source,
            timestamp=datetime.now(UTC).timestamp(),
            payload=payload,
        )
        return await self.emit_event(event)

    async def start(self) -> None:
        """Start event processing loop."""
        self._running = True
        while self._running:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._process_single_event(event)
            except TimeoutError:
                # No events, continue
                pass

    def stop(self) -> None:
        """Stop event processing loop."""
        self._running = False

    def get_state(self) -> CompiledState | None:
        """Get current state."""
        return self._current_state

    def get_history(self) -> list[EventDrivenTransition]:
        """Get transition history."""
        return list(self._history)

    def get_stats(self) -> dict[str, Any]:
        """Get engine statistics."""
        return self._stats.copy()

    def register_handler(self, event_type: str, handler: EventHandler) -> None:
        """Register custom event handler."""
        self._router.register_handler(event_type, handler)

    # ========================================================================
    # Private
    # ========================================================================

    async def _process_single_event(self, event: StateEvent) -> TransitionResult | None:
        """
        Process single event through the pipeline.

        Pipeline:
            1. Compute delta (semantic interpretation - ONCE)
            2. Fast invariant gate (early rejection)
            3. Numeric transition (vectorized)
            4. Commit new state
            5. Record history
        """
        import time

        if self._current_state is None:
            return None

        start_time = time.perf_counter()

        # 1. Compute delta (semantic work happens HERE and NOWHERE ELSE)
        delta = self._delta_computer.compute_delta(event)

        # 2. Check if we have valid inputs and constraints
        if delta.numeric_inputs is None or delta.constraints is None:
            return None

        # 3. Execute numeric transition (fast path)
        result = self._numeric_kernel.transition(
            state=self._current_state,
            inputs=delta.numeric_inputs,
            constraints=delta.constraints,
            transition_type="vectorized_compute",
        )

        # 4. Update stats
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        self._stats["avg_latency_ms"] = self._stats["avg_latency_ms"] * 0.9 + elapsed_ms * 0.1

        if result.success:
            # Commit new state
            self._current_state = result.new_state
            self._stats["transitions"] += 1

            # Record
            record = EventDrivenTransition(
                transition_id=f"tx:{event.event_hash}",
                event=event,
                delta=delta,
                result=result,
                timestamp=datetime.now(UTC).timestamp(),
            )
            self._history.append(record)
        else:
            self._stats["invariant_rejections"] += 1

        return result


# ============================================================================
# Factory
# ============================================================================


def get_event_driven_engine() -> EventDrivenTransitionEngine:
    """Get the singleton event-driven transition engine."""
    return EventDrivenTransitionEngine()
