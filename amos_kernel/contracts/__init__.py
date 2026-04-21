"""Kernel contracts - formal interfaces for all kernel layers."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Generic, Optional, TypeVar


class LawPrecedence(Enum):
    """Law precedence levels. Higher = more fundamental."""

    CONSTITUTIONAL = 100  # Cannot be overridden
    PRIMAL = 90  # Core system laws
    ARCHITECTURAL = 80  # Build/runtime structure
    OPERATIONAL = 70  # Day-to-day operations
    ADVISORY = 60  # Suggestions/warnings


class Quadrant(Enum):
    """Four-quadrant completeness model."""

    CODE = auto()  # Code correctness
    BUILD = auto()  # Build/release correctness
    OPERATIONAL = auto()  # Runtime correctness
    ENVIRONMENT = auto()  # Dependency/context correctness


class InvariantStatus(Enum):
    """Status of invariant validation."""

    SATISFIED = auto()
    VIOLATED = auto()
    INDETERMINATE = auto()
    DEGRADED = auto()


@dataclass(frozen=True)
class Invariant:
    """A formal invariant with precedence."""

    name: str
    expression: str
    precedence: LawPrecedence
    check_fn: str  # Reference to validation function


@dataclass(frozen=True)
class Contradiction:
    """Detected contradiction between claims."""

    claim_a: str
    claim_b: str
    invariant: str
    severity: float  # 0.0 to 1.0
    context: dict[str, Any]
    timestamp: datetime


@dataclass(frozen=True)
class QuadrantScore:
    """Score for one quadrant."""

    quadrant: Quadrant
    score: float  # 0.0 to 1.0
    checks_passed: int
    checks_failed: int
    details: dict[str, Any]


@dataclass(frozen=True)
class IntegrityReport:
    """Four-quadrant integrity report."""

    overall_score: float
    code: QuadrantScore
    build: QuadrantScore
    operational: QuadrantScore
    environment: QuadrantScore
    timestamp: datetime


T = TypeVar("T")


@dataclass(frozen=True)
class KernelResult(Generic[T]):
    """Standard kernel operation result."""

    success: bool
    value: Optional[T]
    contradictions: list[Contradiction]
    integrity: Optional[IntegrityReport]
    errors: list[str]
    validated_by: str  # Which layer validated
    timestamp: datetime

    @classmethod
    def ok(cls, value: T, validator: str) -> "KernelResult[T]":
        return cls(
            success=True,
            value=value,
            contradictions=[],
            integrity=None,
            errors=[],
            validated_by=validator,
            timestamp=datetime.now(UTC),
        )

    @classmethod
    def fail(
        cls, errors: list[str], validator: str, contradictions: Optional[list[Contradiction]] = None
    ) -> "KernelResult[Any]":
        return cls(
            success=False,
            value=None,
            contradictions=contradictions or [],
            integrity=None,
            errors=errors,
            validated_by=validator,
            timestamp=datetime.now(UTC),
        )


CORE_INVARIANTS: list[Invariant] = [
    Invariant(
        name="non_contradiction",
        expression="¬(A ∧ ¬A)",
        precedence=LawPrecedence.CONSTITUTIONAL,
        check_fn="check_non_contradiction",
    ),
    Invariant(
        name="dual_interaction",
        expression="S = (x_internal, x_external), x_external ≠ ∅",
        precedence=LawPrecedence.PRIMAL,
        check_fn="check_dual_interaction",
    ),
    Invariant(
        name="quadrant_completeness",
        expression="∏ I(Q_i) > 0",
        precedence=LawPrecedence.PRIMAL,
        check_fn="check_quadrant_completeness",
    ),
    Invariant(
        name="correction_rate",
        expression="dC/dt ≤ dR/dt",
        precedence=LawPrecedence.ARCHITECTURAL,
        check_fn="check_correction_rate",
    ),
    Invariant(
        name="determinism",
        expression="same(state, inputs, constraints) → same(output_class)",
        precedence=LawPrecedence.ARCHITECTURAL,
        check_fn="check_determinism",
    ),
]

__all__ = [
    "LawPrecedence",
    "Quadrant",
    "InvariantStatus",
    "Invariant",
    "Contradiction",
    "QuadrantScore",
    "IntegrityReport",
    "KernelResult",
    "CORE_INVARIANTS",
]
