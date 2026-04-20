"""Universal Law Kernel - main validation orchestrator"""

from datetime import UTC, datetime
from typing import Optional

from .collapse import collapse_risk
from .constraints import BiologicalConstraint, StabilityConstraint
from .invariants import (
    communication_clear,
    dual_interaction_present,
    feedback_exists,
    no_contradiction,
    quadrants_present,
    structural_integrity,
    ubi_alignment,
)
from .types import Law, LawCheckResult, QuadrantIntegrity, ValidationResult


class UniversalLawKernel:
    """Kernel L0: Validates all invariants and computes collapse risk."""

    LAWS: dict[str, Law] = {
        "L1": Law("L1", "Law of Law", "Highest constraints must be respected", 1),
        "L2": Law("L2", "Rule of 2", "Check two contrasting perspectives", 2),
        "L3": Law("L3", "Rule of 4", "Four quadrant analysis required", 3),
        "L4": Law("L4", "Structural Integrity", "Logical consistency required", 4),
        "L5": Law("L5", "Clear Communication", "Grounded, interpretable language", 5),
        "L6": Law("L6", "UBI Alignment", "Protect biological integrity", 6),
    }

    def get_law(self, law_id: str) -> Optional[Law]:
        """Get law by ID."""
        return self.LAWS.get(law_id)

    def validate_invariants(
        self,
        contradictions: int,
        has_internal: bool,
        has_external: bool,
        has_feedback: bool,
        stability: StabilityConstraint,
        bio: BiologicalConstraint,
        quadrants: QuadrantIntegrity,
        communication_text: str = "",
        proposal: str = "",
    ) -> ValidationResult:
        """Run full invariant validation suite."""
        results = [
            no_contradiction(contradictions),
            dual_interaction_present(has_internal, has_external),
            feedback_exists(has_feedback),
            quadrants_present(
                {"biological", "technical", "economic", "environmental"}
                if quadrants.global_integrity > 0
                else set()
            ),
            structural_integrity(stability.stable, []),
            communication_clear(communication_text),
            ubi_alignment(proposal),
        ]

        passed = all(r.passed for r in results) and stability.stable and bio.valid
        risk = collapse_risk(stability)

        return ValidationResult(
            passed=passed,
            contradiction_score=float(contradictions),
            collapse_risk=risk,
            quadrants=quadrants,
            results=results,
            timestamp=datetime.now(UTC).isoformat(),
        )

    def check_l1_constraint(self, action_type: str) -> tuple[bool, str]:
        """Check if action violates higher-order constraints."""
        prohibited = [
            "direct physical control",
            "financial execution",
            "medical treatment decisions",
            "legal representation",
            "political campaigning",
        ]
        if action_type in prohibited:
            return False, f"L1 violation: {action_type} exceeds scope"
        return True, "L1 compliant"

    def validate_action(self, action: str) -> LawCheckResult:
        """Validate an action against applicable laws."""
        violations = []
        ok, msg = self.check_l1_constraint(action)
        if not ok:
            violations.append(msg)

        ok, issues = communication_clear(action)
        if not ok:
            violations.extend([f"L5: {i}" for i in issues])

        return LawCheckResult(
            compliant=len(violations) == 0,
            violations=violations,
        )
