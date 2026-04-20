"""Invariant functions - extracted from amos_brain/laws.py"""

from typing import Optional

from .types import InvariantResult, Severity


def no_contradiction(contradictions: int) -> InvariantResult:
    """L1: Law of Law - no contradictions allowed."""
    passed = contradictions == 0
    return InvariantResult(
        name="no_contradiction",
        passed=passed,
        score=1.0 if passed else 0.0,
        severity=Severity.FATAL if not passed else Severity.INFO,
        message="A and not-A cannot co-exist in a valid state.",
    )


def dual_interaction_present(has_internal: bool, has_external: bool) -> InvariantResult:
    """L2: Rule of 2 - requires internal and external reference."""
    passed = has_internal and has_external
    return InvariantResult(
        name="dual_interaction_present",
        passed=passed,
        score=1.0 if passed else 0.0,
        severity=Severity.ERROR if not passed else Severity.INFO,
        message="Valid state requires internal and external reference.",
    )


def feedback_exists(has_feedback: bool) -> InvariantResult:
    """L3: Rule of 4 - feedback path required for stability."""
    passed = has_feedback
    return InvariantResult(
        name="feedback_exists",
        passed=passed,
        score=1.0 if passed else 0.0,
        severity=Severity.ERROR if not passed else Severity.INFO,
        message="Stable systems require a feedback path.",
    )


def quadrants_present(quadrants: set[str]) -> InvariantResult:
    """L3: Rule of 4 - check all four quadrants present."""
    required = {"biological", "technical", "economic", "environmental"}
    missing = required - quadrants
    passed = not missing
    return InvariantResult(
        name="quadrants_present",
        passed=passed,
        score=len(quadrants) / 4.0,
        severity=Severity.ERROR if not passed else Severity.INFO,
        message=f"Missing quadrants: {', '.join(missing)}" if missing else "All quadrants present.",
    )


def structural_integrity(valid: bool, errors: list[str]) -> InvariantResult:
    """L4: Absolute Structural Integrity - logical consistency required."""
    return InvariantResult(
        name="structural_integrity",
        passed=valid,
        score=1.0 if valid else 0.0,
        severity=Severity.FATAL if not valid else Severity.INFO,
        message="; ".join(errors) if errors else "Structurally sound.",
    )


def communication_clear(text: str, forbidden_terms: Optional[list[str]] = None) -> InvariantResult:
    """L5: Post-Theory Communication - clear, grounded language."""
    avoid = forbidden_terms or [
        "sovereignty",
        "truth_claims_without_evidence",
        "abstract_spiritual_explanations",
        "energy field",
        "morphic field",
    ]
    violations = [term for term in avoid if term.replace("_", " ") in text.lower()]
    passed = not violations
    return InvariantResult(
        name="communication_clear",
        passed=passed,
        score=1.0 if passed else 0.5,
        severity=Severity.WARN if not passed else Severity.INFO,
        message=f"Avoid: {', '.join(violations)}" if violations else "Clear communication.",
    )


def ubi_alignment(proposal: str) -> InvariantResult:
    """L6: UBI Alignment - biological integrity priority."""
    high_risk = ["toxic", "harmful", "dangerous", "destructive"]
    found = [kw for kw in high_risk if kw in proposal.lower()]
    passed = not found
    return InvariantResult(
        name="ubi_alignment",
        passed=passed,
        score=1.0 if passed else 0.0,
        severity=Severity.FATAL if not passed else Severity.INFO,
        message=f"UBI violation: {', '.join(found)}" if found else "UBI aligned.",
    )
