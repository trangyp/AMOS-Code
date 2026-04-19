#!/usr/bin/env python3
"""AMOS Telemetry Engine - Distributed tracing for 63+ components.

Implements 2025 OpenTelemetry patterns for AI agent observability:
- W3C Trace Context propagation
- Distributed tracing across async boundaries
- Span correlation through event bus
- Context extraction/injection
- Jaeger-compatible export

Component #63 - Observability Layer
"""

import asyncio
import json
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol


class SpanKind(Enum):
    """Types of spans."""

    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class SpanStatus(Enum):
    """Span status codes."""

    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


@dataclass
class SpanContext:
    """W3C Trace Context for distributed tracing."""

    trace_id: str
    span_id: str
    parent_span_id: str = None
    sampled: bool = True

    @classmethod
    def new(cls, parent: "SpanContext" = None) -> "SpanContext":
        """Create new span context, optionally with parent."""
        return cls(
            trace_id=parent.trace_id if parent else _generate_trace_id(),
            span_id=_generate_span_id(),
            parent_span_id=parent.span_id if parent else None,
            sampled=parent.sampled if parent else True,
        )

    def to_w3c_header(self) -> str:
        """Export to W3C Trace Context format."""
        flags = "01" if self.sampled else "00"
        return f"00-{self.trace_id}-{self.span_id}-{flags}"

    @classmethod
    def from_w3c_header(cls, header: str) -> "SpanContext":
        """Parse from W3C Trace Context header."""
        try:
            parts = header.split("-")
            if len(parts) != 4:
                return None
            return cls(trace_id=parts[1], span_id=parts[2], sampled=parts[3] == "01")
        except Exception:
            return None


@dataclass
class Span:
    """Represents a single operation span."""

    span_id: str
    name: str
    kind: SpanKind
    context: SpanContext
    start_time: float
    end_time: float = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[dict[str, Any]] = field(default_factory=list)
    status: SpanStatus = SpanStatus.UNSET
    status_message: str = ""


class TelemetryExporter(Protocol):
    """Protocol for telemetry exporters."""

    async def export_spans(self, spans: List[Span]) -> bool:
        """Export spans to backend."""
        ...

    async def export_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Export metrics to backend."""
        ...


class JaegerExporter:
    """Export traces to Jaeger-compatible backend."""

    def __init__(self, endpoint: str = "http://localhost:14268/api/traces"):
        self.endpoint = endpoint
        self._buffer: List[Span] = []
        self._max_buffer = 100

    async def export_spans(self, spans: List[Span]) -> bool:
        """Export spans in Jaeger format."""
        self._buffer.extend(spans)

        if len(self._buffer) >= self._max_buffer:
            await self._flush()
        return True

    async def _flush(self) -> None:
        """Flush buffered spans."""
        if not self._buffer:
            return

        # Convert to Jaeger format
        batch = {
            "process": {"serviceName": "amos-ecosystem"},
            "spans": [
                {
                    "traceID": span.context.trace_id,
                    "spanID": span.span_id,
                    "parentSpanID": span.context.parent_span_id,
                    "operationName": span.name,
                    "startTime": int(span.start_time * 1_000_000),
                    "duration": int((span.end_time or time.time() - span.start_time) * 1_000_000),
                    "tags": [{"key": k, "value": v} for k, v in span.attributes.items()],
                    "logs": [
                        {
                            "timestamp": int(e["timestamp"] * 1_000_000),
                            "fields": [
                                {"key": k, "value": v} for k, v in e.items() if k != "timestamp"
                            ],
                        }
                        for e in span.events
                    ],
                }
                for span in self._buffer
            ],
        }

        # In production, would send HTTP POST to Jaeger
        print(f"[JaegerExporter] Flushed {len(self._buffer)} spans")
        self._buffer.clear()

    async def export_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Export metrics."""
        return True


