"""Repair layer types"""

from dataclasses import dataclass, field


@dataclass
class RepairAction:
    """Single repair action."""

    kind: str
    target: str
    description: str


@dataclass
class RepairPlan:
    """Complete repair plan."""

    safe: bool
    actions: list[RepairAction] = field(default_factory=list)

    @property
    def action_count(self) -> int:
        return len(self.actions)


@dataclass
class VerificationResult:
    """Repair verification result."""

    passed: bool
    messages: list[str] = field(default_factory=list)
