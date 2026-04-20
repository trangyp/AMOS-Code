"""Deterministic layer types"""

from dataclasses import dataclass
from typing import Any


@dataclass
class PredictionResult:
    """Prediction vs observed comparison."""

    predicted: dict[str, float]
    observed: dict[str, float]
    error: dict[str, float]


@dataclass
class TransitionResult:
    """State transition result."""

    next_state: dict[str, Any]
    changed: bool
    reason: str


@dataclass
class CorrectionResult:
    """Correction application result."""

    corrected: dict[str, float]
    alpha: float
    error_magnitude: float
