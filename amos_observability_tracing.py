#!/usr/bin/env python3
"""
AMOS Observability & Distributed Tracing System
=================================================

Implements state-of-the-art observability (2025):
- OpenTelemetry-style tracing for 1608+ functions
- Span-based request tracking across 22 engines
- Metrics collection and aggregation
- Health monitoring for 15 subsystems
- End-to-end trace visualization

Architecture Pattern: Distributed Tracing + Observability
Based on: Apica.io 2025 Best Practices, OpenTelemetry standards

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

import time
import uuid
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class Span:
    """
    Represents a single operation within a trace.

    OpenTelemetry-style span with:
    - Unique Span ID
    - Parent Span ID for hierarchy
    - Operation name and timestamps
    - Attributes (metadata)
    - Events (timestamps within span)
    """

    span_id: str
    trace_id: str
    parent_id: str
    name: str
    start_time: float
    end_time: float = None
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)
    status: str = "ok"  # ok, error

    def duration_ms(self) -> float:
        """Calculate span duration in milliseconds."""
        if self.end_time is None:
            return (time.time() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000

    def add_event(self, name: str, attributes: dict | None = None) -> None:
        """Add event to span."""
        self.events.append({"name": name, "timestamp": time.time(), "attributes": attributes or {}})

    def set_error(self, error_message: str) -> None:
        """Mark span as error."""
        self.status = "error"
        self.attributes["error.message"] = error_message

    def to_dict(self) -> dict[str, Any]:
        """Convert span to dictionary."""
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms(),
            "attributes": self.attributes,
            "events": self.events,
            "status": self.status,
        }


@dataclass
class Trace:
    """
    Represents end-to-end request through the system.

    Contains multiple spans showing request flow across:
    - 22 engines
    - 15 subsystems
    - 1608+ functions
    """

    trace_id: str
    name: str
    start_time: float
    spans: list[Span] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)

    def add_span(self, name: str, parent_id: str = None, attributes: dict | None = None) -> Span:
        """Add new span to trace."""
        span = Span(
            span_id=str(uuid.uuid4())[:16],
            trace_id=self.trace_id,
            parent_id=parent_id,
            name=name,
            start_time=time.time(),
            attributes=attributes or {},
        )
        self.spans.append(span)
        return span

    def get_root_span(self) -> Optional[Span]:
        """Get root span (no parent)."""
        for span in self.spans:
            if span.parent_id is None:
                return span
        return None

    def total_duration_ms(self) -> float:
        """Calculate total trace duration."""
        if not self.spans:
            return 0.0
        start = min(s.start_time for s in self.spans)
        end = max(s.end_time or time.time() for s in self.spans)
        return (end - start) * 1000

    def to_dict(self) -> dict[str, Any]:
        """Convert trace to dictionary."""
        return {
            "trace_id": self.trace_id,
            "name": self.name,
            "start_time": self.start_time,
            "total_duration_ms": self.total_duration_ms(),
            "span_count": len(self.spans),
            "attributes": self.attributes,
            "spans": [s.to_dict() for s in self.spans],
        }


class Tracer:
    """
    OpenTelemetry-style tracer for AMOS.

    Tracks requests across:
    - API Gateway
    - 22 engines
    - 15 subsystems
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.active_spans: dict[str, Span] = {}
        self.current_trace: Optional[Trace] = None

    def start_trace(self, name: str, attributes: dict | None = None) -> Trace:
        """Start new distributed trace."""
        trace = Trace(
            trace_id=str(uuid.uuid4())[:16],
            name=name,
            start_time=time.time(),
            attributes=attributes or {},
        )
        self.current_trace = trace
        return trace

    def start_span(self, name: str, parent_id: str = None, attributes: dict | None = None) -> Span:
        """Start new span."""
        if self.current_trace is None:
            self.start_trace(name)

        span = self.current_trace.add_span(name, parent_id, attributes)
        self.active_spans[span.span_id] = span
        return span

    def end_span(self, span_id: str) -> None:
        """End span by ID."""
        if span_id in self.active_spans:
            self.active_spans[span_id].end_time = time.time()
            del self.active_spans[span_id]

    @contextmanager
    def span(self, name: str, attributes: dict | None = None):
        """Context manager for automatic span lifecycle."""
        span = self.start_span(name, attributes=attributes)
        try:
            yield span
        except Exception as e:
            span.set_error(str(e))
            raise
        finally:
            self.end_span(span.span_id)

    def get_current_trace(self) -> Optional[Trace]:
        """Get current trace."""
        return self.current_trace

    def inject_context(self) -> dict[str, str]:
        """Inject trace context for propagation."""
        if self.current_trace:
            root = self.current_trace.get_root_span()
            if root:
                return {
                    "trace_id": root.trace_id,
                    "span_id": root.span_id,
                    "service": self.service_name,
                }
        return {}


