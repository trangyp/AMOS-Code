"""
AMOS Delta State Manager
Implements state updates via deltas, not full rebuilds.

From: State_{t+1} = FullRebuild (O(|State|))
To:   State_{t+1} = State_t + Δ_t (O(|Δ|))
"""

import hashlib
import json
import time
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol


class StateView(Protocol):
    """Protocol for state projections."""

    def get(self, path: str, default: Any = None) -> Any: ...

    def to_dict(self) -> Dict[str, Any]: ...


@dataclass(frozen=True)
class StateDelta:
    """Immutable state delta."""

    path: str  # Dot-notation path (e.g., "user.name")
    operation: str  # "set", "delete", "append", "merge"
    value: Any = None
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def compute_hash(self) -> str:
        """Compute deterministic hash for deduplication."""
        content = f"{self.path}:{self.operation}:{json.dumps(self.value, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class DeltaState:
    """
    Persistent state using structural sharing.

    Each state version references parent + deltas.
    Most operations are O(1) due to structural sharing.
    """

    state_id: str
    base_state: Dict[str, Any] = field(default_factory=dict)
    deltas: List[StateDelta] = field(default_factory=list)
    parent_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def apply_delta(self, delta: StateDelta) -> DeltaState:
        """
        Create new state with delta applied.
        O(1) - returns new state, original unchanged.
        """
        new_deltas = self.deltas + [delta]
        return DeltaState(
            state_id=self._compute_new_id(),
            base_state=self.base_state,  # Shared reference
            deltas=new_deltas,
            parent_id=self.state_id,
        )

    def _compute_new_id(self) -> str:
        """Compute unique ID for new state version."""
        content = f"{self.state_id}:{len(self.deltas)}:{time.time()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def get_value(self, path: str = "") -> Any:
        """
        Compute current value at path by applying all deltas.
        O(|deltas|) but typically small for hot paths.
        """
        if not path:
            # Return full state
            result = deepcopy(self.base_state)
            for delta in self.deltas:
                self._apply_to_dict(result, delta)
            return result

        # Get specific path
        parts = path.split(".")

        # Start from base
        current = self.base_state
        for part in parts[:-1]:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        # Apply deltas that affect this path
        final_value = current.get(parts[-1]) if isinstance(current, dict) else None

        for delta in self.deltas:
            if delta.path == path:
                if delta.operation == "set":
                    final_value = delta.value
                elif delta.operation == "delete":
                    final_value = None
                elif delta.operation == "append" and isinstance(final_value, list):
                    final_value = final_value + [delta.value]
                elif delta.operation == "merge" and isinstance(final_value, dict):
                    final_value = {**final_value, **delta.value}

        return final_value

    def _apply_to_dict(self, d: dict, delta: StateDelta) -> None:
        """Apply single delta to dict in-place."""
        parts = delta.path.split(".")
        current = d

        # Navigate to parent of target
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        target = parts[-1]

        if delta.operation == "set":
            current[target] = delta.value
        elif delta.operation == "delete":
            current.pop(target, None)
        elif delta.operation == "append":
            if target not in current:
                current[target] = []
            if isinstance(current[target], list):
                current[target].append(delta.value)
        elif delta.operation == "merge":
            if target not in current or not isinstance(current[target], dict):
                current[target] = {}
            if isinstance(delta.value, dict):
                current[target].update(delta.value)

    def compact(self) -> DeltaState:
        """
        Compress deltas into new base state.
        Reduces delta chain length for performance.
        """
        full_state = self.get_value()
        return DeltaState(
            state_id=self.state_id,
            base_state=full_state,
            deltas=[],
            parent_id=self.parent_id,
        )

    def get_delta_count(self) -> int:
        """Get number of uncommitted deltas."""
        return len(self.deltas)

    def should_compact(self, threshold: int = 100) -> bool:
        """Check if compaction needed."""
        return len(self.deltas) > threshold


