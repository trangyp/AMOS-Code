"""Constraints - extracted from amos_brain/action_gate.py"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StabilityConstraint:
    """System stability metrics."""

    contradiction_rate: float
    correction_rate: float

    @property
    def stable(self) -> bool:
        return self.contradiction_rate <= self.correction_rate

    @property
    def ratio(self) -> float:
        if self.correction_rate <= 0:
            return float("inf")
        return self.contradiction_rate / self.correction_rate


@dataclass(frozen=True)
class BiologicalConstraint:
    """Biological system constraints."""

    load: float
    capacity: float

    @property
    def valid(self) -> bool:
        return self.load <= self.capacity and self.capacity > 0

    @property
    def utilization(self) -> float:
        if self.capacity <= 0:
            return 0.0
        return self.load / self.capacity


@dataclass(frozen=True)
class ActionRequest:
    """Represents a request to execute an action."""

    tool_name: str
    inputs: dict[str, Any]
    agent_id: str
    timestamp: str
    request_id: str


@dataclass(frozen=True)
class ActionResult:
    """Represents the result of an action."""

    success: bool
    output: Any
    error: str = ""
    execution_time_ms: float = 0.0