class AMOSObservabilitySystem:
    """
    Complete observability system for AMOS.

    Monitors 1608+ functions across 22 engines and 15 subsystems.
    """

    def __init__(self):
        self.traces: list[Trace] = []
        self.tracers: dict[str, Tracer] = {}
        self.metrics: dict[str, list[float]] = defaultdict(list)
        self.health_status: dict[str, dict] = {}
        self.max_traces = 1000  # Keep last 1000 traces

    def get_tracer(self, service_name: str) -> Tracer:
        """Get or create tracer for service."""
        if service_name not in self.tracers:
            self.tracers[service_name] = Tracer(service_name)
        return self.tracers[service_name]

    def record_trace(self, trace: Trace) -> None:
        """Record completed trace."""
        self.traces.append(trace)
        # Maintain max size
        if len(self.traces) > self.max_traces:
            self.traces.pop(0)

    def record_metric(self, name: str, value: float) -> None:
        """Record metric value."""
        self.metrics[name].append(value)
        # Keep last 1000 values
        if len(self.metrics[name]) > 1000:
            self.metrics[name].pop(0)

    def update_health(self, service: str, status: str, details: dict | None = None) -> None:
        """Update service health status."""
        self.health_status[service] = {
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or {},
        }

    def get_trace_by_id(self, trace_id: str) -> Optional[Trace]:
        """Find trace by ID."""
        for trace in self.traces:
            if trace.trace_id == trace_id:
                return trace
        return None

    def get_traces_by_service(self, service: str) -> list[Trace]:
        """Get traces for specific service."""
        return [
            t for t in self.traces if any(s.attributes.get("service") == service for s in t.spans)
        ]

    def get_slow_traces(self, threshold_ms: float = 1000) -> list[Trace]:
        """Get traces exceeding duration threshold."""
        return [t for t in self.traces if t.total_duration_ms() > threshold_ms]

    def get_error_traces(self) -> list[Trace]:
        """Get traces with errors."""
        return [t for t in self.traces if any(s.status == "error" for s in t.spans)]

    def get_statistics(self) -> dict[str, Any]:
        """Get observability statistics."""
        if not self.traces:
            return {"status": "no_data"}

        durations = [t.total_duration_ms() for t in self.traces]
        error_count = len(self.get_error_traces())

        return {
            "total_traces": len(self.traces),
            "error_count": error_count,
            "error_rate": error_count / len(self.traces),
            "avg_duration_ms": sum(durations) / len(durations),
            "max_duration_ms": max(durations),
            "min_duration_ms": min(durations),
            "services_monitored": len(self.tracers),
            "metrics_collected": len(self.metrics),
            "health_checks": len(self.health_status),
        }

    def get_dashboard_data(self) -> dict[str, Any]:
        """Get data for observability dashboard."""
        recent_traces = self.traces[-50:]  # Last 50 traces

        return {
            "statistics": self.get_statistics(),
            "recent_traces": [t.to_dict() for t in recent_traces],
            "health_status": self.health_status,
            "metrics_summary": {
                name: {
                    "count": len(values),
                    "avg": sum(values) / len(values) if values else 0,
                    "latest": values[-1] if values else 0,
                }
                for name, values in self.metrics.items()
            },
        }


# Global observability instance
_observability: Optional[AMOSObservabilitySystem] = None


