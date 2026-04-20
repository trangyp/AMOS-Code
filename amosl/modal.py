"""AMOSL Modal Logic - Stratified Truth Domain.

Implements the logical regime:
    - Truth domain T_AMOS = {T, ⊥, Prob(p), Unknown, Ctx(κ), Bound([l,u])}
    - Modal operators: □ (necessity), ◇ (possibility)
    - Observational modality O_m
    - Evolution modality E
"""

import math
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TruthValue(Enum):
    """Truth domain T_AMOS."""

    TRUE = auto()
    FALSE = auto()
    PROBABILISTIC = auto()
    UNKNOWN = auto()
    CONTEXTUAL = auto()
    BOUNDED = auto()


@dataclass
class StratifiedTruth:
    """Stratified truth value."""

    value_type: TruthValue
    probability: float = None
    context: str = None
    lower_bound: float = None
    upper_bound: float = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def is_definitely_true(self) -> bool:
        """Check if definitely true."""
        if self.value_type == TruthValue.TRUE:
            return True
        if self.value_type == TruthValue.PROBABILISTIC and self.probability:
            return self.probability >= 0.99
        if self.value_type == TruthValue.BOUNDED:
            return self.lower_bound and self.lower_bound >= 1.0
        return False

    def is_definitely_false(self) -> bool:
        """Check if definitely false."""
        if self.value_type == TruthValue.FALSE:
            return True
        if self.value_type == TruthValue.PROBABILISTIC and self.probability:
            return self.probability <= 0.01
        if self.value_type == TruthValue.BOUNDED:
            return self.upper_bound and self.upper_bound <= 0.0
        return False

    def confidence(self) -> float:
        """Extract confidence level."""
        if self.value_type == TruthValue.TRUE:
            return 1.0
        if self.value_type == TruthValue.FALSE:
            return 0.0
        if self.value_type == TruthValue.PROBABILISTIC and self.probability:
            return self.probability
        if self.value_type == TruthValue.BOUNDED:
            if self.lower_bound and self.upper_bound:
                return (self.lower_bound + self.upper_bound) / 2
        return 0.5  # Unknown


class ModalLogic:
    """Modal logic operations for AMOSL."""

    def __init__(self):
        self.futures: list[Callable[[], StratifiedTruth]] = []
        self.observations: dict[str, Any] = {}

    def necessity(
        self, predicate: Callable[[Any], StratifiedTruth], domain: list[Any]
    ) -> StratifiedTruth:
        """□P(x) := P(x) holds in all admissible futures.

        Necessity: predicate must hold for all elements in domain.
        """
        if not domain:
            return StratifiedTruth(TruthValue.UNKNOWN)

        results = [predicate(x) for x in domain]

        # Check if all true
        all_true = all(r.is_definitely_true() for r in results)
        if all_true:
            return StratifiedTruth(TruthValue.TRUE)

        # Check if any false (then not necessary)
        any_false = any(r.is_definitely_false() for r in results)
        if any_false:
            return StratifiedTruth(TruthValue.FALSE)

        # Probabilistic necessity
        avg_confidence = sum(r.confidence() for r in results) / len(results)
        return StratifiedTruth(TruthValue.PROBABILISTIC, probability=avg_confidence)

    def possibility(
        self, predicate: Callable[[Any], StratifiedTruth], domain: list[Any]
    ) -> StratifiedTruth:
        """◇P(x) := exists admissible future where P holds.

        Possibility: predicate holds for at least one element in domain.
        """
        if not domain:
            return StratifiedTruth(TruthValue.FALSE)

        results = [predicate(x) for x in domain]

        # Check if any true
        any_true = any(r.is_definitely_true() for r in results)
        if any_true:
            return StratifiedTruth(TruthValue.TRUE)

        # Check if all false (then not possible)
        all_false = all(r.is_definitely_false() for r in results)
        if all_false:
            return StratifiedTruth(TruthValue.FALSE)

        # Probabilistic possibility
        max_confidence = max(r.confidence() for r in results)
        return StratifiedTruth(TruthValue.PROBABILISTIC, probability=max_confidence)

    def observational_modality(
        self, predicate: StratifiedTruth, measurement: str, post_state: Any
    ) -> StratifiedTruth:
        """O_m P := P after measurement/assay m.

        Observational modality: truth after observation perturbation.
        """
        # Observation changes belief
        confidence = predicate.confidence()

        # Measurement adds uncertainty
        new_confidence = confidence * 0.95  # Small perturbation

        return StratifiedTruth(
            TruthValue.PROBABILISTIC,
            probability=new_confidence,
            context=f"after_{measurement}",
            metadata={"post_state": post_state},
        )

    def evolution_modality(
        self, predicate: StratifiedTruth, refinement_level: int
    ) -> StratifiedTruth:
        """E P := P after adaptive refinement.

        Evolution modality: truth after learning/adaptation.
        """
        confidence = predicate.confidence()

        # Refinement increases confidence
        improvement = 1.0 - math.exp(-refinement_level / 10.0)
        new_confidence = min(1.0, confidence + (1.0 - confidence) * improvement)

        return StratifiedTruth(
            TruthValue.PROBABILISTIC,
            probability=new_confidence,
            context=f"refined_{refinement_level}",
            metadata={"improvement": improvement},
        )

    def and_op(self, left: StratifiedTruth, right: StratifiedTruth) -> StratifiedTruth:
        """Logical AND for stratified truth."""
        # Handle definite values
        if left.is_definitely_false() or right.is_definitely_false():
            return StratifiedTruth(TruthValue.FALSE)

        if left.is_definitely_true() and right.is_definitely_true():
            return StratifiedTruth(TruthValue.TRUE)

        # Probabilistic combination
        p_left = left.confidence()
        p_right = right.confidence()
        combined = p_left * p_right  # Independent events

        return StratifiedTruth(TruthValue.PROBABILISTIC, probability=combined)

    def or_op(self, left: StratifiedTruth, right: StratifiedTruth) -> StratifiedTruth:
        """Logical OR for stratified truth."""
        # Handle definite values
        if left.is_definitely_true() or right.is_definitely_true():
            return StratifiedTruth(TruthValue.TRUE)

        if left.is_definitely_false() and right.is_definitely_false():
            return StratifiedTruth(TruthValue.FALSE)

        # Probabilistic combination
        p_left = left.confidence()
        p_right = right.confidence()
        combined = p_left + p_right - p_left * p_right

        return StratifiedTruth(TruthValue.PROBABILISTIC, probability=min(1.0, combined))

    def implies(self, antecedent: StratifiedTruth, consequent: StratifiedTruth) -> StratifiedTruth:
        """Logical implication for stratified truth."""
        # P → Q = ¬P ∨ Q
        p = antecedent.confidence()
        q = consequent.confidence()

        # Material implication
        result = (1.0 - p) + q - (1.0 - p) * q

        return StratifiedTruth(TruthValue.PROBABILISTIC, probability=min(1.0, result))

    def not_op(self, operand: StratifiedTruth) -> StratifiedTruth:
        """Logical NOT for stratified truth."""
        if operand.is_definitely_true():
            return StratifiedTruth(TruthValue.FALSE)

        if operand.is_definitely_false():
            return StratifiedTruth(TruthValue.TRUE)

        return StratifiedTruth(TruthValue.PROBABILISTIC, probability=1.0 - operand.confidence())

    def bounded_truth(self, value: float, lower: float, upper: float) -> StratifiedTruth:
        """Create bounded truth value."""
        return StratifiedTruth(
            TruthValue.BOUNDED,
            lower_bound=lower,
            upper_bound=upper,
            probability=(lower + upper) / 2,
        )

    def contextual_truth(self, base_truth: StratifiedTruth, context: str) -> StratifiedTruth:
        """Create context-dependent truth."""
        return StratifiedTruth(
            value_type=TruthValue.CONTEXTUAL,
            probability=base_truth.confidence(),
            context=context,
            metadata=base_truth.metadata,
        )


