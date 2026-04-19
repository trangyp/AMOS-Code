#!/usr/bin/env python3
"""AMOS Metrics Exporter - Prometheus Integration (Phase 14)
==============================================================

Enterprise observability system integrating Prometheus metrics,
custom AMOS-specific metrics, and health monitoring correlation.

Features:
- Prometheus metrics endpoint (/metrics)
- Custom AMOS metrics (health score, equations, API latency)
- Health monitoring correlation
- Performance tracking
- Business metrics (equation execution count, success rates)

Architecture Pattern: Prometheus Client + FastAPI
Based on: Prometheus Best Practices 2024

Metrics Exposed:
  - amos_health_score - Current system health score (0-100)
  - amos_equation_executions_total - Total equation executions
  - amos_equation_execution_duration - Execution time histogram
  - amos_api_requests_total - API request counter
  - amos_api_request_duration - API latency histogram
  - amos_active_runtime - Runtime active state
  - amos_selfhealing_recovery_attempts - Recovery attempts
  - amos_bootstrap_phase - Current bootstrap phase

Owner: Trang
Version: 1.0.0
Phase: 14
"""

import time
from contextlib import contextmanager
from typing import Any

# Prometheus client
try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        CollectorRegistry,
        Counter,
        Gauge,
        Histogram,
        Info,
        generate_latest,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("prometheus_client not installed. Metrics disabled.")

# FastAPI
try:
    from fastapi import APIRouter, Response
    from fastapi.responses import PlainTextResponse

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Production runtime integration
try:
    from amos_brain_health_monitor import get_health_monitor
    from amos_production_runtime import AMOSProductionRuntime

    RUNTIME_AVAILABLE = True
except ImportError:
    RUNTIME_AVAILABLE = False


