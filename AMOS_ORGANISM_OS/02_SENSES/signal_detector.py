"""Signal Detector — External signal detection for AMOS."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class Signal:
    """An external signal."""

    id: str
    source: str  # filesystem, git, api, timer
    type: str  # change, alert, notification, heartbeat
    priority: str  # low, normal, high, critical
    data: Dict[str, Any]
    timestamp: str


class SignalDetector:
    """Detects external signals and events."""

    def __init__(self):
        self._signals: List[Signal] = []
        self._handlers: Dict[str, Any] = {}
        self._last_check = datetime.utcnow().isoformat()

    def detect(self, source: str = None) -> List[Signal]:
        """Detect signals from sources."""
        new_signals = []

        # Check filesystem changes
        if source is None or source == "filesystem":
            fs_signals = self._check_filesystem()
            new_signals.extend(fs_signals)

        # Check timer/heartbeat
        if source is None or source == "timer":
            timer_signals = self._check_timer()
            new_signals.extend(timer_signals)

        self._signals.extend(new_signals)
        self._last_check = datetime.utcnow().isoformat()

        return new_signals

    def _check_filesystem(self) -> List[Signal]:
        """Check for filesystem signals."""
        # Placeholder for filesystem monitoring
        return []

    def _check_timer(self) -> List[Signal]:
        """Check for timer-based signals."""
        import uuid

        return [
            Signal(
                id=str(uuid.uuid4())[:8],
                source="timer",
                type="heartbeat",
                priority="low",
                data={"interval": "scan"},
                timestamp=datetime.utcnow().isoformat(),
            )
        ]

    def get_signals(self, priority: str = None, limit: int = 50) -> List[Signal]:
        """Get detected signals."""
        signals = self._signals
        if priority:
            signals = [s for s in signals if s.priority == priority]
        return signals[-limit:]

    def acknowledge(self, signal_id: str) -> bool:
        """Acknowledge a signal."""
        for signal in self._signals:
            if signal.id == signal_id:
                self._signals.remove(signal)
                return True
        return False

    def status(self) -> Dict[str, Any]:
        """Get detector status."""
        return {
            "total_signals": len(self._signals),
            "by_source": self._count_by("source"),
            "by_priority": self._count_by("priority"),
            "last_check": self._last_check,
        }

    def _count_by(self, field: str) -> Dict[str, int]:
        """Count signals by field."""
        counts: Dict[str, int] = {}
        for signal in self._signals:
            key = getattr(signal, field)
            counts[key] = counts.get(key, 0) + 1
        return counts