class DeltaStateManager:
    """
    Manages delta states with hot caching.
    """

    def __init__(self, max_cache_size: int = 1000):
        self._states: Dict[str, DeltaState] = {}
        self._hot_cache: Dict[str, Any] = {}  # Path-based value cache
        self._max_cache_size = max_cache_size
        self._access_count = 0
        self._hit_count = 0

    def create_state(self, initial_data: Dict[str, Any] = None) -> DeltaState:
        """Create new root state."""
        state = DeltaState(
            state_id=self._generate_id(),
            base_state=initial_data or {},
        )
        self._states[state.state_id] = state
        return state

    def apply_delta(self, state_id: str, delta: StateDelta) -> Optional[DeltaState]:
        """
        Apply delta to existing state.
        Returns new state or None if parent not found.
        """
        if state_id not in self._states:
            return None

        parent = self._states[state_id]
        new_state = parent.apply_delta(delta)
        self._states[new_state.state_id] = new_state

        # Invalidate cache entries for this path
        cache_key = f"{new_state.state_id}:{delta.path}"
        self._hot_cache.pop(cache_key, None)

        return new_state

    def get_value(self, state_id: str, path: str = "", use_cache: bool = True) -> Any:
        """
        Get value at path with optional caching.
        """
        self._access_count += 1

        # Check hot cache
        if use_cache:
            cache_key = f"{state_id}:{path}"
            if cache_key in self._hot_cache:
                self._hit_count += 1
                return self._hot_cache[cache_key]

        # Compute from state
        if state_id not in self._states:
            return None

        state = self._states[state_id]
        value = state.get_value(path)

        # Cache result
        if use_cache and len(self._hot_cache) < self._max_cache_size:
            self._hot_cache[f"{state_id}:{path}"] = value

        return value

    def get_full_state(self, state_id: str) -> Dict[str, Any]:
        """Get fully materialized state."""
        if state_id not in self._states:
            return None
        return self._states[state_id].get_value()

    def compact_state(self, state_id: str) -> Optional[DeltaState]:
        """Compact state to reduce delta chain."""
        if state_id not in self._states:
            return None

        state = self._states[state_id]
        compacted = state.compact()
        self._states[state_id] = compacted

        # Clear related cache entries
        keys_to_remove = [k for k in self._hot_cache if k.startswith(f"{state_id}:")]
        for key in keys_to_remove:
            del self._hot_cache[key]

        return compacted

    def _generate_id(self) -> str:
        """Generate unique state ID."""
        return hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]

    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics."""
        total_deltas = sum(s.get_delta_count() for s in self._states.values())
        return {
            "total_states": len(self._states),
            "total_deltas": total_deltas,
            "avg_deltas_per_state": total_deltas / max(1, len(self._states)),
            "cache_size": len(self._hot_cache),
            "cache_hit_rate": self._hit_count / max(1, self._access_count),
            "access_count": self._access_count,
        }


# Global singleton
_manager: Optional[DeltaStateManager] = None


def get_delta_manager() -> DeltaStateManager:
    """Get global delta state manager."""
    global _manager
    if _manager is None:
        _manager = DeltaStateManager()
    return _manager


# Convenience functions for delta operations
def create_delta(path: str, value: Any, operation: str = "set") -> StateDelta:
    """Create a state delta."""
    return StateDelta(path=path, operation=operation, value=value)


def apply_state_delta(
    state_id: str, path: str, value: Any, operation: str = "set"
) -> Optional[DeltaState]:
    """Apply delta to state and return new state."""
    delta = create_delta(path, value, operation)
    return get_delta_manager().apply_delta(state_id, delta)


# Test
if __name__ == "__main__":
    print("Delta State Manager Test")
    print("=" * 50)

    # Create initial state
    manager = DeltaStateManager()
    state = manager.create_state({"user": {"name": "Alice"}, "count": 0})
    print(f"Created state: {state.state_id}")
    print(f"Initial: {manager.get_full_state(state.state_id)}")

    # Apply deltas
    state = manager.apply_delta(state.state_id, create_delta("user.name", "Bob"))
    state = manager.apply_delta(state.state_id, create_delta("count", 1))
    state = manager.apply_delta(state.state_id, create_delta("items", ["a"], "append"))

    print(f"After deltas: {manager.get_full_state(state.state_id)}")
    print(f"Delta count: {state.get_delta_count()}")

    # Compact
    state = manager.compact_state(state.state_id)
    print(f"After compact: {manager.get_full_state(state.state_id)}")
    print(f"Delta count: {state.get_delta_count()}")

    # Fast path access
    name = manager.get_value(state.state_id, "user.name")
    print(f"Fast access user.name: {name}")

    print("=" * 50)
    print(manager.get_stats())
