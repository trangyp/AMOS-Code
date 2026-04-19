from typing import Any

"""Brain Event Processor - Event streaming and processing for brain operations.

Provides real-time event emission and processing for brain cognitive operations.
"""
from __future__ import annotations


from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class BrainEvent:
    """Brain processing event."""

    event_type: str
    payload: dict[str, Any]
    timestamp: str
    source: str = "brain"


class BrainEventProcessor:
    """Process and emit brain events."""

    def __init__(self) -> None:
        self._handlers: list[Callable[[BrainEvent], None]] = []
        self._event_history: list[BrainEvent] = []

    def emit(self, event_type: str, payload: dict[str, Any], source: str = "brain") -> None:
        """Emit a brain event."""
        event = BrainEvent(
            event_type=event_type,
            payload=payload,
            timestamp=datetime.now(timezone.utc).isoformat(),
            source=source,
        )
        self._event_history.append(event)

        # Notify handlers
        for handler in self._handlers:
            try:
                handler(event)
            except Exception:
                pass

    def on_event(self, handler: Callable[[BrainEvent], None]) -> None:
        """Register event handler."""
        self._handlers.append(handler)

    def get_events(self, event_type: str | None = None) -> list[BrainEvent]:
        """Get events, optionally filtered by type."""
        if event_type:
            return [e for e in self._event_history if e.event_type == event_type]
        return self._event_history.copy()


# Global event processor
_event_processor: BrainEventProcessor | None = None


def get_event_processor() -> BrainEventProcessor:
    """Get or create global event processor."""
    global _event_processor
    if _event_processor is None:
        _event_processor = BrainEventProcessor()
    return _event_processor


def emit_event(event_type: str, payload: dict[str, Any], source: str = "brain") -> None:
    """Emit event to global processor."""
    processor = get_event_processor()
    processor.emit(event_type, payload, source)
