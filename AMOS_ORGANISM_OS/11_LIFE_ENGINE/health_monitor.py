"""Health Monitor — Self-Monitoring & Healing

Monitors organism health metrics and triggers self-healing actions.
Tracks vital signs and detects health issues.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class HealthStatus(Enum):
    """Overall health status."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class HealthMetricType(Enum):
    """Type of health metric."""

    CPU = "cpu"
    MEMORY = "memory"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    AVAILABILITY = "availability"


@dataclass
class HealthMetric:
    """A health metric reading."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    metric_type: HealthMetricType = HealthMetricType.CPU
    value: float = 0.0
    unit: str = ""
    threshold_warning: float = 0.7
    threshold_critical: float = 0.9
    subsystem: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def get_status(self) -> HealthStatus:
        """Get status based on value."""
        if self.value >= self.threshold_critical:
            return HealthStatus.CRITICAL
        elif self.value >= self.threshold_warning:
            return HealthStatus.WARNING
        return HealthStatus.HEALTHY

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "metric_type": self.metric_type.value,
            "status": self.get_status().value,
        }


@dataclass
class HealingAction:
    """A self-healing action."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    trigger_metric: str = ""
    action_type: str = ""  # restart, scale, reconfigure, isolate
    target_subsystem: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    executed: bool = False
    successful: bool = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    executed_at: str = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class HealthMonitor:
    """Monitors organism health and triggers self-healing.

    Tracks vital signs, detects anomalies, and executes
    healing actions to maintain organism health.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        self.metrics: dict[str, list[HealthMetric]] = {}
        self.healing_actions: dict[str, HealingAction] = {}
        self.healing_log: list[dict[str, Any]] = []
        self.health_history: list[dict[str, Any]] = []

        self._init_default_metrics()

    def _init_default_metrics(self):
        """Initialize default health metrics."""
        self.metrics = {
            "cpu": [],
            "memory": [],
            "response_time": [],
            "error_rate": [],
            "throughput": [],
            "availability": [],
        }

    def record_metric(
        self,
        metric_type: HealthMetricType,
        value: float,
        unit: str,
        subsystem: str,
        warning_threshold: float = 0.7,
        critical_threshold: float = 0.9,
    ) -> HealthMetric:
        """Record a health metric."""
        metric = HealthMetric(
            metric_type=metric_type,
            value=value,
            unit=unit,
            threshold_warning=warning_threshold,
            threshold_critical=critical_threshold,
            subsystem=subsystem,
        )

        metric_key = metric_type.value
        if metric_key not in self.metrics:
            self.metrics[metric_key] = []

        self.metrics[metric_key].append(metric)

        # Keep only last 100 readings
        if len(self.metrics[metric_key]) > 100:
            self.metrics[metric_key] = self.metrics[metric_key][-100:]

        # Check if healing is needed
        if metric.get_status() in (HealthStatus.WARNING, HealthStatus.CRITICAL):
            self._trigger_healing(metric)

        return metric

    def _trigger_healing(self, metric: HealthMetric) -> Optional[HealingAction]:
        """Trigger a healing action based on metric status."""
        action_type = self._determine_healing_action(metric)

        action = HealingAction(
            trigger_metric=metric.id,
            action_type=action_type,
            target_subsystem=metric.subsystem,
            parameters={"metric_value": metric.value, "metric_type": metric.metric_type.value},
        )

        self.healing_actions[action.id] = action
        return action

    def _determine_healing_action(self, metric: HealthMetric) -> str:
        """Determine appropriate healing action for metric."""
        if metric.metric_type == HealthMetricType.CPU:
            return "scale_capacity"
        elif metric.metric_type == HealthMetricType.MEMORY:
            return "free_resources"
        elif metric.metric_type == HealthMetricType.RESPONSE_TIME:
            return "optimize_performance"
        elif metric.metric_type == HealthMetricType.ERROR_RATE:
            return "restart_subsystem"
        elif metric.metric_type == HealthMetricType.THROUGHPUT:
            return "scale_capacity"
        elif metric.metric_type == HealthMetricType.AVAILABILITY:
            return "failover"
        return "investigate"

    def execute_healing(self, action_id: str) -> bool:
        """Execute a healing action."""
        action = self.healing_actions.get(action_id)
        if not action or action.executed:
            return False

        action.executed = True
        action.executed_at = datetime.now(UTC).isoformat()

        # Simulate healing execution
        # In real implementation, this would actually perform the action
        action.successful = True

        self.healing_log.append(
            {
                "action_id": action_id,
                "action_type": action.action_type,
                "target": action.target_subsystem,
                "executed_at": action.executed_at,
                "successful": action.successful,
            }
        )

        self._save_health_data()
        return True

    def get_overall_health(self) -> HealthStatus:
        """Get overall organism health."""
        critical_count = 0
        warning_count = 0

        for metric_list in self.metrics.values():
            if metric_list:
                latest = metric_list[-1]
                status = latest.get_status()
                if status == HealthStatus.CRITICAL:
                    critical_count += 1
                elif status == HealthStatus.WARNING:
                    warning_count += 1

        if critical_count > 0:
            return HealthStatus.CRITICAL
        elif warning_count > 2:
            return HealthStatus.WARNING
        return HealthStatus.HEALTHY

    def get_subsystem_health(self, subsystem: str) -> dict[str, Any]:
        """Get health metrics for a specific subsystem."""
        subsystem_metrics = {}
        for metric_type, metric_list in self.metrics.items():
            for metric in metric_list:
                if metric.subsystem == subsystem:
                    if metric_type not in subsystem_metrics:
                        subsystem_metrics[metric_type] = []
                    subsystem_metrics[metric_type].append(metric.to_dict())

        return {
            "subsystem": subsystem,
            "metrics": subsystem_metrics,
            "latest_status": self._get_latest_subsystem_status(subsystem),
        }

    def _get_latest_subsystem_status(self, subsystem: str) -> str:
        """Get latest health status for subsystem."""
        worst_status = HealthStatus.HEALTHY

        for metric_list in self.metrics.values():
            if metric_list:
                latest = metric_list[-1]
                if latest.subsystem == subsystem:
                    status = latest.get_status()
                    if status == HealthStatus.CRITICAL:
                        return HealthStatus.CRITICAL.value
                    elif status == HealthStatus.WARNING and worst_status == HealthStatus.HEALTHY:
                        worst_status = HealthStatus.WARNING

        return worst_status.value

    def _save_health_data(self):
        """Save health data to disk."""
        health_file = self.data_dir / "health.json"
        data = {
            "metrics": {k: [m.to_dict() for m in v[-10:]] for k, v in self.metrics.items()},
            "healing_actions": [a.to_dict() for a in self.healing_actions.values()],
            "healing_log": self.healing_log,
            "overall_health": self.get_overall_health().value,
            "saved_at": datetime.now(UTC).isoformat(),
        }
        health_file.write_text(json.dumps(data, indent=2))

    def get_status(self) -> dict[str, Any]:
        """Get health monitor status."""
        total_actions = len(self.healing_actions)
        executed = sum(1 for a in self.healing_actions.values() if a.executed)
        successful = sum(1 for a in self.healing_actions.values() if a.successful)

        return {
            "overall_health": self.get_overall_health().value,
            "metric_types_tracked": len(self.metrics),
            "total_readings": sum(len(v) for v in self.metrics.values()),
            "healing_actions": {
                "total": total_actions,
                "executed": executed,
                "successful": successful,
            },
            "pending_healing": total_actions - executed,
        }


_MONITOR: Optional[HealthMonitor] = None


def get_health_monitor(data_dir: Optional[Path] = None) -> HealthMonitor:
    """Get or create global health monitor."""
    global _MONITOR
    if _MONITOR is None:
        _MONITOR = HealthMonitor(data_dir)
    return _MONITOR
