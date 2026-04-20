"""Tests for Law Layer (L0)"""

from amos_kernel.core.law import (
    BiologicalConstraint,
    Law,
    LawCheckResult,
    QuadrantIntegrity,
    StabilityConstraint,
    UniversalLawKernel,
)


class TestUniversalLawKernel:
    def test_get_law_returns_law(self):
        law = UniversalLawKernel()
        result = law.get_law("L1")
        assert isinstance(result, Law)
        assert result.id == "L1"

    def test_get_law_missing_returns_none(self):
        law = UniversalLawKernel()
        result = law.get_law("L99")
        assert result is None

    def test_validate_action_compliant(self):
        law = UniversalLawKernel()
        result = law.validate_action("safe analysis")
        assert isinstance(result, LawCheckResult)

    def test_validate_invariants_passes(self):
        law = UniversalLawKernel()
        result = law.validate_invariants(
            contradictions=0,
            has_internal=True,
            has_external=True,
            has_feedback=True,
            stability=StabilityConstraint(0.1, 0.2),
            bio=BiologicalConstraint(50, 100),
            quadrants=QuadrantIntegrity(1.0, 1.0, 1.0, 1.0),
        )
        assert isinstance(result.passed, bool)
        assert 0.0 <= result.collapse_risk <= 1.0


class TestInvariants:
    from amos_kernel.core.law import no_contradiction

    def test_no_contradiction_passes_with_zero(self):
        result = self.no_contradiction(0)
        assert result.passed is True

    def test_no_contradiction_fails_with_contradictions(self):
        result = self.no_contradiction(1)
        assert result.passed is False