class AMOSMetricsExporter:
    """
    Prometheus metrics exporter for AMOS system.

    Exposes AMOS-specific metrics for monitoring and alerting.
    """

    def __init__(self, registry: Optional[Any] = None):
        if not PROMETHEUS_AVAILABLE:
            self._enabled = False
            return

        self._enabled = True
        self._registry = registry or CollectorRegistry()

        # System info
        self._build_info = Info("amos_build", "AMOS build information", registry=self._registry)
        self._build_info.info({"version": "1.0.0", "phase": "14", "runtime": "production"})

        # Health metrics
        self._health_score = Gauge(
            "amos_health_score", "Current system health score (0-100)", registry=self._registry
        )

        self._subsystem_health = Gauge(
            "amos_subsystem_health",
            "Health status by subsystem",
            ["subsystem"],
            registry=self._registry,
        )

        # Runtime metrics
        self._runtime_active = Gauge(
            "amos_runtime_active",
            "Runtime active state (1=active, 0=inactive)",
            registry=self._registry,
        )

        self._bootstrap_phase = Gauge(
            "amos_bootstrap_phase", "Current bootstrap phase (0-5)", registry=self._registry
        )

        # Equation metrics
        self._equation_executions = Counter(
            "amos_equation_executions_total",
            "Total equation executions",
            ["name", "status"],
            registry=self._registry,
        )

        self._equation_duration = Histogram(
            "amos_equation_execution_duration_seconds",
            "Equation execution time",
            ["name"],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
            registry=self._registry,
        )

        # API metrics
        self._api_requests = Counter(
            "amos_api_requests_total",
            "Total API requests",
            ["method", "endpoint", "status"],
            registry=self._registry,
        )

        self._api_duration = Histogram(
            "amos_api_request_duration_seconds",
            "API request duration",
            ["method", "endpoint"],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self._registry,
        )

        self._api_active_requests = Gauge(
            "amos_api_active_requests", "Currently active API requests", registry=self._registry
        )

        # Self-healing metrics
        self._recovery_attempts = Counter(
            "amos_selfhealing_recovery_attempts_total",
            "Total recovery attempts",
            ["strategy"],
            registry=self._registry,
        )

        self._recovery_success = Counter(
            "amos_selfhealing_recovery_success_total",
            "Successful recoveries",
            ["strategy"],
            registry=self._registry,
        )

        self._escalation_level = Gauge(
            "amos_selfhealing_escalation_level", "Current escalation level", registry=self._registry
        )

        # Auth metrics
        self._auth_attempts = Counter(
            "amos_auth_attempts_total",
            "Authentication attempts",
            ["method", "result"],
            registry=self._registry,
        )

        self._rate_limit_hits = Counter(
            "amos_rate_limit_hits_total", "Rate limit hits", ["key_id"], registry=self._registry
        )

        # WebSocket metrics
        self._websocket_connections = Gauge(
            "amos_websocket_connections", "Active WebSocket connections", registry=self._registry
        )

        self._websocket_messages = Counter(
            "amos_websocket_messages_total", "WebSocket messages sent", registry=self._registry
        )

    def is_enabled(self) -> bool:
        """Check if metrics are enabled."""
        return self._enabled

    # ============================================
    # Metric Recording Methods
    # ============================================

    def record_health_score(self, score: float) -> None:
        """Record current health score."""
        if self._enabled:
            self._health_score.set(score)

    def record_subsystem_health(self, subsystem: str, healthy: bool) -> None:
        """Record subsystem health status."""
        if self._enabled:
            self._subsystem_health.labels(subsystem=subsystem).set(1 if healthy else 0)

    def record_runtime_active(self, active: bool) -> None:
        """Record runtime active state."""
        if self._enabled:
            self._runtime_active.set(1 if active else 0)

    def record_bootstrap_phase(self, phase: int) -> None:
        """Record current bootstrap phase."""
        if self._enabled:
            self._bootstrap_phase.set(phase)

    def record_equation_execution(self, name: str, duration: float, success: bool = True) -> None:
        """Record equation execution metrics."""
        if self._enabled:
            status = "success" if success else "failure"
            self._equation_executions.labels(name=name, status=status).inc()
            self._equation_duration.labels(name=name).observe(duration)

    def record_api_request(self, method: str, endpoint: str, status: int, duration: float) -> None:
        """Record API request metrics."""
        if self._enabled:
            status_class = f"{status // 100}xx"
            self._api_requests.labels(method=method, endpoint=endpoint, status=status_class).inc()
            self._api_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def increment_active_requests(self) -> None:
        """Increment active request count."""
        if self._enabled:
            self._api_active_requests.inc()

    def decrement_active_requests(self) -> None:
        """Decrement active request count."""
        if self._enabled:
            self._api_active_requests.dec()

    @contextmanager
    def track_request(self, method: str, endpoint: str):
        """Context manager to track request duration."""
        if not self._enabled:
            yield
            return

        self.increment_active_requests()
        start = time.time()
        try:
            yield
            status = 200
        except Exception:
            status = 500
            raise
        finally:
            duration = time.time() - start
            self.decrement_active_requests()
            self.record_api_request(method, endpoint, status, duration)

    def record_recovery_attempt(self, strategy: str, success: bool) -> None:
        """Record self-healing recovery attempt."""
        if self._enabled:
            self._recovery_attempts.labels(strategy=strategy).inc()
            if success:
                self._recovery_success.labels(strategy=strategy).inc()

    def record_escalation_level(self, level: int) -> None:
        """Record current escalation level."""
        if self._enabled:
            self._escalation_level.set(level)

    def record_auth_attempt(self, method: str, success: bool) -> None:
        """Record authentication attempt."""
        if self._enabled:
            result = "success" if success else "failure"
            self._auth_attempts.labels(method=method, result=result).inc()

    def record_rate_limit_hit(self, key_id: str) -> None:
        """Record rate limit hit."""
        if self._enabled:
            self._rate_limit_hits.labels(key_id=key_id).inc()

    def record_websocket_connect(self) -> None:
        """Record WebSocket connection."""
        if self._enabled:
            self._websocket_connections.inc()

    def record_websocket_disconnect(self) -> None:
        """Record WebSocket disconnection."""
        if self._enabled:
            self._websocket_connections.dec()

    def record_websocket_message(self) -> None:
        """Record WebSocket message sent."""
        if self._enabled:
            self._websocket_messages.inc()

    # ============================================
    # Metrics Export
    # ============================================

    def get_metrics(self) -> Tuple[str, str]:
        """
        Get metrics in Prometheus format.

        Returns:
            Tuple of (content, content_type)
        """
        if not self._enabled:
            return "# Metrics disabled\n", "text/plain"

        return generate_latest(self._registry).decode(), CONTENT_TYPE_LATEST

    def get_registry(self) -> Any:
        """Get Prometheus registry."""
        return self._registry


