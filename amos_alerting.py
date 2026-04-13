#!/usr/bin/env python3
"""AMOS Alerting System - Production Alerts and Notifications

Features:
- Alert rules based on metrics thresholds
- Multiple notification channels (webhook, email, slack)
- Alert history and acknowledgment
- Escalation policies
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


@dataclass
class AlertRule:
    name: str
    metric: str
    condition: str
    threshold: float
    severity: AlertSeverity
    duration_seconds: int
    description: str
    enabled: bool = True


@dataclass
class Alert:
    id: str
    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    value: float
    threshold: float
    timestamp: datetime
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class NotificationChannel:
    """Base class for notification channels."""
    
    async def send(self, alert: Alert) -> bool:
        raise NotImplementedError


class WebhookChannel(NotificationChannel):
    """Send alerts via HTTP webhook."""
    
    def __init__(self, url: str, headers: Optional[Dict] = None):
        self.url = url
        self.headers = headers or {}
    
    async def send(self, alert: Alert) -> bool:
        try:
            payload = {
                "alert_id": alert.id,
                "rule": alert.rule_name,
                "severity": alert.severity.value,
                "message": alert.message,
                "value": alert.value,
                "threshold": alert.threshold,
                "timestamp": alert.timestamp.isoformat(),
                "status": alert.status.value
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
            return False


class SlackChannel(NotificationChannel):
    """Send alerts to Slack."""
    
    def __init__(self, webhook_url: str, channel: Optional[str] = None):
        self.webhook_url = webhook_url
        self.channel = channel
    
    async def send(self, alert: Alert) -> bool:
        try:
            color = {
                AlertSeverity.INFO: "#36a64f",
                AlertSeverity.WARNING: "#ff9900",
                AlertSeverity.CRITICAL: "#ff0000"
            }.get(alert.severity, "#808080")
            
            payload = {
                "attachments": [{
                    "color": color,
                    "title": f"AMOS Alert: {alert.rule_name}",
                    "text": alert.message,
                    "fields": [
                        {"title": "Severity", "value": alert.severity.value, "short": True},
                        {"title": "Value", "value": str(alert.value), "short": True},
                        {"title": "Threshold", "value": str(alert.threshold), "short": True},
                        {"title": "Status", "value": alert.status.value, "short": True}
                    ],
                    "footer": "AMOS Monitoring",
                    "ts": int(alert.timestamp.timestamp())
                }]
            }
            
            if self.channel:
                payload["channel"] = self.channel
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Slack notification failed: {e}")
            return False


class AMOSAlerting:
    """Production alerting system for AMOS Brain."""
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.channels: Dict[str, NotificationChannel] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.max_history = 1000
        self._alert_counter = 0
        self._rule_states: Dict[str, Dict] = {}
    
    def add_rule(self, rule: AlertRule):
        """Add an alert rule."""
        self.rules.append(rule)
        logger.info(f"Added alert rule: {rule.name}")
    
    def add_channel(self, name: str, channel: NotificationChannel):
        """Add a notification channel."""
        self.channels[name] = channel
        logger.info(f"Added notification channel: {name}")
    
    def evaluate_rules(self, metrics: Dict[str, float]) -> List[Alert]:
        """Evaluate all rules against current metrics."""
        new_alerts = []
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            value = metrics.get(rule.metric)
            if value is None:
                continue
            
            triggered = self._check_condition(value, rule.condition, rule.threshold)
            
            if triggered:
                # Check if this is a new alert or continuing
                existing = self.active_alerts.get(rule.name)
                
                if existing is None:
                    # New alert
                    self._alert_counter += 1
                    alert = Alert(
                        id=f"ALT-{self._alert_counter:04d}",
                        rule_name=rule.name,
                        severity=rule.severity,
                        status=AlertStatus.ACTIVE,
                        message=f"{rule.description}: {value} (threshold: {rule.threshold})",
                        value=value,
                        threshold=rule.threshold,
                        timestamp=datetime.utcnow()
                    )
                    
                    self.active_alerts[rule.name] = alert
                    new_alerts.append(alert)
                    logger.warning(f"Alert triggered: {rule.name}")
        
        # Check for resolved alerts
        resolved = []
        for rule_name, alert in list(self.active_alerts.items()):
            rule = next((r for r in self.rules if r.name == rule_name), None)
            if rule:
                value = metrics.get(rule.metric)
                if value is not None:
                    still_triggered = self._check_condition(value, rule.condition, rule.threshold)
                    if not still_triggered:
                        alert.status = AlertStatus.RESOLVED
                        alert.resolved_at = datetime.utcnow()
                        resolved.append(alert)
                        del self.active_alerts[rule_name]
                        self.alert_history.append(alert)
                        logger.info(f"Alert resolved: {rule_name}")
        
        # Cleanup history
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]
        
        return new_alerts
    
    def _check_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Check if condition is met."""
        if condition == ">":
            return value > threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<":
            return value < threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return value == threshold
        return False
    
    async def send_notifications(self, alerts: List[Alert]):
        """Send notifications for alerts."""
        for alert in alerts:
            for name, channel in self.channels.items():
                success = await channel.send(alert)
                if success:
                    logger.info(f"Alert {alert.id} sent via {name}")
                else:
                    logger.error(f"Failed to send alert {alert.id} via {name}")
    
    def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.active_alerts.values():
            if alert.id == alert_id:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_by = user
                alert.acknowledged_at = datetime.utcnow()
                logger.info(f"Alert {alert_id} acknowledged by {user}")
                return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [a for a in self.alert_history if a.timestamp > cutoff]
    
    def to_dict(self) -> Dict:
        """Convert alerting state to dict."""
        return {
            "rules_count": len(self.rules),
            "channels_count": len(self.channels),
            "active_alerts": len(self.active_alerts),
            "total_history": len(self.alert_history),
            "active": [
                {
                    "id": a.id,
                    "rule": a.rule_name,
                    "severity": a.severity.value,
                    "status": a.status.value,
                    "message": a.message,
                    "timestamp": a.timestamp.isoformat()
                }
                for a in self.active_alerts.values()
            ]
        }


