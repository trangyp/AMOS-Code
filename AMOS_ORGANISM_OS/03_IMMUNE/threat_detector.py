"""Threat Detector — Anomaly detection for AMOS."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Threat:
    """A detected threat."""

    id: str
    timestamp: str
    severity: str  # low, medium, high, critical
    category: str  # execution, access, pattern, anomaly
    description: str
    evidence: Dict[str, Any]


class ThreatDetector:
    """Detects threats and anomalies in organism behavior."""

    def __init__(self):
        self._threats: List[Threat] = []
        self._pattern_history: List[dict] = []
        self._anomaly_threshold = 3  # Consecutive anomalies to trigger alert

    def detect_anomaly(
        self,
        action: str,
        context: Dict[str, Any],
    ) -> List[Threat]:
        """Detect anomalies in an action."""
        threats = []

        # Check for rapid execution (potential attack)
        recent = [
            p
            for p in self._pattern_history
            if (datetime.now(UTC) - datetime.fromisoformat(p["time"])).seconds < 60
        ]
        if len(recent) > 10:
            threats.append(
                Threat(
                    id=f"threat_{len(self._threats)}",
                    timestamp=datetime.now(UTC).isoformat(),
                    severity="high",
                    category="anomaly",
                    description="Rapid action execution detected",
                    evidence={"actions_in_last_minute": len(recent)},
                )
            )

        # Check for unusual patterns
        if action not in [p["action"] for p in self._pattern_history[-100:]]:
            threats.append(
                Threat(
                    id=f"threat_{len(self._threats)}",
                    timestamp=datetime.now(UTC).isoformat(),
                    severity="low",
                    category="pattern",
                    description="Unusual action pattern",
                    evidence={"action": action},
                )
            )

        # Record pattern
        self._pattern_history.append(
            {
                "action": action,
                "time": datetime.now(UTC).isoformat(),
                "context": context,
            }
        )

        # Keep history manageable
        if len(self._pattern_history) > 1000:
            self._pattern_history = self._pattern_history[-500:]

        self._threats.extend(threats)
        return threats

    def get_threats(self, severity: str = None, limit: int = 50) -> List[Threat]:
        """Get detected threats."""
        threats = self._threats
        if severity:
            threats = [t for t in threats if t.severity == severity]
        return threats[-limit:]

    def status(self) -> Dict[str, Any]:
        """Get detector status."""
        return {
            "total_threats": len(self._threats),
            "by_severity": {
                "low": len([t for t in self._threats if t.severity == "low"]),
                "medium": len([t for t in self._threats if t.severity == "medium"]),
                "high": len([t for t in self._threats if t.severity == "high"]),
                "critical": len([t for t in self._threats if t.severity == "critical"]),
            },
            "pattern_history_size": len(self._pattern_history),
        }
