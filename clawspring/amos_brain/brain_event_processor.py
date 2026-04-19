#!/usr/bin/env python3

from typing import Any

"""AMOS Brain Event Processor - Event-driven cognitive processing.

Features:
- Event ingestion from multiple sources
- Brain-powered event analysis
- Automated response generation
- Event-to-task conversion

Owner: Trang Phan
"""
from __future__ import annotations


import asyncio
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone

try:
    from .api_integration import brain_process_sync, brain_submit_task
    from .brain_workflow_engine import create_brain_workflow, run_brain_workflow
except ImportError:
    from api_integration import brain_process_sync


@dataclass
class Event:
    """System event for brain processing."""

    id: str
    source: str
    event_type: str
    payload: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    priority: str = "MEDIUM"


@dataclass
class EventAnalysis:
    """Brain analysis result for event."""

    event_id: str
    domain: str
    severity: str
    recommended_action: str
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)


class BrainEventProcessor:
    """Event processor using brain for cognitive analysis."""

    def __init__(self):
        self._handlers: dict[str, list[Callable]] = {}
        self._event_queue: asyncio.Queue[Event] = asyncio.Queue()
        self._processing = False
        self._processor_task = None
        self._processed_count = 0

    async def start(self) -> None:
        """Start event processor."""
        self._processing = True
        self._processor_task = asyncio.create_task(self._process_loop())
        print("[BrainEventProcessor] Started")

    async def stop(self) -> None:
        """Stop event processor."""
        self._processing = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        print("[BrainEventProcessor] Stopped")

    async def _process_loop(self) -> None:
        """Main processing loop."""
        while self._processing:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._process_event(event)
                self._event_queue.task_done()
            except TimeoutError:
                continue
            except Exception as e:
                print(f"[EventProcessor] Error: {e}")

    async def _process_event(self, event: Event) -> None:
        """Process single event with brain."""
        # Create analysis prompt
        prompt = f"Analyze {event.event_type} event from {event.source}: {event.payload}"

        # Use brain for analysis
        result = await brain_process_sync(prompt, event.priority)

        analysis = EventAnalysis(
            event_id=event.id,
            domain=result.get("domain", "unknown"),
            severity=self._calculate_severity(result),
            recommended_action=self._generate_action(result, event),
            confidence=0.8 if result.get("success") else 0.5,
            metadata={
                "engines_used": result.get("engines_used", []),
                "duration_ms": result.get("duration_ms", 0),
            },
        )

        self._processed_count += 1

        # Call handlers
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event, analysis)
            except Exception as e:
                print(f"[EventProcessor] Handler error: {e}")

    def _calculate_severity(self, result: dict[str, Any]) -> str:
        """Calculate event severity from brain result."""
        domain = result.get("domain", "unknown")
        if domain in {"error", "security", "failure"}:
            return "HIGH"
        elif domain in {"warning", "degraded"}:
            return "MEDIUM"
        return "LOW"

    def _generate_action(self, result: dict[str, Any], event: Event) -> str:
        """Generate recommended action."""
        domain = result.get("domain", "unknown")
        return f"Handle {domain} event from {event.source}"

    async def emit(
        self, source: str, event_type: str, payload: dict[str, Any], priority: str = "MEDIUM"
    ) -> str:
        """Emit event for processing."""
        event_id = f"evt-{uuid.uuid4().hex[:8]}"
        event = Event(
            id=event_id,
            source=source,
            event_type=event_type,
            payload=payload,
            priority=priority,
        )
        await self._event_queue.put(event)
        return event_id

    def on(self, event_type: str, handler: Callable) -> None:
        """Register event handler."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def get_stats(self) -> dict[str, Any]:
        """Get processor statistics."""
        return {
            "processed_count": self._processed_count,
            "queue_size": self._event_queue.qsize(),
            "handler_count": sum(len(h) for h in self._handlers.values()),
            "processing": self._processing,
        }


# Singleton
_processor: BrainEventProcessor | None = None


async def get_event_processor() -> BrainEventProcessor:
    """Get or create singleton processor."""
    global _processor
    if _processor is None:
        _processor = BrainEventProcessor()
        await _processor.start()
    return _processor


async def emit_event(
    source: str, event_type: str, payload: dict[str, Any], priority: str = "MEDIUM"
) -> str:
    """Emit event."""
    processor = await get_event_processor()
    return await processor.emit(source, event_type, payload, priority)


if __name__ == "__main__":

    async def main():
        print("=" * 60)
        print("AMOS BRAIN EVENT PROCESSOR")
        print("=" * 60)

        processor = await get_event_processor()

        # Register handler
        async def log_handler(event: Event, analysis: EventAnalysis) -> None:
            print(f"  → Handled: {event.event_type} ({analysis.severity})")

        processor.on("system_alert", log_handler)
        processor.on("user_action", log_handler)

        # Emit events
        events = [
            ("monitoring", "system_alert", {"cpu": 95, "memory": 88}, "HIGH"),
            ("api", "user_action", {"endpoint": "/api/users", "method": "POST"}, "MEDIUM"),
            ("database", "query_slow", {"duration": 5.2, "query": "SELECT"}, "MEDIUM"),
        ]

        print("\nEmitting events...")
        for source, evt_type, payload, priority in events:
            evt_id = await emit_event(source, evt_type, payload, priority)
            print(f"  Emitted: {evt_id} ({source}/{evt_type})")

        # Wait for processing
        await asyncio.sleep(3)

        # Stats
        stats = processor.get_stats()
        print("\nStats:")
        print(f"  Processed: {stats['processed_count']}")
        print(f"  Queue: {stats['queue_size']}")

        await processor.stop()
        print("\n" + "=" * 60)

    asyncio.run(main())
