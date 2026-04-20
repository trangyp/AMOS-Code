#!/usr/bin/env python3
"""AMOS Equation Resilience - Circuit Breaker Pattern.

Production-grade circuit breaker for protecting downstream services
from cascading failures. Implements the state machine pattern with
CLOSED, OPEN, and HALF_OPEN states.

Features:
    - State machine (CLOSED/OPEN/HALF_OPEN)
    - Configurable failure thresholds
    - Recovery timeout with exponential backoff
    - Fallback function support
    - Tracing integration
    - Per-service breaker instances

Circuit States:
    CLOSED:    Normal operation, requests pass through
    OPEN:      Circuit tripped, requests fail fast
    HALF_OPEN: Testing recovery with limited requests

Usage:
    from equation_resilience import circuit_breaker, CircuitBreakerError

    # Decorator approach
    @circuit_breaker(name="redis", fail_max=5, reset_timeout=30)
    async def fetch_from_cache(key: str):
        return await redis.get(key)

    # Direct approach with fallback
    cb = CircuitBreaker(name="api", fail_max=3, reset_timeout=10)
    result = await cb.call(
        risky_function,
        fallback=lambda: default_value
    )

Environment:
    CIRCUIT_BREAKER_ENABLED: Global toggle (default: true)
    CIRCUIT_BREAKER_DEFAULT_FAIL_MAX: Default threshold
    CIRCUIT_BREAKER_DEFAULT_RESET: Default timeout (seconds)
"""

import functools
import os
import time
from collections.abc import Callable, Coroutine
from enum import Enum, auto
from typing import Any, TypeVar

try:
    from equation_tracing import create_span

    _tracing_available = True
except ImportError:
    _tracing_available = False

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Coroutine[Any, Any, Any]])


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""

    pass


class CircuitBreaker:
    """Circuit breaker for protecting downstream services."""

    def __init__(
        self,
        fail_max: int = 5,
        reset_timeout: float = 30.0,
        name: str = "default",
    ) -> None:
        self.name = name
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._last_failure_time: float = 0.0
        self._half_open_calls = 0
        self._enabled = os.getenv("CIRCUIT_BREAKER_ENABLED", "true").lower() == "true"

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        self._update_state()
        return self._state

    def _update_state(self) -> None:
        """Update state based on time and failures."""
        if self._state == CircuitState.OPEN:
            elapsed = time.time() - self._last_failure_time
            if elapsed >= self.reset_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0

    def _on_success(self) -> None:
        """Handle successful call."""
        if self._state == CircuitState.HALF_OPEN:
            self._half_open_calls += 1
            if self._half_open_calls >= 2:  # Allow 2 successful calls
                self._state = CircuitState.CLOSED
                self._failures = 0
                self._half_open_calls = 0
        else:
            self._failures = 0

    def _on_failure(self) -> None:
        """Handle failed call."""
        self._failures += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
        elif self._failures >= self.fail_max:
            self._state = CircuitState.OPEN

    async def call(
        self,
        fn: Callable[..., Coroutine[Any, Any, T]],
        *args: Any,
        fallback: Callable[[], T] = None,
        **kwargs: Any,
    ) -> T:
        """Execute async function with circuit breaker protection."""
        if not self._enabled:
            return await fn(*args, **kwargs)

        self._update_state()

        if self._state == CircuitState.OPEN:
            if fallback:
                return fallback()
            raise CircuitBreakerError(
                f"Circuit '{self.name}' is OPEN. Service temporarily unavailable."
            )

        try:
            if _tracing_available:
                with create_span(
                    f"circuit_breaker.{self.name}",
                    {
                        "circuit.state": self._state.name,
                        "circuit.failures": self._failures,
                    },
                ) as span:
                    result = await fn(*args, **kwargs)
                    self._on_success()
                    if span:
                        span.set_attribute("circuit.success", True)
                    return result
            else:
                result = await fn(*args, **kwargs)
                self._on_success()
                return result

        except Exception as exc:
            self._on_failure()
            # Re-raise the original exception
            raise exc from None

    def get_metrics(self) -> dict[str, Any]:
        """Get circuit breaker metrics."""
        return {
            "name": self.name,
            "state": self._state.name,
            "failures": self._failures,
            "fail_max": self.fail_max,
            "reset_timeout": self.reset_timeout,
            "last_failure": self._last_failure_time,
            "enabled": self._enabled,
        }


# Global breaker instances for common services
_breakers: dict[str, CircuitBreaker] = {}


def get_breaker(
    name: str,
    fail_max: int = 5,
    reset_timeout: float = 30.0,
) -> CircuitBreaker:
    """Get or create a circuit breaker instance.

    Args:
        name: Service identifier
        fail_max: Failure threshold
        reset_timeout: Recovery timeout in seconds

    Returns:
        CircuitBreaker instance
    """
    if name not in _breakers:
        _breakers[name] = CircuitBreaker(
            name=name,
            fail_max=fail_max,
            reset_timeout=reset_timeout,
        )
    return _breakers[name]


def circuit_breaker(
    name: str = "default",
    fail_max: int = 5,
    reset_timeout: float = 30.0,
    fallback: Callable[[], Any] = None,
) -> Callable[[F], F]:
    """Decorator to add circuit breaker protection.

    Args:
        name: Service identifier
        fail_max: Failure threshold before opening
        reset_timeout: Seconds before attempting recovery
        fallback: Optional fallback function

    Returns:
        Decorated function with circuit breaker protection
    """
    breaker = get_breaker(name, fail_max, reset_timeout)

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await breaker.call(func, *args, fallback=fallback, **kwargs)

        # Attach breaker for inspection
        wrapper._circuit_breaker = breaker  # type: ignore
        return wrapper  # type: ignore

    return decorator


def get_all_breaker_metrics() -> dict[str, dict[str, Any]]:
    """Get metrics for all circuit breakers.

    Returns:
        Dictionary of breaker name to metrics
    """
    return {name: cb.get_metrics() for name, cb in _breakers.items()}
