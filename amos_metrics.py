#!/usr/bin/env python3
"""AMOS Metrics Aggregation System - Prometheus-Style

Production-grade metrics collection with:
- Counter, Gauge, Histogram metric types
- Prometheus-compatible exposition format
- In-memory aggregation with optional Redis persistence
- Automatic metric labeling
- Export to Prometheus/Grafana

Usage:
    from amos_metrics import counter, gauge, histogram

    # Count events
    counter("api_requests_total", {"endpoint": "/api/v1/brain"})

    # Set gauge value
    gauge("active_connections", {}, 42)

    # Record histogram
    histogram("request_duration_seconds", {}, 0.5)

    # Export for Prometheus
    print(generate_prometheus_format())
"""

from __future__ import annotations

import os
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

# Redis integration
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


@dataclass
class MetricValue:
    """Single metric value with timestamp."""
    value: float
    timestamp: float
    labels: dict[str, str]


@dataclass
class Counter:
    """Monotonically increasing counter."""
    name: str
    description: str
    values: dict[str, list[MetricValue]] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def inc(self, labels: dict[str, str] = None, value: float = 1) -> None:
        """Increment counter."""
        label_key = _labels_key(labels or {})
        with self.lock:
            if label_key not in self.values:
                self.values[label_key] = []
            if self.values[label_key]:
                # Increment from last value
                last_val = self.values[label_key][-1].value
                self.values[label_key].append(MetricValue(
                    value=last_val + value,
                    timestamp=time.time(),
                    labels=labels or {}
                ))
            else:
                self.values[label_key].append(MetricValue(
                    value=value,
                    timestamp=time.time(),
                    labels=labels or {}
                ))

    def get(self, labels: dict[str, str] = None) -> float:
        """Get current counter value."""
        label_key = _labels_key(labels or {})
        with self.lock:
            if label_key in self.values and self.values[label_key]:
                return self.values[label_key][-1].value
            return 0


@dataclass
class Gauge:
    """Gauge that can go up and down."""
    name: str
    description: str
    values: dict[str, MetricValue] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def set(self, labels: dict[str, str], value: float) -> None:
        """Set gauge value."""
        label_key = _labels_key(labels)
        with self.lock:
            self.values[label_key] = MetricValue(
                value=value,
                timestamp=time.time(),
                labels=labels
            )

    def inc(self, labels: dict[str, str], value: float = 1) -> None:
        """Increment gauge."""
        label_key = _labels_key(labels)
        with self.lock:
            if label_key in self.values:
                self.values[label_key].value += value
            else:
                self.values[label_key] = MetricValue(
                    value=value,
                    timestamp=time.time(),
                    labels=labels
                )

    def dec(self, labels: dict[str, str], value: float = 1) -> None:
        """Decrement gauge."""
        self.inc(labels, -value)

    def get(self, labels: dict[str, str] = None) -> float:
        """Get current gauge value."""
        label_key = _labels_key(labels or {})
        with self.lock:
            if label_key in self.values:
                return self.values[label_key].value
            return 0


@dataclass
class Histogram:
    """Histogram for measuring distributions."""
    name: str
    description: str
    buckets: list[float] = field(default_factory=lambda: [.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0, float('inf')])
    values: dict[str, list[MetricValue]] = field(default_factory=dict)
    sums: dict[str, float] = field(default_factory=dict)
    counts: dict[str, int] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def observe(self, labels: dict[str, str], value: float) -> None:
        """Observe a value."""
        label_key = _labels_key(labels)
        with self.lock:
            if label_key not in self.values:
                self.values[label_key] = []
                self.sums[label_key] = 0
                self.counts[label_key] = 0

            self.values[label_key].append(MetricValue(
                value=value,
                timestamp=time.time(),
                labels=labels
            ))
            self.sums[label_key] += value
            self.counts[label_key] += 1

    def get_bucket_counts(self, labels: dict[str, str]) -> dict[float, int]:
        """Get bucket counts for histogram."""
        label_key = _labels_key(labels)
        with self.lock:
            if label_key not in self.values:
                return {b: 0 for b in self.buckets}

            bucket_counts = {b: 0 for b in self.buckets}
            for mv in self.values[label_key]:
                for bucket in self.buckets:
                    if mv.value <= bucket:
                        bucket_counts[bucket] += 1
                        break
            return bucket_counts


