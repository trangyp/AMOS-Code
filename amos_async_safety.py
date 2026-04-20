#!/usr/bin/env python3
"""
AMOS Async Safety Patterns Module.

State-of-the-art async patterns for production reliability:
- Circuit breaker pattern
- Bulkhead isolation
- Timeout enforcement
- Retry with exponential backoff
- Async semaphore-based throttling
"""

from __future__ import annotations

import asyncio
import functools
import random
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, TypeVar

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    half_open_max_calls: int = 3
    success_threshold: int = 2


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Prevents cascading failures by stopping calls to failing services.
    """

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float = None
        self._half_open_calls = 0
        self._lock = asyncio.Lock()

    async def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute function with circuit breaker protection."""
        async with self._lock:
            await self._update_state()

            if self.state == CircuitState.OPEN:
                raise CircuitBreakerOpenError(f"Circuit {self.name} is OPEN")

            if self.state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.config.half_open_max_calls:
                    raise CircuitBreakerOpenError(f"Circuit {self.name} HALF_OPEN limit reached")
                self._half_open_calls += 1

        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception:
            await self._on_failure()
            raise

    async def _update_state(self) -> None:
        """Update circuit state based on time and failures."""
        if self.state == CircuitState.OPEN:
            if self.last_failure_time is not None:
                elapsed = time.time() - self.last_failure_time
                if elapsed >= self.config.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
                    self.success_count = 0

    async def _on_success(self) -> None:
        """Record successful call."""
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self._half_open_calls = 0
            else:
                self.failure_count = 0

    async def _on_failure(self) -> None:
        """Record failed call."""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
            elif self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (healthy)."""
        return self.state == CircuitState.CLOSED


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""

    pass


@dataclass
class RetryConfig:
    """Configuration for retry policy."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple[type[Exception], ...] = field(default_factory=lambda: (Exception,))