def init_default_alerting() -> AMOSAlerting:
    """Initialize default alerting configuration."""
    alerting = AMOSAlerting()
    
    # Default alert rules
    alerting.add_rule(AlertRule(
        name="high_error_rate",
        metric="error_rate",
        condition=">",
        threshold=5.0,
        severity=AlertSeverity.WARNING,
        duration_seconds=300,
        description="Error rate exceeds 5%"
    ))
    
    alerting.add_rule(AlertRule(
        name="critical_error_rate",
        metric="error_rate",
        condition=">",
        threshold=10.0,
        severity=AlertSeverity.CRITICAL,
        duration_seconds=60,
        description="Critical: Error rate exceeds 10%"
    ))
    
    alerting.add_rule(AlertRule(
        name="high_latency",
        metric="avg_response_time_ms",
        condition=">",
        threshold=1000.0,
        severity=AlertSeverity.WARNING,
        duration_seconds=180,
        description="Average response time exceeds 1 second"
    ))
    
    alerting.add_rule(AlertRule(
        name="memory_critical",
        metric="memory_usage_percent",
        condition=">",
        threshold=90.0,
        severity=AlertSeverity.CRITICAL,
        duration_seconds=60,
        description="Memory usage exceeds 90%"
    ))
    
    return alerting


if __name__ == "__main__":
    # Test alerting
    alerting = init_default_alerting()
    
    # Simulate metrics
    test_metrics = {
        "error_rate": 12.5,
        "avg_response_time_ms": 500,
        "memory_usage_percent": 85
    }
    
    alerts = alerting.evaluate_rules(test_metrics)
    print(f"Triggered {len(alerts)} alerts")
    
    for alert in alerts:
        print(f"  - {alert.id}: {alert.rule_name} ({alert.severity.value})")
    
    print("\nAlerting state:")
    print(json.dumps(alerting.to_dict(), indent=2))
