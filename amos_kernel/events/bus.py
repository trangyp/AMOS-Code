"""Event Bus - Internal event system for kernel communication"""

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional


@dataclass
class KernelEvent:
    """Event emitted by kernel layers."""

    event_type: str
    source: str  # law, state, interaction, deterministic, observe, repair
    payload: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class KernelEventBus:
    """Event bus for kernel layer communication."""

    def __init__(self):
        self._subscribers: dict[str, list[Callable[[KernelEvent], None]]] = defaultdict(list)
        self._history: list[KernelEvent] = []
        self._max_history = 1000

    def subscribe(self, event_type: str, handler: Callable[[KernelEvent], None]) -> None:
        """Subscribe to event type."""
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[[KernelEvent], None]) -> None:
        """Unsubscribe from event type."""
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    def emit(self, event: KernelEvent) -> None:
        """Emit event to subscribers."""
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)

        # Notify subscribers
        for handler in self._subscribers.get(event.event_type, []):
            handler(event)

        # Notify wildcards
        for handler in self._subscribers.get("*", []):
            handler(event)

    def get_history(self, event_type: Optional[str] = None, limit: int = 100) -> list[KernelEvent]:
        """Get event history."""
        events = self._history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return events[-limit:]

    def clear(self) -> None:
        """Clear history."""
        self._history.clear()


# Global event bus instance
_global_bus: Optional[KernelEventBus] = None


def get_event_bus() -> KernelEventBus:
    """Get global event bus."""
    global _global_bus
    if _global_bus is None:
        _global_bus = KernelEventBus()
    return _global_bus