class AsyncRetry:
    """Retry mechanism with exponential backoff."""

    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()

    async def execute(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute with retry logic."""
        last_exception: Optional[Exception] = None

        for attempt in range(1, self.config.max_attempts + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if not isinstance(e, self.config.retryable_exceptions):
                    raise

                if attempt == self.config.max_attempts:
                    break

                delay = self._calculate_delay(attempt)
                await asyncio.sleep(delay)

        raise last_exception or Exception("Max retries exceeded")

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter."""
        delay = self.config.base_delay * (self.config.exponential_base ** (attempt - 1))
        delay = min(delay, self.config.max_delay)

        if self.config.jitter:
            delay = delay * (0.5 + random.random())

        return delay


class AsyncBulkhead:
    """
    Bulkhead pattern - isolate resources into pools.

    Prevents one part of system from exhausting all resources.
    """

    def __init__(self, name: str, max_concurrent: int = 10, max_queue: int = 100):
        self.name = name
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.queue_size = asyncio.Semaphore(max_queue)
        self.active_count = 0
        self.queue_count = 0

    async def execute(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute with bulkhead isolation."""
        if not self.queue_size.locked():
            async with self.queue_size:
                self.queue_count += 1
                async with self.semaphore:
                    self.queue_count -= 1
                    self.active_count += 1
                    try:
                        return await func(*args, **kwargs)
                    finally:
                        self.active_count -= 1
        else:
            raise BulkheadFullError(f"Bulkhead {self.name} queue full")

    @property
    def utilization(self) -> float:
        """Current utilization ratio."""
        total = self.semaphore._value + self.active_count
        if total == 0:
            return 0.0
        return self.active_count / total


class BulkheadFullError(Exception):
    """Raised when bulkhead is at capacity."""

    pass


@dataclass
class TimeoutConfig:
    """Configuration for timeout enforcement."""

    total_timeout: float = 30.0
    graceful_shutdown: bool = True


class AsyncTimeout:
    """Timeout enforcement with optional graceful shutdown."""

    def __init__(self, config: Optional[TimeoutConfig] = None):
        self.config = config or TimeoutConfig()

    async def execute(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute with timeout."""
        try:
            return await asyncio.wait_for(func(*args, **kwargs), timeout=self.config.total_timeout)
        except TimeoutError:
            raise TimeoutExceededError(f"Operation exceeded {self.config.total_timeout}s timeout")


class TimeoutExceededError(Exception):
    """Raised when operation times out."""

    pass


class AsyncSafetyManager:
    """
    Central manager for all async safety patterns.

    Combines circuit breaker, retry, bulkhead, and timeout.
    """

    def __init__(self):
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.bulkheads: dict[str, AsyncBulkhead] = {}
        self.retry_policies: dict[str, AsyncRetry] = {}

    def get_circuit_breaker(
        self, name: str, config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Get or create circuit breaker."""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(name, config)
        return self.circuit_breakers[name]

    def get_bulkhead(self, name: str, max_concurrent: int = 10) -> AsyncBulkhead:
        """Get or create bulkhead."""
        if name not in self.bulkheads:
            self.bulkheads[name] = AsyncBulkhead(name, max_concurrent)
        return self.bulkheads[name]

    async def protected_execute(
        self,
        func: Callable[..., T],
        circuit_name: str = None,
        bulkhead_name: str = None,
        retry_config: Optional[RetryConfig] = None,
        timeout: float = None,
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Execute with full protection stack."""
        wrapped = func

        # Add retry
        if retry_config:
            retry = AsyncRetry(retry_config)
            original = wrapped
            wrapped = functools.partial(retry.execute, original)

        # Add circuit breaker
        if circuit_name:
            cb = self.get_circuit_breaker(circuit_name)
            original = wrapped
            wrapped = functools.partial(cb.call, original)

        # Add bulkhead
        if bulkhead_name:
            bh = self.get_bulkhead(bulkhead_name)
            original = wrapped
            wrapped = functools.partial(bh.execute, original)

        # Add timeout
        if timeout:
            timeout_wrapper = AsyncTimeout(TimeoutConfig(total_timeout=timeout))
            original = wrapped
            wrapped = functools.partial(timeout_wrapper.execute, original)

        return await wrapped(*args, **kwargs)


# Global safety manager
_safety_manager: Optional[AsyncSafetyManager] = None


def get_safety_manager() -> AsyncSafetyManager:
    """Get global safety manager singleton."""
    global _safety_manager
    if _safety_manager is None:
        _safety_manager = AsyncSafetyManager()
    return _safety_manager


# Convenience decorators
def circuit_breaker(name: str, **config_kwargs: Any) -> Callable[[T], T]:
    """Decorator for circuit breaker pattern."""
    config = CircuitBreakerConfig(**config_kwargs)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            cb = get_safety_manager().get_circuit_breaker(name, config)
            return await cb.call(func, *args, **kwargs)

        return wrapper

    return decorator


def retry(**config_kwargs: Any) -> Callable[[T], T]:
    """Decorator for retry pattern."""
    config = RetryConfig(**config_kwargs)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            retry = AsyncRetry(config)
            return await retry.execute(func, *args, **kwargs)

        return wrapper

    return decorator


def timeout(seconds: float) -> Callable[[T], T]:
    """Decorator for timeout pattern."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            timeout_wrapper = AsyncTimeout(TimeoutConfig(total_timeout=seconds))
            return await timeout_wrapper.execute(func, *args, **kwargs)

        return wrapper

    return decorator


async def demo() -> None:
    """Demo async safety patterns."""
    print("AMOS Async Safety Patterns Demo")
    print("=" * 50)

    # Demo circuit breaker
    cb = CircuitBreaker("test_service")
    print(f"\nCircuit breaker created: {cb.state.value}")

    # Demo retry
    retry = AsyncRetry(RetryConfig(max_attempts=3, base_delay=0.1))
    print(f"Retry policy: max_attempts={retry.config.max_attempts}")

    # Demo bulkhead
    bh = AsyncBulkhead("compute_pool", max_concurrent=2)
    print("Bulkhead created: max_concurrent=2")

    # Demo safety manager
    manager = get_safety_manager()
    print("Safety manager initialized")
    print(f"  Circuit breakers: {len(manager.circuit_breakers)}")
    print(f"  Bulkheads: {len(manager.bulkheads)}")

    print("\n" + "=" * 50)
    print("All async safety patterns ready")


if __name__ == "__main__":
    asyncio.run(demo())
