"""Cognitive Cycle Manager — Focus and attention management

Manages cognitive cycles, attention periods, and
optimal work-rest rhythms for peak performance.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class CyclePhase(Enum):
    """Phases of a cognitive cycle."""

    FOCUS = "focus"
    DIFFUSE = "diffuse"
    REST = "rest"
    BREAK = "break"


class FocusState(Enum):
    """States of focus."""

    DEEP_FOCUS = "deep_focus"
    FOCUSED = "focused"
    SCATTERED = "scattered"
    DISTRACTED = "distracted"


@dataclass
class FocusSession:
    """A focused work session."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    start_time: str = ""
    end_time: Optional[str] = None
    duration_minutes: int = 0
    focus_state: FocusState = FocusState.FOCUSED
    interruptions: int = 0
    productivity_score: float = 0.0  # 0-1
    task_type: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "focus_state": self.focus_state.value,
        }


@dataclass
class CycleRecommendation:
    """A recommendation for cognitive cycles."""

    phase: CyclePhase
    duration_minutes: int
    activity: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "phase": self.phase.value,
        }


class CognitiveCycleManager:
    """Manages cognitive cycles and focus periods.

    Implements focus-rest cycles (Pomodoro-style) and
    provides recommendations for optimal work patterns.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.sessions: list[FocusSession] = []
        self.current_session: Optional[FocusSession] = None
        self.default_focus_duration = 25  # minutes
        self.default_break_duration = 5  # minutes
        self.long_break_duration = 15  # minutes
        self.sessions_before_long_break = 4

        self._load_data()

    def _load_data(self):
        """Load cycle data from disk."""
        data_file = self.data_dir / "cycle_data.json"
        if data_file.exists():
            try:
                data = json.loads(data_file.read_text())
                for s_data in data.get("sessions", []):
                    session = FocusSession(
                        id=s_data["id"],
                        start_time=s_data["start_time"],
                        end_time=s_data.get("end_time"),
                        duration_minutes=s_data["duration_minutes"],
                        focus_state=FocusState(s_data["focus_state"]),
                        interruptions=s_data.get("interruptions", 0),
                        productivity_score=s_data.get("productivity_score", 0),
                        task_type=s_data.get("task_type", ""),
                        notes=s_data.get("notes", ""),
                    )
                    self.sessions.append(session)
            except Exception as e:
                print(f"[CYCLE] Error loading data: {e}")

    def save(self):
        """Save cycle data to disk."""
        data_file = self.data_dir / "cycle_data.json"
        data = {
            "saved_at": datetime.utcnow().isoformat(),
            "sessions": [s.to_dict() for s in self.sessions],
        }
        data_file.write_text(json.dumps(data, indent=2))

    def start_focus_session(
        self, task_type: str = "", duration: Optional[int] = None
    ) -> FocusSession:
        """Start a focused work session."""
        duration = duration or self.default_focus_duration

        session = FocusSession(
            start_time=datetime.utcnow().isoformat(),
            duration_minutes=duration,
            task_type=task_type,
            focus_state=FocusState.FOCUSED,
        )

        self.current_session = session
        self.sessions.append(session)
        self.save()
        return session

    def end_focus_session(self, productivity: float = 0.5) -> Optional[FocusSession]:
        """End the current focus session."""
        if not self.current_session:
            return None

        session = self.current_session
        session.end_time = datetime.utcnow().isoformat()
        session.productivity_score = productivity

        # Calculate actual duration
        start = datetime.fromisoformat(session.start_time)
        end = datetime.fromisoformat(session.end_time)
        actual_duration = int((end - start).total_seconds() / 60)
        session.duration_minutes = actual_duration

        self.current_session = None
        self.save()
        return session

    def record_interruption(self, note: str = ""):
        """Record an interruption to current session."""
        if self.current_session:
            self.current_session.interruptions += 1
            if note:
                self.current_session.notes += f"[Interruption: {note}] "
            self.save()

    def get_today_stats(self) -> dict[str, Any]:
        """Get today's focus session statistics."""
        today = datetime.utcnow().strftime("%Y-%m-%d")

        today_sessions = [s for s in self.sessions if s.start_time.startswith(today) and s.end_time]

        if not today_sessions:
            return {
                "date": today,
                "sessions": 0,
                "total_focus_minutes": 0,
                "average_productivity": 0,
                "interruptions": 0,
            }

        total_minutes = sum(s.duration_minutes for s in today_sessions)
        avg_productivity = sum(s.productivity_score for s in today_sessions) / len(today_sessions)
        total_interruptions = sum(s.interruptions for s in today_sessions)

        return {
            "date": today,
            "sessions": len(today_sessions),
            "total_focus_minutes": total_minutes,
            "average_productivity": round(avg_productivity, 2),
            "interruptions": total_interruptions,
        }

    def get_recommendation(self) -> CycleRecommendation:
        """Get next cycle recommendation."""
        today_stats = self.get_today_stats()
        sessions_today = today_stats["sessions"]

        # If currently in a session, recommend completing it
        if self.current_session:
            elapsed = self._get_elapsed_minutes(self.current_session.start_time)
            remaining = self.current_session.duration_minutes - elapsed

            if remaining > 0:
                return CycleRecommendation(
                    phase=CyclePhase.FOCUS,
                    duration_minutes=remaining,
                    activity=f"Continue focus session ({self.current_session.task_type or 'current task'})",
                    rationale="Complete current focus block",
                )
            else:
                return CycleRecommendation(
                    phase=CyclePhase.BREAK,
                    duration_minutes=self._get_break_duration(sessions_today),
                    activity="Take a break - stretch, hydrate, rest eyes",
                    rationale="Focus session complete",
                )

        # Recommend starting a new session or taking a longer break
        if sessions_today > 0 and sessions_today % self.sessions_before_long_break == 0:
            return CycleRecommendation(
                phase=CyclePhase.REST,
                duration_minutes=self.long_break_duration,
                activity="Take a long break - walk, eat, recharge",
                rationale=f"Completed {self.sessions_before_long_break} sessions - time for deep rest",
            )
        else:
            return CycleRecommendation(
                phase=CyclePhase.FOCUS,
                duration_minutes=self.default_focus_duration,
                activity="Start focused work session",
                rationale="Begin next focus block"
                if sessions_today > 0
                else "Start first focus block of day",
            )

    def _get_elapsed_minutes(self, start_time: str) -> int:
        """Calculate elapsed minutes since start time."""
        start = datetime.fromisoformat(start_time)
        now = datetime.utcnow()
        return int((now - start).total_seconds() / 60)

    def _get_break_duration(self, sessions_completed: int) -> int:
        """Determine break duration based on sessions completed."""
        if sessions_completed > 0 and sessions_completed % self.sessions_before_long_break == 0:
            return self.long_break_duration
        return self.default_break_duration

    def get_focus_patterns(self, days: int = 7) -> dict[str, Any]:
        """Analyze focus patterns over time."""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        recent = [s for s in self.sessions if s.end_time and s.start_time > cutoff]

        if not recent:
            return {"patterns": "insufficient_data"}

        # Group by hour of day
        by_hour = {}
        for s in recent:
            hour = datetime.fromisoformat(s.start_time).hour
            if hour not in by_hour:
                by_hour[hour] = []
            by_hour[hour].append(s.productivity_score)

        # Find most productive hours
        hour_productivity = {h: sum(scores) / len(scores) for h, scores in by_hour.items()}
        best_hours = sorted(hour_productivity.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            "total_sessions": len(recent),
            "most_productive_hours": [h[0] for h in best_hours],
            "average_session_length": sum(s.duration_minutes for s in recent) / len(recent),
            "average_productivity": sum(s.productivity_score for s in recent) / len(recent),
        }

    def get_status(self) -> dict[str, Any]:
        """Get current cognitive cycle status."""
        return {
            "current_session_active": self.current_session is not None,
            "current_task": self.current_session.task_type if self.current_session else None,
            "today_stats": self.get_today_stats(),
            "next_recommendation": self.get_recommendation().to_dict(),
            "focus_patterns": self.get_focus_patterns(7),
        }


# Global instance
_MANAGER: Optional[CognitiveCycleManager] = None


def get_cognitive_cycle_manager(data_dir: Optional[Path] = None) -> CognitiveCycleManager:
    """Get or create global cognitive cycle manager."""
    global _MANAGER
    if _MANAGER is None:
        _MANAGER = CognitiveCycleManager(data_dir)
    return _MANAGER


if __name__ == "__main__":
    print("Cognitive Cycle Manager (10_LIFE_ENGINE)")
    print("=" * 40)

    manager = get_cognitive_cycle_manager()

    print("\nToday's Stats:")
    stats = manager.get_today_stats()
    print(f"  Sessions: {stats['sessions']}")
    print(f"  Focus minutes: {stats['total_focus_minutes']}")

    print("\nNext Recommendation:")
    rec = manager.get_recommendation()
    print(f"  Phase: {rec.phase.value}")
    print(f"  Duration: {rec.duration_minutes} minutes")
    print(f"  Activity: {rec.activity}")
    print(f"  Rationale: {rec.rationale}")
