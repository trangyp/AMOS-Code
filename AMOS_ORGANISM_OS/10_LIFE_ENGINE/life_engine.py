#!/usr/bin/env python3
"""AMOS Life Engine (10_LIFE_ENGINE)
===================================

Personal life management for the operator (Trang).
Handles schedules, routines, habits, health, and life balance.

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Routine:
    """A daily/weekly routine."""

    id: str
    name: str
    frequency: str  # daily, weekly, monthly
    time_slot: str  # e.g., "08:00-09:00"
    category: str  # health, work, learning, rest
    priority: int = 5  # 1-10
    completed: bool = False
    streak: int = 0
    last_completed: Optional[str] = None


@dataclass
class Habit:
    """A habit being tracked."""

    id: str
    name: str
    target_frequency: str  # daily, 3x_week, weekly
    current_streak: int = 0
    longest_streak: int = 0
    total_completions: int = 0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_completed: Optional[str] = None


@dataclass
class LifeGoal:
    """A life goal with milestones."""

    id: str
    title: str
    category: str  # career, health, learning, relationships
    deadline: Optional[str] = None
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    progress: float = 0.0
    status: str = "active"  # active, completed, paused


@dataclass
class DaySummary:
    """Summary of a day's activities."""

    date: str
    routines_completed: int = 0
    routines_total: int = 0
    habits_done: int = 0
    habits_total: int = 0
    energy_level: int = 5  # 1-10
    focus_hours: float = 0.0
    notes: str = ""


