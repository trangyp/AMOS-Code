"""Lifecycle Manager — Birth, Growth & Evolution Tracking

Manages the organism lifecycle from initialization through growth
to maturity and evolution. Tracks lifecycle stages and events.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class LifecycleStage(Enum):
    """Stage in organism lifecycle."""

    SEED = "seed"  # Initial creation
    GERMINATION = "germination"  # Activation/initialization
    GROWTH = "growth"  # Active development
    MATURITY = "maturity"  # Full capability
    EVOLUTION = "evolution"  # Self-modification
    REGENERATION = "regeneration"  # Recovery/rebuild
    DORMANCY = "dormancy"  # Low activity state


class LifecycleEventType(Enum):
    """Type of lifecycle event."""

    BIRTH = "birth"
    MILESTONE = "milestone"
    ADAPTATION = "adaptation"
    GROWTH = "growth"
    HEALING = "healing"
    TRANSFORMATION = "transformation"


@dataclass
class LifecycleEvent:
    """An event in the organism lifecycle."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    event_type: LifecycleEventType = LifecycleEventType.MILESTONE
    description: str = ""
    stage_at_event: LifecycleStage = LifecycleStage.SEED
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "event_type": self.event_type.value,
            "stage_at_event": self.stage_at_event.value,
        }


@dataclass
class LifecycleMilestone:
    """A milestone in organism development."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    criteria: dict[str, Any] = field(default_factory=dict)
    achieved: bool = False
    achieved_at: str = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LifecycleManager:
    """Manages the organism lifecycle.

    Tracks lifecycle stages, records events, manages milestones,
    and guides evolution from birth through maturity.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        self.current_stage: LifecycleStage = LifecycleStage.SEED
        self.stage_entry_time: str = datetime.now(UTC).isoformat()
        self.events: list[LifecycleEvent] = []
        self.milestones: dict[str, LifecycleMilestone] = {}
        self.history: list[dict[str, Any]] = []

        self._init_default_milestones()
        self._record_birth()

    def _init_default_milestones(self):
        """Initialize default lifecycle milestones."""
        default_milestones = [
            LifecycleMilestone(
                name="first_thought",
                description="First cognitive processing cycle",
                criteria={"cycles": 1},
            ),
            LifecycleMilestone(
                name="subsystem_activation",
                description="All subsystems operational",
                criteria={"active_subsystems": 14},
            ),
            LifecycleMilestone(
                name="self_awareness",
                description="Recognizes own existence and state",
                criteria={"self_reference": True},
            ),
            LifecycleMilestone(
                name="first_adaptation",
                description="First successful self-modification",
                criteria={"adaptations": 1},
            ),
            LifecycleMilestone(
                name="external_communication",
                description="First successful external interaction",
                criteria={"external_messages": 1},
            ),
            LifecycleMilestone(
                name="maturity",
                description="Reached full operational capability",
                criteria={"capabilities": 10, "stability_days": 7},
            ),
        ]

        for milestone in default_milestones:
            self.milestones[milestone.name] = milestone

    def _record_birth(self):
        """Record organism birth event."""
        birth_event = LifecycleEvent(
            event_type=LifecycleEventType.BIRTH,
            description="AMOS Organism initialized",
            stage_at_event=LifecycleStage.SEED,
            data={"version": "1.0.0", "subsystems": 14},
        )
        self.events.append(birth_event)
        self._save_lifecycle()

    def transition_stage(self, new_stage: LifecycleStage, reason: str = "") -> bool:
        """Transition to a new lifecycle stage."""
        old_stage = self.current_stage

        # Record transition in history
        self.history.append(
            {
                "from": old_stage.value,
                "to": new_stage.value,
                "reason": reason,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        self.current_stage = new_stage
        self.stage_entry_time = datetime.now(UTC).isoformat()

        # Record as event
        event = LifecycleEvent(
            event_type=LifecycleEventType.TRANSFORMATION,
            description=f"Transitioned from {old_stage.value} to {new_stage.value}: {reason}",
            stage_at_event=new_stage,
            data={"previous_stage": old_stage.value, "reason": reason},
        )
        self.events.append(event)

        self._save_lifecycle()
        return True

    def record_event(
        self,
        event_type: LifecycleEventType,
        description: str,
        data: dict[str, Any],
    ) -> LifecycleEvent:
        """Record a lifecycle event."""
        event = LifecycleEvent(
            event_type=event_type,
            description=description,
            stage_at_event=self.current_stage,
            data=data,
        )
        self.events.append(event)
        self._save_lifecycle()
        return event

    def achieve_milestone(self, milestone_name: str) -> bool:
        """Mark a milestone as achieved."""
        milestone = self.milestones.get(milestone_name)
        if not milestone or milestone.achieved:
            return False

        milestone.achieved = True
        milestone.achieved_at = datetime.now(UTC).isoformat()

        # Record as event
        self.record_event(
            event_type=LifecycleEventType.MILESTONE,
            description=f"Milestone achieved: {milestone_name}",
            data={"milestone": milestone.to_dict()},
        )

        self._save_lifecycle()
        return True

    def check_milestone_criteria(self, milestone_name: str, current_state: dict[str, Any]) -> bool:
        """Check if milestone criteria are met."""
        milestone = self.milestones.get(milestone_name)
        if not milestone:
            return False

        criteria = milestone.criteria
        for key, required_value in criteria.items():
            actual_value = current_state.get(key)
            if actual_value is None:
                return False
            if isinstance(required_value, (int, float)):
                if actual_value < required_value:
                    return False
            elif actual_value != required_value:
                return False

        return True

    def get_stage_duration(self) -> float:
        """Get duration in current stage (hours)."""
        entry_time = datetime.fromisoformat(self.stage_entry_time)
        current_time = datetime.now(UTC)
        duration = current_time - entry_time
        return duration.total_seconds() / 3600

    def get_lifecycle_summary(self) -> dict[str, Any]:
        """Get summary of organism lifecycle."""
        achieved_milestones = sum(1 for m in self.milestones.values() if m.achieved)
        total_milestones = len(self.milestones)

        return {
            "current_stage": self.current_stage.value,
            "stage_duration_hours": self.get_stage_duration(),
            "total_events": len(self.events),
            "milestones": {
                "achieved": achieved_milestones,
                "total": total_milestones,
                "progress": achieved_milestones / total_milestones if total_milestones else 0,
            },
            "stage_transitions": len(self.history),
        }

    def _save_lifecycle(self):
        """Save lifecycle data to disk."""
        lifecycle_file = self.data_dir / "lifecycle.json"
        data = {
            "current_stage": self.current_stage.value,
            "stage_entry_time": self.stage_entry_time,
            "events": [e.to_dict() for e in self.events],
            "milestones": {k: v.to_dict() for k, v in self.milestones.items()},
            "history": self.history,
            "saved_at": datetime.now(UTC).isoformat(),
        }
        lifecycle_file.write_text(json.dumps(data, indent=2))

    def get_status(self) -> dict[str, Any]:
        """Get lifecycle manager status."""
        return {
            **self.get_lifecycle_summary(),
            "stages_available": [s.value for s in LifecycleStage],
            "event_types": [e.value for e in LifecycleEventType],
        }


_MANAGER: Optional[LifecycleManager] = None


def get_lifecycle_manager(data_dir: Optional[Path] = None) -> LifecycleManager:
    """Get or create global lifecycle manager."""
    global _MANAGER
    if _MANAGER is None:
        _MANAGER = LifecycleManager(data_dir)
    return _MANAGER
