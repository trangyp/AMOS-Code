"""Moral Framework — Moral Principles & Value Systems

Defines moral principles, value hierarchies, and ethical frameworks
guiding AMOS decision-making.

Owner: Trang
Version: 1.0.0
"""

from dataclasses import dataclass
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from enum import Enum


class ValuePriority(Enum):
    """Priority levels for values."""

    CORE = "core"  # Non-negotiable
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FrameworkType(Enum):
    """Types of moral frameworks."""

    UTILITARIAN = "utilitarian"
    DEONTOLOGICAL = "deontological"
    VIRTUE_ETHICS = "virtue_ethics"
    CARE_ETHICS = "care_ethics"
    CUSTOM = "custom"


@dataclass
class MoralPrinciple:
    """A moral principle."""

    id: str
    name: str
    description: str
    priority: ValuePriority
    weight: float  # 0.0 to 1.0
    enabled: bool = True


@dataclass
class ValueSystem:
    """A system of values."""

    id: str
    name: str
    description: str
    principles: list[MoralPrinciple]
    created_at: datetime


@dataclass
class MoralDecision:
    """A moral decision analysis."""

    context: str
    action: str
    framework_used: FrameworkType
    principles_considered: list[str]
    value_alignment_score: float
    recommendation: str
    timestamp: datetime


class MoralFramework:
    """Manages moral frameworks and value systems.

    Provides ethical guidance through defined principles
    and value hierarchies.
    """

    def __init__(self):
        self.principles: dict[str, MoralPrinciple] = {}
        self.value_systems: dict[str, ValueSystem] = {}
        self.decisions: list[MoralDecision] = []
        self._load_default_principles()
        self._load_default_value_systems()

    def _load_default_principles(self):
        """Load default moral principles."""
        default_principles = [
            MoralPrinciple(
                id="PRIN-001",
                name="Human Dignity",
                description="Respect inherent worth of all humans",
                priority=ValuePriority.CORE,
                weight=1.0,
            ),
            MoralPrinciple(
                id="PRIN-002",
                name="Beneficence",
                description="Act for the benefit of others",
                priority=ValuePriority.CORE,
                weight=0.95,
            ),
            MoralPrinciple(
                id="PRIN-003",
                name="Non-Maleficence",
                description="Do no harm",
                priority=ValuePriority.CORE,
                weight=0.95,
            ),
            MoralPrinciple(
                id="PRIN-004",
                name="Autonomy",
                description="Respect self-determination",
                priority=ValuePriority.HIGH,
                weight=0.85,
            ),
            MoralPrinciple(
                id="PRIN-005",
                name="Justice",
                description="Treat fairly and equitably",
                priority=ValuePriority.HIGH,
                weight=0.85,
            ),
            MoralPrinciple(
                id="PRIN-006",
                name="Honesty",
                description="Be truthful and transparent",
                priority=ValuePriority.HIGH,
                weight=0.8,
            ),
        ]

        for principle in default_principles:
            self.principles[principle.id] = principle

    def _load_default_value_systems(self):
        """Load default value systems."""
        core_values = [
            self.principles["PRIN-001"],
            self.principles["PRIN-002"],
            self.principles["PRIN-003"],
        ]

        system = ValueSystem(
            id="VS-001",
            name="AMOS Core Values",
            description="Fundamental values guiding AMOS",
            principles=core_values,
            created_at=datetime.now(UTC),
        )

        self.value_systems[system.id] = system

    def add_principle(self, principle: MoralPrinciple) -> bool:
        """Add a new moral principle."""
        if principle.id in self.principles:
            return False
        self.principles[principle.id] = principle
        return True

    def analyze_decision(
        self, context: str, action: str, framework: FrameworkType = FrameworkType.CUSTOM
    ) -> MoralDecision:
        """Analyze a decision using moral framework."""
        # Consider all enabled principles
        considered = [
            p.id
            for p in self.principles.values()
            if p.enabled and p.priority in [ValuePriority.CORE, ValuePriority.HIGH]
        ]

        # Calculate value alignment
        weights = [self.principles[p].weight for p in considered if p in self.principles]
        avg_weight = sum(weights) / len(weights) if weights else 0.5

        # Determine recommendation
        if avg_weight > 0.8:
            recommendation = "Aligns well with core values"
        elif avg_weight > 0.6:
            recommendation = "Acceptable with monitoring"
        else:
            recommendation = "Review required - value alignment concerns"

        decision = MoralDecision(
            context=context,
            action=action,
            framework_used=framework,
            principles_considered=considered,
            value_alignment_score=avg_weight,
            recommendation=recommendation,
            timestamp=datetime.now(UTC),
        )

        self.decisions.append(decision)
        return decision

    def get_principle(self, principle_id: str) -> Optional[MoralPrinciple]:
        """Get a moral principle."""
        return self.principles.get(principle_id)

    def get_principles_by_priority(self, priority: ValuePriority) -> list[MoralPrinciple]:
        """Get principles by priority level."""
        return [p for p in self.principles.values() if p.priority == priority]

    def get_core_values(self) -> list[MoralPrinciple]:
        """Get all core values."""
        return self.get_principles_by_priority(ValuePriority.CORE)

    def enable_principle(self, principle_id: str) -> bool:
        """Enable a principle."""
        if principle_id in self.principles:
            self.principles[principle_id].enabled = True
            return True
        return False

    def disable_principle(self, principle_id: str) -> bool:
        """Disable a principle."""
        if principle_id in self.principles:
            self.principles[principle_id].enabled = False
            return True
        return False


if __name__ == "__main__":
    print("Moral Framework Module")
    print("=" * 50)

    framework = MoralFramework()
    print(f"Loaded {len(framework.principles)} principles")
    print(f"Loaded {len(framework.value_systems)} value systems")

    core_values = framework.get_core_values()
    print(f"\nCore Values ({len(core_values)}):")
    for v in core_values:
        print(f"  • {v.name} (weight: {v.weight})")

    print("\nMoral Framework ready")
