"""AMOS Health Monitor - Production observability for SuperBrain.

Provides real-time health monitoring, metrics collection, and alerting
for the AMOS SuperBrain system. Implements 2025 AI agent observability
best practices.

Reference:
- OpenTelemetry AI Agent Observability 2025
- Microsoft Agent Factory Best Practices
- Azure AI Agent Observability Patterns
"""

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class HealthStatus(Enum):
    """Health status levels for components."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Health state for a single component."""

    name: str
    status: HealthStatus
    health_score: float  # 0.0 to 1.0
    last_check: datetime
    message: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealth:
    """Overall system health snapshot."""

    timestamp: datetime
    overall_score: float
    overall_status: HealthStatus
    components: Dict[str, ComponentHealth]
    alerts: List[str]


class HealthMonitor:
    """Production health monitoring for AMOS SuperBrain.

    Implements:
    - Real-time health checks
    - Metrics collection
    - Alert generation
    - Health history tracking
    """

    def __init__(self, check_interval: int = 60):
        """Initialize health monitor.

        Args:
            check_interval: Seconds between health checks
        """
        self.check_interval = check_interval
        self._components: Dict[str, Callable[[], ComponentHealth]] = {}
        self._history: List[SystemHealth] = []
        self._max_history = 1000
        self._lock = threading.Lock()
        self._running = False
        self._monitor_thread: threading.Thread = None
        self._alert_handlers: List[Callable[[str], None]] = []

    def register_component(self, name: str, health_check: Callable[[], ComponentHealth]) -> None:
        """Register a component for health monitoring.

        Args:
            name: Component identifier
            health_check: Function returning ComponentHealth
        """
        with self._lock:
            self._components[name] = health_check

    def register_alert_handler(self, handler: Callable[[str], None]) -> None:
        """Register an alert handler callback.

        Args:
            handler: Function called with alert messages
        """
        self._alert_handlers.append(handler)

    def start(self) -> None:
        """Start continuous health monitoring."""
        if self._running:
            return

        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def stop(self) -> None:
        """Stop health monitoring."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)

    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._running:
            try:
                self.check_health()
                time.sleep(self.check_interval)
            except Exception as e:
                self._trigger_alert(f"Health monitor error: {e}")
                time.sleep(self.check_interval)

    def check_health(self) -> SystemHealth:
        """Execute health checks for all components.

        Returns:
            SystemHealth snapshot
        """
        with self._lock:
            components: Dict[str, ComponentHealth] = {}
            alerts: List[str] = []

            for name, check_fn in self._components.items():
                try:
                    health = check_fn()
                    components[name] = health

                    # Generate alerts
                    if health.status == HealthStatus.UNHEALTHY:
                        alerts.append(f"CRITICAL: {name} is unhealthy - {health.message}")
                    elif health.status == HealthStatus.DEGRADED:
                        alerts.append(f"WARNING: {name} is degraded - {health.message}")

                except Exception as e:
                    components[name] = ComponentHealth(
                        name=name,
                        status=HealthStatus.UNKNOWN,
                        health_score=0.0,
                        last_check=datetime.now(UTC),
                        message=f"Health check failed: {e}",
                    )
                    alerts.append(f"ERROR: {name} health check failed - {e}")

            # Calculate overall health
            if components:
                overall_score = sum(c.health_score for c in components.values()) / len(components)
                unhealthy_count = sum(
                    1 for c in components.values() if c.status == HealthStatus.UNHEALTHY
                )
                degraded_count = sum(
                    1 for c in components.values() if c.status == HealthStatus.DEGRADED
                )

                if unhealthy_count > 0:
                    overall_status = HealthStatus.UNHEALTHY
                elif degraded_count > 0:
                    overall_status = HealthStatus.DEGRADED
                else:
                    overall_status = HealthStatus.HEALTHY
            else:
                overall_score = 0.0
                overall_status = HealthStatus.UNKNOWN

            system_health = SystemHealth(
                timestamp=datetime.now(UTC),
                overall_score=overall_score,
                overall_status=overall_status,
                components=components,
                alerts=alerts,
            )

            # Store history
            self._history.append(system_health)
            if len(self._history) > self._max_history:
                self._history.pop(0)

            # Trigger alerts
            for alert in alerts:
                self._trigger_alert(alert)

            return system_health

    def _trigger_alert(self, message: str) -> None:
        """Trigger alert handlers."""
        for handler in self._alert_handlers:
            try:
                handler(message)
            except Exception:
                pass

    def get_current_health(self) -> Optional[SystemHealth]:
        """Get most recent health snapshot.

        Returns:
            Latest SystemHealth or None if no checks run
        """
        with self._lock:
            return self._history[-1] if self._history else None

    def get_health_history(self, last_n: int = 100) -> List[SystemHealth]:
        """Get health check history.

        Args:
            last_n: Number of recent checks to return

        Returns:
            List of SystemHealth snapshots
        """
        with self._lock:
            return self._history[-last_n:]

    def get_component_trend(
        self, component_name: str, last_n: int = 100
    ) -> List[tuple[datetime, float]]:
        """Get health score trend for a component.

        Args:
            component_name: Component to analyze
            last_n: Number of data points

        Returns:
            List of (timestamp, health_score) tuples
        """
        with self._lock:
            trend = []
            for snapshot in self._history[-last_n:]:
                if component_name in snapshot.components:
                    comp = snapshot.components[component_name]
                    trend.append((comp.last_check, comp.health_score))
            return trend


class AMOSHealthReporter:
    """Health reporter for AMOS SuperBrain components."""

    @staticmethod
    def create_superbrain_health_check(brain) -> Callable[[], ComponentHealth]:
        """Create health check for SuperBrain instance.

        Args:
            brain: SuperBrain instance

        Returns:
            Health check function
        """

        def check() -> ComponentHealth:
            try:
                state = brain.get_state()

                # Determine status based on health score
                if state.health_score >= 0.9:
                    status = HealthStatus.HEALTHY
                elif state.health_score >= 0.5:
                    status = HealthStatus.DEGRADED
                else:
                    status = HealthStatus.UNHEALTHY

                return ComponentHealth(
                    name="SuperBrain",
                    status=status,
                    health_score=state.health_score,
                    last_check=datetime.now(UTC),
                    message=f"Tools: {len(state.loaded_tools)}, Models: {len(state.available_models)}",
                    metrics={
                        "tool_count": len(state.loaded_tools),
                        "model_count": len(state.available_models),
                        "math_status": state.math_framework_status,
                    },
                )
            except Exception as e:
                return ComponentHealth(
                    name="SuperBrain",
                    status=HealthStatus.UNHEALTHY,
                    health_score=0.0,
                    last_check=datetime.now(UTC),
                    message=f"Health check error: {e}",
                )

        return check

    @staticmethod
    def create_math_framework_health_check() -> Callable[[], ComponentHealth]:
        """Create health check for Math Framework."""

        def check() -> ComponentHealth:
            try:
                from clawspring.amos_brain.mathematical_framework_engine import get_framework_engine

                engine = get_framework_engine()
                stats = engine.get_stats()

                equation_count = stats.get("total_equations", 0)

                if equation_count >= 20:
                    status = HealthStatus.HEALTHY
                    score = 1.0
                elif equation_count > 0:
                    status = HealthStatus.DEGRADED
                    score = equation_count / 20.0
                else:
                    status = HealthStatus.UNHEALTHY
                    score = 0.0

                return ComponentHealth(
                    name="MathFramework",
                    status=status,
                    health_score=score,
                    last_check=datetime.now(UTC),
                    message=f"{equation_count} equations active",
                    metrics=stats,
                )
            except Exception as e:
                return ComponentHealth(
                    name="MathFramework",
                    status=HealthStatus.UNHEALTHY,
                    health_score=0.0,
                    last_check=datetime.now(UTC),
                    message=f"Not available: {e}",
                )

        return check


# Global health monitor instance
_health_monitor: Optional[HealthMonitor] = None


def get_health_monitor() -> HealthMonitor:
    """Get or create global health monitor instance."""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor


def initialize_health_monitoring(brain) -> HealthMonitor:
    """Initialize health monitoring for AMOS SuperBrain.

    Args:
        brain: SuperBrain instance to monitor

    Returns:
        Configured HealthMonitor
    """
    monitor = get_health_monitor()

    # Register component health checks
    reporter = AMOSHealthReporter()

    monitor.register_component("superbrain", reporter.create_superbrain_health_check(brain))

    monitor.register_component("math_framework", reporter.create_math_framework_health_check())

    # Register console alert handler
    def console_alert(message: str) -> None:
        print(f"[HEALTH ALERT] {datetime.now(UTC).isoformat()}: {message}")

    monitor.register_alert_handler(console_alert)

    # Start monitoring
    monitor.start()

    print("✅ Health Monitor: ACTIVE (60s intervals)")

    return monitor
