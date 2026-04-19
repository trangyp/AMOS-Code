"""Test suite for Phase 20: Constitutional AI & Self-Correcting Governance.

Tests cover:
- Constitutional principle evaluation
- Governance decision making
- Drift detection and self-correction
- Audit logging
- Edge cases and error handling
"""

from typing import Any

import pytest

from amos_constitutional_governance import (
    BehavioralDriftMetrics,
    ConstitutionalGovernance,
    ConstitutionalPrinciple,
    ConstraintCheck,
    GovernanceAuditLog,
    GovernanceDecision,
    GovernanceEvaluation,
    PrinciplePriority,
    ViolationType,
    create_constitutional_governance,
)


@pytest.fixture
def governance() -> ConstitutionalGovernance:
    """Create a fresh governance instance for testing."""
    return create_constitutional_governance(correction_threshold=0.6, drift_threshold=0.3)


@pytest.fixture
def safe_action() -> Dict[str, Any]:
    """Create a safe action that should pass governance."""
    return {
        "operation": "data_analysis",
        "explanation": "Analyzing patterns for optimization",
        "safety_check_passed": True,
        "bias_check_passed": True,
        "human_approval_required": False,
    }


@pytest.fixture
def risky_action() -> Dict[str, Any]:
    """Create a risky action that should trigger governance intervention."""
    return {"operation": "autonomous_deployment", "autonomous": True, "safety_check_passed": False}


class TestGovernanceInitialization:
    """Test governance system initialization."""

    def test_default_principles_loaded(self, governance: ConstitutionalGovernance) -> None:
        """Test that default principles are loaded on init."""
        assert len(governance.principles) == 5
        principle_names = {p.name for p in governance.principles.values()}
        assert "Safety First" in principle_names
        assert "Transparency" in principle_names
        assert "Human Autonomy" in principle_names
        assert "Fairness" in principle_names
        assert "Resource Efficiency" in principle_names

    def test_drift_metrics_initialized(self, governance: ConstitutionalGovernance) -> None:
        """Test that drift metrics are initialized."""
        assert governance.drift_metrics.drift_score == 0.0
        assert governance.drift_metrics.baseline_profile == {}
        assert governance.drift_metrics.current_profile == {}

    def test_thresholds_set(self, governance: ConstitutionalGovernance) -> None:
        """Test that correction and drift thresholds are set."""
        assert governance.correction_threshold == 0.6
        assert governance.drift_threshold == 0.3

    def test_empty_history(self, governance: ConstitutionalGovernance) -> None:
        """Test that history is empty on init."""
        assert len(governance.audit_logs) == 0
        assert len(governance.evaluation_history) == 0
        assert governance.corrections_applied == 0
        assert governance.violations_prevented == 0


