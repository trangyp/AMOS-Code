#!/usr/bin/env python3
"""AMOS Observability Engine - Metrics, Traces & Health.

Unified observability for the 14-Layer AMOS System:
- Prometheus-compatible metrics export
- OpenTelemetry-style tracing
- Health check aggregation
- Structured logging

Architecture:
- MetricsRegistry: Counter, Gauge, Histogram metrics
- Tracer: Span-based distributed tracing
- HealthAggregator: Layer health status
- ObservabilityEngine: Unified interface
"""

from __future__ import annotations

import asyncio
import json
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class MetricType(Enum):
    """Types of metrics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


@dataclass
class MetricValue:
    """A metric value with timestamp."""

    value: float
    timestamp: float
    labels: dict[str, str] = field(default_factory=dict)


class Counter:
    """Monotonically increasing counter."""

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self._value = 0.0
        self._lock = asyncio.Lock()

    async def inc(self, value: float = 1.0) -> None:
        """Increment counter."""
        async with self._lock:
            self._value += value

    async def get(self) -> float:
        """Get current value."""
        async with self._lock:
            return self._value

    def to_prometheus(self) -> str:
        """Export as Prometheus format."""
        return (
            f"# HELP {self.name} {self.description}\n"
            f"# TYPE {self.name} counter\n"
            f"{self.name} {self._value}"
        )


class Gauge:
    """Value that can go up or down."""

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self._value = 0.0
        self._lock = asyncio.Lock()

    async def set(self, value: float) -> None:
        """Set gauge value."""
        async with self._lock:
            self._value = value

    async def inc(self, value: float = 1.0) -> None:
        """Increment gauge."""
        async with self._lock:
            self._value += value

    async def dec(self, value: float = 1.0) -> None:
        """Decrement gauge."""
        async with self._lock:
            self._value -= value

    async def get(self) -> float:
        """Get current value."""
        async with self._lock:
            return self._value

    def to_prometheus(self) -> str:
        """Export as Prometheus format."""
        return (
            f"# HELP {self.name} {self.description}\n"
            f"# TYPE {self.name} gauge\n"
            f"{self.name} {self._value}"
        )


class Histogram:
    """Distribution of values."""

    def __init__(self, name: str, description: str = "", buckets: list[float] = None) -> None:
        self.name = name
        self.description = description
        self.buckets = buckets or [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
        self._values: deque[float] = deque(maxlen=10000)
        self._lock = asyncio.Lock()

    async def observe(self, value: float) -> None:
        """Record a value observation."""
        async with self._lock:
            self._values.append(value)

    async def get_stats(self) -> dict[str, float]:
        """Get histogram statistics."""
        async with self._lock:
            if not self._values:
                return {"count": 0, "sum": 0, "avg": 0}
            values = list(self._values)
            return {
                "count": len(values),
                "sum": sum(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
            }

    def to_prometheus(self) -> str:
        """Export as Prometheus format."""
        lines = [f"# HELP {self.name} {self.description}", f"# TYPE {self.name} histogram"]

        async def get_stats():
            async with self._lock:
                return list(self._values)

        # Note: synchronous access for export
        values = list(self._values)
        for bucket in self.buckets:
            count = sum(1 for v in values if v <= bucket)
            lines.append(f'{self.name}_bucket{{le="{bucket}"}} {count}')
        lines.append(f'{self.name}_bucket{{le="+Inf"}} {len(values)}')
        lines.append(f"{self.name}_count {len(values)}")
        lines.append(f"{self.name}_sum {sum(values)}")
        return "\n".join(lines)


@dataclass
class Span:
    """A trace span."""

    name: str
    trace_id: str
    span_id: str
    start_time: float
    end_time: float = None
    parent_id: str = None
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    def finish(self, attributes: dict[str, Any] = None) -> None:
        """Finish the span."""
        self.end_time = time.time()
        if attributes:
            self.attributes.update(attributes)

    def add_event(self, name: str, attributes: dict[str, Any] = None) -> None:
        """Add event to span."""
        self.events.append({"name": name, "timestamp": time.time(), "attributes": attributes or {}})

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": (self.end_time - self.start_time) * 1000 if self.end_time else None,
            "attributes": self.attributes,
            "events": self.events,
        }


class Tracer:
    """Simple span-based tracer."""

    def __init__(self, service_name: str = "amos") -> None:
        self.service_name = service_name
        self._spans: deque[Span] = deque(maxlen=1000)
        self._current_spans: dict[str, Span] = {}
        self._lock = asyncio.Lock()

    async def start_span(
        self, name: str, parent_id: str = None, attributes: dict[str, Any] = None
    ) -> Span:
        """Start a new span."""
        import uuid

        span = Span(
            name=name,
            trace_id=str(uuid.uuid4()),
            span_id=str(uuid.uuid4())[:16],
            start_time=time.time(),
            parent_id=parent_id,
            attributes=attributes or {},
        )
        async with self._lock:
            self._current_spans[span.span_id] = span
        return span

    async def finish_span(self, span: Span, attributes: dict[str, Any] = None) -> None:
        """Finish a span."""
        span.finish(attributes)
        async with self._lock:
            if span.span_id in self._current_spans:
                del self._current_spans[span.span_id]
            self._spans.append(span)

    async def get_traces(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent traces."""
        async with self._lock:
            return [s.to_dict() for s in list(self._spans)[-limit:]]