class LifeEngine:
    """Life management engine for operator productivity and wellness.
    Tracks routines, habits, goals, and life balance.
    """

    def __init__(self, organism_root: Path) -> None:
        self.root = organism_root
        self.life_dir = organism_root / "10_LIFE_ENGINE"
        self.data_dir = self.life_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.routines: List[Routine] = []
        self.habits: List[Habit] = []
        self.goals: List[LifeGoal] = []
        self.day_summaries: List[DaySummary] = []

        self._load_state()
        self._setup_defaults()

    def _setup_defaults(self) -> None:
        """Set up default routines and habits if none exist."""
        if not self.routines:
            default_routines = [
                Routine(
                    id="routine_001",
                    name="Morning meditation",
                    frequency="daily",
                    time_slot="07:00-07:15",
                    category="health",
                    priority=8,
                ),
                Routine(
                    id="routine_002",
                    name="Exercise",
                    frequency="daily",
                    time_slot="07:30-08:30",
                    category="health",
                    priority=9,
                ),
                Routine(
                    id="routine_003",
                    name="Deep work block",
                    frequency="daily",
                    time_slot="09:00-12:00",
                    category="work",
                    priority=10,
                ),
                Routine(
                    id="routine_004",
                    name="Learning session",
                    frequency="daily",
                    time_slot="14:00-15:00",
                    category="learning",
                    priority=7,
                ),
                Routine(
                    id="routine_005",
                    name="Evening review",
                    frequency="daily",
                    time_slot="20:00-20:30",
                    category="rest",
                    priority=6,
                ),
            ]
            self.routines.extend(default_routines)
            self._save_state()

        if not self.habits:
            default_habits = [
                Habit(id="habit_001", name="Read 30 minutes", target_frequency="daily"),
                Habit(id="habit_002", name="Drink 8 glasses water", target_frequency="daily"),
                Habit(id="habit_003", name="No screen after 22:00", target_frequency="daily"),
            ]
            self.habits.extend(default_habits)
            self._save_state()

    def _load_state(self) -> None:
        """Load life data from disk."""
        state_file = self.data_dir / "life_state.json"
        if state_file.exists():
            try:
                with open(state_file, encoding="utf-8") as f:
                    data = json.load(f)

                for r in data.get("routines", []):
                    self.routines.append(Routine(**r))
                for h in data.get("habits", []):
                    self.habits.append(Habit(**h))
                for g in data.get("goals", []):
                    self.goals.append(LifeGoal(**g))
                for d in data.get("day_summaries", []):
                    self.day_summaries.append(DaySummary(**d))

            except Exception as e:
                print(f"[LIFE] Error loading state: {e}")

    def _save_state(self) -> None:
        """Save life data to disk."""
        state_file = self.data_dir / "life_state.json"

        data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "routines": [
                {
                    "id": r.id,
                    "name": r.name,
                    "frequency": r.frequency,
                    "time_slot": r.time_slot,
                    "category": r.category,
                    "priority": r.priority,
                    "completed": r.completed,
                    "streak": r.streak,
                    "last_completed": r.last_completed,
                }
                for r in self.routines
            ],
            "habits": [
                {
                    "id": h.id,
                    "name": h.name,
                    "target_frequency": h.target_frequency,
                    "current_streak": h.current_streak,
                    "longest_streak": h.longest_streak,
                    "total_completions": h.total_completions,
                    "created_at": h.created_at,
                    "last_completed": h.last_completed,
                }
                for h in self.habits
            ],
            "goals": [
                {
                    "id": g.id,
                    "title": g.title,
                    "category": g.category,
                    "deadline": g.deadline,
                    "milestones": g.milestones,
                    "progress": g.progress,
                    "status": g.status,
                }
                for g in self.goals
            ],
            "day_summaries": [
                {
                    "date": d.date,
                    "routines_completed": d.routines_completed,
                    "routines_total": d.routines_total,
                    "habits_done": d.habits_done,
                    "habits_total": d.habits_total,
                    "energy_level": d.energy_level,
                    "focus_hours": d.focus_hours,
                    "notes": d.notes,
                }
                for d in self.day_summaries[-30:]  # Keep last 30 days
            ],
        }

        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def complete_routine(self, routine_id: str) -> bool:
        """Mark a routine as completed for today."""
        for routine in self.routines:
            if routine.id == routine_id:
                routine.completed = True
                routine.last_completed = datetime.utcnow().isoformat()

                # Update streak
                if routine.last_completed:
                    last = datetime.fromisoformat(routine.last_completed.replace("Z", "+00:00"))
                    today = datetime.utcnow()
                    if (today - last).days <= 1:
                        routine.streak += 1
                    else:
                        routine.streak = 1

                self._save_state()
                print(f"[LIFE] Done: {routine.name}")
                print(f"         Streak: {routine.streak} days")
                return True
        return False

    def complete_habit(self, habit_id: str) -> bool:
        """Mark a habit as completed for today."""
        for habit in self.habits:
            if habit.id == habit_id:
                habit.total_completions += 1
                habit.last_completed = datetime.utcnow().isoformat()

                # Update streak
                if habit.last_completed:
                    last = datetime.fromisoformat(habit.last_completed.replace("Z", "+00:00"))
                    today = datetime.utcnow()
                    if (today - last).days <= 1:
                        habit.current_streak += 1
                    else:
                        habit.current_streak = 1

                    if habit.current_streak > habit.longest_streak:
                        habit.longest_streak = habit.current_streak

                self._save_state()
                print(f"[LIFE] Habit done: {habit.name}")
                return True
        return False

    def get_today_schedule(self) -> List[Dict[str, Any]]:
        """Get today's schedule with routines."""
        today = datetime.utcnow().strftime("%Y-%m-%d")

        schedule = []
        for routine in self.routines:
            if routine.frequency == "daily":
                schedule.append(
                    {
                        "time": routine.time_slot,
                        "activity": routine.name,
                        "category": routine.category,
                        "priority": routine.priority,
                        "completed": routine.completed,
                        "streak": routine.streak,
                    }
                )

        return sorted(schedule, key=lambda x: x["time"])

    def get_habit_stats(self) -> Dict[str, Any]:
        """Get habit tracking statistics."""
        total_habits = len(self.habits)
        if total_habits == 0:
            return {"total": 0, "avg_streak": 0, "strongest_habit": None}

        avg_streak = sum(h.current_streak for h in self.habits) / total_habits
        strongest = max(self.habits, key=lambda h: h.current_streak)

        return {
            "total": total_habits,
            "avg_streak": round(avg_streak, 1),
            "strongest_habit": strongest.name,
            "strongest_streak": strongest.current_streak,
            "total_completions_all": sum(h.total_completions for h in self.habits),
        }

    def calculate_life_balance(self) -> Dict[str, float]:
        """Calculate life balance across categories."""
        categories = ["health", "work", "learning", "rest", "relationships"]
        balance = dict.fromkeys(categories, 5.0)  # Default middle score

        # Score based on routine completion
        for routine in self.routines:
            if routine.category in balance:
                if routine.completed:
                    balance[routine.category] = min(10.0, balance[routine.category] + 1)
                else:
                    balance[routine.category] = max(1.0, balance[routine.category] - 0.5)

        return balance

    def add_goal(self, title: str, category: str, deadline: Optional[str] = None) -> LifeGoal:
        """Add a new life goal."""
        goal = LifeGoal(
            id=f"goal_{len(self.goals) + 1:03d}", title=title, category=category, deadline=deadline
        )
        self.goals.append(goal)
        self._save_state()
        print(f"[LIFE] New goal: {title}")
        return goal

    def get_status(self) -> Dict[str, Any]:
        """Get life engine status."""
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        # Count completed routines today
        routines_done = sum(1 for r in self.routines if r.completed)

        return {
            "status": "operational",
            "date": today_str,
            "routines": {
                "total": len(self.routines),
                "completed_today": routines_done,
                "pending": len(self.routines) - routines_done,
            },
            "habits": self.get_habit_stats(),
            "goals": {
                "total": len(self.goals),
                "active": len([g for g in self.goals if g.status == "active"]),
            },
            "life_balance": self.calculate_life_balance(),
        }


def main() -> int:
    """CLI for Life Engine."""
    print("=" * 50)
    print("AMOS Life Engine (10_LIFE_ENGINE)")
    print("=" * 50)

    organism_root = Path(__file__).parent.parent
    engine = LifeEngine(organism_root)

    # Show today's schedule
    print("\nToday's Schedule:")
    schedule = engine.get_today_schedule()
    for item in schedule:
        status = "✓" if item["completed"] else "○"
        time = item["time"]
        activity = item["activity"]
        print(f"  {status} [{time}] {activity}")

    # Show habit stats
    print("\nHabit Statistics:")
    stats = engine.get_habit_stats()
    print(f"  Total habits: {stats['total']}")
    print(f"  Average streak: {stats['avg_streak']} days")
    if stats["strongest_habit"]:
        print(f"  Strongest: {stats['strongest_habit']}")

    # Show life balance
    print("\nLife Balance Scores:")
    balance = engine.calculate_life_balance()
    for category, score in balance.items():
        filled = int(score)
        empty = 10 - filled
        bar = "█" * filled + "░" * empty
        print(f"  {category:12} [{bar}] {score:.1f}")

    # Show status
    print("\nLife Engine Status:")
    status = engine.get_status()
    routines = status["routines"]
    completed = routines["completed_today"]
    total = routines["total"]
    print(f"  Routines: {completed}/{total} completed")
    print(f"  Active goals: {status['goals']['active']}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