# Global registry
_counters: dict[str, Counter] = {}
_gauges: dict[str, Gauge] = {}
_histograms: dict[str, Histogram] = {}
_registry_lock = threading.Lock()


def _labels_key(labels: dict[str, str]) -> str:
    """Generate key from labels dict."""
    return ','.join(f'{k}="{v}"' for k, v in sorted(labels.items()))


def counter(name: str, description: str = "", labels: dict[str, str] = None) -> Counter:
    """Get or create counter."""
    with _registry_lock:
        if name not in _counters:
            _counters[name] = Counter(name=name, description=description)
        return _counters[name]


def gauge(name: str, description: str = "") -> Gauge:
    """Get or create gauge."""
    with _registry_lock:
        if name not in _gauges:
            _gauges[name] = Gauge(name=name, description=description)
        return _gauges[name]


def histogram(name: str, description: str = "", buckets: list[float] = None) -> Histogram:
    """Get or create histogram."""
    with _registry_lock:
        if name not in _histograms:
            _histograms[name] = Histogram(
                name=name,
                description=description,
                buckets=buckets or [.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0, float('inf')]
            )
        return _histograms[name]


def generate_prometheus_format() -> str:
    """Generate Prometheus exposition format."""
    lines = []

    # Counters
    for name, counter in _counters.items():
        lines.append(f"# HELP {name} {counter.description}")
        lines.append(f"# TYPE {name} counter")
        for label_key, values in counter.values.items():
            if values:
                val = values[-1].value
                lines.append(f'{name}{{{label_key}}} {val}')
        lines.append("")

    # Gauges
    for name, gauge in _gauges.items():
        lines.append(f"# HELP {name} {gauge.description}")
        lines.append(f"# TYPE {name} gauge")
        for label_key, value in gauge.values.items():
            lines.append(f'{name}{{{label_key}}} {value.value}')
        lines.append("")

    # Histograms
    for name, hist in _histograms.items():
        lines.append(f"# HELP {name} {hist.description}")
        lines.append(f"# TYPE {name} histogram")
        for label_key in hist.values:
            bucket_counts = hist.get_bucket_counts(hist.values[label_key][0].labels if hist.values[label_key] else {})
            for bucket, count in bucket_counts.items():
                bucket_str = '+Inf' if bucket == float('inf') else str(bucket)
                lines.append(f'{name}_bucket{{le="{bucket_str}",{label_key}}} {count}')
            if label_key in hist.sums:
                lines.append(f'{name}_sum{{{label_key}}} {hist.sums[label_key]}')
                lines.append(f'{name}_count{{{label_key}}} {hist.counts[label_key]}')
        lines.append("")

    return '\n'.join(lines)


def get_metrics_summary() -> dict[str, Any]:
    """Get metrics summary for JSON API."""
    return {
        "counters": {name: {"description": c.description, "values": len(c.values)} for name, c in _counters.items()},
        "gauges": {name: {"description": g.description, "values": len(g.values)} for name, g in _gauges.items()},
        "histograms": {name: {"description": h.description, "values": sum(len(v) for v in h.values.values())} for name, h in _histograms.items()},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# Convenience metrics
api_requests_total = counter("api_requests_total", "Total API requests")
api_request_duration = histogram("api_request_duration_seconds", "API request duration")
active_connections = gauge("active_connections", "Number of active connections")
brain_think_duration = histogram("brain_think_duration_seconds", "Brain think operation duration")