@dataclass
class HealthStatus:
    """Health status for a component."""

    component: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: str = ""
    last_check: float = field(default_factory=time.time)
    metrics: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "component": self.component,
            "status": self.status,
            "message": self.message,
            "last_check": self.last_check,
            "metrics": self.metrics,
        }


class HealthAggregator:
    """Aggregates health status from all layers."""

    def __init__(self) -> None:
        self._statuses: dict[str, HealthStatus] = {}
        self._lock = asyncio.Lock()

    async def update(self, status: HealthStatus) -> None:
        """Update health status for a component."""
        async with self._lock:
            self._statuses[status.component] = status

    async def get_status(self, component: str = None) -> dict[str, Any]:
        """Get health status."""
        async with self._lock:
            if component:
                s = self._statuses.get(component)
                return s.to_dict() if s else {"error": "Component not found"}

            statuses = {k: v.to_dict() for k, v in self._statuses.items()}
            healthy = sum(1 for s in self._statuses.values() if s.status == "healthy")
            total = len(self._statuses)

            return {
                "overall": "healthy"
                if healthy == total
                else "degraded"
                if healthy > 0
                else "unhealthy",
                "healthy_count": healthy,
                "total_count": total,
                "components": statuses,
            }


class MetricsRegistry:
    """Registry for all metrics."""

    def __init__(self) -> None:
        self._counters: dict[str, Counter] = {}
        self._gauges: dict[str, Gauge] = {}
        self._histograms: dict[str, Histogram] = {}
        self._lock = asyncio.Lock()

    async def counter(self, name: str, description: str = "") -> Counter:
        """Get or create counter."""
        async with self._lock:
            if name not in self._counters:
                self._counters[name] = Counter(name, description)
            return self._counters[name]

    async def gauge(self, name: str, description: str = "") -> Gauge:
        """Get or create gauge."""
        async with self._lock:
            if name not in self._gauges:
                self._gauges[name] = Gauge(name, description)
            return self._gauges[name]

    async def histogram(self, name: str, description: str = "") -> Histogram:
        """Get or create histogram."""
        async with self._lock:
            if name not in self._histograms:
                self._histograms[name] = Histogram(name, description)
            return self._histograms[name]

    def to_prometheus(self) -> str:
        """Export all metrics in Prometheus format."""
        lines = []
        for counter in self._counters.values():
            lines.append(counter.to_prometheus())
        for gauge in self._gauges.values():
            lines.append(gauge.to_prometheus())
        for hist in self._histograms.values():
            lines.append(hist.to_prometheus())
        return "\n\n".join(lines)