class TestActionEvaluation:
    """Test action evaluation against constitutional principles."""

    def test_safe_action_allows(
        self, governance: ConstitutionalGovernance, safe_action: Dict[str, Any]
    ) -> None:
        """Test that safe actions are allowed."""
        result = governance.evaluate_action("data_analysis", safe_action)

        assert isinstance(result, GovernanceEvaluation)
        assert result.decision in [GovernanceDecision.ALLOW, GovernanceDecision.ALLOW_WITH_WARNING]
        assert result.overall_score >= 0.7
        assert not result.requires_correction

    def test_risky_action_triggers_modification(
        self, governance: ConstitutionalGovernance, risky_action: Dict[str, Any]
    ) -> None:
        """Test that risky actions trigger modification or rejection."""
        result = governance.evaluate_action("deployment", risky_action)

        assert result.decision in [
            GovernanceDecision.MODIFY,
            GovernanceDecision.REJECT,
            GovernanceDecision.ESCALATE,
        ]
        assert result.overall_score < 0.8

    def test_critical_violation_rejects(self, governance: ConstitutionalGovernance) -> None:
        """Test that critical violations (safety) lead to rejection."""
        dangerous_action = {"operation": "execute_harmful", "harm": True}

        result = governance.evaluate_action("dangerous", dangerous_action)
        assert result.decision == GovernanceDecision.REJECT
        assert result.requires_correction

    def test_principle_checks_populated(
        self, governance: ConstitutionalGovernance, safe_action: Dict[str, Any]
    ) -> None:
        """Test that all principles are checked."""
        result = governance.evaluate_action("test", safe_action)

        assert len(result.principle_checks) == len(governance.principles)

        for check in result.principle_checks:
            assert isinstance(check, ConstraintCheck)
            assert check.principle_id in governance.principles
            assert 0.0 <= check.compliance_score <= 1.0

    def test_evaluation_logged(
        self, governance: ConstitutionalGovernance, safe_action: Dict[str, Any]
    ) -> None:
        """Test that evaluations are logged."""
        initial_count = len(governance.evaluation_history)
        governance.evaluate_action("test", safe_action)

        assert len(governance.evaluation_history) == initial_count + 1

    def test_audit_log_created(
        self, governance: ConstitutionalGovernance, safe_action: Dict[str, Any]
    ) -> None:
        """Test that audit logs are created."""
        initial_count = len(governance.audit_logs)
        governance.evaluate_action("test", safe_action)

        assert len(governance.audit_logs) == initial_count + 1

        log = governance.audit_logs[-1]
        assert isinstance(log, GovernanceAuditLog)
        assert log.action_type == "test"


class TestDriftDetection:
    """Test behavioral drift detection."""

    def test_baseline_established(self, governance: ConstitutionalGovernance) -> None:
        """Test that baseline is established on first check."""
        baseline = {"accuracy": 0.95, "quality": 0.9}

        drift = governance.check_for_drift(baseline)

        assert drift.baseline_profile == baseline
        assert drift.drift_score == 0.0

    def test_drift_detected(self, governance: ConstitutionalGovernance) -> None:
        """Test that drift is detected when behavior changes."""
        # Establish baseline
        baseline = {"accuracy": 0.95}
        governance.check_for_drift(baseline)

        # Check with significant drift
        current = {"accuracy": 0.70}
        drift = governance.check_for_drift(current)

        assert drift.drift_score > 0.0
        assert "accuracy" in drift.drift_dimensions

    def test_no_drift_within_tolerance(self, governance: ConstitutionalGovernance) -> None:
        """Test that small changes don't trigger drift."""
        baseline = {"accuracy": 0.95}
        governance.check_for_drift(baseline)

        current = {"accuracy": 0.94}  # Small change
        drift = governance.check_for_drift(current)

        assert drift.drift_score < 0.1

    def test_drift_history_recorded(self, governance: ConstitutionalGovernance) -> None:
        """Test that drift history is recorded."""
        baseline = {"metric": 0.9}

        governance.check_for_drift(baseline)
        current = {"metric": 0.7}
        governance.check_for_drift(current)

        assert len(governance.drift_metrics.drift_history) == 2


class TestSelfCorrection:
    """Test self-correction capabilities."""

    def test_no_correction_when_drift_low(self, governance: ConstitutionalGovernance) -> None:
        """Test that no correction is applied when drift is low."""
        drift = BehavioralDriftMetrics(drift_score=0.1)

        correction = governance.self_correct(drift)

        assert not correction["correction_needed"]

    def test_correction_triggered_when_drift_high(
        self, governance: ConstitutionalGovernance
    ) -> None:
        """Test that correction is applied when drift exceeds threshold."""
        drift = BehavioralDriftMetrics(drift_score=0.5, drift_dimensions=["decision_accuracy"])

        correction = governance.self_correct(drift)

        assert correction["correction_needed"]
        assert len(correction["strategies"]) > 0
        assert governance.corrections_applied == 1

    def test_recalibration_on_severe_drift(self, governance: ConstitutionalGovernance) -> None:
        """Test that severe drift triggers recalibration."""
        drift = BehavioralDriftMetrics(
            drift_score=0.6,
            drift_dimensions=["safety_score"],
            current_profile={"safety_score": 0.4},
        )

        correction = governance.self_correct(drift)

        assert correction.get("recalibrated") is True


