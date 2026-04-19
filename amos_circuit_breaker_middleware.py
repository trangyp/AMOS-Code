#!/usr/bin/env python3
"""AMOS FastAPI Circuit Breaker Middleware - Production Resilience (Phase 14+ Enhancement)
========================================================================================

Enterprise-grade circuit breaker middleware for FastAPI endpoints with:
- Automatic circuit breaker per endpoint
- Configurable failure thresholds and timeouts
- Half-open state testing
- Metrics and health reporting
- Integration with existing AMOS resilience infrastructure

Architecture:
- Middleware pattern for transparent endpoint protection
- Per-route circuit breaker registry
- Async-safe state transitions
- Integration with amos_resilience_engine
- Prometheus metrics export

Usage:
    from fastapi import FastAPI
    from amos_circuit_breaker_middleware import CircuitBreakerMiddleware

    app = FastAPI()
    app.add_middleware(
        CircuitBreakerMiddleware,
        failure_threshold=5,
        recovery_timeout=60.0,
        excluded_paths=["/health", "/metrics"]
    )

    # Or use decorator for specific endpoints
    from amos_circuit_breaker_middleware import circuit_breaker

    @circuit_breaker(failure_threshold=3, recovery_timeout=30.0)
    @app.get("/api/external-service")
    async def external_service():
        return await call_external_api()

Integration:
- amos_resilience_engine - Shared circuit breaker state
- amos_metrics_exporter - Failure/recovery metrics
- amos_health_monitor - Circuit health reporting

Owner: Trang
Version: 1.0.0
Phase: 14 Enhancement
"""

import functools
import time
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, TypeVar

# FastAPI imports
try:
    from fastapi import Request, Response
    from fastapi.responses import JSONResponse
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.types import ASGIApp

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("⚠️  FastAPI not available. Circuit breaker middleware disabled.")

# AMOS resilience integration
try:
    from amos_resilience_engine import CircuitState, get_resilience_engine

    RESILIENCE_AVAILABLE = True
except ImportError:
    RESILIENCE_AVAILABLE = False

# Metrics integration
try:
    from collections.abc import Callable

    from amos_metrics_exporter import get_metrics_exporter

    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False


T = TypeVar("T")


class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = auto()  # Normal operation
    OPEN = auto()  # Failing, reject requests
    HALF_OPEN = auto()  # Testing if recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_max_calls: int = 3
    success_threshold: int = 2
    excluded_paths: List[str] = field(default_factory=list)
    excluded_methods: List[str] = field(default_factory=lambda: ["OPTIONS", "HEAD"])


