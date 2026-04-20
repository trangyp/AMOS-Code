"""
L1 - Deterministic Core

The reasoning engine. Not the UI, not the server, not infra.

Responsibilities:
- state transition
- prediction update
- correction loop
- consistency-preserving execution
- bounded adaptation

Core equation:
    S_{t+1} = F((i_A ⊗ i_B), Feedback, Constraints, Integrity)

Deterministic rule:
    Same state + same inputs + same constraints = same output class.

Not necessarily byte-identical prose.
But identical structural decision.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional

from amos_kernel.contracts import KernelResult


@dataclass
class StateTransition:
    """A single state transition record."""

    from_state: str  # Hash of source state
    to_state: str  # Hash of destination state
    input_hash: str  # Hash of inputs
    constraint_hash: str  # Hash of constraints
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    integrity_at_transition: float = 1.0


@dataclass
class Prediction:
    """A prediction with confidence."""

    expected_state_hash: str
    confidence: float  # 0.0 to 1.0
    prediction_type: str  # "deterministic", "probabilistic", "heuristic"
    basis: dict[str, Any] = field(default_factory=dict)


@dataclass
class Correction:
    """A correction to apply."""

    error_signal: dict[str, Any]
    correction_type: str  # "feedback", "constraint", "integrity"
    magnitude: float
    target_axis: str  # "mu", "nu", "alpha", "beta"


class DeterministicCore:
    """
    The brain stem. All state transitions go through here.

    Maintains determinism: same inputs + same state + same constraints
    = same structural output class.
    """

    _instance: Optional[DeterministicCore] = None

    def __new__(cls) -> DeterministicCore:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._transition_history: list[StateTransition] = []
        self._prediction_history: list[Prediction] = []
        self._correction_history: list[Correction] = []
        self._transition_functions: dict[str, Callable] = {}
        self._initialized = True

    def transition(
        self,
        state: dict[str, Any],
        inputs: dict[str, Any],
        constraints: dict[str, Any],
        integrity: float = 1.0,
    ) -> KernelResult[dict[str, Any]]:
        """
        Execute state transition.

        S_{t+1} = F((i_A ⊗ i_B), Feedback, Constraints, Integrity)
        """
        # Compute input hash for determinism check
        input_hash = self._hash_dict(inputs)
        constraint_hash = self._hash_dict(constraints)
        state_hash = state.get("canonical_hash", self._hash_dict(state))

        # Build interaction operator: i_A ⊗ i_B
        interaction = self._build_interaction(inputs)

        # Apply constraints
        constrained = self._apply_constraints(interaction, constraints)

        # Apply integrity modulation
        if integrity < 0.5:
            # Low integrity: restrict transitions
            constrained = self._restrict_transitions(constrained)

        # Execute transition
        next_state = self._execute_transition(state, constrained, inputs)

        # Record
        transition = StateTransition(
            from_state=state_hash,
            to_state=next_state.get("canonical_hash", self._hash_dict(next_state)),
            input_hash=input_hash,
            constraint_hash=constraint_hash,
            integrity_at_transition=integrity,
        )
        self._transition_history.append(transition)

        return KernelResult.ok(next_state, "DeterministicCore")

    def predict(
        self,
        state: dict[str, Any],
        inputs: dict[str, Any],
        horizon: int = 1,
    ) -> Prediction:
        """
        Predict next state.

        Returns prediction with confidence based on pattern matching
        with historical transitions.
        """
        state_hash = state.get("canonical_hash", self._hash_dict(state))
        input_hash = self._hash_dict(inputs)

        # Search history for matching transitions
        matches = [
            t
            for t in self._transition_history
            if t.from_state == state_hash and t.input_hash == input_hash
        ]

        if matches:
            # Deterministic prediction based on history
            most_common = max(
                set(m.to_state for m in matches),
                key=lambda x: sum(1 for m in matches if m.to_state == x),
            )
            confidence = len([m for m in matches if m.to_state == most_common]) / len(matches)

            prediction = Prediction(
                expected_state_hash=most_common,
                confidence=confidence,
                prediction_type="deterministic" if confidence > 0.9 else "probabilistic",
                basis={
                    "historical_matches": len(matches),
                    "unique_outcomes": len(set(m.to_state for m in matches)),
                },
            )
        else:
            # No history: heuristic prediction
            prediction = Prediction(
                expected_state_hash=self._heuristic_prediction(state, inputs),
                confidence=0.5,
                prediction_type="heuristic",
                basis={"method": "structural_similarity"},
            )

        self._prediction_history.append(prediction)
        return prediction

    def compare(
        self,
        prediction: Prediction,
        observation: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Compare prediction with observation.

        Returns error signal for correction.
        """
        observed_hash = observation.get("canonical_hash", self._hash_dict(observation))

        if prediction.expected_state_hash == observed_hash:
            # Prediction correct
            return {
                "match": True,
                "error_magnitude": 0.0,
                "error_signal": {},
            }

        # Mismatch: compute error
        error_magnitude = 1.0 - prediction.confidence
        error_signal = {
            "predicted": prediction.expected_state_hash,
            "observed": observed_hash,
            "prediction_type": prediction.prediction_type,
            "confidence_at_prediction": prediction.confidence,
        }

        return {
            "match": False,
            "error_magnitude": error_magnitude,
            "error_signal": error_signal,
        }

    def correct(
        self,
        state: dict[str, Any],
        error: dict[str, Any],
    ) -> KernelResult[dict[str, Any]]:
        """
        Apply correction to state.

        Bounded adaptation: corrections are constrained to preserve
        core invariants.
        """
        if error.get("match", False):
            # No correction needed
            return KernelResult.ok(state, "DeterministicCore")

        error_signal = error.get("error_signal", {})
        magnitude = error.get("error_magnitude", 0.0)

        # Determine correction type based on error
        correction_type = self._classify_error(error_signal)

        # Apply bounded correction
        corrected = self._apply_bounded_correction(state, error_signal, magnitude, correction_type)

        # Record
        correction = Correction(
            error_signal=error_signal,
            correction_type=correction_type,
            magnitude=magnitude,
            target_axis=self._identify_target_axis(error_signal),
        )
        self._correction_history.append(correction)

        return KernelResult.ok(corrected, "DeterministicCore")

    def register_transition_function(self, name: str, fn: Callable[[dict, dict], dict]) -> None:
        """Register a transition function."""
        self._transition_functions[name] = fn

    def get_transition_history(self) -> list[StateTransition]:
        """Get transition history."""
        return self._transition_history.copy()

    def get_correction_rate(self) -> float:
        """Get current correction rate (corrections per transition)."""
        if not self._transition_history:
            return 0.0
        return len(self._correction_history) / len(self._transition_history)

    def _hash_dict(self, d: dict[str, Any]) -> str:
        """Compute hash of dict for determinism tracking."""
        import hashlib
        import json

        normalized = json.dumps(d, sort_keys=True, default=str)
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def _build_interaction(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Build interaction operator: i_A ⊗ i_B."""
        # Extract internal and external from inputs
        internal = inputs.get("internal", {})
        external = inputs.get("external", {})

        # Tensor product (simplified as combined dict)
        return {
            "internal": internal,
            "external": external,
            "interaction_strength": inputs.get("interaction_strength", 1.0),
        }

    def _apply_constraints(
        self, interaction: dict[str, Any], constraints: dict[str, Any]
    ) -> dict[str, Any]:
        """Apply constraints to interaction."""
        constrained = interaction.copy()

        # Apply allowed transitions constraint
        allowed = constraints.get("allowed_transitions", [])
        if allowed:
            constrained["allowed"] = allowed

        # Apply rate limits
        max_rate = constraints.get("max_transition_rate", float("inf"))
        constrained["max_rate"] = max_rate

        return constrained

    def _restrict_transitions(self, constrained: dict[str, Any]) -> dict[str, Any]:
        """Restrict transitions when integrity is low."""
        # Low integrity: only allow safe transitions
        restricted = constrained.copy()
        restricted["safe_mode"] = True
        restricted["allowed_transitions"] = ["maintenance", "repair", "observe"]
        return restricted

    def _execute_transition(
        self,
        state: dict[str, Any],
        constrained: dict[str, Any],
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute the actual state transition."""
        # Start from current state
        next_state = state.copy()

        # Apply transition functions
        for name, fn in self._transition_functions.items():
            try:
                result = fn(state, inputs)
                next_state.update(result)
            except Exception:
                # Transition function failed: preserve state
                pass

        # Apply constrained modifications
        if constrained.get("safe_mode"):
            # Safe mode: minimal state changes
            next_state["safe_mode"] = True

        # Update timestamp
        next_state["last_transition"] = datetime.now(UTC).isoformat()

        return next_state

    def _heuristic_prediction(self, state: dict[str, Any], inputs: dict[str, Any]) -> str:
        """Generate heuristic prediction when no history exists."""
        # Use structural similarity to nearest historical state
        if not self._transition_history:
            return "unknown"

        current_hash = state.get("canonical_hash", self._hash_dict(state))

        # Find nearest state in history (simplified: first match on partial hash)
        for transition in reversed(self._transition_history):
            if transition.from_state[:8] == current_hash[:8]:
                return transition.to_state

        return "unknown"

    def _classify_error(self, error_signal: dict[str, Any]) -> str:
        """Classify error type."""
        predicted = error_signal.get("predicted", "")
        observed = error_signal.get("observed", "")
        prediction_type = error_signal.get("prediction_type", "heuristic")

        if prediction_type == "deterministic" and predicted != observed:
            return "integrity"  # Deterministic prediction failed: integrity issue
        elif prediction_type == "probabilistic":
            return "feedback"  # Probabilistic: needs feedback correction
        else:
            return "constraint"  # Heuristic: constraint adjustment

    def _apply_bounded_correction(
        self,
        state: dict[str, Any],
        error_signal: dict[str, Any],
        magnitude: float,
        correction_type: str,
    ) -> dict[str, Any]:
        """Apply correction with bounds."""
        corrected = state.copy()

        # Bound magnitude
        bounded_magnitude = min(magnitude, 0.5)  # Max 50% correction per step

        if correction_type == "integrity":
            # Integrity correction: enter safe mode
            corrected["integrity_mode"] = "restricted"
            corrected["safe_mode"] = True
        elif correction_type == "feedback":
            # Feedback correction: adjust based on error
            current_confidence = corrected.get("confidence", 0.5)
            corrected["confidence"] = max(0.1, current_confidence - bounded_magnitude)
        elif correction_type == "constraint":
            # Constraint correction: tighten constraints
            corrected["constraint_tightness"] = (
                corrected.get("constraint_tightness", 1.0) + bounded_magnitude
            )

        corrected["last_correction"] = datetime.now(UTC).isoformat()
        corrected["correction_type"] = correction_type

        return corrected

    def _identify_target_axis(self, error_signal: dict[str, Any]) -> str:
        """Identify which tensor axis to target."""
        prediction_type = error_signal.get("prediction_type", "heuristic")

        if prediction_type == "deterministic":
            return "nu"  # Cognition/prediction axis
        elif prediction_type == "probabilistic":
            return "mu"  # Load/regulation axis
        else:
            return "alpha"  # Policy axis


def get_deterministic_core() -> DeterministicCore:
    """Get the singleton deterministic core."""
    return DeterministicCore()
