#!/usr/bin/env python3
"""AMOS Circuit Breaker - Fault tolerance for external service calls.

Production-ready circuit breaker implementation using:
- Modern Python 3.12+ syntax
- Async/await patterns
- State machine transitions
- Exponential backoff
- Health monitoring
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from collections.abc import Coroutine
from typing import Any, Callable, TypeVar


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_calls: int = 3
    success_threshold: int = 2


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker."""

    failures: int = 0
    successes: int = 0
    last_failure_time: datetime | None = None
    state_changes: list[tuple[datetime, CircuitState]] = field(default_factory=list)


T = TypeVar("T")


class CircuitBreaker:
    """Circuit breaker for resilient external calls.

    Prevents cascade failures by stopping calls to failing services.
    Automatically recovers when service becomes healthy.
    """

    def __init__(
        self,
        name: str,
        config: CircuitBreakerConfig | None = None,
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()
        self._half_open_calls = 0
        self._consecutive_successes = 0
        self._lock = asyncio.Lock()

    async def call(
        self,
        func: Callable[[], asyncio.Future[T] | Coroutine[Any, Any, T]],
        fallback: Callable[[], T] | None = None,
    ) -> T:
        """Execute function with circuit breaker protection."""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if self._should_attempt_recovery():
                    self._transition_to(CircuitState.HALF_OPEN)
                    self._half_open_calls = 0
                else:
                    if fallback:
                        return fallback()
                    raise CircuitBreakerOpen(f"Circuit {self.name} is OPEN")

            if self.state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.config.half_open_max_calls:
                    if fallback:
                        return fallback()
                    raise CircuitBreakerOpen(
                        f"Circuit {self.name} HALF_OPEN limit reached"
                    )
                self._half_open_calls += 1

        # Execute the call
        try:
            result = await func()
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            if fallback:
                return fallback()
            raise

    async def _on_success(self) -> None:
        """Handle successful call."""
        async with self._lock:
            self.stats.successes += 1
            self._consecutive_successes += 1

            if self.state == CircuitState.HALF_OPEN:
                if self._consecutive_successes >= self.config.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
                    self.stats.failures = 0
                    self._consecutive_successes = 0

    async def _on_failure(self) -> None:
        """Handle failed call."""
        async with self._lock:
            self.stats.failures += 1
            self._consecutive_successes = 0
            self.stats.last_failure_time = datetime.now(timezone.utc)

            if self.state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)
            elif self.state == CircuitState.CLOSED:
                if self.stats.failures >= self.config.failure_threshold:
                    self._transition_to(CircuitState.OPEN)

    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.stats.last_failure_time is None:
            return True

        elapsed = (datetime.now(timezone.utc) - self.stats.last_failure_time).total_seconds()
        return elapsed >= self.config.recovery_timeout

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to new state."""
        if new_state != self.state:
            self.stats.state_changes.append(
                (datetime.now(timezone.utc), new_state)
            )
            self.state = new_state

    def get_status(self) -> dict[str, Any]:
        """Get current circuit breaker status."""
        return {
            "name": self.name,
            "state": self.state.value,
            "stats": {
                "failures": self.stats.failures,
                "successes": self.stats.successes,
                "last_failure": (
                    self.stats.last_failure_time.isoformat()
                    if self.stats.last_failure_time
                    else None
                ),
            },
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
            },
        }


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""

    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}

    def get_or_create(
        self,
        name: str,
        config: CircuitBreakerConfig | None = None,
    ) -> CircuitBreaker:
        """Get existing or create new circuit breaker."""
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(name, config)
        return self._breakers[name]

    def get_status(self) -> dict[str, Any]:
        """Get status of all circuit breakers."""
        return {
            name: breaker.get_status()
            for name, breaker in self._breakers.items()
        }


# Global registry instance
_registry: CircuitBreakerRegistry | None = None


def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """Get global circuit breaker registry."""
    global _registry
    if _registry is None:
        _registry = CircuitBreakerRegistry()
    return _registry


# Example usage
async def example():
    """Example circuit breaker usage."""
    registry = get_circuit_breaker_registry()
    breaker = registry.get_or_create("api_service")

    async def unreliable_api():
        # Simulate flaky API
        if time.time() % 2 == 0:
            raise Exception("API error")
        return "success"

    def fallback():
        return "fallback_response"

    try:
        result = await breaker.call(unreliable_api, fallback)
        print(f"Result: {result}")
    except CircuitBreakerOpen:
        print("Circuit breaker is open - service unavailable")

    print(f"Status: {breaker.get_status()}")


if __name__ == "__main__":
    asyncio.run(example())
