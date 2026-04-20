"""AMOS Observability v2.0 - Production Monitoring Layer.

Provides:
- Prometheus metrics collection for all engines
- Health checks for production deployments
- Performance monitoring and alerting
- Operational dashboards data feed
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc, timezone

UTC = UTC
from enum import Enum
from typing import Any, Optional


class MetricType(Enum):
    """Types of metrics collected."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class EngineMetric:
    """Metric data point for engine monitoring."""

    name: str
    value: float
    metric_type: MetricType
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class HealthStatus:
    """Health status for component."""

    component: str
    status: str  # healthy, degraded, unhealthy
    last_check: str
    latency_ms: float
    message: str = ""


class AMOSObservabilityV2:
    """
    Production observability layer for AMOS.

    Collects metrics, health status, and operational data
    from all 4 engines for monitoring and alerting.
    """

    def __init__(self) -> None:
        self._metrics: dict[str, list[EngineMetric]] = {}
        self._health_status: dict[str, HealthStatus] = {}
        self._collectors: list[Callable[[], Awaitable[list[EngineMetric]]]] = []
        self._running = False
        self._collection_task: asyncio.Task = None

    async def initialize(self) -> None:
        """Initialize observability system."""
        self._running = True
        self._collection_task = asyncio.create_task(self._metric_collection_loop())

    async def stop(self) -> None:
        """Stop observability collection."""
        self._running = False
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass

    def register_collector(self, collector: Callable[[], Awaitable[list[EngineMetric]]]) -> None:
        """Register a metric collector function."""
        self._collectors.append(collector)

    async def _metric_collection_loop(self) -> None:
        """Background loop for metric collection."""
        while self._running:
            for collector in self._collectors:
                try:
                    metrics = await collector()
                    for metric in metrics:
                        if metric.name not in self._metrics:
                            self._metrics[metric.name] = []
                        self._metrics[metric.name].append(metric)
                        # Keep only last 1000 data points
                        if len(self._metrics[metric.name]) > 1000:
                            self._metrics[metric.name] = self._metrics[metric.name][-1000:]
                except Exception as e:
                    print(f"Metric collection error: {e}")

            await asyncio.sleep(10)  # Collect every 10 seconds

    def record_metric(self, metric: EngineMetric) -> None:
        """Record a single metric."""
        if metric.name not in self._metrics:
            self._metrics[metric.name] = []
        self._metrics[metric.name].append(metric)

    async def check_health(
        self, component: str, check_fn: Callable[[], Awaitable[tuple[bool, str]]]
    ) -> HealthStatus:
        """Run health check for component."""
        start = time.time()
        try:
            healthy, message = await check_fn()
            latency = (time.time() - start) * 1000

            status = HealthStatus(
                component=component,
                status="healthy" if healthy else "unhealthy",
                last_check=datetime.now(timezone.utc).isoformat(),
                latency_ms=latency,
                message=message,
            )
        except Exception as e:
            status = HealthStatus(
                component=component,
                status="unhealthy",
                last_check=datetime.now(timezone.utc).isoformat(),
                latency_ms=(time.time() - start) * 1000,
                message=str(e),
            )

        self._health_status[component] = status
        return status

    def get_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []

        for name, metrics in self._metrics.items():
            if not metrics:
                continue

            # Get latest value for gauge, count for counter
            latest = metrics[-1]

            if latest.metric_type == MetricType.GAUGE:
                lines.append(f"# HELP {name} Current value of {name}")
                lines.append(f"# TYPE {name} gauge")
                label_str = ",".join(f'{k}="{v}"' for k, v in latest.labels.items())
                if label_str:
                    lines.append(f"{name}{{{label_str}}} {latest.value}")
                else:
                    lines.append(f"{name} {latest.value}")

            elif latest.metric_type == MetricType.COUNTER:
                total = sum(m.value for m in metrics)
                lines.append(f"# HELP {name} Total count of {name}")
                lines.append(f"# TYPE {name} counter")
                lines.append(f"{name} {total}")

        # Add health metrics
        for component, status in self._health_status.items():
            health_value = 1 if status.status == "healthy" else 0
            lines.append(f'amos_health{{component="{component}"}} {health_value}')

        return "\n".join(lines)

    def get_health_summary(self) -> dict[str, Any]:
        """Get summary of all health checks."""
        healthy = sum(1 for s in self._health_status.values() if s.status == "healthy")
        total = len(self._health_status)

        return {
            "overall_status": "healthy"
            if healthy == total
            else "degraded"
            if healthy > 0
            else "unhealthy",
            "healthy_components": healthy,
            "total_components": total,
            "components": {
                name: {
                    "status": s.status,
                    "latency_ms": s.latency_ms,
                    "last_check": s.last_check,
                    "message": s.message,
                }
                for name, s in self._health_status.items()
            },
        }


# Global instance
_observability: Optional[AMOSObservabilityV2] = None


def get_observability() -> AMOSObservabilityV2:
    """Get global observability instance."""
    global _observability
    if _observability is None:
        _observability = AMOSObservabilityV2()
    return _observability


if __name__ == "__main__":

    async def demo():
        obs = get_observability()
        await obs.initialize()

        # Record some metrics
        obs.record_metric(EngineMetric("engine_operations", 42, MetricType.COUNTER))
        obs.record_metric(EngineMetric("active_simulations", 5, MetricType.GAUGE))

        # Run health check
        async def check_temporal():
            return True, "Temporal engine running"

        await obs.check_health("temporal", check_temporal)

        # Export Prometheus metrics
        prometheus_output = obs.get_prometheus_metrics()
        print("Prometheus Metrics:")
        print(prometheus_output)

        print("\nHealth Summary:")
        print(obs.get_health_summary())

        await obs.stop()

    asyncio.run(demo())
