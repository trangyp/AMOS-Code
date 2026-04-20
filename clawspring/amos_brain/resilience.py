#!/usr/bin/env python3
"""AMOS Ecosystem v2.5 - Self-Healing & Resilience System.

Automatic failure detection, recovery, and graceful degradation
for production reliability.
"""

from __future__ import annotations

import sys
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class FailureType(Enum):
    """Types of failures."""

    TRANSIENT = "transient"  # Temporary, retry may succeed
    PERSISTENT = "persistent"  # Requires intervention
    CRITICAL = "critical"  # System-wide impact
    DEGRADATION = "degradation"  # Performance issue


@dataclass
class Failure:
    """Failure event."""

    component: str
    failure_type: FailureType
    error: str
    timestamp: datetime
    retry_count: int = 0
    resolved: bool = False


@dataclass
class RecoveryAction:
    """Recovery action result."""

    action: str
    success: bool
    message: str
    timestamp: datetime


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time: datetime = None
        self.state = "closed"  # closed, open, half-open
        self._lock = threading.Lock()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        with self._lock:
            if self.state == "open":
                if self._should_attempt_reset():
                    self.state = "half-open"
                else:
                    raise Exception(f"Circuit breaker open for {func.__name__}")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time passed to attempt recovery."""
        if not self.last_failure_time:
            return True
        elapsed = (datetime.now() - self.last_failure_time).seconds
        return elapsed >= self.recovery_timeout

    def _on_success(self) -> None:
        """Handle successful call."""
        with self._lock:
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0

    def _on_failure(self) -> None:
        """Handle failed call."""
        with self._lock:
            self.failures += 1
            self.last_failure_time = datetime.now()

            if self.failures >= self.failure_threshold:
                self.state = "open"


class RetryPolicy:
    """Configurable retry policy."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute with retry logic."""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = min(self.base_delay * (self.exponential_base**attempt), self.max_delay)
                    time.sleep(delay)

        raise last_exception


