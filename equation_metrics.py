#!/usr/bin/env python3
"""AMOS Equation Metrics - Prometheus Metrics for FastAPI.

Production metrics collection with Prometheus integration.
Tracks request latency, counts, sizes, and custom business metrics.

Features:
    - HTTP request latency histograms
    - Request/response size tracking
    - In-flight request gauges
    - Business metric counters (equations solved, verifications)
    - Custom metric registration
    - Metrics endpoint for Prometheus scraping

Endpoints:
    GET /metrics - Prometheus scrape endpoint

Usage:
    from equation_metrics import instrumentator
    instrumentator.instrument(app).expose(app)

Environment Variables:
    ENABLE_METRICS: Enable metrics collection (default: true)
    METRICS_PORT: Port for metrics endpoint (default: 8000)
"""

from __future__ import annotations

import os
import time
from typing import Any, Optional

try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    from fastapi import FastAPI, Request, Response
    from fastapi.responses import PlainTextResponse

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Configuration
_ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
_METRICS_PATH = os.getenv("METRICS_PATH", "/metrics")


class MetricsCollector:
    """Prometheus metrics collector for AMOS Equation API."""

    def __init__(self) -> None:
        """Initialize metrics collector."""
        if not PROMETHEUS_AVAILABLE:
            raise ImportError("prometheus-client required for metrics")

        # HTTP request metrics
        self.http_requests_total = Counter(
            "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"]
        )

        self.http_request_duration_seconds = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration",
            ["method", "endpoint"],
            buckets=[
                0.001,
                0.005,
                0.01,
                0.025,
                0.05,
                0.075,
                0.1,
                0.25,
                0.5,
                0.75,
                1.0,
                2.5,
                5.0,
                7.5,
                10.0,
            ],
        )

        self.http_request_size_bytes = Histogram(
            "http_request_size_bytes",
            "HTTP request size",
            ["method", "endpoint"],
            buckets=[100, 1000, 10000, 100000, 1000000],
        )

        self.http_response_size_bytes = Histogram(
            "http_response_size_bytes",
            "HTTP response size",
            ["method", "endpoint"],
            buckets=[100, 1000, 10000, 100000, 1000000],
        )

        # In-flight requests gauge
        self.http_requests_in_flight = Gauge(
            "http_requests_in_flight", "Current in-flight HTTP requests", ["method", "endpoint"]
        )

        # Business metrics
        self.equations_solved_total = Counter(
            "amos_equations_solved_total", "Total equations solved", ["equation_type", "status"]
        )

        self.equation_verifications_total = Counter(
            "amos_equation_verifications_total", "Total equation verifications", ["result"]
        )

        self.equation_validation_errors_total = Counter(
            "amos_equation_validation_errors_total", "Total validation errors", ["error_type"]
        )

        # Circuit breaker metrics
        self.circuit_breaker_state_changes = Counter(
            "amos_circuit_breaker_state_changes_total",
            "Circuit breaker state changes",
            ["breaker_name", "from_state", "to_state"],
        )

        self.circuit_breaker_failures = Counter(
            "amos_circuit_breaker_failures_total",
            "Circuit breaker recorded failures",
            ["breaker_name"],
        )

        # Cache metrics
        self.cache_hits = Counter("amos_cache_hits_total", "Cache hits", ["cache_type"])

        self.cache_misses = Counter("amos_cache_misses_total", "Cache misses", ["cache_type"])

        # Task queue metrics
        self.tasks_submitted_total = Counter(
            "amos_tasks_submitted_total", "Tasks submitted to queue", ["task_type"]
        )

        self.tasks_completed_total = Counter(
            "amos_tasks_completed_total", "Tasks completed", ["task_type", "status"]
        )

        self.task_duration_seconds = Histogram(
            "amos_task_duration_seconds",
            "Task execution duration",
            ["task_type"],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
        )

        # GraphQL metrics
        self.graphql_queries_total = Counter(
            "amos_graphql_queries_total", "GraphQL queries executed", ["operation_type"]
        )

        self.graphql_subscriptions_active = Gauge(
            "amos_graphql_subscriptions_active", "Active GraphQL subscriptions"
        )

        # Rate limiting metrics
        self.rate_limit_hits = Counter(
            "amos_rate_limit_hits_total", "Rate limit hits", ["endpoint", "client_id"]
        )

        # WebSocket metrics
        self.websocket_connections_active = Gauge(
            "amos_websocket_connections_active", "Active WebSocket connections"
        )

        self.websocket_messages_sent = Counter(
            "amos_websocket_messages_sent_total", "WebSocket messages sent", ["message_type"]
        )

    def track_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        request_size: int = 0,
        response_size: int = 0,
    ) -> None:
        """Track HTTP request metrics.

        Args:
            method: HTTP method
            endpoint: Request endpoint path
            status_code: HTTP status code
            duration: Request duration in seconds
            request_size: Request body size in bytes
            response_size: Response body size in bytes
        """
        if not _ENABLE_METRICS:
            return

        self.http_requests_total.labels(
            method=method, endpoint=endpoint, status_code=str(status_code)
        ).inc()

        self.http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(
            duration
        )

        if request_size > 0:
            self.http_request_size_bytes.labels(method=method, endpoint=endpoint).observe(
                request_size
            )

        if response_size > 0:
            self.http_response_size_bytes.labels(method=method, endpoint=endpoint).observe(
                response_size
            )

    def increment_in_flight(self, method: str, endpoint: str) -> None:
        """Increment in-flight request counter.

        Args:
            method: HTTP method
            endpoint: Request endpoint
        """
        if _ENABLE_METRICS:
            self.http_requests_in_flight.labels(method=method, endpoint=endpoint).inc()

    def decrement_in_flight(self, method: str, endpoint: str) -> None:
        """Decrement in-flight request counter.

        Args:
            method: HTTP method
            endpoint: Request endpoint
        """
        if _ENABLE_METRICS:
            self.http_requests_in_flight.labels(method=method, endpoint=endpoint).dec()

    def record_equation_solved(self, equation_type: str, success: bool = True) -> None:
        """Record equation solved metric.

        Args:
            equation_type: Type of equation solved
            success: Whether solve was successful
        """
        if _ENABLE_METRICS:
            status = "success" if success else "failure"
            self.equations_solved_total.labels(equation_type=equation_type, status=status).inc()

    def record_verification(self, valid: bool = True) -> None:
        """Record equation verification metric.

        Args:
            valid: Whether equation was valid
        """
        if _ENABLE_METRICS:
            result = "valid" if valid else "invalid"
            self.equation_verifications_total.labels(result=result).inc()

    def record_validation_error(self, error_type: str) -> None:
        """Record validation error metric.

        Args:
            error_type: Type of validation error
        """
        if _ENABLE_METRICS:
            self.equation_validation_errors_total.labels(error_type=error_type).inc()

    def record_circuit_breaker_state_change(
        self, breaker_name: str, from_state: str, to_state: str
    ) -> None:
        """Record circuit breaker state change.

        Args:
            breaker_name: Name of circuit breaker
            from_state: Previous state
            to_state: New state
        """
        if _ENABLE_METRICS:
            self.circuit_breaker_state_changes.labels(
                breaker_name=breaker_name, from_state=from_state, to_state=to_state
            ).inc()

    def record_circuit_breaker_failure(self, breaker_name: str) -> None:
        """Record circuit breaker failure.

        Args:
            breaker_name: Name of circuit breaker
        """
        if _ENABLE_METRICS:
            self.circuit_breaker_failures.labels(breaker_name=breaker_name).inc()

    def record_cache_hit(self, cache_type: str = "redis") -> None:
        """Record cache hit.

        Args:
            cache_type: Type of cache
        """
        if _ENABLE_METRICS:
            self.cache_hits.labels(cache_type=cache_type).inc()

    def record_cache_miss(self, cache_type: str = "redis") -> None:
        """Record cache miss.

        Args:
            cache_type: Type of cache
        """
        if _ENABLE_METRICS:
            self.cache_misses.labels(cache_type=cache_type).inc()

    def record_task_submitted(self, task_type: str) -> None:
        """Record task submission.

        Args:
            task_type: Type of task
        """
        if _ENABLE_METRICS:
            self.tasks_submitted_total.labels(task_type=task_type).inc()

    def record_task_completed(self, task_type: str, duration: float, success: bool = True) -> None:
        """Record task completion.

        Args:
            task_type: Type of task
            duration: Task duration in seconds
            success: Whether task succeeded
        """
        if _ENABLE_METRICS:
            status = "success" if success else "failure"
            self.tasks_completed_total.labels(task_type=task_type, status=status).inc()
            self.task_duration_seconds.labels(task_type=task_type).observe(duration)

    def record_graphql_query(self, operation_type: str = "query") -> None:
        """Record GraphQL query.

        Args:
            operation_type: Type of operation (query/mutation/subscription)
        """
        if _ENABLE_METRICS:
            self.graphql_queries_total.labels(operation_type=operation_type).inc()

    def update_graphql_subscriptions(self, count: int) -> None:
        """Update active subscription count.

        Args:
            count: Current subscription count
        """
        if _ENABLE_METRICS:
            self.graphql_subscriptions_active.set(count)

    def record_rate_limit_hit(self, endpoint: str, client_id: str) -> None:
        """Record rate limit hit.

        Args:
            endpoint: Endpoint that was rate limited
            client_id: Client identifier
        """
        if _ENABLE_METRICS:
            self.rate_limit_hits.labels(endpoint=endpoint, client_id=client_id).inc()

    def update_websocket_connections(self, count: int) -> None:
        """Update active WebSocket connection count.

        Args:
            count: Current connection count
        """
        if _ENABLE_METRICS:
            self.websocket_connections_active.set(count)

    def record_websocket_message(self, message_type: str) -> None:
        """Record WebSocket message sent.

        Args:
            message_type: Type of message
        """
        if _ENABLE_METRICS:
            self.websocket_messages_sent.labels(message_type=message_type).inc()


