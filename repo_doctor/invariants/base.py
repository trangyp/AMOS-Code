"""Base invariant class."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class InvariantSeverity(Enum):
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"


@dataclass
class InvariantResult:
    """Result of invariant check."""

    name: str
    passed: bool
    severity: InvariantSeverity
    message: str = ""
    details: Dict[str, Any] = None
    affected_files: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details or {},
            "affected_files": self.affected_files or [],
        }


class Invariant(ABC):
    """Base class for hard invariants."""

    def __init__(self, name: str, severity: InvariantSeverity = InvariantSeverity.ERROR):
        self.name = name
        self.severity = severity

    @abstractmethod
    def check(self, repo_path: str, context: Dict[str, Any] = None) -> InvariantResult:
        """Check if invariant holds."""
        pass

    def __and__(self, other: Invariant) -> InvariantGroup:
        """Compose invariants with AND."""
        return InvariantGroup([self, other], "and")


class InvariantGroup:
    """Group of invariants composed together."""

    def __init__(self, invariants: List[Invariant], operator: str = "and"):
        self.invariants = invariants
        self.operator = operator

    def check_all(self, repo_path: str, context: Dict[str, Any] = None) -> List[InvariantResult]:
        """Check all invariants."""
        return [inv.check(repo_path, context) for inv in self.invariants]
