"""Geopolitical Monitor — Political stability and global events

Tracks geopolitical events, regional stability, and
global risk factors affecting AMOS operations.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class RiskLevel(Enum):
    """Risk severity levels."""

    LOW = 1
    MODERATE = 2
    ELEVATED = 3
    HIGH = 4
    SEVERE = 5


class EventType(Enum):
    """Types of geopolitical events."""

    ELECTION = "election"
    CONFLICT = "conflict"
    TRADE_POLICY = "trade_policy"
    REGULATION = "regulation"
    DIPLOMATIC = "diplomatic"
    ECONOMIC = "economic"
    SECURITY = "security"


@dataclass
class GeopoliticalEvent:
    """A geopolitical event."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    event_type: EventType = EventType.DIPLOMATIC
    title: str = ""
    description: str = ""
    region: str = ""  # country, region, or global
    risk_level: RiskLevel = RiskLevel.LOW
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    expected_duration_days: int = 1
    affected_sectors: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    resolved: bool = False
    resolution_time: str = None

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "event_type": self.event_type.value,
            "risk_level": self.risk_level.value,
        }


@dataclass
class RegionalStability:
    """Stability metrics for a region."""

    region: str = ""
    stability_score: float = 0.5  # 0-1, higher is more stable
    trend: str = "stable"  # improving, deteriorating, stable
    active_events: int = 0
    last_updated: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class GeopoliticalMonitor:
    """Monitors geopolitical conditions and risks.

    Tracks events, assesses regional stability, and
    provides risk assessment for operations.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.events: list[GeopoliticalEvent] = []
        self.regional_stability: dict[str, RegionalStability] = {}

        self._load_data()

    def _load_data(self):
        """Load geopolitical data from disk."""
        data_file = self.data_dir / "geopolitical_data.json"
        if data_file.exists():
            try:
                data = json.loads(data_file.read_text())
                for evt_data in data.get("events", []):
                    evt = GeopoliticalEvent(
                        id=evt_data["id"],
                        event_type=EventType(evt_data["event_type"]),
                        title=evt_data["title"],
                        description=evt_data["description"],
                        region=evt_data["region"],
                        risk_level=RiskLevel(evt_data["risk_level"]),
                        timestamp=evt_data["timestamp"],
                        expected_duration_days=evt_data.get("expected_duration_days", 1),
                        affected_sectors=evt_data.get("affected_sectors", []),
                        sources=evt_data.get("sources", []),
                        resolved=evt_data.get("resolved", False),
                        resolution_time=evt_data.get("resolution_time"),
                    )
                    self.events.append(evt)

                for region, stab_data in data.get("regional_stability", {}).items():
                    self.regional_stability[region] = RegionalStability(
                        region=stab_data["region"],
                        stability_score=stab_data["stability_score"],
                        trend=stab_data["trend"],
                        active_events=stab_data["active_events"],
                        last_updated=stab_data["last_updated"],
                    )
            except Exception as e:
                print(f"[GEOPOLITICAL] Error loading data: {e}")

    def save(self):
        """Save geopolitical data to disk."""
        data_file = self.data_dir / "geopolitical_data.json"
        data = {
            "saved_at": datetime.now(UTC).isoformat(),
            "events": [e.to_dict() for e in self.events],
            "regional_stability": {r: s.to_dict() for r, s in self.regional_stability.items()},
        }
        data_file.write_text(json.dumps(data, indent=2))

    def record_event(self, event: GeopoliticalEvent) -> GeopoliticalEvent:
        """Record a new geopolitical event."""
        self.events.append(event)
        self._update_regional_stability(event.region)
        self.save()
        return event

    def _update_regional_stability(self, region: str):
        """Update stability metrics for a region."""
        active = [e for e in self.events if e.region == region and not e.resolved]

        # Calculate stability score
        if not active:
            score = 0.9
        else:
            total_risk = sum(e.risk_level.value for e in active)
            score = max(0.1, 1.0 - (total_risk / (len(active) * 5)))

        # Determine trend
        prev = self.regional_stability.get(region)
        if prev:
            if score > prev.stability_score + 0.1:
                trend = "improving"
            elif score < prev.stability_score - 0.1:
                trend = "deteriorating"
            else:
                trend = "stable"
        else:
            trend = "stable"

        self.regional_stability[region] = RegionalStability(
            region=region,
            stability_score=score,
            trend=trend,
            active_events=len(active),
        )

    def resolve_event(self, event_id: str) -> bool:
        """Mark an event as resolved."""
        for event in self.events:
            if event.id == event_id and not event.resolved:
                event.resolved = True
                event.resolution_time = datetime.now(UTC).isoformat()
                self._update_regional_stability(event.region)
                self.save()
                return True
        return False

    def get_active_events(
        self,
        region: str = None,
        risk_threshold: RiskLevel = RiskLevel.LOW,
    ) -> list[dict[str, Any]]:
        """Get active events matching criteria."""
        events = [
            e for e in self.events if not e.resolved and e.risk_level.value >= risk_threshold.value
        ]

        if region:
            events = [e for e in events if e.region == region]

        return sorted(
            [e.to_dict() for e in events],
            key=lambda x: x["risk_level"],
            reverse=True,
        )

    def assess_risk(self, regions: list[str]) -> dict[str, Any]:
        """Assess geopolitical risk for given regions."""
        region_risks = {}
        total_risk = 0

        for region in regions:
            stab = self.regional_stability.get(region)
            if stab:
                # Convert stability to risk (inverse)
                risk = 1.0 - stab.stability_score
                region_risks[region] = {
                    "risk_score": risk,
                    "stability": stab.stability_score,
                    "trend": stab.trend,
                    "active_events": stab.active_events,
                }
                total_risk += risk
            else:
                region_risks[region] = {"risk_score": 0.5, "note": "No data available"}
                total_risk += 0.5

        avg_risk = total_risk / len(regions) if regions else 0.5

        return {
            "overall_risk": avg_risk,
            "risk_level": self._risk_to_level(avg_risk).name,
            "by_region": region_risks,
            "recommendation": self._get_recommendation(avg_risk),
        }

    def _risk_to_level(self, risk_score: float) -> RiskLevel:
        """Convert risk score to level."""
        if risk_score < 0.2:
            return RiskLevel.LOW
        elif risk_score < 0.4:
            return RiskLevel.MODERATE
        elif risk_score < 0.6:
            return RiskLevel.ELEVATED
        elif risk_score < 0.8:
            return RiskLevel.HIGH
        return RiskLevel.SEVERE

    def _get_recommendation(self, risk_score: float) -> str:
        """Get recommendation based on risk."""
        if risk_score < 0.3:
            return "Normal operations"
        elif risk_score < 0.5:
            return "Monitor closely, maintain contingency plans"
        elif risk_score < 0.7:
            return "Reduce exposure, increase monitoring"
        return "Consider suspending operations in high-risk regions"

    def get_global_summary(self) -> dict[str, Any]:
        """Get global geopolitical summary."""
        active = [e for e in self.events if not e.resolved]
        by_type = {}
        for e in active:
            t = e.event_type.value
            by_type[t] = by_type.get(t, 0) + 1

        by_region = {}
        for region, stab in self.regional_stability.items():
            by_region[region] = stab.to_dict()

        return {
            "total_active_events": len(active),
            "by_event_type": by_type,
            "regional_stability": by_region,
            "highest_risk_regions": self._get_highest_risk(),
            "updated_at": datetime.now(UTC).isoformat(),
        }

    def _get_highest_risk(self, n: int = 3) -> list[dict[str, Any]]:
        """Get regions with highest risk."""
        regions = sorted(
            self.regional_stability.values(),
            key=lambda x: x.stability_score,
        )
        return [r.to_dict() for r in regions[:n]]


# Global instance
_MONITOR: Optional[GeopoliticalMonitor] = None


def get_geopolitical_monitor(data_dir: Optional[Path] = None) -> GeopoliticalMonitor:
    """Get or create global geopolitical monitor."""
    global _MONITOR
    if _MONITOR is None:
        _MONITOR = GeopoliticalMonitor(data_dir)
    return _MONITOR


if __name__ == "__main__":
    print("Geopolitical Monitor (08_WORLD_MODEL)")
    print("=" * 40)

    monitor = get_geopolitical_monitor()

    # Add sample event
    event = GeopoliticalEvent(
        event_type=EventType.TRADE_POLICY,
        title="New Trade Agreement",
        description="Regional trade agreement signed",
        region="APAC",
        risk_level=RiskLevel.LOW,
        affected_sectors=["trade", "manufacturing"],
    )
    monitor.record_event(event)

    print(f"\nActive events: {len(monitor.get_active_events())}")
    print(f"Regions tracked: {len(monitor.regional_stability)}")