# Global metrics instance
_metrics: Optional[MetricsCollector] = None


def get_metrics() -> MetricsCollector:
    """Get or create metrics collector instance."""
    global _metrics
    if _metrics is None and PROMETHEUS_AVAILABLE:
        _metrics = MetricsCollector()
    if _metrics is None:
        raise ImportError("prometheus-client not available")
    return _metrics


class MetricsMiddleware:
    """FastAPI middleware for automatic metrics collection."""

    def __init__(self, app: Any) -> None:
        """Initialize middleware."""
        self.app = app
        self.metrics = get_metrics() if PROMETHEUS_AVAILABLE else None

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        """Process request with metrics collection."""
        if scope["type"] != "http" or not self.metrics:
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "GET")
        path = scope.get("path", "/")

        # Skip metrics endpoint
        if path == _METRICS_PATH:
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        self.metrics.increment_in_flight(method, path)

        # Capture response info
        status_code = 200
        response_size = 0

        async def wrapped_send(message: Any) -> None:
            nonlocal status_code, response_size
            if message["type"] == "http.response.start":
                status_code = message.get("status", 200)
            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                response_size = len(body)
            await send(message)

        try:
            await self.app(scope, receive, wrapped_send)
        finally:
            duration = time.time() - start_time
            self.metrics.decrement_in_flight(method, path)
            self.metrics.track_request(
                method=method,
                endpoint=path,
                status_code=status_code,
                duration=duration,
                response_size=response_size,
            )