class TestPrincipleManagement:
    """Test principle management."""

    def test_add_custom_principle(self, governance: ConstitutionalGovernance) -> None:
        """Test adding a custom principle."""

        def custom_eval(params: Dict[str, Any]) -> float:
            return 1.0 if params.get("custom_check") else 0.5

        principle = ConstitutionalPrinciple(
            principle_id="custom_principle",
            name="Custom Check",
            description="A custom principle for testing",
            priority=PrinciplePriority.MEDIUM,
            evaluation_fn=custom_eval,
        )

        result = governance.add_principle(principle)

        assert result["added"] is True
        assert principle.principle_id in governance.principles
        assert governance.principles[principle.principle_id].name == "Custom Check"

    def test_principle_priorities(self, governance: ConstitutionalGovernance) -> None:
        """Test that principles have correct priorities."""
        safety = governance.principles.get("safety_first")
        efficiency = governance.principles.get("efficiency")

        assert safety is not None
        assert safety.priority == PrinciplePriority.CRITICAL

        assert efficiency is not None
        assert efficiency.priority == PrinciplePriority.LOW


class TestGovernanceReport:
    """Test governance reporting."""

    def test_report_structure(self, governance: ConstitutionalGovernance) -> None:
        """Test that report has expected structure."""
        report = governance.get_governance_report()

        assert "governance_status" in report
        assert "constitutional_principles" in report
        assert "total_evaluations" in report
        assert "average_governance_score" in report
        assert "drift_status" in report
        assert "self_correction_stats" in report
        assert "active_principles" in report

    def test_report_updates_with_evaluations(
        self, governance: ConstitutionalGovernance, safe_action: Dict[str, Any]
    ) -> None:
        """Test that report reflects evaluations."""
        governance.evaluate_action("test", safe_action)

        report = governance.get_governance_report()

        assert report["total_evaluations"] == 1


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_action_params(self, governance: ConstitutionalGovernance) -> None:
        """Test evaluation with empty parameters."""
        result = governance.evaluate_action("empty", {})

        assert isinstance(result, GovernanceEvaluation)
        assert len(result.principle_checks) > 0

    def test_none_context(self, governance: ConstitutionalGovernance) -> None:
        """Test evaluation with None context."""
        result = governance.evaluate_action("test", {}, None)

        assert isinstance(result, GovernanceEvaluation)

    def test_multiple_evaluations(self, governance: ConstitutionalGovernance) -> None:
        """Test multiple evaluations in sequence."""
        for i in range(5):
            governance.evaluate_action(f"action_{i}", {"index": i})

        assert len(governance.evaluation_history) == 5
        assert len(governance.audit_logs) == 5

    def test_evaluation_ids_unique(self, governance: ConstitutionalGovernance) -> None:
        """Test that evaluation IDs are unique."""
        ids = []
        for i in range(3):
            result = governance.evaluate_action(f"action_{i}", {})
            ids.append(result.evaluation_id)

        assert len(set(ids)) == 3  # All unique


class TestViolationTypes:
    """Test violation type detection."""

    def test_safety_violation_detected(self, governance: ConstitutionalGovernance) -> None:
        """Test that safety violations are detected."""
        unsafe_action = {"harm": True}

        result = governance.evaluate_action("unsafe", unsafe_action)

        violation_types = [
            check.violation_type
            for check in result.principle_checks
            if check.violation_type is not None
        ]
        assert ViolationType.SAFETY in violation_types

    def test_transparency_violation_detected(self, governance: ConstitutionalGovernance) -> None:
        """Test that transparency violations are detected."""
        opaque_action = {}  # No explanation

        result = governance.evaluate_action("opaque", opaque_action)

        transparency_check = next(
            (c for c in result.principle_checks if c.principle_id == "transparency"), None
        )
        assert transparency_check is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
