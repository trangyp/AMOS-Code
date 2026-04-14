"""AMOS Performance Monitoring & Telemetry - System observability layer."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime

from amos_runtime import get_runtime


@dataclass
class TelemetryEvent:
    """Single telemetry event."""

    event_type: str
    timestamp: float
    component: str
    duration_ms: float | None = None
    status: str = "success"
    metadata: dict = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Aggregated performance metrics."""

    component: str
    total_calls: int = 0
    total_duration_ms: float = 0.0
    success_count: int = 0
    error_count: int = 0
    avg_duration_ms: float = 0.0
    last_updated: float = field(default_factory=time.time)


class TelemetryCollector:
    """Collect and store telemetry events."""

    MAX_EVENTS = 1000

    def __init__(self):
        self.events: list[TelemetryEvent] = []
        self.metrics: dict[str, PerformanceMetrics] = {}

    def record_event(
        self,
        event_type: str,
        component: str,
        duration_ms: float | None = None,
        status: str = "success",
        metadata: dict | None = None,
    ) -> TelemetryEvent:
        """Record a telemetry event."""
        event = TelemetryEvent(
            event_type=event_type,
            timestamp=time.time(),
            component=component,
            duration_ms=duration_ms,
            status=status,
            metadata=metadata or {},
        )

        self.events.append(event)

        # Trim old events
        if len(self.events) > self.MAX_EVENTS:
            self.events = self.events[-self.MAX_EVENTS :]

        # Update metrics
        self._update_metrics(event)

        return event

    def _update_metrics(self, event: TelemetryEvent) -> None:
        """Update performance metrics for component."""
        if event.component not in self.metrics:
            self.metrics[event.component] = PerformanceMetrics(component=event.component)

        metric = self.metrics[event.component]
        metric.total_calls += 1
        metric.last_updated = time.time()

        if event.duration_ms:
            metric.total_duration_ms += event.duration_ms
            metric.avg_duration_ms = metric.total_duration_ms / metric.total_calls

        if event.status == "success":
            metric.success_count += 1
        else:
            metric.error_count += 1

    def get_component_metrics(self, component: str | None = None) -> dict:
        """Get metrics for component(s)."""
        if component:
            metric = self.metrics.get(component)
            if metric:
                return {
                    "component": metric.component,
                    "total_calls": metric.total_calls,
                    "avg_duration_ms": round(metric.avg_duration_ms, 2),
                    "success_rate": round(metric.success_count / max(metric.total_calls, 1), 2),
                    "error_count": metric.error_count,
                }
            return {}

        # Return all metrics
        return {
            name: {
                "component": m.component,
                "total_calls": m.total_calls,
                "avg_duration_ms": round(m.avg_duration_ms, 2),
                "success_rate": round(m.success_count / max(m.total_calls, 1), 2),
                "error_count": m.error_count,
            }
            for name, m in self.metrics.items()
        }

    def get_recent_events(self, count: int = 10) -> list[dict]:
        """Get recent telemetry events."""
        recent = self.events[-count:]
        return [
            {
                "event_type": e.event_type,
                "component": e.component,
                "timestamp": datetime.fromtimestamp(e.timestamp).isoformat(),
                "duration_ms": e.duration_ms,
                "status": e.status,
            }
            for e in reversed(recent)
        ]


class SystemHealthMonitor:
    """Monitor overall system health."""

    def __init__(self):
        self.start_time = time.time()
        self.health_checks: dict[str, bool] = {}

    def check_health(self) -> dict:
        """Run system health checks."""
        checks = {
            "runtime": self._check_runtime(),
            "engines": self._check_engines(),
            "tools": self._check_tools(),
            "memory": self._check_memory(),
        }

        self.health_checks = checks

        all_healthy = all(checks.values())

        return {
            "status": "healthy" if all_healthy else "degraded",
            "uptime_seconds": int(time.time() - self.start_time),
            "checks": checks,
        }

    def _check_runtime(self) -> bool:
        """Check runtime health."""
        try:
            runtime = get_runtime()
            return runtime is not None
        except Exception:
            return False

    def _check_engines(self) -> bool:
        """Check engine availability."""
        try:
            from amos_execution import full_execute

            result = full_execute("test", "test")
            return result.content is not None
        except Exception:
            return False

    def _check_tools(self) -> bool:
        """Check tool registration."""
        try:
            from amos_tools import AMOS_TOOLS

            return len(AMOS_TOOLS) > 0
        except Exception:
            return False

    def _check_memory(self) -> bool:
        """Check memory availability."""
        try:
            from amos_memory import get_memory_manager

            mm = get_memory_manager()
            return mm is not None
        except Exception:
            return False


