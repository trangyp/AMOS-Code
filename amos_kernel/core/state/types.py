"""State layer type definitions - TensorState, IntegrityTensor"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TensorState:
    """Four-quadrant state tensor."""

    biological: dict[str, float] = field(default_factory=dict)
    cognitive: dict[str, float] = field(default_factory=dict)
    system: dict[str, float] = field(default_factory=dict)
    environment: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_quadrants(self) -> set[str]:
        """Return which quadrants have data."""
        q = set()
        if self.biological:
            q.add("biological")
        if self.cognitive:
            q.add("cognitive")
        if self.system:
            q.add("technical")
        if self.environment:
            q.add("environmental")
        return q


@dataclass
class IntegrityTensor:
    """Integrity scores for each quadrant."""

    biological: float
    cognitive: float
    system: float
    environment: float

    @property
    def global_integrity(self) -> float:
        return (self.biological + self.cognitive + self.system + self.environment) / 4.0

    def to_quadrant(self) -> "QuadrantIntegrity":
        """Convert to QuadrantIntegrity for law validation."""
        from ..law.types import QuadrantIntegrity

        return QuadrantIntegrity(
            code=self.cognitive,
            build=self.system,
            runtime=self.system,
            environment=self.environment,
        )
