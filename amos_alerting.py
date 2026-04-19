"""AMOS Alerting - Production alerting system.

Monitors system health and metrics, sends alerts when thresholds are exceeded.
"""


import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from amos_health_monitor import SystemHealth


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """An alert notification."""

    id: str
    severity: AlertSeverity
    component: str
    message: str
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "severity": self.severity.value,
            "component": self.component,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
            "resolved": self.resolved,
        }


class AlertRule:
    """A rule that triggers alerts."""

    def __init__(
        self,
        name: str,
        severity: AlertSeverity,
        condition: Callable[[Any], bool],
        message_template: str,
    ):
        self.name = name
        self.severity = severity
        self.condition = condition
        self.message_template = message_template

    def check(self, data: Any) -> Optional[Alert]:
        """Check if alert should be triggered."""
        if self.condition(data):
            return Alert(
                id=f"{self.name}_{datetime.now().timestamp()}",
                severity=self.severity,
                component=self.name,
                message=self.message_template.format(data),
                timestamp=datetime.now(),
            )
        return None


class AlertManager:
    """Manages alerts and notifications."""

    def __init__(self, alert_file: str = "AMOS_ORGANISM_OS/alerts.json"):
        self.alert_file = Path(alert_file)
        self.rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default alerting rules."""
        # Health check rules
        self.add_rule(
            AlertRule(
                name="component_unhealthy",
                severity=AlertSeverity.CRITICAL,
                condition=lambda health: any(c.status == "unhealthy" for c in health.components),
                message_template="Component is unhealthy: {}",
            )
        )

        self.add_rule(
            AlertRule(
                name="high_error_rate",
                severity=AlertSeverity.WARNING,
                condition=lambda metrics: metrics.get("error_rate", 0) > 5,
                message_template="High error rate detected: {}%",
            )
        )

        self.add_rule(
            AlertRule(
                name="slow_response_time",
                severity=AlertSeverity.WARNING,
                condition=lambda metrics: metrics.get("avg_response_time_ms", 0) > 1000,
                message_template="Slow response time: {}ms average",
            )
        )

    def add_rule(self, rule: AlertRule):
        """Add an alert rule."""
        self.rules.append(rule)

    def check_health(self, health: SystemHealth) -> List[Alert]:
        """Check health data against rules."""
        triggered = []

        for rule in self.rules:
            alert = rule.check(health)
            if alert and alert.id not in self.active_alerts:
                self.active_alerts[alert.id] = alert
                triggered.append(alert)

        return triggered

    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert."""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True

    def resolve_alert(self, alert_id: str):
        """Resolve an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts.pop(alert_id)
            alert.resolved = True
            self.alert_history.append(alert)
            self._save_alerts()

    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get active alerts, optionally filtered by severity."""
        alerts = list(self.active_alerts.values())
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of alert status."""
        active = self.get_active_alerts()
        return {
            "total_active": len(active),
            "critical": sum(1 for a in active if a.severity == AlertSeverity.CRITICAL),
            "warning": sum(1 for a in active if a.severity == AlertSeverity.WARNING),
            "info": sum(1 for a in active if a.severity == AlertSeverity.INFO),
            "alerts": [a.to_dict() for a in active[:10]],
        }

    def _save_alerts(self):
        """Save alert history to file."""
        data = {
            "active": [a.to_dict() for a in self.active_alerts.values()],
            "history": [a.to_dict() for a in self.alert_history[-100:]],
        }
        with open(self.alert_file, "w") as f:
            json.dump(data, f, indent=2)


# Global alert manager
_alert_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """Get global alert manager."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager


def init_default_alerting() -> AlertManager:
    """Initialize default alerting configuration."""
    manager = get_alert_manager()
    return manager


async def monitor_loop(check_interval: int = 60):
    """Run continuous monitoring loop."""
    from amos_health_monitor import get_health_monitor
    from amos_metrics_collector import get_metrics_collector

    health_monitor = get_health_monitor()
    alert_manager = get_alert_manager()
    _ = get_metrics_collector()

    while True:
        try:
            # Check health
            health = await health_monitor.check_all()
            alerts = alert_manager.check_health(health)

            if alerts:
                for alert in alerts:
                    print(f"🚨 ALERT: [{alert.severity.value.upper()}] {alert.message}")

            # Save health report
            health_monitor.save_report()

        except Exception as e:
            print(f"Monitor loop error: {e}")

        await asyncio.sleep(check_interval)


