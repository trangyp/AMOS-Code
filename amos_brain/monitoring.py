from __future__ import annotations

from typing import Any, Optional

"""AMOS Brain Monitoring - Production monitoring and metrics.

Provides health checks, metrics collection, and monitoring for
brain operations in production environments.
"""


import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc



@dataclass
class BrainMetrics:
    """Brain performance metrics."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time_ms: float = 0.0
    active_sessions: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class HealthStatus:
    """Brain health status."""

    status: str = "unknown"
    healthy: bool = False
    last_check: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checks: dict[str, bool] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)


class BrainMonitor:
    """Production monitoring for brain operations."""

    def __init__(self) -> None:
        self._metrics = BrainMetrics()
        self._start_time = time.time()
        self._request_times: list[float] = []
        self._max_history = 1000

    def record_request(self, success: bool, response_time_ms: float) -> None:
        """Record a request metric."""
        self._metrics.total_requests += 1

        if success:
            self._metrics.successful_requests += 1
        else:
            self._metrics.failed_requests += 1

        # Track response times for averaging
        self._request_times.append(response_time_ms)
        if len(self._request_times) > self._max_history:
            self._request_times = self._request_times[-self._max_history :]

        # Calculate average
        if self._request_times:
            self._metrics.average_response_time_ms = sum(self._request_times) / len(
                self._request_times
            )

        self._metrics.timestamp = datetime.now(timezone.utc).isoformat()

    def get_metrics(self) -> BrainMetrics:
        """Get current metrics."""
        return self._metrics

    def health_check(self) -> HealthStatus:
        """Perform health check."""
        from .facade import BrainClient

        checks: dict[str, bool] = {}

        # Check brain client
        try:
            BrainClient()
            checks["brain_client"] = True
        except Exception:
            checks["brain_client"] = False

        # Check if we have recent successful requests
        checks["recent_activity"] = self._metrics.total_requests > 0

        # Overall health
        healthy = all(checks.values())

        uptime_seconds = time.time() - self._start_time

        return HealthStatus(
            status="healthy" if healthy else "unhealthy",
            healthy=healthy,
            checks=checks,
            details={
                "uptime_seconds": uptime_seconds,
                "total_requests": self._metrics.total_requests,
                "version": "2.0.0",
            },
        )


# Global monitor instance
_monitor: Optional[BrainMonitor] = None


def get_monitor() -> BrainMonitor:
    """Get or create global monitor."""
    global _monitor
    if _monitor is None:
        _monitor = BrainMonitor()
    return _monitor


def record_brain_request(success: bool, response_time_ms: float) -> None:
    """Record a brain request metric."""
    monitor = get_monitor()
    monitor.record_request(success, response_time_ms)


def get_brain_health() -> HealthStatus:
    """Get brain health status."""
    monitor = get_monitor()
    return monitor.health_check()