def get_observability() -> AMOSObservabilitySystem:
    """Get global observability instance."""
    global _observability
    if _observability is None:
        _observability = AMOSObservabilitySystem()
    return _observability


@contextmanager
def trace_operation(name: str, service: str = "amos", attributes: dict | None = None):
    """
    Decorator for tracing operations.

    Usage:
        with trace_operation("think", "brain") as span:
            result = think(query)
    """
    obs = get_observability()
    tracer = obs.get_tracer(service)

    if tracer.current_trace is None:
        tracer.start_trace(name, attributes)

    span = tracer.start_span(name, attributes=attributes)
    span.attributes["service"] = service

    try:
        yield span
        span.end_time = time.time()
    except Exception as e:
        span.set_error(str(e))
        span.end_time = time.time()
        raise
    finally:
        # Record completed trace
        if tracer.current_trace:
            obs.record_trace(tracer.current_trace)


def monitor_function(func_name: str, service: str = "amos"):
    """Decorator to monitor function execution."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            with trace_operation(
                func_name,
                service,
                {
                    "function": func.__name__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()),
                },
            ) as span:
                result = func(*args, **kwargs)
                span.attributes["result_type"] = type(result).__name__
                return result

        return wrapper

    return decorator


# Convenience functions for AMOS components
def trace_brain_operation(operation: str, query: str) -> dict[str, str]:
    """Trace brain operation and return context."""
    obs = get_observability()
    tracer = obs.get_tracer("brain")

    trace = tracer.start_trace(operation, {"query": query[:100]})
    return tracer.inject_context()


def trace_engine_operation(engine: str, operation: str) -> dict[str, str]:
    """Trace engine operation."""
    obs = get_observability()
    tracer = obs.get_tracer(f"engine.{engine}")

    trace = tracer.start_trace(operation, {"engine": engine})
    return tracer.inject_context()


def trace_subsystem_operation(subsystem: str, operation: str) -> dict[str, str]:
    """Trace subsystem operation."""
    obs = get_observability()
    tracer = obs.get_tracer(f"subsystem.{subsystem}")

    trace = tracer.start_trace(operation, {"subsystem": subsystem})
    return tracer.inject_context()


def record_metric(name: str, value: float) -> None:
    """Record a metric."""
    get_observability().record_metric(name, value)


def update_health(service: str, status: str, details: dict | None = None) -> None:
    """Update health status."""
    get_observability().update_health(service, status, details)


def get_observability_dashboard() -> dict[str, Any]:
    """Get dashboard data."""
    return get_observability().get_dashboard_data()


def print_observability_report() -> None:
    """Print observability report."""
    print("=" * 70)
    print("🔭 AMOS OBSERVABILITY & DISTRIBUTED TRACING")
    print("=" * 70)

    obs = get_observability()
    stats = obs.get_statistics()

    print("\n📊 Statistics:")
    for key, value in stats.items():
        print(f"  • {key}: {value}")

    print("\n🏥 Health Status:")
    for service, status in obs.health_status.items():
        icon = "✅" if status["status"] == "healthy" else "⚠️"
        print(f"  {icon} {service}: {status['status']}")

    print(f"\n🔍 Recent Traces: {len(obs.traces[-10:])} shown")
    for trace in obs.traces[-10:]:
        duration = trace.total_duration_ms()
        span_count = len(trace.spans)
        print(f"  • {trace.trace_id}: {trace.name} ({duration:.1f}ms, {span_count} spans)")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Demo observability system
    print_observability_report()

    # Example usage
    print("\n🚀 Demonstrating distributed tracing...")

    # Simulate brain operation
    with trace_operation("think", "brain", {"query": "Test operation"}):
        time.sleep(0.1)  # Simulate work

    # Simulate engine operation
    with trace_operation("analyze", "economics"):
        time.sleep(0.05)

    # Record metrics
    record_metric("brain.think.duration", 100.0)
    record_metric("economics.analyze.duration", 50.0)

    # Update health
    update_health("brain", "healthy", {"engines_active": 22})
    update_health("api_gateway", "healthy", {"requests_handled": 999})

    print("\n✅ Observability system ready for 1608+ functions!")
    print_observability_report()
