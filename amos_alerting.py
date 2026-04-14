"""AMOS Alerting - Production alerting system.

Monitors system health and metrics, sends alerts when thresholds are exceeded.
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from amos_health_monitor import HealthStatus, SystemHealth


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
            "resolved": self.resolved
        }


class AlertRule:
    """A rule that triggers alerts."""
    
    def __init__(
        self,
        name: str,
        severity: AlertSeverity,
        condition: Callable[[Any], bool],
        message_template: str
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
                timestamp=datetime.now()
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
        self.add_rule(AlertRule(
            name="component_unhealthy",
            severity=AlertSeverity.CRITICAL,
            condition=lambda health: any(
                c.status == "unhealthy" for c in health.components
            ),
            message_template="Component is unhealthy: {}"
        ))
        
        self.add_rule(AlertRule(
            name="high_error_rate",
            severity=AlertSeverity.WARNING,
            condition=lambda metrics: metrics.get("error_rate", 0) > 5,
            message_template="High error rate detected: {}%"
        ))
        
        self.add_rule(AlertRule(
            name="slow_response_time",
            severity=AlertSeverity.WARNING,
            condition=lambda metrics: metrics.get("avg_response_time_ms", 0) > 1000,
            message_template="Slow response time: {}ms average"
        ))
    
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
            "alerts": [a.to_dict() for a in active[:10]]
        }
    
    def _save_alerts(self):
        """Save alert history to file."""
        data = {
            "active": [a.to_dict() for a in self.active_alerts.values()],
            "history": [a.to_dict() for a in self.alert_history[-100:]]
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


async def monitor_loop(check_interval: int = 60):
    """Run continuous monitoring loop."""
    from amos_health_monitor import get_health_monitor
    from amos_metrics_collector import get_collector
    
    health_monitor = get_health_monitor()
    alert_manager = get_alert_manager()
    collector = get_collector()
    
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


if __name__ == "__main__":
    # Run monitoring loop
    print("Starting AMOS Alert Monitor...")
    asyncio.run(monitor_loop())
