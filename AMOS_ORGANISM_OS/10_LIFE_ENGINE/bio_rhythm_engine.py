"""Bio Rhythm Engine — Circadian cycles and energy management

Tracks biological rhythms, sleep cycles, and energy states
to optimize cognitive performance.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class CircadianPhase(Enum):
    """Phases of the circadian cycle."""

    DEEP_SLEEP = "deep_sleep"
    LIGHT_SLEEP = "light_sleep"
    REM_SLEEP = "rem_sleep"
    WAKE_UP = "wake_up"
    MORNING = "morning"
    MIDDAY = "midday"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    WIND_DOWN = "wind_down"


class EnergyState(Enum):
    """Energy level states."""

    EXHAUSTED = 1
    VERY_TIRED = 2
    TIRED = 3
    MODERATE = 4
    GOOD = 5
    HIGH = 6
    PEAK = 7


@dataclass
class SleepSession:
    """A sleep session record."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    start_time: str = ""
    end_time: str = None
    duration_minutes: int = 0
    quality_score: float = 0.0  # 0-1
    phases: list[dict[str, Any]] = field(default_factory=list)
    interruptions: int = 0
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EnergyLog:
    """Energy level at a point in time."""

    timestamp: str
    level: int  # 1-7
    state: EnergyState
    activity: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "state": self.state.name,
        }