class CircuitBreaker:
    """
    Individual circuit breaker for a specific endpoint or service.

    Implements the standard circuit breaker pattern:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failure threshold exceeded, requests rejected immediately
    - HALF_OPEN: Testing if service recovered, limited requests allowed
    """

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float = None
        self.half_open_calls = 0
        self._lock = False  # Simple async lock

    async def _acquire_lock(self) -> bool:
        """Acquire async lock (simplified)."""
        if self._lock:
            return False
        self._lock = True
        return True

    def _release_lock(self) -> None:
        """Release async lock."""
        self._lock = False

    def can_execute(self) -> bool:
        """Check if request can be executed based on circuit state."""
        if self.state == CircuitBreakerState.CLOSED:
            return True

        if self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time is not None:
                elapsed = time.time() - self.last_failure_time
                if elapsed >= self.config.recovery_timeout:
                    # Transition to half-open
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.half_open_calls = 0
                    self.success_count = 0
                    return True
            return False

        if self.state == CircuitBreakerState.HALF_OPEN:
            # Allow limited calls in half-open state
            return self.half_open_calls < self.config.half_open_max_calls

        return True

    def record_success(self) -> None:
        """Record successful request."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                # Transition to closed
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                self.half_open_calls = 0
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = 0

    def record_failure(self) -> None:
        """Record failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitBreakerState.HALF_OPEN:
            # Transition back to open
            self.state = CircuitBreakerState.OPEN
        elif self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                # Transition to open
                self.state = CircuitBreakerState.OPEN

    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status."""
        return {
            "name": self.name,
            "state": self.state.name,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "half_open_calls": self.half_open_calls,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
            },
        }


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""

    _instance: Optional[CircuitBreakerRegistry] = None

    def __new__(cls) -> CircuitBreakerRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._breakers: Dict[str, CircuitBreaker] = {}

    def get_or_create(
        self, name: str, config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Get existing or create new circuit breaker."""
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(name, config)
        return self._breakers[name]

    def get_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name."""
        return self._breakers.get(name)

    def get_all_status(self) -> List[dict[str, Any]]:
        """Get status of all circuit breakers."""
        return [breaker.get_status() for breaker in self._breakers.values()]

    def reset_all(self) -> None:
        """Reset all circuit breakers to closed state."""
        for breaker in self._breakers.values():
            breaker.state = CircuitBreakerState.CLOSED
            breaker.failure_count = 0
            breaker.success_count = 0
            breaker.last_failure_time = None
            breaker.half_open_calls = 0


class CircuitBreakerMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic circuit breaker protection.

    Wraps all HTTP requests with circuit breaker pattern:
    - Tracks failures per route
    - Opens circuit after threshold
    - Automatic recovery testing
    - Excludes health checks and metrics
    """

    def __init__(
        self,
        app: ASGIApp,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        excluded_paths: List[str] = None,
        excluded_methods: List[str] = None,
    ):
        super().__init__(app)
        self.config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            excluded_paths=excluded_paths
            or ["/health", "/metrics", "/docs", "/redoc", "/openapi.json"],
            excluded_methods=excluded_methods or ["OPTIONS", "HEAD"],
        )
        self.registry = CircuitBreakerRegistry()

    def _get_circuit_name(self, request: Request) -> str:
        """Generate circuit breaker name from request."""
        return f"{request.method}:{request.url.path}"

    def _is_excluded(self, request: Request) -> bool:
        """Check if request path is excluded from circuit breaker."""
        path = request.url.path
        method = request.method

        # Check excluded methods
        if method in self.config.excluded_methods:
            return True

        # Check excluded paths
        for excluded in self.config.excluded_paths:
            if path.startswith(excluded):
                return True

        return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with circuit breaker protection."""
        # Skip excluded paths
        if self._is_excluded(request):
            return await call_next(request)

        circuit_name = self._get_circuit_name(request)
        breaker = self.registry.get_or_create(circuit_name, self.config)

        # Check if circuit allows execution
        if not breaker.can_execute():
            # Circuit is open - reject request
            if METRICS_AVAILABLE:
                metrics = get_metrics_exporter()
                metrics._circuit_breaker_state.labels(
                    circuit_name=circuit_name, state="rejected"
                ).inc()

            return JSONResponse(
                status_code=503,
                content={
                    "error": "Service temporarily unavailable",
                    "message": f"Circuit breaker is OPEN for {circuit_name}",
                    "retry_after": int(self.config.recovery_timeout),
                },
                headers={"Retry-After": str(int(self.config.recovery_timeout))},
            )

        # Execute request
        try:
            if breaker.state == CircuitBreakerState.HALF_OPEN:
                breaker.half_open_calls += 1

            response = await call_next(request)

            # Record success for 2xx responses
            if 200 <= response.status_code < 300:
                breaker.record_success()
            elif response.status_code >= 500:
                # Server error counts as failure
                breaker.record_failure()
                if METRICS_AVAILABLE:
                    metrics = get_metrics_exporter()
                    metrics._circuit_breaker_state.labels(
                        circuit_name=circuit_name, state="open"
                    ).inc()

            return response

        except Exception:
            # Record failure
            breaker.record_failure()

            if METRICS_AVAILABLE:
                metrics = get_metrics_exporter()
                metrics._circuit_breaker_state.labels(circuit_name=circuit_name, state="open").inc()

            # Re-raise exception
            raise


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    half_open_max_calls: int = 3,
    success_threshold: int = 2,
) -> Callable:
    """
    Decorator for adding circuit breaker to specific endpoints.

    Usage:
        @circuit_breaker(failure_threshold=3)
        async def my_endpoint():
            return await risky_operation()
    """
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        half_open_max_calls=half_open_max_calls,
        success_threshold=success_threshold,
    )

    def decorator(
        func: Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        breaker = CircuitBreaker(func.__name__, config)

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            if not breaker.can_execute():
                raise CircuitBreakerOpenError(f"Circuit breaker is OPEN for {func.__name__}")

            try:
                result = await func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception:
                breaker.record_failure()
                raise

        # Attach breaker for external access
        wrapper._circuit_breaker = breaker  # type: ignore
        return wrapper

    return decorator


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""

    pass


def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """Get the global circuit breaker registry."""
    return CircuitBreakerRegistry()


# Convenience function to add middleware to FastAPI app
def add_circuit_breaker_middleware(
    app: Any,
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    excluded_paths: List[str] = None,
) -> bool:
    """
    Add circuit breaker middleware to FastAPI application.

    Args:
        app: FastAPI application
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before testing recovery
        excluded_paths: Paths to exclude from circuit breaker

    Returns:
        True if middleware added successfully
    """
    if not FASTAPI_AVAILABLE:
        print("⚠️  FastAPI not available. Cannot add circuit breaker middleware.")
        return False

    app.add_middleware(
        CircuitBreakerMiddleware,
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout,
        excluded_paths=excluded_paths,
    )
    print("✅ Circuit breaker middleware added to FastAPI app")
    return True


__all__ = [
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerState",
    "CircuitBreakerMiddleware",
    "CircuitBreakerRegistry",
    "circuit_breaker",
    "CircuitBreakerOpenError",
    "get_circuit_breaker_registry",
    "add_circuit_breaker_middleware",
]