class AMOSObservabilityEngine:
    """Main observability engine for AMOS."""

    def __init__(self) -> None:
        self.metrics = MetricsRegistry()
        self.tracer = Tracer("amos")
        self.health = HealthAggregator()
        self._running = False
        self._export_task: asyncio.Task = None
        self._layer_metrics: dict[str, dict[str, Any]] = {}

    async def start(self) -> None:
        """Start observability engine."""
        print("[ObservabilityEngine] Starting...")
        self._running = True

        # Initialize layer metrics
        layers = [
            f"{i:02d}_{n}"
            for i, n in enumerate(
                [
                    "ROOT",
                    "BRAIN",
                    "SENSES",
                    "IMMUNE",
                    "BLOOD",
                    "NERVES",
                    "MUSCLE",
                    "METABOLISM",
                    "GROWTH",
                    "SOCIAL",
                    "MEMORY",
                    "LEGAL",
                    "ETHICS",
                    "TIME",
                    "INTERFACES",
                ]
            )
        ]

        for layer in layers:
            self._layer_metrics[layer] = {
                "cycles": await self.metrics.counter(f"amos_{layer}_cycles", f"Cycles for {layer}"),
                "errors": await self.metrics.counter(f"amos_{layer}_errors", f"Errors for {layer}"),
                "latency": await self.metrics.histogram(
                    f"amos_{layer}_latency", f"Latency for {layer}"
                ),
                "health": await self.metrics.gauge(
                    f"amos_{layer}_health", f"Health score for {layer}"
                ),
            }

        # Start periodic export
        self._export_task = asyncio.create_task(self._periodic_export())
        print("[ObservabilityEngine] Active")

    async def stop(self) -> None:
        """Stop observability engine."""
        print("[ObservabilityEngine] Stopping...")
        self._running = False
        if self._export_task:
            self._export_task.cancel()
            try:
                await self._export_task
            except asyncio.CancelledError:
                pass
        print("[ObservabilityEngine] Stopped")

    async def _periodic_export(self) -> None:
        """Periodically export metrics."""
        while self._running:
            try:
                # Export to file for scraping
                metrics_path = Path("_AMOS_BRAIN/metrics.prom")
                metrics_path.parent.mkdir(parents=True, exist_ok=True)
                metrics_path.write_text(self.metrics.to_prometheus())
            except Exception as e:
                print(f"[ObservabilityEngine] Export error: {e}")
            await asyncio.sleep(15)  # Export every 15s

    async def record_cycle(self, layer: str, latency_ms: float, error: bool = False) -> None:
        """Record a layer cycle."""
        if layer in self._layer_metrics:
            m = self._layer_metrics[layer]
            await m["cycles"].inc()
            await m["latency"].observe(latency_ms / 1000)  # Convert to seconds
            if error:
                await m["errors"].inc()

    async def update_health(self, layer: str, score: float, message: str = "") -> None:
        """Update layer health."""
        if layer in self._layer_metrics:
            await self._layer_metrics[layer]["health"].set(score)

        status = "healthy" if score > 0.8 else "degraded" if score > 0.5 else "unhealthy"
        await self.health.update(
            HealthStatus(
                component=layer, status=status, message=message, metrics={"health_score": score}
            )
        )

    async def start_trace(self, name: str, **kwargs) -> Span:
        """Start a trace span."""
        return await self.tracer.start_span(name, attributes=kwargs)

    async def finish_trace(self, span: Span, **kwargs) -> None:
        """Finish a trace span."""
        await self.tracer.finish_span(span, attributes=kwargs)

    def get_metrics(self) -> str:
        """Get Prometheus metrics."""
        return self.metrics.to_prometheus()

    async def get_health(self) -> dict[str, Any]:
        """Get health status."""
        return await self.health.get_status()

    async def get_traces(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent traces."""
        return await self.tracer.get_traces(limit)


# Global instance
_observability_engine: Optional[AMOSObservabilityEngine] = None


def get_observability_engine() -> AMOSObservabilityEngine:
    """Get or create global observability engine."""
    global _observability_engine
    if _observability_engine is None:
        _observability_engine = AMOSObservabilityEngine()
    return _observability_engine


if __name__ == "__main__":

    async def demo():
        engine = get_observability_engine()
        await engine.start()

        # Simulate some activity
        for i in range(10):
            await engine.record_cycle("01_BRAIN", latency_ms=50 + i * 10)
            await engine.update_health("01_BRAIN", 0.95)

        # Start a trace
        span = await engine.start_trace("brain_cycle", layer="01_BRAIN")
        await asyncio.sleep(0.1)
        await engine.finish_trace(span, result="success")

        # Get metrics
        print("\n=== Prometheus Metrics ===")
        print(engine.get_metrics()[:1000] + "...")

        print("\n=== Health Status ===")
        health = await engine.get_health()
        print(json.dumps(health, indent=2))

        await engine.stop()

    asyncio.run(demo())