class AlertStatus(Enum):
    """Alert status enumeration."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


@dataclass
class BaseAlert:
    """Base alert class for metric-based alerting."""
    id: str
    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    value: float
    threshold: float
    timestamp: datetime
    acknowledged_by: str  = None
    acknowledged_at: datetime  = None


@dataclass
class MetricAlertRule:
    """Alert rule for metric-based threshold alerting."""
    name: str
    metric: str
    condition: str  # '>', '<', '==', '>=', '<='
    threshold: float
    severity: AlertSeverity
    duration_seconds: int
    description: str

    def check(self, metric_value: float) -> bool:
        """Check if metric value triggers this rule."""
        if self.condition == ">":
            return metric_value > self.threshold
        elif self.condition == "<":
            return metric_value < self.threshold
        elif self.condition == ">=":
            return metric_value >= self.threshold
        elif self.condition == "<=":
            return metric_value <= self.threshold
        elif self.condition == "==":
            return metric_value == self.threshold
        return False


class ConsoleChannel:
    """Console notification channel."""

    async def send(self, alert: BaseAlert) -> bool:
        """Print alert to console."""
        severity_icon = {"info": "ℹ️", "warning": "⚠️", "critical": "🔴"}.get(
            alert.severity.value, "ℹ️"
        )
        print(f"\n[ALERT] {severity_icon} {alert.severity.value.upper()}")
        print(f"  Rule: {alert.rule_name}")
        print(f"  Message: {alert.message}")
        print(f"  Value: {alert.value} (threshold: {alert.threshold})")
        print(f"  Time: {alert.timestamp.isoformat()}")
        return True


class WebhookChannel:
    """Webhook notification channel."""

    def __init__(self, url: str, headers: dict  = None):
        self.url = url
        self.headers = headers or {}

    async def send(self, alert: BaseAlert) -> bool:
        """Send alert to webhook."""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "rule": alert.rule_name,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "value": alert.value,
                    "threshold": alert.threshold,
                    "timestamp": alert.timestamp.isoformat(),
                }
                async with session.post(self.url, json=payload, headers=self.headers) as resp:
                    return resp.status == 200
        except Exception as e:
            print(f"[Webhook] Failed to send: {e}")
            return False


class SlackChannel:
    """Slack notification channel."""

    def __init__(self, webhook_url: str, channel: str  = None):
        self.webhook_url = webhook_url
        self.channel = channel

    async def send(self, alert: BaseAlert) -> bool:
        """Send alert to Slack."""
        import aiohttp
from typing import Callable
        try:
            async with aiohttp.ClientSession() as session:
                text = f"*{alert.severity.value.upper()}*: {alert.message}\n"
                text += f"Value: `{alert.value}` (threshold: `{alert.threshold}`)\n"
                text += f"Rule: `{alert.rule_name}`"

                payload = {"text": text}
                if self.channel:
                    payload["channel"] = self.channel

                async with session.post(self.webhook_url, json=payload) as resp:
                    return resp.status == 200
        except Exception as e:
            print(f"[Slack] Failed to send: {e}")
            return False


class AMOSAlerting:
    """Main alerting system for metric-based rules."""

    def __init__(self):
        self.rules: List[MetricAlertRule] = []
        self.channels: Dict[str, Any] = {}
        self.active_alerts: Dict[str, BaseAlert] = {}
        self.alert_history: List[BaseAlert] = []

    def add_rule(self, rule: MetricAlertRule):
        """Add an alert rule."""
        self.rules.append(rule)

    def add_channel(self, name: str, channel: Any):
        """Add a notification channel."""
        self.channels[name] = channel

    def evaluate_rules(self, metrics: Dict[str, float]) -> List[BaseAlert]:
        """Evaluate all rules against current metrics."""
        triggered = []

        for rule in self.rules:
            metric_value = metrics.get(rule.metric)
            if metric_value is not None:
                if rule.check(metric_value):
                    # Check if we already have an active alert for this rule
                    existing = False
                    for alert in self.active_alerts.values():
                        if alert.rule_name == rule.name and alert.status == AlertStatus.ACTIVE:
                            existing = True
                            break

                    if not existing:
                        alert_id = f"{rule.name}_{datetime.now().timestamp()}"
                        alert = BaseAlert(
                            id=alert_id,
                            rule_name=rule.name,
                            severity=rule.severity,
                            status=AlertStatus.ACTIVE,
                            message=rule.description,
                            value=metric_value,
                            threshold=rule.threshold,
                            timestamp=datetime.now(),
                        )
                        self.active_alerts[alert_id] = alert
                        triggered.append(alert)

        return triggered

    def acknowledge_alert(self, alert_id: str, user: str = "system"):
        """Acknowledge an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = user
            alert.acknowledged_at = datetime.now()

    def resolve_alert(self, alert_id: str):
        """Resolve an alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts.pop(alert_id)
            alert.status = AlertStatus.RESOLVED
            self.alert_history.append(alert)

    def get_active_alerts(self) -> List[BaseAlert]:
        """Get all active alerts."""
        return [a for a in self.active_alerts.values() if a.status == AlertStatus.ACTIVE]


if __name__ == "__main__":
    # Run monitoring loop
    print("Starting AMOS Alert Monitor...")
    asyncio.run(monitor_loop())
