"""Health Monitor — System health and wellness tracking

Monitors health metrics, stress levels, and overall
wellness indicators for the organism.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any


class HealthStatus(Enum):
    """Overall health status levels."""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of health metrics."""

    STRESS = "stress"
    RECOVERY = "recovery"
    COGNITIVE_LOAD = "cognitive_load"
    PHYSICAL_ACTIVITY = "physical_activity"
    HYDRATION = "hydration"
    NUTRITION = "nutrition"


@dataclass
class HealthMetric:
    """A health metric reading."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    metric_type: MetricType = MetricType.STRESS
    value: float = 0.0  # Normalized 0-1 or 0-100 depending on metric
    unit: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    source: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "metric_type": self.metric_type.value,
        }


@dataclass
class HealthAlert:
    """A health alert or warning."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    alert_type: str = ""  # stress_high, recovery_low, etc.
    severity: int = 1  # 1-5
    message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    acknowledged: bool = False
    resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HealthMonitor:
    """Monitors health and wellness metrics.

    Tracks stress, recovery, cognitive load, and
    generates health alerts when needed.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.metrics: List[HealthMetric] = []
        self.alerts: List[HealthAlert] = []

        self._load_data()

    def _load_data(self):
        """Load health data from disk."""
        data_file = self.data_dir / "health_data.json"
        if data_file.exists():
            try:
                data = json.loads(data_file.read_text())
                for m_data in data.get("metrics", []):
                    metric = HealthMetric(
                        id=m_data["id"],
                        metric_type=MetricType(m_data["metric_type"]),
                        value=m_data["value"],
                        unit=m_data.get("unit", ""),
                        timestamp=m_data["timestamp"],
                        source=m_data.get("source", ""),
                        notes=m_data.get("notes", ""),
                    )
                    self.metrics.append(metric)

                for a_data in data.get("alerts", []):
                    alert = HealthAlert(**a_data)
                    self.alerts.append(alert)
            except Exception as e:
                print(f"[HEALTH] Error loading data: {e}")

    def save(self):
        """Save health data to disk."""
        data_file = self.data_dir / "health_data.json"
        data = {
            "saved_at": datetime.now(UTC).isoformat(),
            "metrics": [m.to_dict() for m in self.metrics],
            "alerts": [a.to_dict() for a in self.alerts],
        }
        data_file.write_text(json.dumps(data, indent=2))

    def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        unit: str = "",
        source: str = "",
    ) -> HealthMetric:
        """Record a health metric."""
        metric = HealthMetric(
            metric_type=metric_type,
            value=value,
            unit=unit,
            source=source,
        )
        self.metrics.append(metric)

        # Check for alerts
        self._check_alerts(metric)

        self.save()
        return metric

    def _check_alerts(self, metric: HealthMetric):
        """Check if metric triggers any alerts."""
        # High stress alert
        if metric.metric_type == MetricType.STRESS and metric.value > 70:
            alert = HealthAlert(
                alert_type="stress_high",
                severity=3,
                message=f"High stress level detected: {metric.value}",
            )
            self.alerts.append(alert)

        # Low recovery alert
        if metric.metric_type == MetricType.RECOVERY and metric.value < 30:
            alert = HealthAlert(
                alert_type="recovery_low",
                severity=4,
                message=f"Low recovery rate: {metric.value}",
            )
            self.alerts.append(alert)

        # High cognitive load
        if metric.metric_type == MetricType.COGNITIVE_LOAD and metric.value > 80:
            alert = HealthAlert(
                alert_type="cognitive_overload",
                severity=3,
                message=f"High cognitive load: {metric.value}",
            )
            self.alerts.append(alert)

    def get_recent_metrics(
        self,
        metric_type: Optional[MetricType] = None,
        hours: int = 24,
    ) -> list[dict[str, Any]]:
        """Get recent metrics."""
        cutoff = (datetime.now(UTC) - timedelta(hours=hours)).isoformat()

        metrics = [m for m in self.metrics if m.timestamp > cutoff]
        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]

        return [m.to_dict() for m in metrics]

    def get_health_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get health summary for a period."""
        recent = self.get_recent_metrics(hours=hours)

        by_type = {}
        for m in recent:
            t = m["metric_type"]
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(m["value"])

        # Calculate averages
        summary = {}
        for t, values in by_type.items():
            summary[t] = {
                "average": round(sum(values) / len(values), 2),
                "min": min(values),
                "max": max(values),
                "samples": len(values),
            }

        return {
            "period_hours": hours,
            "metrics": summary,
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "overall_status": self._calculate_overall_status(summary),
        }

    def _calculate_overall_status(self, summary: dict) -> str:
        """Calculate overall health status."""
        stress_avg = summary.get("stress", {}).get("average", 50)
        recovery_avg = summary.get("recovery", {}).get("average", 50)

        # Simple scoring
        if stress_avg > 70 and recovery_avg < 30:
            return HealthStatus.POOR.value
        elif stress_avg > 50 or recovery_avg < 40:
            return HealthStatus.FAIR.value
        elif stress_avg < 30 and recovery_avg > 60:
            return HealthStatus.EXCELLENT.value
        else:
            return HealthStatus.GOOD.value

    def get_active_alerts(self) -> list[dict[str, Any]]:
        """Get active (unresolved) alerts."""
        active = [a for a in self.alerts if not a.resolved]
        return sorted(
            [a.to_dict() for a in active],
            key=lambda x: x["severity"],
            reverse=True,
        )

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                self.save()
                return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                self.save()
                return True
        return False

    def get_recommendations(self) -> List[str]:
        """Get health recommendations based on current state."""
        recs = []
        summary = self.get_health_summary()

        stress = summary["metrics"].get("stress", {}).get("average", 50)
        recovery = summary["metrics"].get("recovery", {}).get("average", 50)

        if stress > 60:
            recs.append("Consider stress reduction techniques: breaks, meditation")

        if recovery < 40:
            recs.append("Prioritize rest and recovery. Ensure adequate sleep.")

        if not recs:
            recs.append("Health metrics within normal ranges. Maintain current habits.")

        return recs


# Global instance
_MONITOR: Optional[HealthMonitor] = None


def get_health_monitor(data_dir: Optional[Path] = None) -> HealthMonitor:
    """Get or create global health monitor."""
    global _MONITOR
    if _MONITOR is None:
        _MONITOR = HealthMonitor(data_dir)
    return _MONITOR


if __name__ == "__main__":
    print("Health Monitor (10_LIFE_ENGINE)")
    print("=" * 40)

    monitor = get_health_monitor()

    # Record some sample metrics
    monitor.record_metric(MetricType.STRESS, 45, "percent")
    monitor.record_metric(MetricType.RECOVERY, 65, "percent")
    monitor.record_metric(MetricType.COGNITIVE_LOAD, 55, "percent")

    print("\nHealth Summary:")
    summary = monitor.get_health_summary()
    print(f"  Overall status: {summary['overall_status']}")
    print(f"  Active alerts: {summary['active_alerts']}")

    print("\nRecommendations:")
    for rec in monitor.get_recommendations():
        print(f"  - {rec}")
