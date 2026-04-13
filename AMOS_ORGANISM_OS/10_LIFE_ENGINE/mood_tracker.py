"""
Mood Tracker — Emotional state and sentiment monitoring

Tracks mood states, emotional patterns, and provides
insights into psychological well-being.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class MoodState(Enum):
    """Primary mood states."""
    EXCITED = "excited"
    HAPPY = "happy"
    CONTENT = "content"
    CALM = "calm"
    NEUTRAL = "neutral"
    TENSE = "tense"
    STRESSED = "stressed"
    SAD = "sad"
    FRUSTRATED = "frustrated"


@dataclass
class MoodEntry:
    """A mood entry at a specific time."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    mood: MoodState = MoodState.NEUTRAL
    intensity: int = 5  # 1-10
    valence: float = 0.0  # -1.0 (negative) to 1.0 (positive)
    arousal: float = 0.0  # -1.0 (low) to 1.0 (high)
    context: str = ""  # what was happening
    notes: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "mood": self.mood.value,
        }


class MoodTracker:
    """
    Tracks mood patterns and emotional states.

    Logs mood entries, analyzes patterns, and provides
    insights into emotional well-being.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.entries: List[MoodEntry] = []

        self._load_data()

    def _load_data(self):
        """Load mood data from disk."""
        data_file = self.data_dir / "mood_data.json"
        if data_file.exists():
            try:
                data = json.loads(data_file.read_text())
                for e_data in data.get("entries", []):
                    entry = MoodEntry(
                        id=e_data["id"],
                        mood=MoodState(e_data["mood"]),
                        intensity=e_data["intensity"],
                        valence=e_data["valence"],
                        arousal=e_data["arousal"],
                        context=e_data.get("context", ""),
                        notes=e_data.get("notes", ""),
                        timestamp=e_data["timestamp"],
                        tags=e_data.get("tags", []),
                    )
                    self.entries.append(entry)
            except Exception as e:
                print(f"[MOOD] Error loading data: {e}")

    def save(self):
        """Save mood data to disk."""
        data_file = self.data_dir / "mood_data.json"
        data = {
            "saved_at": datetime.utcnow().isoformat(),
            "entries": [e.to_dict() for e in self.entries],
        }
        data_file.write_text(json.dumps(data, indent=2))

    def log_mood(
        self,
        mood: MoodState,
        intensity: int = 5,
        context: str = "",
        notes: str = "",
    ) -> MoodEntry:
        """Log a mood entry."""
        # Calculate valence and arousal based on mood
        valence, arousal = self._calculate_dimensions(mood, intensity)

        entry = MoodEntry(
            mood=mood,
            intensity=intensity,
            valence=valence,
            arousal=arousal,
            context=context,
            notes=notes,
        )
        self.entries.append(entry)
        self.save()
        return entry

    def _calculate_dimensions(self, mood: MoodState, intensity: int) -> tuple:
        """Calculate valence and arousal from mood and intensity."""
        # Map moods to dimensions
        mood_map = {
            MoodState.EXCITED: (0.8, 0.8),
            MoodState.HAPPY: (0.8, 0.4),
            MoodState.CONTENT: (0.6, -0.2),
            MoodState.CALM: (0.4, -0.4),
            MoodState.NEUTRAL: (0.0, 0.0),
            MoodState.TENSE: (-0.4, 0.6),
            MoodState.STRESSED: (-0.6, 0.6),
            MoodState.SAD: (-0.6, -0.4),
            MoodState.FRUSTRATED: (-0.4, 0.4),
        }

        base_valence, base_arousal = mood_map.get(mood, (0.0, 0.0))
        
        # Scale by intensity (1-10)
        intensity_scale = intensity / 5.0
        valence = base_valence * intensity_scale
        arousal = base_arousal * intensity_scale

        return (round(valence, 2), round(arousal, 2))

    def get_recent_moods(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent mood entries."""
        cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        recent = [e for e in self.entries if e.timestamp > cutoff]
        return [e.to_dict() for e in recent]

    def get_mood_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get mood summary for a period."""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        recent = [e for e in self.entries if e.timestamp > cutoff]

        if not recent:
            return {"period_days": days, "entries": 0, "average_valence": 0}

        # Calculate averages
        valences = [e.valence for e in recent]
        arousals = [e.arousal for e in recent]

        # Mood distribution
        mood_counts = {}
        for e in recent:
            m = e.mood.value
            mood_counts[m] = mood_counts.get(m, 0) + 1

        # Most common mood
        most_common = max(mood_counts.items(), key=lambda x: x[1])[0] if mood_counts else "unknown"

        return {
            "period_days": days,
            "entries": len(recent),
            "average_valence": round(sum(valences) / len(valences), 2),
            "average_arousal": round(sum(arousals) / len(arousals), 2),
            "dominant_mood": most_common,
            "mood_distribution": mood_counts,
            "positive_ratio": len([v for v in valences if v > 0]) / len(valences) if valences else 0,
        }

    def get_mood_trend(self, days: int = 7) -> str:
        """Analyze mood trend."""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        recent = [e for e in self.entries if e.timestamp > cutoff]

        if len(recent) < 2:
            return "insufficient_data"

        # Sort by time
        recent.sort(key=lambda x: x.timestamp)

        # Compare first half vs second half
        mid = len(recent) // 2
        first_valence = sum(e.valence for e in recent[:mid]) / mid if mid > 0 else 0
        second_valence = sum(e.valence for e in recent[mid:]) / (len(recent) - mid) if len(recent) > mid else 0

        diff = second_valence - first_valence

        if diff > 0.2:
            return "improving"
        elif diff < -0.2:
            return "declining"
        else:
            return "stable"

    def get_recommendations(self) -> List[str]:
        """Get mood-based recommendations."""
        recs = []
        summary = self.get_mood_summary(7)
        trend = self.get_mood_trend(7)

        valence = summary.get("average_valence", 0)

        if valence < -0.3:
            recs.append("Consider mood-lifting activities: exercise, social connection")
        elif valence > 0.5:
            recs.append("Positive mood sustained - good time for challenging tasks")

        if trend == "declining":
            recs.append("Mood trend declining - identify stressors and take preventive action")

        if not recs:
            recs.append("Mood stable - maintain current practices")

        return recs


# Global instance
_TRACKER: Optional[MoodTracker] = None


def get_mood_tracker(data_dir: Optional[Path] = None) -> MoodTracker:
    """Get or create global mood tracker."""
    global _TRACKER
    if _TRACKER is None:
        _TRACKER = MoodTracker(data_dir)
    return _TRACKER


if __name__ == "__main__":
    print("Mood Tracker (10_LIFE_ENGINE)")
    print("=" * 40)

    tracker = get_mood_tracker()

    # Log some moods
    tracker.log_mood(MoodState.HAPPY, 7, "Completed project milestone")
    tracker.log_mood(MoodState.CALM, 6, "Afternoon break")
    tracker.log_mood(MoodState.FOCUSED, 8, "Deep work session")

    print("\nMood Summary (last 7 days):")
    summary = tracker.get_mood_summary()
    print(f"  Entries: {summary['entries']}")
    print(f"  Average valence: {summary['average_valence']}")
    print(f"  Dominant mood: {summary['dominant_mood']}")

    print(f"\nTrend: {tracker.get_mood_trend()}")
