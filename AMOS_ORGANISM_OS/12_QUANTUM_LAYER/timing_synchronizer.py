"""Timing Synchronizer for AMOS"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC, timedelta
from pathlib import Path
from typing import Any, Optional


@dataclass
class SynchronicityEvent:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    significance: float = 0.5  # 0-1
    related_events: list[str] = field(default_factory=list)
    context: str = ""

    def to_dict(self):
        return asdict(self)


class TimingSynchronizer:
    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(__file__).parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.events: list[SynchronicityEvent] = []
        self._load_data()

    def _load_data(self):
        f = self.data_dir / "timing.json"
        if f.exists():
            try:
                data = json.loads(f.read_text())
                for e in data.get("events", []):
                    self.events.append(SynchronicityEvent(**e))
            except Exception:
                pass

    def save(self):
        f = self.data_dir / "timing.json"
        f.write_text(
            json.dumps(
                {
                    "saved_at": datetime.now(UTC).isoformat(),
                    "events": [e.to_dict() for e in self.events],
                },
                indent=2,
            )
        )

    def record_event(
        self, description: str, significance: float = 0.5, context: str = ""
    ) -> SynchronicityEvent:
        event = SynchronicityEvent(
            description=description, significance=significance, context=context
        )
        self.events.append(event)
        self.save()
        return event

    def find_patterns(self, hours: int = 24) -> list[dict[str, Any]]:
        cutoff = (datetime.now(UTC) - timedelta(hours=hours)).isoformat()
        recent = [e for e in self.events if e.timestamp > cutoff]
        by_context = {}
        for e in recent:
            by_context[e.context] = by_context.get(e.context, 0) + 1
        return [{"context": c, "frequency": n} for c, n in by_context.items() if n > 1]

    def get_optimal_timing(self, action_type: str) -> dict[str, Any]:
        # Simple heuristic based on patterns
        patterns = self.find_patterns(168)  # 1 week
        relevant = [p for p in patterns if action_type in p["context"]]
        if relevant:
            return {
                "confidence": 0.7,
                "recommendation": f"Optimal timing for {action_type} based on patterns",
            }
        return {"confidence": 0.5, "recommendation": "Insufficient data for timing optimization"}


_MANAGER: Optional[TimingSynchronizer] = None


def get_timing_synchronizer(data_dir=None):
    global _MANAGER
    if _MANAGER is None:
        _MANAGER = TimingSynchronizer(data_dir)
    return _MANAGER
