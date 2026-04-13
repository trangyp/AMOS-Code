"""Metrics collection for AMOS local runtime.

Tracks latency, errors, token usage, and backend health for
operational visibility.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    backend: str
    model: str
    start_time: float
    end_time: float = 0.0
    success: bool = False
    error_type: str = ""
    tokens_generated: int = 0
    first_token_latency: float = 0.0

    @property
    def latency_ms(self) -> float:
        """Total request latency in milliseconds."""
        if self.end_time > self.start_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0


@dataclass
class BackendMetrics:
    """Aggregated metrics for a backend."""
    backend: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    errors: dict[str, int] = field(default_factory=dict)

    @property
    def avg_latency_ms(self) -> float:
        """Average latency per request."""
        if self.total_requests > 0:
            return self.total_latency_ms / self.total_requests
        return 0.0

    @property
    def success_rate(self) -> float:
        """Percentage of successful requests."""
        if self.total_requests > 0:
            return self.successful_requests / self.total_requests
        return 0.0


class MetricsCollector:
    """Collect and aggregate metrics for AMOS local runtime.

    Tracks per-request metrics and provides aggregated statistics
    for operational visibility and debugging.
    """

    def __init__(self):
        self._request_history: list[RequestMetrics] = []
        self._backend_stats: dict[str, BackendMetrics] = {}
        self._max_history = 1000

    def start_request(self, backend: str, model: str) -> RequestMetrics:
        """Start tracking a new request.

        Args:
            backend: Backend type (ollama, lmstudio, etc.)
            model: Model name being used

        Returns:
            RequestMetrics object to be completed on request end
        """
        return RequestMetrics(
            backend=backend,
            model=model,
            start_time=time.time(),
        )

    def end_request(
        self,
        metrics: RequestMetrics,
        success: bool,
        error_type: str = "",
        tokens: int = 0,
    ) -> None:
        """Complete request tracking and record metrics.

        Args:
            metrics: RequestMetrics from start_request()
            success: Whether request succeeded
            error_type: Type of error if failed
            tokens: Number of tokens generated
        """
        metrics.end_time = time.time()
        metrics.success = success
        metrics.error_type = error_type
        metrics.tokens_generated = tokens

        # Add to history
        self._request_history.append(metrics)
        if len(self._request_history) > self._max_history:
            self._request_history.pop(0)

        # Update backend stats
        backend = metrics.backend
        if backend not in self._backend_stats:
            self._backend_stats[backend] = BackendMetrics(backend=backend)

        stats = self._backend_stats[backend]
        stats.total_requests += 1
        stats.total_latency_ms += metrics.latency_ms

        if success:
            stats.successful_requests += 1
        else:
            stats.failed_requests += 1
            if error_type:
                stats.errors[error_type] = stats.errors.get(error_type, 0) + 1

    def get_summary(self) -> dict[str, Any]:
        """Get summary of all collected metrics.

        Returns:
            Dict with overall and per-backend statistics
        """
        total_requests = len(self._request_history)
        if total_requests == 0:
            return {"status": "no_data"}

        total_latency = sum(r.latency_ms for r in self._request_history)
        successful = sum(
            1 for r in self._request_history if r.success
        )

        # Calculate percentiles
        latencies = sorted(
            r.latency_ms for r in self._request_history
        )
        p50 = latencies[len(latencies) // 2] if latencies else 0
        p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0

        return {
            "total_requests": total_requests,
            "successful": successful,
            "failed": total_requests - successful,
            "success_rate": successful / total_requests if total_requests else 0,
            "avg_latency_ms": (
                total_latency / total_requests if total_requests else 0
            ),
            "p50_latency_ms": p50,
            "p95_latency_ms": p95,
            "backends": {
                name: {
                    "total": stats.total_requests,
                    "success_rate": stats.success_rate,
                    "avg_latency_ms": stats.avg_latency_ms,
                    "errors": stats.errors,
                }
                for name, stats in self._backend_stats.items()
            },
        }

    def get_recent_errors(self, count: int = 10) -> list[dict[str, Any]]:
        """Get recent error details.

        Args:
            count: Number of recent errors to return

        Returns:
            List of error details
        """
        errors = [
            {
                "time": r.start_time,
                "backend": r.backend,
                "model": r.model,
                "error": r.error_type,
                "latency_ms": r.latency_ms,
            }
            for r in reversed(self._request_history)
            if not r.success
        ]
        return errors[:count]

    def reset(self) -> None:
        """Clear all collected metrics."""
        self._request_history.clear()
        self._backend_stats.clear()


# Global metrics collector instance
_metrics: MetricsCollector | None = None


def get_metrics() -> MetricsCollector:
    """Get or create global metrics collector."""
    global _metrics
    if _metrics is None:
        _metrics = MetricsCollector()
    return _metrics
