#!/usr/bin/env python3
"""AMOS Alert Manager - IMMUNE Subsystem Integration
=================================================

Integrates the alerting system into the IMMUNE subsystem for
anomaly-based alerting and notification management.

Owner: Trang
Version: 1.0.0
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Add repo root to path to import amos_alerting
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from amos_alerting import AlertRule, AlertSeverity, AMOSAlerting, SlackChannel, WebhookChannel


class AlertManager:
    """Alert manager for IMMUNE subsystem.
    Connects anomaly detection to alerting system.
    """

    def __init__(self, organism_root: Path):
        self.root = organism_root
        self.immune_dir = organism_root / "03_IMMUNE"
        self.alerting = AMOSAlerting()
        self._setup_default_rules()
        self._setup_default_channels()

    def _setup_default_rules(self):
        """Set up default alert rules."""
        default_rules = [
            AlertRule(
                name="high_subsystem_load",
                metric="subsystem_load",
                condition=">",
                threshold=80.0,
                severity=AlertSeverity.WARNING,
                duration_seconds=60,
                description="Subsystem load exceeded 80%",
            ),
            AlertRule(
                name="critical_subsystem_load",
                metric="subsystem_load",
                condition=">",
                threshold=95.0,
                severity=AlertSeverity.CRITICAL,
                duration_seconds=30,
                description="Critical: Subsystem load exceeded 95%",
            ),
            AlertRule(
                name="task_queue_backlog",
                metric="pending_tasks",
                condition=">",
                threshold=10.0,
                severity=AlertSeverity.WARNING,
                duration_seconds=300,
                description="Task queue has more than 10 pending tasks",
            ),
            AlertRule(
                name="anomaly_detected",
                metric="anomaly_count",
                condition=">",
                threshold=0.0,
                severity=AlertSeverity.WARNING,
                duration_seconds=0,
                description="Anomalies detected in system",
            ),
        ]

        for rule in default_rules:
            self.alerting.add_rule(rule)

    def _setup_default_channels(self):
        """Set up default notification channels."""
        # Console channel (always available)
        self.alerting.add_channel("console", ConsoleChannel())

    def evaluate_and_alert(self, metrics: dict[str, float]) -> list[dict[str, Any]]:
        """Evaluate metrics and send alerts if needed."""
        alerts = self.alerting.evaluate_rules(metrics)

        # Send notifications for new alerts
        for alert in alerts:
            if alert.status.value == "active":
                # Run async notification
                try:
                    asyncio.run(self._send_notifications(alert))
                except Exception as e:
                    print(f"[ALERT] Notification error: {e}")

        return [self._alert_to_dict(a) for a in alerts]

    async def _send_notifications(self, alert):
        """Send alert through all channels."""
        for name, channel in self.alerting.channels.items():
            try:
                await channel.send(alert)
            except Exception as e:
                print(f"[ALERT] Failed to send to {name}: {e}")

    def _alert_to_dict(self, alert) -> dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "id": alert.id,
            "rule_name": alert.rule_name,
            "severity": alert.severity.value,
            "status": alert.status.value,
            "message": alert.message,
            "value": alert.value,
            "threshold": alert.threshold,
            "timestamp": alert.timestamp.isoformat(),
        }

    def get_active_alerts(self) -> list[dict[str, Any]]:
        """Get all active alerts."""
        return [self._alert_to_dict(a) for a in self.alerting.active_alerts.values()]

    def get_alert_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get alert history."""
        history = self.alerting.alert_history[-limit:]
        return [self._alert_to_dict(a) for a in history]

    def acknowledge_alert(self, alert_id: str, user: str = "system") -> bool:
        """Acknowledge an alert."""
        for alert in self.alerting.active_alerts.values():
            if alert.id == alert_id:
                alert.status = self.alerting.AlertStatus.ACKNOWLEDGED
                alert.acknowledged_by = user
                alert.acknowledged_at = datetime.now()
                return True
        return False

    def add_webhook_channel(self, name: str, url: str, headers: Optional[dict] = None):
        """Add a webhook notification channel."""
        self.alerting.add_channel(name, WebhookChannel(url, headers))

    def add_slack_channel(self, name: str, webhook_url: str, channel: Optional[str] = None):
        """Add a Slack notification channel."""
        self.alerting.add_channel(name, SlackChannel(webhook_url, channel))

    def get_status(self) -> dict[str, Any]:
        """Get alert manager status."""
        return {
            "rules_configured": len(self.alerting.rules),
            "channels_configured": len(self.alerting.channels),
            "active_alerts": len(self.alerting.active_alerts),
            "total_alerts_ever": len(self.alerting.alert_history),
        }


class ConsoleChannel:
    """Console notification channel."""

    async def send(self, alert) -> bool:
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


def main():
    """CLI for Alert Manager."""
    print("=" * 50)
    print("AMOS Alert Manager")
    print("=" * 50)

    organism_root = Path(__file__).parent.parent
    manager = AlertManager(organism_root)

    # Show status
    status = manager.get_status()
    print("\nStatus:")
    print(f"  Rules: {status['rules_configured']}")
    print(f"  Channels: {status['channels_configured']}")
    print(f"  Active alerts: {status['active_alerts']}")

    # Demo: Evaluate some metrics
    print("\n" + "=" * 50)
    print("Demo: Evaluating sample metrics")
    print("=" * 50)

    test_metrics = {
        "subsystem_load": 85.0,  # Should trigger warning
        "pending_tasks": 15.0,  # Should trigger warning
        "anomaly_count": 2.0,  # Should trigger warning
    }

    alerts = manager.evaluate_and_alert(test_metrics)

    if alerts:
        print(f"\nGenerated {len(alerts)} alerts")
    else:
        print("\nNo alerts generated")

    # Show active alerts
    active = manager.get_active_alerts()
    print(f"\nActive alerts: {len(active)}")
    for alert in active:
        print(f"  - {alert['id']}: {alert['rule_name']} ({alert['severity']})")

    print("\n" + "=" * 50)
    print("Alert Manager ready")
    print("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(main())
