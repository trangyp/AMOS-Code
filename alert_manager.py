"""Alert Manager stub for compatibility."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class Alert:
    """Represents an alert."""

    id: str
    level: str  # info, warning, error, critical
    message: str
    source: str
    timestamp: datetime
    metadata: Dict[str, Any]


class AlertManager:
    """Manager for system alerts."""

    def __init__(self):
        self.alerts: List[Alert] = []
        self.handlers: List[Callable] = []

    def add_handler(self, handler: Callable) -> None:
        """Add alert handler."""
        self.handlers.append(handler)

    def create_alert(
        self,
        level: str,
        message: str,
        source: str = "system",
        metadata: Dict[str, Any] = None,
    ) -> Alert:
        """Create new alert."""
        alert = Alert(
            id=f"alert-{len(self.alerts)}",
            level=level,
            message=message,
            source=source,
            timestamp=datetime.now(),
            metadata=metadata or {},
        )
        self.alerts.append(alert)
        return alert

    def get_alerts(self, level: str = None) -> List[Alert]:
        """Get alerts, optionally filtered by level."""
        if level:
            return [a for a in self.alerts if a.level == level]
        return self.alerts.copy()


# Default instance
default_manager = AlertManager()

__all__ = ["Alert", "AlertManager", "default_manager"]
