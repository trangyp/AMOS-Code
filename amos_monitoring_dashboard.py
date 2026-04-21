#!/usr/bin/env python3
"""AMOS Monitoring Dashboard - Real-time system monitoring.

WebSocket-based dashboard for monitoring:
- System health
- Component status
- Performance metrics
- Active workflows
- Circuit breaker states
"""

from __future__ import annotations

import asyncio
import json
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class MetricPoint:
    """Single metric data point."""

    timestamp: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class MetricSeries:
    """Time series of metrics."""

    name: str
    unit: str
    data: deque[MetricPoint] = field(default_factory=lambda: deque(maxlen=1000))

    def add(self, value: float, labels: dict[str, str] | None = None) -> None:
        """Add new data point."""
        point = MetricPoint(
            timestamp=datetime.now(timezone.utc).isoformat(),
            value=value,
            labels=labels or {},
        )
        self.data.append(point)


class AMOSMonitoringDashboard:
    """Real-time monitoring dashboard backend."""

    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics: dict[str, MetricSeries] = {}
        self._subscribers: list[Any] = []
        self._running = False
        self._monitor_task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start monitoring."""
        if self._running:
            return

        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        print("[Dashboard] Monitoring started")

    async def stop(self) -> None:
        """Stop monitoring."""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        print("[Dashboard] Monitoring stopped")

    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                # Collect metrics from components
                await self._collect_system_metrics()
                await self._collect_component_metrics()

                # Broadcast to subscribers
                await self._broadcast_update()

                await asyncio.sleep(5)  # Update every 5 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[Dashboard] Monitor error: {e}")
                await asyncio.sleep(1)

    async def _collect_system_metrics(self) -> None:
        """Collect system-level metrics."""
        try:
            import psutil

            # CPU usage
            self._ensure_series("system_cpu_percent", "%")
            self.metrics["system_cpu_percent"].add(psutil.cpu_percent())

            # Memory usage
            self._ensure_series("system_memory_percent", "%")
            self.metrics["system_memory_percent"].add(
                psutil.virtual_memory().percent
            )

            # Disk usage
            self._ensure_series("system_disk_percent", "%")
            self.metrics["system_disk_percent"].add(
                psutil.disk_usage("/").percent
            )
        except ImportError:
            pass

    async def _collect_component_metrics(self) -> None:
        """Collect AMOS component metrics."""
        # Try to get metrics from orchestrator
        try:
            from amos_unified_orchestrator_v2 import get_orchestrator

            orchestrator = await get_orchestrator()
            status = orchestrator.get_status()

            # Task metrics
            self._ensure_series("amos_tasks_submitted", "count")
            self.metrics["amos_tasks_submitted"].add(
                status["stats"]["tasks_submitted"]
            )

            self._ensure_series("amos_tasks_completed", "count")
            self.metrics["amos_tasks_completed"].add(
                status["stats"]["tasks_completed"]
            )

            # Workflow metrics
            self._ensure_series("amos_workflows_executed", "count")
            self.metrics["amos_workflows_executed"].add(
                status["stats"]["workflows_executed"]
            )
        except Exception:
            pass

    def _ensure_series(self, name: str, unit: str) -> None:
        """Ensure metric series exists."""
        if name not in self.metrics:
            self.metrics[name] = MetricSeries(name=name, unit=unit)

    async def _broadcast_update(self) -> None:
        """Broadcast update to all subscribers."""
        if not self._subscribers:
            return

        data = self.get_current_metrics()
        message = json.dumps(data)

        # Send to all subscribers
        disconnected = []
        for subscriber in self._subscribers:
            try:
                if hasattr(subscriber, "send_text"):
                    await subscriber.send_text(message)
                elif hasattr(subscriber, "put"):
                    await subscriber.put(data)
            except Exception:
                disconnected.append(subscriber)

        # Remove disconnected subscribers
        for sub in disconnected:
            self._subscribers.remove(sub)

    def get_current_metrics(self) -> dict[str, Any]:
        """Get current metrics snapshot."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                name: {
                    "unit": series.unit,
                    "latest": (
                        series.data[-1].value if series.data else None
                    ),
                    "count": len(series.data),
                }
                for name, series in self.metrics.items()
            },
        }

    def get_historical_data(
        self,
        metric_name: str,
        limit: int = 100,
    ) -> list[dict[str, Any]] | None:
        """Get historical data for a metric."""
        if metric_name not in self.metrics:
            return None

        series = self.metrics[metric_name]
        data = list(series.data)[-limit:]

        return [
            {
                "timestamp": point.timestamp,
                "value": point.value,
                "labels": point.labels,
            }
            for point in data
        ]

    def subscribe(self, subscriber: Any) -> None:
        """Add a subscriber."""
        self._subscribers.append(subscriber)

    def unsubscribe(self, subscriber: Any) -> None:
        """Remove a subscriber."""
        if subscriber in self._subscribers:
            self._subscribers.remove(subscriber)


# Global dashboard instance
_dashboard: AMOSMonitoringDashboard | None = None


async def get_dashboard() -> AMOSMonitoringDashboard:
    """Get global dashboard instance."""
    global _dashboard
    if _dashboard is None:
        _dashboard = AMOSMonitoringDashboard()
    return _dashboard


# FastAPI WebSocket endpoint
async def dashboard_websocket(websocket):
    """WebSocket endpoint for dashboard."""
    dashboard = await get_dashboard()
    dashboard.subscribe(websocket)

    try:
        # Send initial data
        await websocket.send_json(dashboard.get_current_metrics())

        # Keep connection open
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("action") == "get_history":
                metric = message.get("metric")
                history = dashboard.get_historical_data(metric)
                await websocket.send_json({
                    "metric": metric,
                    "history": history,
                })
    except Exception:
        pass
    finally:
        dashboard.unsubscribe(websocket)


if __name__ == "__main__":
    # Run standalone for testing
    async def test():
        dashboard = await get_dashboard()
        await dashboard.start()

        print("Dashboard running. Press Ctrl+C to stop.")
        while True:
            print(json.dumps(dashboard.get_current_metrics(), indent=2))
            await asyncio.sleep(10)

    asyncio.run(test())
