"""
L3 - Interaction Engine

Implements the interaction operator:
    E = i_A ⊗ i_B

Responsibilities:
- interaction operator
- internal/external state coupling
- feedback extraction
- signal transformation

This layer bridges internal cognition (i_A) with external context (i_B).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from typing import Any, Optional


@dataclass
class InteractionOperator:
    """
    Interaction operator: E = i_A ⊗ i_B

    Couples internal state with external context.
    """

    internal_component: dict[str, Any] = field(default_factory=dict)
    external_component: dict[str, Any] = field(default_factory=dict)
    interaction_strength: float = 1.0
    coupling_type: str = "tensor"  # "tensor", "additive", "multiplicative"

    def compute(self) -> dict[str, Any]:
        """Compute interaction result."""
        if self.coupling_type == "tensor":
            return self._tensor_product()
        elif self.coupling_type == "additive":
            return self._additive_coupling()
        elif self.coupling_type == "multiplicative":
            return self._multiplicative_coupling()
        else:
            return self._tensor_product()

    def _tensor_product(self) -> dict[str, Any]:
        """Tensor product: i_A ⊗ i_B."""
        # Simplified tensor product as combined structure
        return {
            "internal": self.internal_component,
            "external": self.external_component,
            "interaction_matrix": self._build_interaction_matrix(),
            "strength": self.interaction_strength,
        }

    def _additive_coupling(self) -> dict[str, Any]:
        """Additive coupling: i_A + i_B."""
        return {
            "combined": {**self.internal_component, **self.external_component},
            "strength": self.interaction_strength,
        }

    def _multiplicative_coupling(self) -> dict[str, Any]:
        """Multiplicative coupling: i_A * i_B."""
        # Element-wise multiplication where keys match
        common_keys = set(self.internal_component.keys()) & set(self.external_component.keys())
        result = {}
        for key in common_keys:
            result[key] = self.internal_component.get(key, 0) * self.external_component.get(key, 0)

        return {
            "product": result,
            "strength": self.interaction_strength,
        }

    def _build_interaction_matrix(self) -> list[list[float]]:
        """Build interaction matrix between internal and external."""
        # Simplified: identity-like matrix scaled by strength
        size = max(len(self.internal_component), len(self.external_component))
        size = max(size, 1)

        matrix = []
        for i in range(size):
            row = []
            for j in range(size):
                if i == j:
                    row.append(self.interaction_strength)
                else:
                    row.append(0.0)
            matrix.append(row)

        return matrix


@dataclass
class FeedbackExtraction:
    """Extracted feedback from interaction."""

    source: str  # "internal", "external", "coupled"
    signal_type: str  # "error", "reward", "neutral"
    magnitude: float
    raw_signal: dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class InteractionEngine:
    """
    Manages all system interactions.

    Bridges internal cognition with external reality.
    """

    _instance: Optional[InteractionEngine] = None

    def __new__(cls) -> InteractionEngine:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._interactions: list[InteractionOperator] = []
        self._feedback_history: list[FeedbackExtraction] = []
        self._initialized = True

    def create_interaction(
        self,
        internal: dict[str, Any],
        external: dict[str, Any],
        strength: float = 1.0,
        coupling: str = "tensor",
    ) -> InteractionOperator:
        """Create an interaction operator."""
        operator = InteractionOperator(
            internal_component=internal,
            external_component=external,
            interaction_strength=strength,
            coupling_type=coupling,
        )
        self._interactions.append(operator)
        return operator

    def extract_feedback(
        self, interaction: InteractionOperator, result: dict[str, Any]
    ) -> FeedbackExtraction:
        """Extract feedback from interaction result."""
        # Determine signal type based on result characteristics
        signal_type = self._classify_signal(result)

        # Compute magnitude
        magnitude = self._compute_magnitude(result)

        feedback = FeedbackExtraction(
            source="coupled",
            signal_type=signal_type,
            magnitude=magnitude,
            raw_signal=result,
        )

        self._feedback_history.append(feedback)
        return feedback

    def transform_signal(self, signal: dict[str, Any], target_format: str) -> dict[str, Any]:
        """Transform signal to target format."""
        transformers = {
            "normalized": self._normalize_signal,
            "scaled": self._scale_signal,
            "filtered": self._filter_signal,
        }

        transformer = transformers.get(target_format, lambda x: x)
        return transformer(signal)

    def get_feedback_history(self) -> list[FeedbackExtraction]:
        """Get feedback history."""
        return self._feedback_history.copy()

    def _classify_signal(self, result: dict[str, Any]) -> str:
        """Classify signal type."""
        # Error signals typically contain these keys
        error_indicators = ["error", "mismatch", "contradiction", "failure"]
        if any(k in str(result).lower() for k in error_indicators):
            return "error"

        # Reward signals
        reward_indicators = ["success", "improvement", "gain"]
        if any(k in str(result).lower() for k in reward_indicators):
            return "reward"

        return "neutral"

    def _compute_magnitude(self, result: dict[str, Any]) -> float:
        """Compute signal magnitude."""

        # Simple magnitude: depth of nested structure
        def depth(d: Any, level: int = 0) -> int:
            if not isinstance(d, dict):
                return level
            if not d:
                return level
            return max(depth(v, level + 1) for v in d.values())

        return min(depth(result) * 0.1, 1.0)

    def _normalize_signal(self, signal: dict[str, Any]) -> dict[str, Any]:
        """Normalize signal values."""
        return {
            k: v / max(abs(v), 1e-6) if isinstance(v, (int, float)) else v
            for k, v in signal.items()
        }

    def _scale_signal(self, signal: dict[str, Any]) -> dict[str, Any]:
        """Scale signal values."""
        return {k: v * 0.5 if isinstance(v, (int, float)) else v for k, v in signal.items()}

    def _filter_signal(self, signal: dict[str, Any]) -> dict[str, Any]:
        """Filter to significant values only."""
        return {k: v for k, v in signal.items() if v != 0 and v is not None}


def get_interaction_engine() -> InteractionEngine:
    """Get the singleton interaction engine."""
    return InteractionEngine()