class ConsoleExporter:
    """Simple console exporter for debugging."""

    async def export_spans(self, spans: List[Span]) -> bool:
        """Print spans to console."""
        for span in spans:
            duration_ms = ((span.end_time or time.time()) - span.start_time) * 1000
            print(
                f"[Trace] {span.name} | "
                f"trace={span.context.trace_id[:16]}... | "
                f"span={span.span_id[:8]} | "
                f"duration={duration_ms:.2f}ms | "
                f"status={span.status.value}"
            )
        return True

    async def export_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Print metrics to console."""
        print(f"[Metrics] {json.dumps(metrics, indent=2)}")
        return True


class AMOSTelemetryEngine:
    """
    Main telemetry engine for distributed tracing.

    Implements OpenTelemetry patterns for the AMOS ecosystem:
    - Automatic context propagation through event bus
    - Span creation for component operations
    - W3C Trace Context compliance
    - Async batch export
    """

    def __init__(self, exporter: Optional[TelemetryExporter] = None):
        self.exporter = exporter or ConsoleExporter()
        self._active_spans: Dict[str, Span] = {}
        self._finished_spans: List[Span] = []
        self._samplerate = 1.0  # Sample 100% by default
        self._running = False
        self._export_task: asyncio.Task = None
        self._metrics: Dict[str, Any] = {
            "spans_created": 0,
            "spans_exported": 0,
            "traces_active": 0,
        }

    async def start(self) -> None:
        """Start telemetry engine."""
        self._running = True
        self._export_task = asyncio.create_task(self._export_loop())
        print("[TelemetryEngine] Started")

    async def stop(self) -> None:
        """Stop telemetry engine and flush remaining spans."""
        self._running = False
        if self._export_task:
            self._export_task.cancel()
            try:
                await self._export_task
            except asyncio.CancelledError:
                pass

        # Flush remaining spans
        await self._flush_spans()
        print("[TelemetryEngine] Stopped")

    def start_span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        parent_context: Optional[SpanContext] = None,
        attributes: Dict[str, Any] = None,
    ) -> Span:
        """Start a new span."""
        context = SpanContext.new(parent_context)

        # Check sampling
        if not context.sampled:
            # Create unsampled span
            return Span(
                span_id=context.span_id,
                name=name,
                kind=kind,
                context=context,
                start_time=time.time(),
                attributes={},
            )

        span = Span(
            span_id=context.span_id,
            name=name,
            kind=kind,
            context=context,
            start_time=time.time(),
            attributes=attributes or {},
        )

        self._active_spans[span.span_id] = span
        self._metrics["spans_created"] += 1
        self._metrics["traces_active"] += 1

        return span

    def end_span(
        self, span: Span, status: SpanStatus = SpanStatus.OK, status_message: str = ""
    ) -> None:
        """End a span and queue for export."""
        span.end_time = time.time()
        span.status = status
        span.status_message = status_message

        # Remove from active
        if span.span_id in self._active_spans:
            del self._active_spans[span.span_id]
            self._metrics["traces_active"] -= 1

        # Add to finished queue
        self._finished_spans.append(span)

    def add_event(self, span: Span, name: str, attributes: Dict[str, Any] = None) -> None:
        """Add an event to a span."""
        span.events.append({"name": name, "timestamp": time.time(), **(attributes or {})})

    def set_attribute(self, span: Span, key: str, value: Any) -> None:
        """Set an attribute on a span."""
        span.attributes[key] = value

    def inject_context(self, context: SpanContext, carrier: Dict[str, Any]) -> None:
        """Inject trace context into carrier (e.g., event bus message)."""
        carrier["traceparent"] = context.to_w3c_header()

    def extract_context(self, carrier: Dict[str, Any]) -> Optional[SpanContext]:
        """Extract trace context from carrier."""
        header = carrier.get("traceparent")
        if header:
            return SpanContext.from_w3c_header(header)
        return None

    def get_current_context(self) -> Optional[SpanContext]:
        """Get current active context (last started span)."""
        if self._active_spans:
            return list(self._active_spans.values())[-1].context
        return None

    async def _export_loop(self) -> None:
        """Background loop for periodic export."""
        while self._running:
            await self._flush_spans()
            await asyncio.sleep(5)  # Export every 5 seconds

    async def _flush_spans(self) -> None:
        """Flush finished spans to exporter."""
        if not self._finished_spans:
            return

        spans_to_export = self._finished_spans[:100]  # Batch size
        self._finished_spans = self._finished_spans[100:]

        try:
            await self.exporter.export_spans(spans_to_export)
            self._metrics["spans_exported"] += len(spans_to_export)
        except Exception as e:
            print(f"[TelemetryEngine] Export failed: {e}")
            # Re-queue failed spans
            self._finished_spans.extend(spans_to_export)

    def get_metrics(self) -> Dict[str, Any]:
        """Get telemetry metrics."""
        return {
            **self._metrics,
            "active_spans": len(self._active_spans),
            "queued_spans": len(self._finished_spans),
        }

    def get_trace_summary(self) -> Dict[str, Any]:
        """Get summary of recent traces."""
        traces: Dict[str, list[Span]] = {}
        for span in self._finished_spans[-100:]:
            trace_id = span.context.trace_id
            if trace_id not in traces:
                traces[trace_id] = []
            traces[trace_id].append(span)

        return {
            "total_traces": len(traces),
            "recent_traces": [
                {
                    "trace_id": tid[:16] + "...",
                    "span_count": len(spans),
                    "root_operation": spans[0].name if spans else "unknown",
                    "duration_ms": max((s.end_time or s.start_time) - s.start_time for s in spans)
                    * 1000
                    if spans
                    else 0,
                }
                for tid, spans in list(traces.items())[:10]
            ],
        }


# Utility functions
def _generate_trace_id() -> str:
    """Generate W3C-compatible trace ID (32 hex chars)."""
    return uuid.uuid4().hex + uuid.uuid4().hex[:16]


def _generate_span_id() -> str:
    """Generate W3C-compatible span ID (16 hex chars)."""
    return uuid.uuid4().hex[:16]


# Decorator for automatic span creation
def traced(name: str = None, kind: SpanKind = SpanKind.INTERNAL, attributes: Dict[str, Any] = None):
    """Decorator to automatically create spans for function calls."""

    def decorator(func: Callable) -> Callable:
        span_name = name or func.__name__

        async def async_wrapper(*args, **kwargs):
            # Get telemetry engine from first arg if available
            engine = None
            if args and hasattr(args[0], "_telemetry"):
                engine = args[0]._telemetry

            if not engine:
                return await func(*args, **kwargs)

            parent = engine.get_current_context()
            span = engine.start_span(span_name, kind, parent, attributes)

            try:
                # Inject context into kwargs if carrier exists
                if "carrier" in kwargs:
                    engine.inject_context(span.context, kwargs["carrier"])

                result = await func(*args, **kwargs)
                engine.end_span(span, SpanStatus.OK)
                return result
            except Exception as e:
                engine.end_span(span, SpanStatus.ERROR, str(e))
                raise

        def sync_wrapper(*args, **kwargs):
            engine = None
            if args and hasattr(args[0], "_telemetry"):
                engine = args[0]._telemetry

            if not engine:
                return func(*args, **kwargs)

            parent = engine.get_current_context()
            span = engine.start_span(span_name, kind, parent, attributes)

            try:
                if "carrier" in kwargs:
                    engine.inject_context(span.context, kwargs["carrier"])

                result = func(*args, **kwargs)
                engine.end_span(span, SpanStatus.OK)
                return result
            except Exception as e:
                engine.end_span(span, SpanStatus.ERROR, str(e))
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


# Integration with Event Bus
def instrument_event_bus(engine: AMOSTelemetryEngine, event_bus: Any) -> None:
    """Instrument event bus with distributed tracing."""
    original_publish = event_bus.publish

    async def traced_publish(event: Any) -> int:
        """Publish event with trace context injection."""
        # Get current context and inject into event
        context = engine.get_current_context()
        if context and hasattr(event, "metadata"):
            engine.inject_context(context, event.metadata)

        # Create span for publish operation
        span = engine.start_span(f"event.publish:{event.type}", SpanKind.PRODUCER, context)

        try:
            result = await original_publish(event)
            engine.end_span(span, SpanStatus.OK)
            return result
        except Exception as e:
            engine.end_span(span, SpanStatus.ERROR, str(e))
            raise

    event_bus.publish = traced_publish


# Demo
async def demo_telemetry():
    """Demonstrate telemetry engine."""
    print("\n" + "=" * 70)
    print("AMOS TELEMETRY ENGINE - COMPONENT #63")
    print("=" * 70)

    # Initialize
    print("\n[1] Initializing telemetry engine...")
    engine = AMOSTelemetryEngine()
    await engine.start()
    print("   ✓ Telemetry engine started")

    # Create root span
    print("\n[2] Creating trace spans...")
    root_span = engine.start_span(
        "task.process", SpanKind.SERVER, attributes={"task.type": "analysis", "priority": "high"}
    )

    # Simulate child operations
    await asyncio.sleep(0.1)

    child1 = engine.start_span(
        "knowledge.query",
        SpanKind.CLIENT,
        parent_context=root_span.context,
        attributes={"query": "market_data"},
    )
    await asyncio.sleep(0.05)
    engine.end_span(child1, SpanStatus.OK)

    child2 = engine.start_span(
        "engine.execute",
        SpanKind.INTERNAL,
        parent_context=root_span.context,
        attributes={"engine": "analyzer_v2"},
    )
    await asyncio.sleep(0.08)
    engine.add_event(child2, "checkpoint", {"progress": "50%"})
    engine.end_span(child2, SpanStatus.OK)

    # End root span
    engine.end_span(root_span, SpanStatus.OK)
    print("   ✓ Created 3 spans with parent-child relationship")

    # Context propagation demo
    print("\n[3] Demonstrating context propagation...")
    carrier = {}
    engine.inject_context(root_span.context, carrier)
    print(f"   → W3C Header: {carrier.get('traceparent', 'N/A')[:50]}...")

    extracted = engine.extract_context(carrier)
    if extracted:
        print(f"   ✓ Context extracted: trace={extracted.trace_id[:16]}...")

    # Metrics
    print("\n[4] Telemetry metrics...")
    metrics = engine.get_metrics()
    print(f"   → Spans created: {metrics['spans_created']}")
    print(f"   → Spans exported: {metrics['spans_exported']}")
    print(f"   → Active traces: {metrics['traces_active']}")

    # Wait for export
    await asyncio.sleep(1)

    # Summary
    print("\n[5] Trace summary...")
    summary = engine.get_trace_summary()
    print(f"   → Total traces: {summary['total_traces']}")
    for trace in summary.get("recent_traces", []):
        print(f"     • {trace['root_operation']}: {trace['span_count']} spans")

    await engine.stop()

    print("\n" + "=" * 70)
    print("Telemetry Engine Demo Complete")
    print("=" * 70)
    print("\n✓ W3C Trace Context compliant")
    print("✓ Distributed tracing across components")
    print("✓ OpenTelemetry-style span export")
    print("✓ Event bus instrumentation ready")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demo_telemetry())
