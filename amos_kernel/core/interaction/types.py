from __future__ import annotations

"""Interaction layer types"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class InteractionResult:
    """Result of applying interaction operator."""

    data: dict[str, Any]
    internal: Optional[dict[str, Any]] = None
    external: Optional[dict[str, Any]] = None
    feedback: Optional[dict[str, Any]] = None
    coupling_strength: float = 0.0

    def __post_init__(self):
        if self.internal is None:
            self.internal = self.data.get("internal", {})
        if self.external is None:
            self.external = self.data.get("external", {})
        if self.feedback is None:
            emergence = self.data.get("emergence", {})
            self.feedback = {
                "coupling_strength": emergence.get("coupling_strength", 0.0),
                "error_signal": emergence.get("difference", 0.0),
            }
        if self.coupling_strength == 0.0:
            self.coupling_strength = float(bool(self.internal) and bool(self.external))
