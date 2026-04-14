#!/usr/bin/env python3
"""AMOS Ecosystem v2.2 - Real-Time Telemetry & Monitoring System.

Provides production observability with metrics collection,
distributed tracing, and health monitoring.
"""

import json
import sys
import threading
import time
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Optional

sys.path.insert(0, ".")
sys.path.insert(0, "clawspring")
sys.path.insert(0, "clawspring/amos_brain")


@dataclass
class MetricPoint:
    """Single metric data point."""

    timestamp: float
    name: str
    value: float
    labels: dict[str, str]


@dataclass
class HealthCheck:
    """Health check result."""

    component: str
    status: str  # "healthy", "degraded", "unhealthy"
    latency_ms: float
    message: str
    timestamp: datetime


class MetricsCollector:
    """Collects and stores system metrics."""

    def __init__(self, retention_seconds: int = 3600):
        self.retention = retention_seconds
        self.metrics: dict[str, deque] = {}
        self._lock = threading.Lock()
        self._counters: dict[str, int] = {}
        self._gauges: dict[str, float] = {}

    def record(self, name: str, value: float, labels: Optional[dict[str, str]] = None) -> None:
        """Record a metric value."""
        with self._lock:
            if name not in self.metrics:
                self.metrics[name] = deque(maxlen=10000)

            point = MetricPoint(timestamp=time.time(), name=name, value=value, labels=labels or {})
            self.metrics[name].append(point)

    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a counter metric."""
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + value
            self.record(name + "_total", float(self._counters[name]))

    def set_gauge(self, name: str, value: float) -> None:
        """Set a gauge metric."""
        with self._lock:
            self._gauges[name] = value
            self.record(name, value)

    def get_metrics(self, name: Optional[str] = None) -> dict[str, list[dict]]:
        """Get collected metrics."""
        with self._lock:
            if name:
                return {name: [asdict(m) for m in self.metrics.get(name, [])]}
            return {k: [asdict(m) for m in v] for k, v in self.metrics.items()}

    def get_summary(self) -> dict[str, Any]:
        """Get metrics summary."""
        with self._lock:
            summary = {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "metric_names": list(self.metrics.keys()),
                "total_datapoints": sum(len(v) for v in self.metrics.values()),
            }
            return summary


class HealthMonitor:
    """Monitors system health."""

    def __init__(self):
        self.checks: dict[str, Callable[[], HealthCheck]] = {}
        self.results: deque = deque(maxlen=1000)
        self._lock = threading.Lock()

    def register_check(self, name: str, check_fn: Callable[[], HealthCheck]) -> None:
        """Register a health check."""
        self.checks[name] = check_fn

    def run_check(self, name: str) -> Optional[HealthCheck]:
        """Run a single health check."""
        if name not in self.checks:
            return None

        start = time.time()
        try:
            result = self.checks[name]()
        except Exception as e:
            result = HealthCheck(
                component=name,
                status="unhealthy",
                latency_ms=(time.time() - start) * 1000,
                message=str(e),
                timestamp=datetime.now(),
            )

        with self._lock:
            self.results.append(result)

        return result

    def run_all_checks(self) -> list[HealthCheck]:
        """Run all registered health checks."""
        results = []
        for name in self.checks:
            result = self.run_check(name)
            if result:
                results.append(result)
        return results

    def get_health_summary(self) -> dict[str, Any]:
        """Get health summary."""
        checks = self.run_all_checks()

        healthy = sum(1 for c in checks if c.status == "healthy")
        degraded = sum(1 for c in checks if c.status == "degraded")
        unhealthy = sum(1 for c in checks if c.status == "unhealthy")

        overall = "healthy"
        if unhealthy > 0:
            overall = "unhealthy"
        elif degraded > 0:
            overall = "degraded"

        return {
            "overall_status": overall,
            "checks_total": len(checks),
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "checks": [{"component": c.component, "status": c.status} for c in checks],
        }


class TelemetrySystem:
    """Main telemetry system."""

    def __init__(self):
        self.metrics = MetricsCollector()
        self.health = HealthMonitor()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._interval = 30  # seconds

    def start(self) -> None:
        """Start telemetry collection."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._collect_loop, daemon=True)
        self._thread.start()
        print("[Telemetry] Collection started")

    def stop(self) -> None:
        """Stop telemetry collection."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("[Telemetry] Collection stopped")

    def _collect_loop(self) -> None:
        """Background collection loop."""
        while self._running:
            try:
                # Collect system metrics
                import psutil

                self.metrics.set_gauge("system.cpu_percent", psutil.cpu_percent())
                self.metrics.set_gauge("system.memory_percent", psutil.virtual_memory().percent)

                # Run health checks
                self.health.run_all_checks()

            except Exception as e:
                print(f"[Telemetry] Collection error: {e}")

            time.sleep(self._interval)

    def get_dashboard_data(self) -> dict[str, Any]:
        """Get data for telemetry dashboard."""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics.get_summary(),
            "health": self.health.get_health_summary(),
        }

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []

        # Gauges
        for name, value in self.metrics._gauges.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {value}")

        # Counters
        for name, value in self.metrics._counters.items():
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {value}")

        return "\n".join(lines)


# Global instance
_telemetry: Optional[TelemetrySystem] = None


def get_telemetry() -> TelemetrySystem:
    """Get or create global telemetry system."""
    global _telemetry
    if _telemetry is None:
        _telemetry = TelemetrySystem()
    return _telemetry


def main():
    """Demo telemetry system."""
    print("=" * 70)
    print("AMOS ECOSYSTEM v2.2 - TELEMETRY SYSTEM DEMO")
    print("=" * 70)

    telemetry = get_telemetry()

    # Register health checks
    def check_cognitive():
        start = time.time()
        try:
            from amos_cognitive_router import CognitiveRouter

            r = CognitiveRouter()
            r.analyze("test")
            return HealthCheck(
                "cognitive", "healthy", (time.time() - start) * 1000, "OK", datetime.now()
            )
        except Exception as e:
            return HealthCheck("cognitive", "unhealthy", 0, str(e), datetime.now())

    def check_validator():
        start = time.time()
        try:
            from system_validator import SystemValidator

            v = SystemValidator()
            v.validate_all()
            return HealthCheck(
                "validator", "healthy", (time.time() - start) * 1000, "OK", datetime.now()
            )
        except Exception as e:
            return HealthCheck("validator", "unhealthy", 0, str(e), datetime.now())

    telemetry.health.register_check("cognitive", check_cognitive)
    telemetry.health.register_check("validator", check_validator)

    # Start collection
    telemetry.start()

    # Record some metrics
    telemetry.metrics.increment_counter("requests_total", 100)
    telemetry.metrics.set_gauge("active_sessions", 5)

    # Wait a bit
    time.sleep(2)

    # Get dashboard data
    data = telemetry.get_dashboard_data()
    print("\nTelemetry Dashboard Data:")
    print(json.dumps(data, indent=2, default=str))

    # Export Prometheus format
    print("\nPrometheus Export:")
    print(telemetry.export_prometheus())

    # Stop
    telemetry.stop()

    print("\n" + "=" * 70)
    print("Telemetry system ready for production monitoring!")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
