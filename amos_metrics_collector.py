#!/usr/bin/env python3
"""AMOS Metrics Collector - API Usage Analytics and Metrics

Collects:
- Request metrics (count, latency, status codes)
- Endpoint usage statistics
- Error rates and types
- Active users and sessions
- Resource utilization

Provides:
- Real-time metrics endpoint
- Historical aggregation
- Prometheus-compatible export
"""

from __future__ import annotations

import json
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any, Optional

UTC = UTC


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


@dataclass
class Metric:
    name: str
    type: MetricType
    value: float
    timestamp: datetime
    labels: dict[str, str] = field(default_factory=dict)
    unit: str = ""


@dataclass
class RequestMetrics:
    path: str
    method: str
    status_code: int
    duration_ms: float
    timestamp: datetime
    client_ip: str = ""
    user_agent: str = ""


class AMOSMetricsCollector:
    """Collect and aggregate API metrics for AMOS Brain."""

    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.requests: deque = deque(maxlen=10000)
        self.counters: dict[str, float] = defaultdict(float)
        self.gauges: dict[str, float] = {}
        self.histograms: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()
        self._start_time = time.time()

    def record_request(
        self,
        path: str,
        method: str,
        status_code: int,
        duration_ms: float,
        client_ip: str = "",
        user_agent: str = "",
    ):
        """Record an API request."""
        with self._lock:
            self.requests.append(
                RequestMetrics(
                    path=path,
                    method=method,
                    status_code=status_code,
                    duration_ms=duration_ms,
                    timestamp=datetime.now(UTC),
                    client_ip=client_ip,
                    user_agent=user_agent,
                )
            )

            # Update counters
            self.counters["requests_total"] += 1
            self.counters[f"requests_{method.lower()}"] += 1
            self.counters[f"requests_path_{path}"] += 1
            self.counters[f"status_{status_code}"] += 1

            # Track latency histogram
            self.histograms["request_duration_ms"].append(duration_ms)
            if len(self.histograms["request_duration_ms"]) > 1000:
                self.histograms["request_duration_ms"].pop(0)

    def set_gauge(self, name: str, value: float):
        """Set a gauge metric."""
        with self._lock:
            self.gauges[name] = value

    def increment(self, name: str, value: float = 1):
        """Increment a counter."""
        with self._lock:
            self.counters[name] += value

    def get_summary(self, minutes: int = 5) -> dict[str, Any]:
        """Get metrics summary for recent period."""
        cutoff = datetime.now(UTC) - timedelta(minutes=minutes)

        with self._lock:
            recent = [r for r in self.requests if r.timestamp > cutoff]

            if not recent:
                return {
                    "period_minutes": minutes,
                    "total_requests": 0,
                    "message": "No recent requests",
                }

            # Calculate metrics
            total = len(recent)
            error_count = sum(1 for r in recent if r.status_code >= 400)

            # Response time stats
            durations = [r.duration_ms for r in recent]
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            p95 = (
                sorted(durations)[int(len(durations) * 0.95)]
                if len(durations) > 1
                else durations[0]
            )

            # Status code breakdown
            status_codes = defaultdict(int)
            for r in recent:
                status_codes[r.status_code] += 1

            # Top endpoints
            endpoints = defaultdict(int)
            for r in recent:
                endpoints[r.path] += 1

            top_endpoints = sorted(endpoints.items(), key=lambda x: x[1], reverse=True)[:5]

            return {
                "period_minutes": minutes,
                "total_requests": total,
                "requests_per_second": round(total / (minutes * 60), 2),
                "error_count": error_count,
                "error_rate": round(error_count / total * 100, 2),
                "response_time_ms": {
                    "avg": round(avg_duration, 2),
                    "min": round(min_duration, 2),
                    "max": round(max_duration, 2),
                    "p95": round(p95, 2),
                },
                "status_codes": dict(status_codes),
                "top_endpoints": [{"path": path, "count": count} for path, count in top_endpoints],
                "unique_clients": len(set(r.client_ip for r in recent if r.client_ip)),
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
            }

    def get_endpoint_stats(self, path: str, hours: int = 24) -> dict:
        """Get detailed stats for a specific endpoint."""
        cutoff = datetime.now(UTC) - timedelta(hours=hours)

        with self._lock:
            requests = [r for r in self.requests if r.path == path and r.timestamp > cutoff]

            if not requests:
                return {"path": path, "message": "No data available"}

            durations = [r.duration_ms for r in requests]

            return {
                "path": path,
                "period_hours": hours,
                "total_calls": len(requests),
                "avg_duration_ms": round(sum(durations) / len(durations), 2),
                "p50_ms": round(sorted(durations)[len(durations) // 2], 2),
                "p95_ms": round(sorted(durations)[int(len(durations) * 0.95)], 2),
                "p99_ms": round(sorted(durations)[int(len(durations) * 0.99)], 2)
                if len(durations) > 10
                else None,
                "error_count": sum(1 for r in requests if r.status_code >= 400),
                "success_rate": round(
                    sum(1 for r in requests if r.status_code < 400) / len(requests) * 100, 2
                ),
            }

    def get_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []

        with self._lock:
            # Counters
            for name, value in self.counters.items():
                lines.append(f"# TYPE {name} counter")
                lines.append(f"{name} {value}")

            # Gauges
            for name, value in self.gauges.items():
                lines.append(f"# TYPE {name} gauge")
                lines.append(f"{name} {value}")

            # Histograms
            for name, values in self.histograms.items():
                if values:
                    lines.append(f"# TYPE {name} histogram")
                    lines.append(f"{name}_count {len(values)}")
                    lines.append(f"{name}_sum {sum(values)}")
                    for bucket in [10, 50, 100, 250, 500, 1000, 2500, 5000]:
                        count = sum(1 for v in values if v <= bucket)
                        lines.append(f'{name}_bucket{{le="{bucket}"}} {count}')

        return "\n".join(lines)

    def to_json(self) -> str:
        """Export all metrics as JSON."""
        return json.dumps(
            {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "summary": self.get_summary(minutes=60),
                "uptime_seconds": time.time() - self._start_time,
            },
            indent=2,
            default=str,
        )


# Global collector instance
_collector: Optional[AMOSMetricsCollector] = None


def get_metrics_collector() -> AMOSMetricsCollector:
    """Get or create global metrics collector."""
    global _collector
    if _collector is None:
        _collector = AMOSMetricsCollector()
    return _collector


if __name__ == "__main__":
    # Test metrics collector
    collector = get_metrics_collector()

    # Simulate some requests
    import random

    for i in range(100):
        collector.record_request(
            path=random.choice(["/health", "/think", "/decide", "/status"]),
            method="POST" if i % 3 == 0 else "GET",
            status_code=200 if i % 10 != 0 else 500,
            duration_ms=random.uniform(10, 500),
            client_ip=f"192.168.1.{i % 10}",
        )

    print("Recent Summary (5 min):")
    print(json.dumps(collector.get_summary(minutes=5), indent=2))

    print("\nEndpoint Stats (/think):")
    print(json.dumps(collector.get_endpoint_stats("/think"), indent=2))

    print("\nPrometheus Format (sample):")
    print(collector.get_prometheus_metrics()[:500] + "...")
