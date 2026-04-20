#!/usr/bin/env python3
"""AMOS Unified Observability Platform - Phase 27
Real-time observability for 26-Phase AMOS Architecture.
Integrates metrics, logs, traces from all phases with WebSocket streaming.

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime

UTC = UTC
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class TelemetryType(Enum):
    METRIC = "metric"
    LOG = "log"
    TRACE = "trace"
    EVENT = "event"


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class TelemetryPoint:
    """Single telemetry data point."""

    timestamp: datetime
    telemetry_type: TelemetryType
    phase: int
    component: str
    metric_name: str
    value: float | str | dict
    labels: dict[str, str] = field(default_factory=dict)
    trace_id: str = None
    span_id: str = None

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "telemetry_type": self.telemetry_type.value,
            "phase": self.phase,
            "component": self.component,
            "metric_name": self.metric_name,
            "value": self.value,
            "labels": self.labels,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
        }


@dataclass
class Alert:
    """Alert definition and state."""

    alert_id: str
    name: str
    description: str
    severity: AlertSeverity
    query: str
    threshold: float
    operator: str
    duration_seconds: int
    status: str = "inactive"
    fired_at: datetime = None
    value: float = None


class AMOSTelemetryCollector:
    """Collects telemetry from all 26 AMOS phases."""

    def __init__(self):
        self.metrics: dict[str, list[TelemetryPoint]] = defaultdict(list)
        self.logs: list[TelemetryPoint] = []
        self.traces: dict[str, list[TelemetryPoint]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def collect_metric(self, phase: int, component: str, metric: str, value: float) -> None:
        """Collect metric from any phase."""
        point = TelemetryPoint(
            timestamp=datetime.now(UTC),
            telemetry_type=TelemetryType.METRIC,
            phase=phase,
            component=component,
            metric_name=metric,
            value=value,
        )
        async with self._lock:
            key = f"{phase}:{component}:{metric}"
            self.metrics[key].append(point)

    def get_metrics(self, phase: int = None, limit: int = 100) -> dict[str, list[TelemetryPoint]]:
        """Get metrics with optional filtering."""
        if phase is None:
            return dict(self.metrics)
        return {k: v for k, v in self.metrics.items() if k.startswith(f"{phase}:")}


class AMOSAlertManager:
    """Alert management for AMOS observability."""

    def __init__(self, collector: AMOSTelemetryCollector):
        self.collector = collector
        self.alerts: dict[str, Alert] = {}
        self._running = False

    def create_alert(
        self, name: str, severity: AlertSeverity, query: str, threshold: float, operator: str = ">"
    ) -> Alert:
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            name=name,
            description=f"Alert for {name}",
            severity=severity,
            query=query,
            threshold=threshold,
            operator=operator,
            duration_seconds=300,
        )
        self.alerts[alert.alert_id] = alert
        return alert

    async def evaluate_alerts(self) -> list[Alert]:
        """Evaluate all alert rules."""
        firing = []
        for alert in self.alerts.values():
            parts = alert.query.split(":")
            if len(parts) == 3:
                phase, comp, metric = parts
                metrics = self.collector.get_metrics(phase=int(phase))
                key = f"{phase}:{comp}:{metric}"
                if key in metrics and metrics[key]:
                    latest = metrics[key][-1].value
                    if isinstance(latest, float) and latest > alert.threshold:
                        alert.value = latest
                        alert.status = "firing"
                        firing.append(alert)
        return firing

    async def start(self) -> None:
        """Start alert evaluation loop."""
        self._running = True
        while self._running:
            await self.evaluate_alerts()
            await asyncio.sleep(60)


class AMOSDashboard:
    """Real-time dashboard backend with WebSocket support."""

    def __init__(self, collector: AMOSTelemetryCollector, alert_manager: AMOSAlertManager):
        self.collector = collector
        self.alert_manager = alert_manager
        self.clients: set[Any] = set()
        self._running = False

    async def broadcast(self, message: dict) -> None:
        """Broadcast to all connected clients."""
        if not self.clients:
            return
        message_json = json.dumps(message)
        disconnected = set()
        for client in self.clients:
            try:
                await client.send(message_json)
            except Exception:
                disconnected.add(client)
        for client in disconnected:
            self.clients.discard(client)

    async def stream(self) -> None:
        """Stream telemetry updates."""
        self._running = True
        while self._running:
            metrics = self.collector.get_metrics()
            firing = [a for a in self.alert_manager.alerts.values() if a.status == "firing"]
            await self.broadcast(
                {
                    "type": "update",
                    "metrics_count": len(metrics),
                    "alerts": len(firing),
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
            await asyncio.sleep(5)


class AMOSObservabilityPlatform:
    """Unified observability platform for 26-phase AMOS."""

    def __init__(self):
        self.collector = AMOSTelemetryCollector()
        self.alert_manager = AMOSAlertManager(self.collector)
        self.dashboard = AMOSDashboard(self.collector, self.alert_manager)

    async def initialize(self) -> bool:
        """Initialize platform with default alerts."""
        # Create alerts for critical phases
        self.alert_manager.create_alert(
            "DB Latency", AlertSeverity.WARNING, "16:database:latency_ms", 100.0
        )
        self.alert_manager.create_alert(
            "Cache Miss Rate", AlertSeverity.WARNING, "19:cache:miss_rate", 0.2
        )
        self.alert_manager.create_alert(
            "Service Mesh Errors", AlertSeverity.CRITICAL, "23:mesh:error_rate", 0.05
        )
        self.alert_manager.create_alert(
            "Event Lag", AlertSeverity.WARNING, "24:event_streaming:lag", 1000.0
        )
        return True

    async def start(self) -> None:
        """Start all observability services."""
        await self.initialize()
        asyncio.create_task(self.alert_manager.start())
        asyncio.create_task(self.dashboard.stream())
        logger.info("AMOS Observability Platform started")


# Global instance
_observability_platform: Optional[AMOSObservabilityPlatform] = None


def get_observability_platform() -> AMOSObservabilityPlatform:
    """Get global observability platform instance."""
    global _observability_platform
    if _observability_platform is None:
        _observability_platform = AMOSObservabilityPlatform()
    return _observability_platform


async def demo():
    """Demonstrate observability platform."""
    print("=" * 60)
    print("AMOS Phase 27: Unified Observability Platform")
    print("=" * 60)

    platform = get_observability_platform()
    await platform.start()

    # Simulate telemetry from various phases
    for phase in [16, 19, 23, 24]:
        await platform.collector.collect_metric(
            phase, "component", "test_metric", float(phase * 10)
        )
        print(f"  - Collected metric from Phase {phase}")

    # Wait for alert evaluation
    await asyncio.sleep(2)

    # Check firing alerts
    firing = await platform.alert_manager.evaluate_alerts()
    print(f"\nFiring Alerts: {len(firing)}")
    for alert in firing:
        print(f"  - {alert.name}: {alert.value}")

    print("\nPhase 27: Observability Platform Operational")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demo())
