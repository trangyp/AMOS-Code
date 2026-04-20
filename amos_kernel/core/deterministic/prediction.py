"""Prediction comparison - extracted from amos_brain/thinking_engine.py"""

from .types import PredictionResult


def compare(predicted: dict[str, float], observed: dict[str, float]) -> PredictionResult:
    """Compare predicted vs observed values."""
    keys = sorted(set(predicted) | set(observed))
    error = {k: abs(observed.get(k, 0.0) - predicted.get(k, 0.0)) for k in keys}
    return PredictionResult(predicted=predicted, observed=observed, error=error)


def prediction_accuracy(result: PredictionResult) -> float:
    """Calculate overall prediction accuracy (0-1)."""
    if not result.error:
        return 1.0
    total_error = sum(result.error.values())
    max_possible = len(result.error)  # Assuming 0-1 range
    if max_possible == 0:
        return 1.0
    return max(0.0, 1.0 - (total_error / max_possible))