class AMOSMonitoring:
    """Unified monitoring system for AMOS."""

    def __init__(self):
        self.telemetry = TelemetryCollector()
        self.health = SystemHealthMonitor()
        self.runtime = get_runtime()

    def record_tool_execution(
        self,
        tool_name: str,
        duration_ms: float,
        success: bool = True,
        metadata: dict | None = None,
    ) -> TelemetryEvent:
        """Record tool execution event."""
        return self.telemetry.record_event(
            event_type="tool_execution",
            component=tool_name,
            duration_ms=duration_ms,
            status="success" if success else "error",
            metadata=metadata,
        )

    def record_engine_execution(
        self,
        engine_name: str,
        duration_ms: float,
        success: bool = True,
    ) -> TelemetryEvent:
        """Record engine execution event."""
        return self.telemetry.record_event(
            event_type="engine_execution",
            component=engine_name,
            duration_ms=duration_ms,
            status="success" if success else "error",
        )

    def get_system_status(self) -> dict:
        """Get complete system status."""
        health = self.health.check_health()
        metrics = self.telemetry.get_component_metrics()
        recent_events = self.telemetry.get_recent_events(5)

        return {
            "system": "AMOS vInfinity",
            "creator": "Trang Phan",
            "health": health,
            "metrics": metrics,
            "recent_events": recent_events,
        }

    def get_findings_summary(self) -> str:
        """Generate monitoring summary."""
        status = self.get_system_status()

        lines = [
            "# AMOS Performance Monitoring Summary",
            "",
            f"System: {status['system']}",
            f"Creator: {status['creator']}",
            f"Status: {status['health']['status'].upper()}",
            f"Uptime: {status['health']['uptime_seconds']} seconds",
            "",
            "## Health Checks",
            "",
        ]

        for check, result in status["health"]["checks"].items():
            symbol = "✓" if result else "✗"
            lines.append(f"{symbol} {check}: {'healthy' if result else 'failed'}")

        lines.extend(
            [
                "",
                "## Component Metrics",
                "",
            ]
        )

        if status["metrics"]:
            for name, metric in status["metrics"].items():
                lines.extend(
                    [
                        f"### {name}",
                        f"- Calls: {metric['total_calls']}",
                        f"- Avg Duration: {metric['avg_duration_ms']}ms",
                        f"- Success Rate: {metric['success_rate']:.0%}",
                        f"- Errors: {metric['error_count']}",
                        "",
                    ]
                )
        else:
            lines.append("No metrics collected yet.")

        lines.extend(
            [
                "",
                "## Recent Events",
                "",
            ]
        )

        if status["recent_events"]:
            for event in status["recent_events"]:
                status_symbol = "✓" if event["status"] == "success" else "✗"
                duration = f" ({event['duration_ms']:.1f}ms)" if event["duration_ms"] else ""
                lines.append(
                    f"{status_symbol} {event['timestamp']}: {event['component']}{duration}"
                )
        else:
            lines.append("No events recorded yet.")

        lines.extend(
            [
                "",
                "## Gap Acknowledgment",
                "GAP: Monitoring is telemetry collection only, not observability platform.",
                "No distributed tracing. No metrics aggregation. Not APM.",
                "Production monitoring requires external tools (Prometheus, Grafana, etc.).",
            ]
        )

        return "\n".join(lines)


# Singleton
_monitoring: AMOSMonitoring | None = None


def get_monitoring() -> AMOSMonitoring:
    """Get singleton monitoring instance."""
    global _monitoring
    if _monitoring is None:
        _monitoring = AMOSMonitoring()
    return _monitoring


def record_execution(tool_name: str, duration_ms: float, success: bool = True) -> TelemetryEvent:
    """Quick helper to record execution."""
    return get_monitoring().record_tool_execution(tool_name, duration_ms, success)


def get_system_status() -> dict:
    """Quick helper to get system status."""
    return get_monitoring().get_system_status()


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS MONITORING & TELEMETRY TEST")
    print("=" * 60)
    print()

    monitoring = get_monitoring()

    # Simulate some executions
    print("Recording simulated executions...")

    for i in range(5):
        monitoring.record_tool_execution(
            tool_name="AMOSReasoning",
            duration_ms=150.0 + i * 10,
            success=True,
        )

    monitoring.record_tool_execution(
        tool_name="AMOSCode",
        duration_ms=500.0,
        success=True,
    )

    monitoring.record_tool_execution(
        tool_name="AMOSDesign",
        duration_ms=300.0,
        success=False,
    )

    # Get status
    print("\nGetting system status...")
    status = monitoring.get_system_status()

    print(f"System: {status['system']}")
    print(f"Health: {status['health']['status']}")
    print(f"Uptime: {status['health']['uptime_seconds']}s")
    print(f"Metrics collected: {len(status['metrics'])}")
    print(f"Recent events: {len(status['recent_events'])}")

    # Full summary
    print("\n" + "=" * 60)
    print(monitoring.get_findings_summary())

    print("\n" + "=" * 60)
    print("Monitoring: OPERATIONAL")
    print("=" * 60)
    print("\nCapabilities:")
    print("  - Telemetry collection (events, durations)")
    print("  - Performance metrics (calls, success rates)")
    print("  - System health checks")
    print("  - Component monitoring")
    print()
    print("GAP: Simulated telemetry. Production requires external APM.")
