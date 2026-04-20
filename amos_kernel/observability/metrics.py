from __future__ import annotations

"""Kernel Metrics - Prometheus-compatible metrics for observability"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class MetricPoint:
    """Single metric data point."""

    value: float
    timestamp: float
    labels: dict[str, str] = field(default_factory=dict)


class KernelMetrics:
    """Metrics collection for kernel operations."""

    def __init__(self):
        self._counters: dict[str, list[MetricPoint]] = defaultdict(list)
        self._gauges: dict[str, list[MetricPoint]] = defaultdict(list)
        self._histograms: dict[str, list[MetricPoint]] = defaultdict(list)
        self._max_history = 10000

    def increment(
        self, name: str, value: float = 1.0, labels: Optional[dict[str, str]] = None
    ) -> None:
        """Increment a counter metric."""
        point = MetricPoint(
            value=value,
            timestamp=time.time(),
            labels=labels or {},
        )
        self._counters[name].append(point)
        if len(self._counters[name]) > self._max_history:
            self._counters[name].pop(0)

    def gauge(self, name: str, value: float, labels: Optional[dict[str, str]] = None) -> None:
        """Set a gauge metric."""
        point = MetricPoint(
            value=value,
            timestamp=time.time(),
            labels=labels or {},
        )
        self._gauges[name].append(point)
        if len(self._gauges[name]) > self._max_history:
            self._gauges[name].pop(0)

    def histogram(self, name: str, value: float, labels: Optional[dict[str, str]] = None) -> None:
        """Record a histogram observation."""
        point = MetricPoint(
            value=value,
            timestamp=time.time(),
            labels=labels or {},
        )
        self._histograms[name].append(point)
        if len(self._histograms[name]) > self._max_history:
            self._histograms[name].pop(0)

    def get_counter(self, name: str) -> float:
        """Get counter total."""
        return sum(p.value for p in self._counters[name])

    def get_gauge_latest(self, name: str) -> Optional[float]:
        """Get latest gauge value."""
        if self._gauges[name]:
            return self._gauges[name][-1].value
        return None

    def get_histogram_stats(self, name: str) -> dict[str, float]:
        """Get histogram statistics."""
        values = [p.value for p in self._histograms[name]]
        if not values:
            return {"count": 0, "sum": 0.0, "avg": 0.0, "min": 0.0, "max": 0.0}

        return {
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus text format."""
        lines = []

        # Counters
        for name, points in self._counters.items():
            total = sum(p.value for p in points)
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {total}")

        # Gauges
        for name, points in self._gauges.items():
            if points:
                latest = points[-1].value
                lines.append(f"# TYPE {name} gauge")
                lines.append(f"{name} {latest}")

        # Histograms
        for name, points in self._histograms.items():
            stats = self.get_histogram_stats(name)
            lines.append(f"# TYPE {name} histogram")
            lines.append(f'{name}_bucket{{le="+Inf"}} {stats["count"]}')
            lines.append(f"{name}_sum {stats['sum']}")
            lines.append(f"{name}_count {stats['count']}")

        return "\n".join(lines)

    def get_all_metrics(self) -> dict[str, Any]:
        """Get all metrics as dict."""
        return {
            "counters": {k: self.get_counter(k) for k in self._counters},
            "gauges": {k: self.get_gauge_latest(k) for k in self._gauges},
            "histograms": {k: self.get_histogram_stats(k) for k in self._histograms},
        }


# Global metrics instance
_metrics = KernelMetrics()


def get_metrics() -> KernelMetrics:
    """Get global metrics instance."""
    return _metrics


def record_workflow_execution(workflow_id: str, duration: float, success: bool) -> None:
    """Record workflow execution metric."""
    m = get_metrics()
    m.increment("kernel_workflows_total", 1, {"workflow_id": workflow_id, "success": str(success)})
    m.histogram("kernel_workflow_duration_seconds", duration)


def record_law_validation(passed: bool, collapse_risk: float) -> None:
    """Record law validation metric."""
    m = get_metrics()
    m.increment("kernel_law_validations_total", 1, {"passed": str(passed)})
    m.gauge("kernel_collapse_risk", collapse_risk)


def record_state_transition(duration: float, success: bool) -> None:
    """Record state transition metric."""
    m = get_metrics()
    m.increment("kernel_transitions_total", 1, {"success": str(success)})
    m.histogram("kernel_transition_duration_seconds", duration)
