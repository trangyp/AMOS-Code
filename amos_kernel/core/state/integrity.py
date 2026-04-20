"""Integrity calculation - extracted from amos_brain/health.py"""

from .types import IntegrityTensor, TensorState


def bounded_score(values: dict[str, float]) -> float:
    """Calculate bounded integrity score from quadrant values."""
    if not values:
        return 0.0
    # Only process numeric values
    numeric = []
    for v in values.values():
        if isinstance(v, (int, float)):
            numeric.append(max(min(float(v), 1.0), 0.0))
    if not numeric:
        return 0.0
    raw = sum(numeric) / len(numeric)
    return round(raw, 4)


def integrity(state: TensorState) -> IntegrityTensor:
    """Calculate integrity tensor from state quadrants."""
    return IntegrityTensor(
        biological=bounded_score(state.biological),
        cognitive=bounded_score(state.cognitive),
        system=bounded_score(state.system),
        environment=bounded_score(state.environment),
    )