class AdmissibilityLogic:
    """Logic of admissibility for AMOSL constraints."""

    def __init__(self, modal_logic: ModalLogic):
        self.modal = modal_logic
        self.constraints: list[Callable[[Any], StratifiedTruth]] = []

    def add_constraint(self, constraint: Callable[[Any], StratifiedTruth]):
        """Add hard constraint."""
        self.constraints.append(constraint)

    def check_admissibility(self, state: Any) -> StratifiedTruth:
        """Check if state satisfies all constraints.

        Valid(x) = ∧_i C_i(x)
        """
        if not self.constraints:
            return StratifiedTruth(TruthValue.TRUE)

        # Check all constraints
        results = [c(state) for c in self.constraints]

        # Combine with AND
        combined = results[0]
        for r in results[1:]:
            combined = self.modal.and_op(combined, r)

        return combined

    def necessity_of_commitment(self, state: Any, future_states: list[Any]) -> StratifiedTruth:
        """Check necessity of Commit(x') → Valid(x') = 1.

        □(Commit → Valid)
        """

        def implies_valid(future):
            # Simulate commitment to future
            # Check if valid
            valid = self.check_admissibility(future)
            # Return implication
            return self.modal.implies(
                StratifiedTruth(TruthValue.TRUE),  # Assume committed
                valid,
            )

        return self.modal.necessity(implies_valid, future_states)

    def possibility_of_explanation(self, ledger: list[Any], outcome: Any) -> StratifiedTruth:
        """Check possibility of Explain(L) = Outcome.

        ◇(Explain(L) = Outcome)
        """

        def explains(l):
            # Check if ledger entry explains outcome
            if hasattr(l, "outcome"):
                matches = l.outcome == outcome
                return StratifiedTruth(TruthValue.TRUE if matches else TruthValue.FALSE)
            return StratifiedTruth(TruthValue.UNKNOWN)

        return self.modal.possibility(explains, ledger)


def truth_to_bool(truth: StratifiedTruth, threshold: float = 0.5) -> bool:
    """Convert stratified truth to boolean (for traditional interfaces)."""
    return truth.confidence() >= threshold
