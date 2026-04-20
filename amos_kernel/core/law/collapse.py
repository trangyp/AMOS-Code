"""Collapse risk calculation - determines system stability threshold"""

from .constraints import StabilityConstraint


def collapse_risk(constraint: StabilityConstraint) -> float:
    """Calculate collapse risk from stability constraints.

    Risk = max(0, (contradiction_rate / correction_rate) - 1.0)
    Clamped to [0.0, 1.0]
    """
    if constraint.correction_rate <= 0:
        return 1.0
    ratio = constraint.contradiction_rate / constraint.correction_rate
    return min(max(ratio - 1.0, 0.0), 1.0)


def should_collapse(risk: float, threshold: float = 0.8) -> bool:
    """Determine if system should enter collapse state."""
    return risk >= threshold
