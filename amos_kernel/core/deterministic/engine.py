"""Deterministic Core - prediction/correction/transition engine"""

from .correction import correct
from .prediction import compare, prediction_accuracy
from .transition import transition
from .types import CorrectionResult, PredictionResult, TransitionResult


class DeterministicCore:
    """Kernel L3: Deterministic prediction and correction engine."""

    def predict(self, state: dict, observation_keys: list[str]) -> dict[str, float]:
        """Generate predictions for given keys."""
        base = state.get("prediction", {})
        return {k: float(base.get(k, 0.0)) for k in observation_keys}

    def compare(self, predicted: dict[str, float], observed: dict[str, float]) -> PredictionResult:
        """Compare prediction with observation."""
        return compare(predicted, observed)

    def correct(
        self, current: dict[str, float], error: dict[str, float], alpha: float = 0.1
    ) -> CorrectionResult:
        """Apply correction based on error."""
        return correct(current, error, alpha)

    def transition(self, state: dict, interaction: dict, constraints_ok: bool) -> TransitionResult:
        """Execute state transition."""
        return transition(state, interaction, constraints_ok)

    def accuracy(self, predicted: dict[str, float], observed: dict[str, float]) -> float:
        """Calculate prediction accuracy."""
        result = self.compare(predicted, observed)
        return prediction_accuracy(result)