# Global exporter instance
_metrics_exporter: Optional[AMOSMetricsExporter] = None


def get_metrics_exporter() -> AMOSMetricsExporter:
    """Get or create global metrics exporter."""
    global _metrics_exporter
    if _metrics_exporter is None:
        _metrics_exporter = AMOSMetricsExporter()
    return _metrics_exporter


# ============================================
# FastAPI Integration
# ============================================


def create_metrics_router() -> APIRouter:
    """Create FastAPI router for metrics endpoint."""
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI not available")

    router = APIRouter(prefix="/metrics", tags=["monitoring"])

    @router.get("", response_class=PlainTextResponse)
    async def metrics():
        """Prometheus metrics endpoint."""
        exporter = get_metrics_exporter()
        content, content_type = exporter.get_metrics()
        return Response(content=content, media_type=content_type)

    @router.get("/health")
    async def metrics_health():
        """Metrics exporter health check."""
        exporter = get_metrics_exporter()
        return {"status": "healthy", "enabled": exporter.is_enabled(), "timestamp": time.time()}

    return router


# ============================================
# Metrics Collection Task
# ============================================


async def collect_system_metrics() -> None:
    """
    Background task to collect system metrics.
    Should be run periodically (e.g., every 30 seconds).
    """
    if not RUNTIME_AVAILABLE:
        return

    try:
        exporter = get_metrics_exporter()

        # Collect from production runtime if available
        # This is a placeholder - in production, you'd get the actual runtime
        # For now, just record that metrics collection ran
        exporter.record_health_score(95.0)  # Placeholder

    except Exception:
        # Don't let metrics collection break the system
        pass


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    print("AMOS Metrics Exporter - Phase 14")
    print("=" * 60)

    exporter = get_metrics_exporter()

    if exporter.is_enabled():
        print("\n✅ Prometheus metrics enabled")

        # Record some example metrics
        exporter.record_health_score(95.5)
        exporter.record_runtime_active(True)
        exporter.record_bootstrap_phase(5)

        exporter.record_equation_execution("softmax", 0.025, success=True)
        exporter.record_equation_execution("consensus", 0.150, success=True)

        exporter.record_api_request("GET", "/health", 200, 0.005)
        exporter.record_api_request("POST", "/equations/execute", 200, 0.150)

        exporter.record_auth_attempt("api_key", success=True)
        exporter.record_recovery_attempt("circuit_breaker_reset", success=True)

        # Get metrics
        content, content_type = exporter.get_metrics()
        print(f"\n📊 Metrics content type: {content_type}")
        print(f"📊 Metrics size: {len(content)} bytes")
        print("\n📊 Sample metrics output:")
        print("-" * 40)
        # Print first few lines
        for line in content.split("\n")[:20]:
            print(line)
        print("...")

    else:
        print("\n⚠️  Prometheus metrics disabled")
        print("    Install: pip install prometheus-client")

    print("\n" + "=" * 60)
    print("✅ AMOS Metrics Exporter ready!")
