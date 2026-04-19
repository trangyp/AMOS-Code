"""Growth Engine — Self-Modification & Expansion

Manages organism growth, capability expansion, and self-improvement.
Tracks growth plans and executes staged expansion.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class GrowthStage(Enum):
    """Stage of growth for a plan."""

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"


class GrowthType(Enum):
    """Type of growth."""

    CAPABILITY = "capability"  # New functionality
    CAPACITY = "capacity"  # Scale increase
    EFFICIENCY = "efficiency"  # Performance improvement
    KNOWLEDGE = "knowledge"  # Learning/understanding


@dataclass
class GrowthPlan:
    """A plan for organism growth."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    growth_type: GrowthType = GrowthType.CAPABILITY
    target_subsystem: str = ""
    requirements: List[str] = field(default_factory=list)
    expected_outcome: Dict[str, Any] = field(default_factory=dict)
    stage: GrowthStage = GrowthStage.PLANNED
    progress: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    started_at: str = None
    completed_at: str = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "growth_type": self.growth_type.value,
            "stage": self.stage.value,
        }


class GrowthEngine:
    """Manages organism growth and self-improvement.

    Handles growth planning, staged execution, and
    capability expansion tracking.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        self.plans: Dict[str, GrowthPlan] = {}
        self.growth_history: List[dict[str, Any]] = []
        self.capabilities: Dict[str, dict[str, Any]] = {}

        self._init_default_capabilities()

    def _init_default_capabilities(self):
        """Initialize default organism capabilities."""
        self.capabilities = {
            "self_awareness": {
                "description": "Knowledge of own state and structure",
                "level": 1.0,
                "acquired_at": datetime.now(UTC).isoformat(),
            },
            "learning": {
                "description": "Ability to learn from experience",
                "level": 1.0,
                "acquired_at": datetime.now(UTC).isoformat(),
            },
            "adaptation": {
                "description": "Ability to adapt to changes",
                "level": 0.5,
                "acquired_at": datetime.now(UTC).isoformat(),
            },
            "self_improvement": {
                "description": "Ability to improve own code",
                "level": 0.3,
                "acquired_at": datetime.now(UTC).isoformat(),
            },
        }

    def create_plan(
        self,
        name: str,
        description: str,
        growth_type: GrowthType,
        target_subsystem: str,
        requirements: List[str],
        expected_outcome: Dict[str, Any],
    ) -> GrowthPlan:
        """Create a new growth plan."""
        plan = GrowthPlan(
            name=name,
            description=description,
            growth_type=growth_type,
            target_subsystem=target_subsystem,
            requirements=requirements,
            expected_outcome=expected_outcome,
        )
        self.plans[plan.id] = plan
        return plan

    def start_growth(self, plan_id: str) -> bool:
        """Start executing a growth plan."""
        plan = self.plans.get(plan_id)
        if not plan or plan.stage != GrowthStage.PLANNED:
            return False

        plan.stage = GrowthStage.IN_PROGRESS
        plan.started_at = datetime.now(UTC).isoformat()
        return True

    def update_progress(self, plan_id: str, progress: float) -> bool:
        """Update progress of a growth plan."""
        plan = self.plans.get(plan_id)
        if not plan or plan.stage != GrowthStage.IN_PROGRESS:
            return False

        plan.progress = max(0.0, min(1.0, progress))

        if plan.progress >= 1.0:
            self._complete_growth(plan_id)

        return True

    def _complete_growth(self, plan_id: str) -> bool:
        """Complete a growth plan."""
        plan = self.plans.get(plan_id)
        if not plan:
            return False

        plan.stage = GrowthStage.COMPLETED
        plan.progress = 1.0
        plan.completed_at = datetime.now(UTC).isoformat()

        # Record in history
        self.growth_history.append(
            {
                "plan_id": plan_id,
                "name": plan.name,
                "growth_type": plan.growth_type.value,
                "completed_at": plan.completed_at,
                "outcome": plan.expected_outcome,
            }
        )

        # Update capabilities if applicable
        if plan.growth_type == GrowthType.CAPABILITY:
            cap_name = plan.name.lower().replace(" ", "_")
            self.capabilities[cap_name] = {
                "description": plan.description,
                "level": 1.0,
                "acquired_at": plan.completed_at,
            }

        self._save_plans()
        return True

    def pause_growth(self, plan_id: str) -> bool:
        """Pause a growth plan."""
        plan = self.plans.get(plan_id)
        if not plan or plan.stage != GrowthStage.IN_PROGRESS:
            return False

        plan.stage = GrowthStage.PAUSED
        return True

    def abandon_plan(self, plan_id: str, reason: str = "") -> bool:
        """Abandon a growth plan."""
        plan = self.plans.get(plan_id)
        if not plan:
            return False

        plan.stage = GrowthStage.ABANDONED
        self.growth_history.append(
            {
                "plan_id": plan_id,
                "name": plan.name,
                "abandoned": True,
                "reason": reason,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return True

    def get_capability_level(self, capability: str) -> float:
        """Get level of a capability."""
        cap = self.capabilities.get(capability)
        return cap["level"] if cap else 0.0

    def improve_capability(self, capability: str, increment: float = 0.1) -> bool:
        """Improve a capability level."""
        if capability not in self.capabilities:
            return False

        cap = self.capabilities[capability]
        cap["level"] = min(1.0, cap["level"] + increment)
        cap["last_improved"] = datetime.now(UTC).isoformat()
        return True

    def _save_plans(self):
        """Save growth plans to disk."""
        plans_file = self.data_dir / "growth_plans.json"
        data = {
            "plans": [p.to_dict() for p in self.plans.values()],
            "history": self.growth_history,
            "capabilities": self.capabilities,
            "saved_at": datetime.now(UTC).isoformat(),
        }
        plans_file.write_text(json.dumps(data, indent=2))

    def list_plans(self, stage: Optional[GrowthStage] = None) -> List[dict[str, Any]]:
        """List growth plans."""
        plans = self.plans.values()
        if stage:
            plans = [p for p in plans if p.stage == stage]
        return [p.to_dict() for p in plans]

    def get_status(self) -> Dict[str, Any]:
        """Get growth engine status."""
        active = sum(1 for p in self.plans.values() if p.stage == GrowthStage.IN_PROGRESS)
        completed = sum(1 for p in self.plans.values() if p.stage == GrowthStage.COMPLETED)
        planned = sum(1 for p in self.plans.values() if p.stage == GrowthStage.PLANNED)

        return {
            "total_plans": len(self.plans),
            "active": active,
            "completed": completed,
            "planned": planned,
            "total_capabilities": len(self.capabilities),
            "capabilities": {name: info["level"] for name, info in self.capabilities.items()},
        }


_ENGINE: Optional[GrowthEngine] = None


def get_growth_engine(data_dir: Optional[Path] = None) -> GrowthEngine:
    """Get or create global growth engine."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = GrowthEngine(data_dir)
    return _ENGINE
