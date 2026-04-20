"""Correction logic - extracted from amos_brain/repair_bridge.py"""

from .types import CorrectionResult


def correct(
    current: dict[str, float], error: dict[str, float], alpha: float = 0.1
) -> CorrectionResult:
    """Apply error correction with learning rate alpha."""
    updated = dict(current)
    total_error = 0.0
    for key, err in error.items():
        updated[key] = current.get(key, 0.0) + alpha * err
        total_error += abs(err)

    return CorrectionResult(
        corrected=updated,
        alpha=alpha,
        error_magnitude=total_error / len(error) if error else 0.0,
    )