class BioRhythmEngine:
    """Manages biological rhythms and energy cycles.

    Tracks sleep patterns, circadian rhythms, and
    provides energy optimization recommendations.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.sleep_sessions: List[SleepSession] = []
        self.energy_logs: List[EnergyLog] = []
        self.circadian_phase: CircadianPhase = CircadianPhase.MORNING

        self._load_data()

    def _load_data(self):
        """Load bio rhythm data from disk."""
        data_file = self.data_dir / "bio_rhythm.json"
        if data_file.exists():
            try:
                data = json.loads(data_file.read_text())
                for s_data in data.get("sleep_sessions", []):
                    session = SleepSession(**s_data)
                    self.sleep_sessions.append(session)

                for e_data in data.get("energy_logs", []):
                    log = EnergyLog(
                        timestamp=e_data["timestamp"],
                        level=e_data["level"],
                        state=EnergyState[e_data["state"]],
                        activity=e_data.get("activity", ""),
                        notes=e_data.get("notes", ""),
                    )
                    self.energy_logs.append(log)
            except Exception as e:
                print(f"[BIO_RHYTHM] Error loading data: {e}")

    def save(self):
        """Save bio rhythm data to disk."""
        data_file = self.data_dir / "bio_rhythm.json"
        data = {
            "saved_at": datetime.now(UTC).isoformat(),
            "sleep_sessions": [s.to_dict() for s in self.sleep_sessions],
            "energy_logs": [e.to_dict() for e in self.energy_logs],
        }
        data_file.write_text(json.dumps(data, indent=2))

    def start_sleep_session(self) -> SleepSession:
        """Start tracking a sleep session."""
        session = SleepSession(
            start_time=datetime.now(UTC).isoformat(),
        )
        self.sleep_sessions.append(session)
        self.save()
        return session

    def end_sleep_session(self, session_id: str, quality: float = 0.5) -> Optional[SleepSession]:
        """End a sleep session."""
        for session in self.sleep_sessions:
            if session.id == session_id and session.end_time is None:
                session.end_time = datetime.now(UTC).isoformat()

                # Calculate duration
                start = datetime.fromisoformat(session.start_time)
                end = datetime.fromisoformat(session.end_time)
                session.duration_minutes = int((end - start).total_seconds() / 60)
                session.quality_score = quality

                self.save()
                return session
        return None

    def log_energy(self, level: int, activity: str = "", notes: str = "") -> EnergyLog:
        """Log current energy level (1-7)."""
        level = max(1, min(7, level))
        state = EnergyState(level)

        log = EnergyLog(
            timestamp=datetime.now(UTC).isoformat(),
            level=level,
            state=state,
            activity=activity,
            notes=notes,
        )
        self.energy_logs.append(log)
        self.save()
        return log

    def get_current_circadian_phase(self) -> CircadianPhase:
        """Determine current circadian phase based on time."""
        hour = datetime.now(UTC).hour

        if 0 <= hour < 4:
            return CircadianPhase.DEEP_SLEEP
        elif 4 <= hour < 6:
            return CircadianPhase.REM_SLEEP
        elif 6 <= hour < 8:
            return CircadianPhase.WAKE_UP
        elif 8 <= hour < 11:
            return CircadianPhase.MORNING
        elif 11 <= hour < 14:
            return CircadianPhase.MIDDAY
        elif 14 <= hour < 17:
            return CircadianPhase.AFTERNOON
        elif 17 <= hour < 20:
            return CircadianPhase.EVENING
        else:
            return CircadianPhase.WIND_DOWN

    def get_energy_trend(self, hours: int = 24) -> Dict[str, Any]:
        """Get energy trend over recent hours."""
        cutoff = (datetime.now(UTC) - timedelta(hours=hours)).isoformat()
        recent = [e for e in self.energy_logs if e.timestamp > cutoff]

        if not recent:
            return {"average": 0, "trend": "unknown", "samples": 0}

        levels = [e.level for e in recent]
        avg = sum(levels) / len(levels)

        # Determine trend
        if len(levels) >= 3:
            if levels[-1] > levels[0]:
                trend = "improving"
            elif levels[-1] < levels[0]:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "average": round(avg, 2),
            "min": min(levels),
            "max": max(levels),
            "trend": trend,
            "samples": len(levels),
        }

    def get_sleep_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get sleep statistics for recent days."""
        cutoff = (datetime.now(UTC) - timedelta(days=days)).isoformat()
        recent = [s for s in self.sleep_sessions if s.end_time and s.end_time > cutoff]

        if not recent:
            return {"sessions": 0, "average_duration": 0, "average_quality": 0}

        durations = [s.duration_minutes for s in recent if s.duration_minutes > 0]
        qualities = [s.quality_score for s in recent]

        return {
            "sessions": len(recent),
            "average_duration_hours": round(sum(durations) / len(durations) / 60, 1)
            if durations
            else 0,
            "average_quality": round(sum(qualities) / len(qualities), 2) if qualities else 0,
            "total_sleep_hours": round(sum(durations) / 60, 1) if durations else 0,
        }

    def get_optimal_work_window(self) -> Dict[str, Any]:
        """Get recommended work window based on circadian rhythm."""
        phase = self.get_current_circadian_phase()

        # Peak performance windows
        optimal_phases = [CircadianPhase.MORNING, CircadianPhase.MIDDAY]
        good_phases = [CircadianPhase.AFTERNOON]
        avoid_phases = [
            CircadianPhase.WIND_DOWN,
            CircadianPhase.DEEP_SLEEP,
            CircadianPhase.LIGHT_SLEEP,
            CircadianPhase.REM_SLEEP,
        ]

        if phase in optimal_phases:
            recommendation = "high_performance"
            efficiency = 1.0
        elif phase in good_phases:
            recommendation = "good_performance"
            efficiency = 0.8
        elif phase in avoid_phases:
            recommendation = "rest_recovery"
            efficiency = 0.3
        else:
            recommendation = "moderate_performance"
            efficiency = 0.6

        return {
            "current_phase": phase.value,
            "recommendation": recommendation,
            "efficiency_estimate": efficiency,
            "next_optimal_window": self._get_next_optimal_window(),
        }

    def _get_next_optimal_window(self) -> str:
        """Calculate next optimal work window."""
        now = datetime.now(UTC)
        # Morning window starts at 8 AM
        if now.hour < 8:
            return "08:00 (Morning peak)"
        elif now.hour < 14:
            return "Tomorrow 08:00 (Morning peak)"
        else:
            return "Tomorrow 08:00 (Morning peak)"

    def get_status(self) -> Dict[str, Any]:
        """Get current bio rhythm status."""
        return {
            "current_phase": self.get_current_circadian_phase().value,
            "energy_trend": self.get_energy_trend(24),
            "sleep_stats": self.get_sleep_stats(7),
            "optimal_window": self.get_optimal_work_window(),
            "total_sessions": len(self.sleep_sessions),
            "total_energy_logs": len(self.energy_logs),
        }


# Global instance
_ENGINE: Optional[BioRhythmEngine] = None


def get_bio_rhythm_engine(data_dir: Optional[Path] = None) -> BioRhythmEngine:
    """Get or create global bio rhythm engine."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = BioRhythmEngine(data_dir)
    return _ENGINE


if __name__ == "__main__":
    print("Bio Rhythm Engine (10_LIFE_ENGINE)")
    print("=" * 40)

    engine = get_bio_rhythm_engine()

    print(f"\nCurrent circadian phase: {engine.get_current_circadian_phase().value}")

    print("\nOptimal work window:")
    window = engine.get_optimal_work_window()
    print(f"  Recommendation: {window['recommendation']}")
    print(f"  Efficiency: {window['efficiency_estimate']:.0%}")
    print(f"  Next optimal: {window['next_optimal_window']}")