class ResilienceManager:
    """Manages system resilience and self-healing."""

    def __init__(self):
        self.failures: list[Failure] = []
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.retry_policy = RetryPolicy()
        self.recovery_handlers: dict[str, Callable] = {}
        self._running = False
        self._monitor_thread: threading.Thread = None
        self._lock = threading.Lock()

    def register_component(
        self,
        name: str,
        circuit_breaker: CircuitBreaker | None = None,
        recovery_handler: Callable | None = None,
    ) -> None:
        """Register a component for resilience management."""
        if circuit_breaker:
            self.circuit_breakers[name] = circuit_breaker
        if recovery_handler:
            self.recovery_handlers[name] = recovery_handler

    def execute_with_resilience(self, component: str, func: Callable, *args, **kwargs) -> Any:
        """Execute function with full resilience protection."""
        try:
            # Check circuit breaker
            if component in self.circuit_breakers:
                return self.circuit_breakers[component].call(
                    self._execute_with_retry, component, func, *args, **kwargs
                )
            else:
                return self._execute_with_retry(component, func, *args, **kwargs)

        except Exception as e:
            self._record_failure(component, e)
            self._attempt_recovery(component)
            raise e

    def _execute_with_retry(self, component: str, func: Callable, *args, **kwargs) -> Any:
        """Execute with retry policy."""
        return self.retry_policy.execute(func, *args, **kwargs)

    def _record_failure(self, component: str, error: Exception) -> None:
        """Record a failure."""
        failure = Failure(
            component=component,
            failure_type=self._classify_error(error),
            error=str(error),
            timestamp=datetime.now(),
        )

        with self._lock:
            self.failures.append(failure)

        print(f"[Resilience] Failure recorded: {component} - {error}")

    def _classify_error(self, error: Exception) -> FailureType:
        """Classify error type."""
        error_str = str(error).lower()

        if any(kw in error_str for kw in ["timeout", "connection", "temporary"]):
            return FailureType.TRANSIENT
        elif any(kw in error_str for kw in ["critical", "fatal", "crash"]):
            return FailureType.CRITICAL
        elif any(kw in error_str for kw in ["slow", "degraded", "performance"]):
            return FailureType.DEGRADATION
        else:
            return FailureType.PERSISTENT

    def _attempt_recovery(self, component: str) -> bool:
        """Attempt to recover a failed component."""
        if component not in self.recovery_handlers:
            return False

        try:
            print(f"[Resilience] Attempting recovery: {component}")
            self.recovery_handlers[component]()

            # Mark failures as resolved
            with self._lock:
                for f in self.failures:
                    if f.component == component and not f.resolved:
                        f.resolved = True

            print(f"[Resilience] Recovery successful: {component}")
            return True

        except Exception as e:
            print(f"[Resilience] Recovery failed: {component} - {e}")
            return False

    def start_monitoring(self) -> None:
        """Start resilience monitoring."""
        if self._running:
            return

        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        print("[Resilience] Monitoring started")

    def stop_monitoring(self) -> None:
        """Stop resilience monitoring."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        print("[Resilience] Monitoring stopped")

    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while self._running:
            try:
                self._check_system_health()
                time.sleep(10)
            except Exception as e:
                print(f"[Resilience] Monitor error: {e}")

    def _check_system_health(self) -> None:
        """Check overall system health."""
        with self._lock:
            recent_failures = [
                f
                for f in self.failures
                if (datetime.now() - f.timestamp).seconds < 300  # 5 min
                and not f.resolved
            ]

        if len(recent_failures) > 10:
            print(f"[Resilience] WARNING: {len(recent_failures)} recent failures")

    def get_resilience_report(self) -> dict[str, Any]:
        """Get resilience status report."""
        with self._lock:
            total = len(self.failures)
            resolved = sum(1 for f in self.failures if f.resolved)
            by_type: dict[str, int] = {}

            for f in self.failures:
                ft = f.failure_type.value
                by_type[ft] = by_type.get(ft, 0) + 1

            return {
                "total_failures": total,
                "resolved": resolved,
                "unresolved": total - resolved,
                "by_type": by_type,
                "circuit_breakers": {name: cb.state for name, cb in self.circuit_breakers.items()},
                "status": "healthy" if (total - resolved) < 5 else "degraded",
            }


# Global instance
_resilience: ResilienceManager | None = None


def get_resilience() -> ResilienceManager:
    """Get or create global resilience manager."""
    global _resilience
    if _resilience is None:
        _resilience = ResilienceManager()
    return _resilience


def resilient(component: str):
    """Decorator for resilient function execution."""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            return get_resilience().execute_with_resilience(component, func, *args, **kwargs)

        return wrapper

    return decorator


def main():
    """Demo resilience system."""
    print("=" * 70)
    print("AMOS ECOSYSTEM v2.5 - RESILIENCE SYSTEM DEMO")
    print("=" * 70)

    resilience = get_resilience()

    # Register components
    def recover_cognitive():
        print("  Reinitializing cognitive router...")

    def recover_bridge():
        print("  Reconnecting organism bridge...")

    resilience.register_component(
        "cognitive_router", CircuitBreaker(failure_threshold=3), recover_cognitive
    )
    resilience.register_component(
        "organism_bridge", CircuitBreaker(failure_threshold=5), recover_bridge
    )

    # Start monitoring
    resilience.start_monitoring()

    # Demo resilient execution
    print("\nDemo: Resilient execution")

    @resilient("cognitive_router")
    def risky_operation():
        import random

        if random.random() < 0.3:  # 30% failure rate
            raise Exception("Simulated transient error")
        return "Success"

    for i in range(5):
        try:
            result = risky_operation()
            print(f"  Call {i + 1}: {result}")
        except Exception as e:
            print(f"  Call {i + 1}: Failed - {e}")

    # Get report
    time.sleep(1)
    print("\nResilience Report:")
    report = resilience.get_resilience_report()
    for k, v in report.items():
        print(f"  {k}: {v}")

    # Stop
    resilience.stop_monitoring()

    print("\n" + "=" * 70)
    print("Resilience system operational!")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
