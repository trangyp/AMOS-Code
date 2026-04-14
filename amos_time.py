#!/usr/bin/env python3
"""AMOS Time Engine - Section 14 of Architecture

Θ_t = (Past_t, Present_t, Future_t, Recovery_t, Branches_t)

AMOS reasons across temporal paths, not just snapshots.

Key concepts:
- Event sourcing: Event = (type, source, target, timestamp, payload, outcome)
- Temporal value: V = Σ γ^h · Reward_{t+h}
- Path selection: Path* = argmin[GoalDistance(path) + Risk(path) + Drift(path) - Coherence(path)]
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional


@dataclass
class Event:
    """Event = (type, source, target, timestamp, payload, outcome)
    Immutable event for event sourcing.
    """

    event_type: str
    source: str
    target: str
    timestamp: datetime
    payload: dict[str, Any]
    outcome: Optional[str] = None
    event_id: str = field(default_factory=lambda: f"evt_{datetime.utcnow().timestamp()}")

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "type": self.event_type,
            "source": self.source,
            "target": self.target,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
            "outcome": self.outcome,
        }


@dataclass
class TemporalState:
    """A state at a specific point in time."""

    timestamp: datetime
    state_data: dict[str, Any]
    event_id: Optional[str] = None
    branch_id: Optional[str] = None

    def distance_to(self, other: "TemporalState") -> float:
        """Compute state distance (simplified)."""
        # Temporal distance
        time_diff = abs((self.timestamp - other.timestamp).total_seconds())

        # State difference
        common_keys = set(self.state_data.keys()) & set(other.state_data.keys())
        if not common_keys:
            return float("inf")

        diffs = []
        for key in common_keys:
            v1 = self.state_data.get(key, 0)
            v2 = other.state_data.get(key, 0)
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                diffs.append(abs(v1 - v2))

        state_dist = sum(diffs) / len(diffs) if diffs else 1.0

        # Combined distance
        return state_dist + (time_diff / 3600)  # Normalize time to hours


@dataclass
class TemporalPath:
    """A path through time with multiple states."""

    path_id: str
    states: list[TemporalState]
    events: list[Event]

    # Path metrics
    goal_distance: float = 0.0
    risk: float = 0.0
    drift: float = 0.0
    coherence: float = 1.0
    total_reward: float = 0.0

    def __post_init__(self):
        if not self.path_id:
            self.path_id = f"path_{datetime.utcnow().timestamp()}"

    def compute_metrics(self, goal_state: dict[str, Any]):
        """Compute path quality metrics."""
        if not self.states:
            return

        # Goal distance: distance from final state to goal
        final_state = self.states[-1]
        self.goal_distance = self._state_distance(final_state.state_data, goal_state)

        # Risk: accumulate risk from events
        self.risk = sum(e.payload.get("risk", 0.0) for e in self.events) / max(len(self.events), 1)

        # Drift: state change rate
        if len(self.states) > 1:
            total_drift = 0
            for i in range(1, len(self.states)):
                total_drift += self.states[i - 1].distance_to(self.states[i])
            self.drift = total_drift / (len(self.states) - 1)

        # Coherence: consistency of state transitions
        self.coherence = 1.0 - min(self.drift, 1.0)

        # Total reward
        self.total_reward = sum(e.payload.get("reward", 0.0) for e in self.events)

    def _state_distance(self, state1: dict, state2: dict) -> float:
        """Compute distance between two states."""
        common = set(state1.keys()) & set(state2.keys())
        if not common:
            return 1.0

        diffs = []
        for key in common:
            v1 = state1.get(key, 0)
            v2 = state2.get(key, 0)
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                diffs.append(abs(v1 - v2))

        return sum(diffs) / len(diffs) if diffs else 1.0

    def temporal_value(self, gamma: float = 0.95) -> float:
        """Compute temporal value: V = Σ γ^h · Reward_{t+h}"""
        value = 0.0
        for i, event in enumerate(self.events):
            reward = event.payload.get("reward", 0.0)
            value += (gamma**i) * reward
        return value


class EventStore:
    """Event sourcing store.
    Immutable log of all system events.
    """

    def __init__(self):
        self.events: list[Event] = []
        self.event_index: dict[str, list[Event]] = defaultdict(list)

    def append(self, event: Event):
        """Append event to store (immutable)."""
        self.events.append(event)

        # Index by various keys for fast retrieval
        self.event_index[event.event_type].append(event)
        self.event_index[event.source].append(event)
        self.event_index[event.target].append(event)

    def get_events(
        self,
        event_type: Optional[str] = None,
        source: Optional[str] = None,
        target: Optional[str] = None,
        after: Optional[datetime] = None,
        before: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[Event]:
        """Query events by criteria."""
        candidates = self.events

        if event_type:
            candidates = [e for e in candidates if e.event_type == event_type]
        if source:
            candidates = [e for e in candidates if e.source == source]
        if target:
            candidates = [e for e in candidates if e.target == target]
        if after:
            candidates = [e for e in candidates if e.timestamp >= after]
        if before:
            candidates = [e for e in candidates if e.timestamp <= before]

        # Sort by timestamp
        candidates.sort(key=lambda e: e.timestamp)

        return candidates[-limit:]  # Most recent

    def replay(self, start_time: Optional[datetime] = None) -> list[Event]:
        """Replay events from a point in time."""
        if start_time is None:
            return self.events.copy()
        return [e for e in self.events if e.timestamp >= start_time]

    def get_state_at(self, timestamp: datetime) -> dict[str, Any]:
        """Reconstruct state at a specific time by replaying events."""
        state = {}
        relevant_events = [e for e in self.events if e.timestamp <= timestamp]

        for event in relevant_events:
            # Apply event to state
            if event.event_type == "state_change":
                state.update(event.payload.get("changes", {}))
            elif event.event_type == "state_reset":
                state = event.payload.get("new_state", {})

        return state


class TimeEngine:
    """Θ_t = (Past_t, Present_t, Future_t, Recovery_t, Branches_t)

    Manages temporal reasoning across past, present, and future.
    """

    def __init__(self):
        self.event_store = EventStore()
        self.present: Optional[TemporalState] = None
        self.future_projections: list[TemporalPath] = []
        self.past_states: list[TemporalState] = []
        self.recovery_points: list[datetime] = []  # Snapshots for rollback

        # Temporal parameters
        self.gamma = 0.95  # Discount factor for future rewards
        self.planning_horizon = 10  # Steps to look ahead

    def observe_present(self, state_data: dict[str, Any]):
        """Record current present state."""
        self.present = TemporalState(timestamp=datetime.utcnow(), state_data=state_data)

        # Archive previous present to past
        if self.past_states:
            last_past = self.past_states[-1]
            time_diff = (self.present.timestamp - last_past.timestamp).total_seconds()
            if time_diff > 60:  # Archive if more than 1 minute old
                self.past_states.append(self.present)
        else:
            self.past_states.append(self.present)

        # Create event
        event = Event(
            event_type="state_observation",
            source="time_engine",
            target="present",
            timestamp=self.present.timestamp,
            payload={"state": state_data},
        )
        self.event_store.append(event)

    def project_future(self, possible_actions: list[dict], n_paths: int = 3) -> list[TemporalPath]:
        """Generate possible future paths.

        Path* = argmin[GoalDistance(path) + Risk(path) + Drift(path) - Coherence(path)]
        """
        if not self.present:
            return []

        paths = []

        for i, action in enumerate(possible_actions[:n_paths]):
            path = self._project_single_path(action, path_id=f"future_{i+1}")
            paths.append(path)

        self.future_projections = paths
        return paths

    def _project_single_path(self, action: dict, path_id: str) -> TemporalPath:
        """Project a single future path."""
        states = [self.present] if self.present else []
        events = []

        # Simulate action execution
        current_time = datetime.utcnow()

        # Action event
        action_event = Event(
            event_type="action_projected",
            source="time_engine",
            target=action.get("target", "system"),
            timestamp=current_time,
            payload={
                "action": action,
                "risk": action.get("risk", 0.1),
                "reward": action.get("expected_reward", 0.0),
            },
        )
        events.append(action_event)

        # Project state change
        projected_state = self._apply_action(
            self.present.state_data if self.present else {}, action
        )
        new_state = TemporalState(
            timestamp=current_time + timedelta(seconds=1),
            state_data=projected_state,
            event_id=action_event.event_id,
        )
        states.append(new_state)

        # Add some downstream effects (simplified)
        for step in range(1, 3):
            effect_event = Event(
                event_type="downstream_effect",
                source="projection",
                target="system",
                timestamp=current_time + timedelta(seconds=step + 1),
                payload={
                    "risk": 0.05 * step,
                    "reward": action.get("expected_reward", 0.0) * (0.5**step),
                },
            )
            events.append(effect_event)

            downstream_state = TemporalState(
                timestamp=current_time + timedelta(seconds=step + 1),
                state_data=projected_state,  # Simplified: state persists
                event_id=effect_event.event_id,
            )
            states.append(downstream_state)

        path = TemporalPath(path_id=path_id, states=states, events=events)

        # Compute metrics with goal = action's goal
        goal_state = action.get("goal_state", {})
        path.compute_metrics(goal_state)

        return path

    def _apply_action(self, current_state: dict, action: dict) -> dict:
        """Apply action to state (simplified simulation)."""
        new_state = current_state.copy()

        # Apply changes specified in action
        changes = action.get("state_changes", {})
        new_state.update(changes)

        return new_state

    def select_optimal_path(self, goal_state: dict[str, Any]) -> Optional[TemporalPath]:
        """Select optimal temporal path.

        Path* = argmin[GoalDistance + Risk + Drift - Coherence]
        """
        if not self.future_projections:
            return None

        best_path = None
        best_score = float("inf")

        for path in self.future_projections:
            # Score = GoalDistance + Risk + Drift - Coherence
            score = path.goal_distance + path.risk + path.drift - path.coherence

            if score < best_score:
                best_score = score
                best_path = path

        return best_path

    def create_recovery_point(self, label: str = "") -> datetime:
        """Create a snapshot for potential rollback."""
        timestamp = datetime.utcnow()
        self.recovery_points.append(timestamp)

        event = Event(
            event_type="recovery_point_created",
            source="time_engine",
            target="system",
            timestamp=timestamp,
            payload={"label": label, "state": self.present.state_data if self.present else {}},
        )
        self.event_store.append(event)

        return timestamp

    def rollback_to(self, recovery_point: datetime) -> Optional[dict]:
        """Rollback to a previous recovery point."""
        state = self.event_store.get_state_at(recovery_point)

        event = Event(
            event_type="rollback_executed",
            source="time_engine",
            target="system",
            timestamp=datetime.utcnow(),
            payload={"recovery_point": recovery_point.isoformat(), "restored_state": state},
        )
        self.event_store.append(event)

        return state

    def get_temporal_context(self) -> dict[str, Any]:
        """Get complete temporal context."""
        return {
            "past_events": len(self.past_states),
            "present": self.present.timestamp if self.present else None,
            "future_projections": len(self.future_projections),
            "recovery_points": len(self.recovery_points),
            "total_events": len(self.event_store.events),
        }

    def query_past(self, query: str, n_results: int = 5) -> list[Event]:
        """Query past events semantically."""
        # Simplified: search by event type and content
        all_events = self.event_store.events

        # Score by relevance
        scored = []
        for event in all_events:
            score = self._relevance_score(query, event)
            scored.append((event, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [e[0] for e in scored[:n_results]]

    def _relevance_score(self, query: str, event: Event) -> float:
        """Compute relevance of event to query."""
        query_words = set(query.lower().split())
        content = f"{event.event_type} {event.source} {event.target} {str(event.payload)}"
        content_words = set(content.lower().split())

        if not query_words:
            return 0.0

        overlap = len(query_words & content_words)
        return overlap / len(query_words)


def demo_time_engine():
    """Demonstrate AMOS Time Engine."""
    print("=" * 70)
    print("⏱️  AMOS TIME ENGINE - Section 14")
    print("=" * 70)
    print("\nΘ_t = (Past_t, Present_t, Future_t, Recovery_t, Branches_t)")
    print("V = Σ γ^h · Reward_{t+h}")
    print("=" * 70)

    # Initialize time engine
    time_engine = TimeEngine()

    # 1. Observe present
    print("\n[1] Observing Present State")
    time_engine.observe_present(
        {"system_health": 0.95, "active_tasks": 3, "memory_usage": 0.6, "cpu_load": 0.4}
    )
    print(f"  ✓ Present state recorded at {time_engine.present.timestamp.strftime('%H:%M:%S')}")

    # 2. Create recovery point
    print("\n[2] Creating Recovery Point")
    recovery_time = time_engine.create_recovery_point(label="before_decision")
    print(f"  ✓ Recovery point created: {recovery_time.strftime('%H:%M:%S')}")

    # 3. Project futures
    print("\n[3] Projecting Future Paths")
    possible_actions = [
        {
            "name": "optimize_system",
            "target": "performance",
            "risk": 0.2,
            "expected_reward": 10.0,
            "state_changes": {"cpu_load": 0.3, "memory_usage": 0.5},
            "goal_state": {"system_health": 1.0, "cpu_load": 0.2},
        },
        {
            "name": "add_new_feature",
            "target": "functionality",
            "risk": 0.4,
            "expected_reward": 15.0,
            "state_changes": {"active_tasks": 5, "memory_usage": 0.8},
            "goal_state": {"system_health": 0.9, "active_tasks": 5},
        },
        {
            "name": "maintain_status_quo",
            "target": "stability",
            "risk": 0.05,
            "expected_reward": 2.0,
            "state_changes": {},
            "goal_state": {"system_health": 0.95},
        },
    ]

    paths = time_engine.project_future(possible_actions, n_paths=3)

    print(f"  ✓ Generated {len(paths)} future paths:")
    for path in paths:
        print(
            f"    - {path.path_id}: {len(path.events)} events, "
            f"goal_dist={path.goal_distance:.2f}, risk={path.risk:.2f}"
        )

    # 4. Select optimal path
    print("\n[4] Selecting Optimal Path")
    goal = {"system_health": 1.0, "cpu_load": 0.2}
    optimal = time_engine.select_optimal_path(goal)

    if optimal:
        print(f"  ✓ Selected: {optimal.path_id}")
        print(f"    - Goal distance: {optimal.goal_distance:.2f}")
        print(f"    - Risk: {optimal.risk:.2f}")
        print(f"    - Drift: {optimal.drift:.2f}")
        print(f"    - Coherence: {optimal.coherence:.2f}")
        print(f"    - Temporal value: {optimal.temporal_value(gamma=0.95):.2f}")

    # 5. Query past
    print("\n[5] Querying Past Events")
    results = time_engine.query_past("state system", n_results=3)
    print(f"  ✓ Found {len(results)} relevant past events")
    for event in results:
        print(f"    - {event.event_type} at {event.timestamp.strftime('%H:%M:%S')}")

    # 6. Temporal context
    print("\n[6] Temporal Context Summary")
    context = time_engine.get_temporal_context()
    for key, value in context.items():
        print(f"  • {key}: {value}")

    print("\n" + "=" * 70)
    print("✅ AMOS TIME ENGINE OPERATIONAL")
    print("=" * 70)
    print("\nTemporal Capabilities:")
    print("  • Event sourcing (immutable history)")
    print("  • Past reconstruction from events")
    print("  • Future path projection")
    print("  • Temporal value computation")
    print("  • Recovery point management")
    print("  • Optimal path selection across time")
    print("=" * 70)


# EventSourcing alias for backward compatibility
class EventSourcing(EventStore):
    """Alias for EventStore with simplified interface."""

    def __init__(self):
        super().__init__()

    def record_event(self, action: str, data: dict):
        """Record an event (simplified interface)."""
        event = Event(
            event_type=action,
            source="sourcing",
            target=data.get("target", "system"),
            timestamp=datetime.utcnow(),
            payload=data,
        )
        self.append(event)
        return event.event_id


def demo_time_engine():
    """Demonstrate AMOS Time Engine."""
    print("=" * 70)
    print("⏱️  AMOS TIME ENGINE - Section 14")
    print("=" * 70)
    print("\nΘ_t = (Past_t, Present_t, Future_t, Recovery_t, Branches_t)")
    print("V = Σ γ^h · Reward_{t+h}")
    print("=" * 70)

    # Initialize time engine
    time_engine = TimeEngine()

    # 1. Observe present
    print("\n[1] Observing Present State")
    time_engine.observe_present(
        {"system_health": 0.95, "active_tasks": 3, "memory_usage": 0.6, "cpu_load": 0.4}
    )
    print(f"  ✓ Present state recorded at {time_engine.present.timestamp.strftime('%H:%M:%S')}")

    # 2. Create recovery point
    print("\n[2] Creating Recovery Point")
    recovery_time = time_engine.create_recovery_point(label="before_decision")
    print(f"  ✓ Recovery point created: {recovery_time.strftime('%H:%M:%S')}")

    # 3. Project futures
    print("\n[3] Projecting Future Paths")
    possible_actions = [
        {
            "name": "optimize_system",
            "target": "performance",
            "risk": 0.2,
            "expected_reward": 10.0,
            "state_changes": {"cpu_load": 0.3, "memory_usage": 0.5},
            "goal_state": {"system_health": 1.0, "cpu_load": 0.2},
        },
        {
            "name": "add_new_feature",
            "target": "functionality",
            "risk": 0.4,
            "expected_reward": 15.0,
            "state_changes": {"active_tasks": 5, "memory_usage": 0.8},
            "goal_state": {"system_health": 0.9, "active_tasks": 5},
        },
        {
            "name": "maintain_status_quo",
            "target": "stability",
            "risk": 0.05,
            "expected_reward": 2.0,
            "state_changes": {},
            "goal_state": {"system_health": 0.95},
        },
    ]

    paths = time_engine.project_future(possible_actions, n_paths=3)

    print(f"  ✓ Generated {len(paths)} future paths:")
    for path in paths:
        print(
            f"    - {path.path_id}: {len(path.events)} events, "
            f"goal_dist={path.goal_distance:.2f}, risk={path.risk:.2f}"
        )

    # 4. Select optimal path
    print("\n[4] Selecting Optimal Path")
    goal = {"system_health": 1.0, "cpu_load": 0.2}
    optimal = time_engine.select_optimal_path(goal)

    if optimal:
        print(f"  ✓ Selected: {optimal.path_id}")
        print(f"    - Goal distance: {optimal.goal_distance:.2f}")
        print(f"    - Risk: {optimal.risk:.2f}")
        print(f"    - Drift: {optimal.drift:.2f}")
        print(f"    - Coherence: {optimal.coherence:.2f}")
        print(f"    - Temporal value: {optimal.temporal_value(gamma=0.95):.2f}")

    # 5. Query past
    print("\n[5] Querying Past Events")
    results = time_engine.query_past("state system", n_results=3)
    print(f"  ✓ Found {len(results)} relevant past events")
    for event in results:
        print(f"    - {event.event_type} at {event.timestamp.strftime('%H:%M:%S')}")

    # 6. Temporal context
    print("\n[6] Temporal Context Summary")
    context = time_engine.get_temporal_context()
    for key, value in context.items():
        print(f"  • {key}: {value}")

    print("\n" + "=" * 70)
    print("✅ AMOS TIME ENGINE OPERATIONAL")
    print("=" * 70)
    print("\nTemporal Capabilities:")
    print("  • Event sourcing (immutable history)")
    print("  • Past reconstruction from events")
    print("  • Future path projection")
    print("  • Temporal value computation")
    print("  • Recovery point management")
    print("  • Optimal path selection across time")
    print("=" * 70)


if __name__ == "__main__":
    demo_time_engine()
