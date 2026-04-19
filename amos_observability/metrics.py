"""Custom metrics for AMOS Equation API analytics."""

import time
from collections import defaultdict
from typing import Any

try:
    from opentelemetry.metrics import Counter, Histogram, UpDownCounter

    from .telemetry import get_meter

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False


class EquationMetrics:
    """Metrics collector for equation usage analytics."""

    def __init__(self) -> None:
        self._meter = get_meter() if OTEL_AVAILABLE else None
        self._counters: Dict[str, Any] = {}
        self._histograms: Dict[str, Any] = {}

        if OTEL_AVAILABLE and self._meter:
            self._init_metrics()

    def _init_metrics(self) -> None:
        """Initialize OpenTelemetry metrics instruments."""
        # Counters
        self._counters["equation_calls"] = self._meter.create_counter(
            "amos.equation.calls",
            description="Total number of equation computation calls",
            unit="1",
        )

        self._counters["equation_errors"] = self._meter.create_counter(
            "amos.equation.errors",
            description="Total number of equation computation errors",
            unit="1",
        )

        self._counters["equation_cache_hits"] = self._meter.create_counter(
            "amos.equation.cache_hits",
            description="Number of cache hits for equation results",
            unit="1",
        )

        # Histograms
        self._histograms["equation_duration"] = self._meter.create_histogram(
            "amos.equation.duration", description="Time taken to compute equations", unit="ms"
        )

        self._histograms["equation_batch_size"] = self._meter.create_histogram(
            "amos.equation.batch_size",
            description="Number of equations in batch requests",
            unit="1",
        )

        # Domain-specific counters
        self._counters["equation_by_domain"] = defaultdict(int)

    def record_equation_call(
        self, equation_name: str, domain: str, success: bool = True, cached: bool = False
    ) -> None:
        """Record an equation computation call."""
        attributes = {
            "equation.name": equation_name,
            "equation.domain": domain,
            "equation.success": str(success),
        }

        if OTEL_AVAILABLE and self._counters.get("equation_calls"):
            self._counters["equation_calls"].add(1, attributes)

        if not success and OTEL_AVAILABLE and self._counters.get("equation_errors"):
            self._counters["equation_errors"].add(1, attributes)

        if cached and OTEL_AVAILABLE and self._counters.get("equation_cache_hits"):
            self._counters["equation_cache_hits"].add(1, attributes)

        # Track domain usage
        self._counters["equation_by_domain"][domain] += 1

    def record_duration(self, equation_name: str, duration_ms: float) -> None:
        """Record computation duration."""
        attributes = {"equation.name": equation_name}

        if OTEL_AVAILABLE and self._histograms.get("equation_duration"):
            self._histograms["equation_duration"].record(duration_ms, attributes)

    def record_batch_size(self, size: int) -> None:
        """Record batch request size."""
        if OTEL_AVAILABLE and self._histograms.get("equation_batch_size"):
            self._histograms["equation_batch_size"].record(size)

    def get_domain_stats(self) -> dict[str, int]:
        """Get equation call statistics by domain."""
        return dict(self._counters.get("equation_by_domain", {}))


class PerformanceMetrics:
    """System performance metrics collector."""

    def __init__(self) -> None:
        self._meter = get_meter() if OTEL_AVAILABLE else None
        self._counters: Dict[str, Any] = {}
        self._up_down_counters: Dict[str, Any] = {}
        self._histograms: Dict[str, Any] = {}

        if OTEL_AVAILABLE and self._meter:
            self._init_metrics()

    def _init_metrics(self) -> None:
        """Initialize performance metrics instruments."""
        # Active requests
        self._up_down_counters["active_requests"] = self._meter.create_up_down_counter(
            "amos.http.active_requests", description="Number of active HTTP requests", unit="1"
        )

        # Request duration
        self._histograms["request_duration"] = self._meter.create_histogram(
            "amos.http.request_duration", description="HTTP request duration", unit="ms"
        )

        # Response size
        self._histograms["response_size"] = self._meter.create_histogram(
            "amos.http.response_size", description="HTTP response size in bytes", unit="By"
        )

        # Rate limiting
        self._counters["rate_limited"] = self._meter.create_counter(
            "amos.http.rate_limited", description="Number of rate-limited requests", unit="1"
        )

    def start_request(self) -> None:
        """Mark start of request."""
        if OTEL_AVAILABLE and self._up_down_counters.get("active_requests"):
            self._up_down_counters["active_requests"].add(1)

    def end_request(
        self, duration_ms: float, status_code: int, response_size_bytes: int = 0
    ) -> None:
        """Mark end of request with metrics."""
        if OTEL_AVAILABLE and self._up_down_counters.get("active_requests"):
            self._up_down_counters["active_requests"].add(-1)

        attributes = {"http.status_code": str(status_code)}

        if OTEL_AVAILABLE and self._histograms.get("request_duration"):
            self._histograms["request_duration"].record(duration_ms, attributes)

        if response_size_bytes and OTEL_AVAILABLE and self._histograms.get("response_size"):
            self._histograms["response_size"].record(response_size_bytes, attributes)

    def record_rate_limited(self, client_ip: str) -> None:
        """Record rate-limited request."""
        attributes = {"client.ip": client_ip}

        if OTEL_AVAILABLE and self._counters.get("rate_limited"):
            self._counters["rate_limited"].add(1, attributes)


class MetricsContext:
    """Context manager for timing operations."""

    def __init__(self, metrics: EquationMetrics, equation_name: str, domain: str) -> None:
        self.metrics = metrics
        self.equation_name = equation_name
        self.domain = domain
        self.start_time: float = 0.0
        self.success = True

    def __enter__(self) -> MetricsContext:
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        duration_ms = (time.perf_counter() - self.start_time) * 1000

        if exc_type is not None:
            self.success = False

        self.metrics.record_equation_call(self.equation_name, self.domain, success=self.success)
        self.metrics.record_duration(self.equation_name, duration_ms)
