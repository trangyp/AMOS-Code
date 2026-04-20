"""Observe layer types"""

from dataclasses import dataclass, field


@dataclass
class DriftItem:
    """Single drift detection item."""

    code: str
    message: str
    severity: str


@dataclass
class DriftReport:
    """Complete drift report."""

    healthy: bool
    items: list[DriftItem] = field(default_factory=list)

    @property
    def has_fatal(self) -> bool:
        return any(item.severity == "fatal" for item in self.items)

    @property
    def issue_count(self) -> int:
        return len(self.items)