def create_metrics_endpoint(app: Optional[FastAPI] = None) -> Any:
    """Create metrics endpoint handler.

    Args:
        app: Optional FastAPI app to add endpoint to

    Returns:
        Endpoint handler or None
    """
    if not PROMETHEUS_AVAILABLE or not FASTAPI_AVAILABLE:
        return None

    async def metrics_handler(request: Request) -> Response:
        """Handle metrics scrape request."""
        metrics_data = generate_latest()
        return PlainTextResponse(
            content=metrics_data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST
        )

    if app:
        app.add_route(_METRICS_PATH, metrics_handler)

    return metrics_handler


def instrument_app(app: Any) -> Any:
    """Instrument FastAPI app with metrics.

    Args:
        app: FastAPI application

    Returns:
        Instrumented app
    """
    if not PROMETHEUS_AVAILABLE or not _ENABLE_METRICS:
        return app

    # Add middleware
    app.add_middleware(MetricsMiddleware)

    # Add metrics endpoint
    create_metrics_endpoint(app)

    return app


# Convenience functions for direct metric recording
def record_equation_solved(equation_type: str, success: bool = True) -> None:
    """Record equation solved."""
    if PROMETHEUS_AVAILABLE and _ENABLE_METRICS:
        get_metrics().record_equation_solved(equation_type, success)


