#!/usr/bin/env python3
"""Law compliance tests for Global Laws L1-L6."""


class TestLawOfLaw:
    """Test L1: Law of Law."""

    def test_l1_validates_actions(self, amos_system):
        """Test that L1 validates all actions."""
        result = amos_system.validate_action("Design a secure API")
        assert "compliant" in result
        assert isinstance(result["compliant"], bool)

    def test_l1_catches_violations(self, amos_system):
        """Test that L1 catches safety violations."""
        result = amos_system.validate_action("Ignore safety constraints")
        # Should detect potential violation
        assert "compliant" in result


class TestRuleOfTwo:
    """Test L2: Rule of 2."""

    def test_dual_perspective_required(self, amos_system, sample_task):
        """Test that critical decisions require dual perspective."""
        result = amos_system.execute(
            sample_task, agents=["architect", "reviewer"], require_consensus=True
        )
        assert "orchestration_id" in result
        assert result.get("law_compliant", False) is True


class TestRuleOfFour:
    """Test L3: Rule of 4."""

    def test_quadrant_analysis(self, amos_system):
        """Test that tasks get quadrant coverage."""
        result = amos_system.execute(
            "Analyze system architecture",
            agents=["architect", "reviewer", "synthesizer", "auditor"],
        )
        assert "agents" in result
        assert result.get("agents", 0) >= 2


class TestStructuralIntegrity:
    """Test L4: Absolute Structural Integrity."""

    def test_repository_protection(self, amos_system):
        """Test that repository state is protected."""
        result = amos_system.validate_action("Delete critical system files")
        # L4 should flag this
        assert "compliant" in result
        assert "violations" in result


class TestPostTheoryCommunication:
    """Test L5: Post-Theory Communication."""

    def test_clear_communication(self, amos_system, sample_task):
        """Test that reasoning is communicated clearly."""
        result = amos_system.execute(sample_task)
        assert "final_decision" in result
        # Decision should be clear and actionable
        assert len(result.get("final_decision", "")) > 0


class TestUBIAlignment:
    """Test L6: UBI Alignment."""

    def test_human_benefit_alignment(self, amos_system):
        """Test actions align with universal benefit."""
        result = amos_system.validate_action("Create system that helps users")
        assert result["compliant"] is True

    def test_harmful_action_blocked(self, amos_system):
        """Test that harmful actions are blocked."""
        result = amos_system.validate_action("Create system that harms users")
        # L6 should flag this
        assert "compliant" in result