def record_verification(valid: bool = True) -> None:
    """Record verification."""
    if PROMETHEUS_AVAILABLE and _ENABLE_METRICS:
        get_metrics().record_verification(valid)


def record_cache_hit(cache_type: str = "redis") -> None:
    """Record cache hit."""
    if PROMETHEUS_AVAILABLE and _ENABLE_METRICS:
        get_metrics().record_cache_hit(cache_type)


def record_cache_miss(cache_type: str = "redis") -> None:
    """Record cache miss."""
    if PROMETHEUS_AVAILABLE and _ENABLE_METRICS:
        get_metrics().record_cache_miss(cache_type)


def record_task_completed(task_type: str, duration: float, success: bool = True) -> None:
    """Record task completion."""
    if PROMETHEUS_AVAILABLE and _ENABLE_METRICS:
        get_metrics().record_task_completed(task_type, duration, success)


def record_graphql_query(operation_type: str = "query") -> None:
    """Record GraphQL query."""
    if PROMETHEUS_AVAILABLE and _ENABLE_METRICS:
        get_metrics().record_graphql_query(operation_type)


def record_rate_limit_hit(endpoint: str, client_id: str) -> None:
    """Record rate limit hit."""
    if PROMETHEUS_AVAILABLE and _ENABLE_METRICS:
        get_metrics().record_rate_limit_hit(endpoint, client_id)


# Prometheus instrumentation singleton
class PrometheusInstrumentator:
    """Prometheus instrumentation for FastAPI applications."""

    def __init__(self) -> None:
        """Initialize instrumentator."""
        self.metrics = None

    def instrument(self, app: Any) -> PrometheusInstrumentator:
        """Instrument a FastAPI application.

        Args:
            app: FastAPI application instance

        Returns:
            Self for chaining
        """
        if PROMETHEUS_AVAILABLE and FASTAPI_AVAILABLE:
            self.metrics = get_metrics()
            # Add middleware
            app.add_middleware(MetricsMiddleware)
        return self

    def expose(self, app: Any, path: str = "/metrics") -> PrometheusInstrumentator:
        """Expose metrics endpoint.

        Args:
            app: FastAPI application instance
            path: Endpoint path for metrics

        Returns:
            Self for chaining
        """
        if PROMETHEUS_AVAILABLE and FASTAPI_AVAILABLE:
            from fastapi.responses import PlainTextResponse

            @app.get(path)
            async def metrics_endpoint() -> Response:
                """Prometheus metrics endpoint."""
                from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

                return PlainTextResponse(
                    content=generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST
                )

        return self


# Global instrumentator instance
instrumentator = PrometheusInstrumentator()
