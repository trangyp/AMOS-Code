"""Phase 15: Multi-Agent Orchestration & Agent Economics Test Suite (2026)."""

import pytest

from amos_superbrain_equation_bridge import Domain, MathematicalPattern, SuperBrainEquationRegistry


class TestPhase15MultiAgentOrchestration:
    """Test Phase 15: Multi-Agent Orchestration equations."""

    @pytest.fixture
    def registry(self):
        return SuperBrainEquationRegistry()

    def test_multi_agent_consensus_basic(self, registry):
        """Test multi-agent consensus with basic parameters."""
        result = registry.execute(
            "multi_agent_consensus",
            {"agent_confidences": [0.8, 0.9, 0.7, 0.85], "agreement_threshold": 0.6},
        )
        assert result.invariants_valid
        assert "consensus_score" in result.outputs["result"]
        assert "consensus_reached" in result.outputs["result"]
        assert "agent_count" in result.outputs["result"]
        assert result.outputs["result"]["consensus_score"] > 0
        assert result.outputs["result"]["agent_count"] == 4

    def test_multi_agent_consensus_high_confidence(self, registry):
        """Test consensus with high confidence agents."""
        result = registry.execute(
            "multi_agent_consensus",
            {"agent_confidences": [0.95, 0.92, 0.88], "agreement_threshold": 0.6},
        )
        assert result.invariants_valid
        assert result.outputs["result"]["consensus_reached"] is True
        assert result.outputs["result"]["consensus_score"] > 0.9

    def test_multi_agent_consensus_low_confidence(self, registry):
        """Test consensus with low confidence agents."""
        result = registry.execute(
            "multi_agent_consensus",
            {"agent_confidences": [0.3, 0.4, 0.35], "agreement_threshold": 0.6},
        )
        assert result.invariants_valid
        assert result.outputs["result"]["consensus_reached"] is False

    def test_agent_communication_cost_basic(self, registry):
        """Test agent communication cost calculation."""
        result = registry.execute(
            "agent_communication_cost", {"message_size_bytes": 1024, "agent_count": 5, "rounds": 3}
        )
        assert result.invariants_valid
        assert "bandwidth_bytes" in result.outputs["result"]
        assert "overhead_factor" in result.outputs["result"]
        assert result.outputs["result"]["bandwidth_bytes"] > 0

    def test_agent_communication_cost_scaling(self, registry):
        """Test that communication cost scales with agent count."""
        result_small = registry.execute(
            "agent_communication_cost", {"message_size_bytes": 1000, "agent_count": 3, "rounds": 1}
        )
        result_large = registry.execute(
            "agent_communication_cost", {"message_size_bytes": 1000, "agent_count": 10, "rounds": 1}
        )
        assert (
            result_large.outputs["result"]["bandwidth_bytes"]
            > result_small.outputs["result"]["bandwidth_bytes"]
        )

    def test_agent_load_balance_basic(self, registry):
        """Test agent load balancing."""
        result = registry.execute(
            "agent_load_balance",
            {
                "task_complexity": 100,
                "agent_capacities": [50, 75, 100],
                "agent_costs": [1.0, 0.8, 0.6],
            },
        )
        assert result.invariants_valid
        assert "optimal_agent" in result.outputs["result"]
        assert "allocation_ratio" in result.outputs["result"]
        assert "balance_score" in result.outputs["result"]

    def test_agent_load_balance_prefers_capacity(self, registry):
        """Test that load balancing prefers high capacity, low cost agents."""
        result = registry.execute(
            "agent_load_balance",
            {"task_complexity": 100, "agent_capacities": [100, 50], "agent_costs": [0.5, 0.5]},
        )
        # Should prefer agent with higher capacity (index 0)
        assert result.outputs["result"]["optimal_agent"] == 0

    def test_agent_load_balance_capacity_mismatch(self, registry):
        """Test load balancing when task exceeds all capacities."""
        result = registry.execute(
            "agent_load_balance",
            {
                "task_complexity": 1000,
                "agent_capacities": [50, 75, 100],
                "agent_costs": [1.0, 0.8, 0.6],
            },
        )
        assert result.invariants_valid
        assert "error" in result.outputs["result"]
        assert "exceeds" in result.outputs["result"]["error"].lower()

    def test_agent_cost_optimization_basic(self, registry):
        """Test agent cost optimization."""
        result = registry.execute(
            "agent_cost_optimization",
            {
                "task_complexity": 1000,
                "frontier_cost_per_token": 0.01,
                "midtier_cost_per_token": 0.003,
                "small_cost_per_token": 0.001,
                "frontier_quality": 0.95,
                "midtier_quality": 0.85,
                "small_quality": 0.75,
            },
        )
        assert result.invariants_valid
        assert "recommended_mix" in result.outputs["result"]
        assert "cost_estimate" in result.outputs["result"]
        assert "meets_target" in result.outputs["result"]

    def test_agent_cost_optimization_prefers_cheaper(self, registry):
        """Test that optimization prefers cheaper models when quality allows."""
        result = registry.execute(
            "agent_cost_optimization",
            {
                "task_complexity": 100,
                "frontier_cost_per_token": 0.01,
                "midtier_cost_per_token": 0.003,
                "small_cost_per_token": 0.001,
                "frontier_quality": 0.95,
                "midtier_quality": 0.85,
                "small_quality": 0.75,
            },
        )
        mix = result.outputs["result"]["recommended_mix"]
        # For simple tasks, should prefer cheaper models
        assert mix["small_pct"] >= mix["frontier_pct"]

    def test_bounded_autonomy_score_basic(self, registry):
        """Test bounded autonomy scoring."""
        result = registry.execute(
            "bounded_autonomy_score",
            {"task_risk": 0.7, "agent_confidence": 0.6, "governance_level": "strict"},
        )
        assert result.invariants_valid
        assert "escalation_score" in result.outputs["result"]
        assert "requires_oversight" in result.outputs["result"]
        assert "governance_multiplier" in result.outputs["result"]

    def test_bounded_autonomy_high_risk(self, registry):
        """Test that high risk tasks require oversight."""
        result = registry.execute(
            "bounded_autonomy_score",
            {"task_risk": 0.9, "agent_confidence": 0.95, "governance_level": "strict"},
        )
        assert result.outputs["result"]["requires_oversight"] is True
        assert result.outputs["result"]["escalation_score"] > 0.5

    def test_bounded_autonomy_low_risk(self, registry):
        """Test that low risk, high confidence tasks don't require oversight."""
        result = registry.execute(
            "bounded_autonomy_score",
            {"task_risk": 0.2, "agent_confidence": 0.9, "governance_level": "standard"},
        )
        assert result.outputs["result"]["requires_oversight"] is False
        assert result.outputs["result"]["escalation_score"] < 0.5

    def test_bounded_autonomy_governance_levels(self, registry):
        """Test different governance levels affect escalation."""
        for level in ["minimal", "standard", "strict", "airgap"]:
            result = registry.execute(
                "bounded_autonomy_score",
                {"task_risk": 0.5, "agent_confidence": 0.5, "governance_level": level},
            )
            assert result.invariants_valid
            assert "governance_multiplier" in result.outputs["result"]


class TestPhase15Metadata:
    """Test Phase 15 equation metadata."""

    @pytest.fixture
    def registry(self):
        return SuperBrainEquationRegistry()

    def test_phase15_equations_registered(self, registry):
        """Test that all Phase 15 equations are registered."""
        phase15_equations = [
            "multi_agent_consensus",
            "agent_communication_cost",
            "agent_load_balance",
            "agent_cost_optimization",
            "bounded_autonomy_score",
        ]
        for eq_name in phase15_equations:
            assert eq_name in registry.equations
            assert eq_name in registry.metadata

    def test_phase15_domains_correct(self, registry):
        """Test that Phase 15 equations have correct domains."""
        domain_map = {
            "multi_agent_consensus": Domain.MULTI_AGENT_ORCHESTRATION,
            "agent_communication_cost": Domain.AGENT_PROTOCOL,
            "agent_load_balance": Domain.MULTI_AGENT_ORCHESTRATION,
            "agent_cost_optimization": Domain.AGENT_ECONOMICS,
            "bounded_autonomy_score": Domain.AGENT_GOVERNANCE,
        }
        for eq_name, expected_domain in domain_map.items():
            assert registry.metadata[eq_name].domain == expected_domain

    def test_phase15_patterns_correct(self, registry):
        """Test that Phase 15 equations have correct patterns."""
        pattern_map = {
            "multi_agent_consensus": MathematicalPattern.CONSENSUS_MECHANISM,
            "agent_communication_cost": MathematicalPattern.COMMUNICATION_PROTOCOL,
            "agent_load_balance": MathematicalPattern.LOAD_BALANCING,
            "agent_cost_optimization": MathematicalPattern.COST_OPTIMIZATION,
            "bounded_autonomy_score": MathematicalPattern.AGENT_NEGOTIATION,
        }
        for eq_name, expected_pattern in pattern_map.items():
            assert registry.metadata[eq_name].pattern == expected_pattern

    def test_phase15_phase_number(self, registry):
        """Test that all Phase 15 equations have phase=15."""
        phase15_equations = [
            "multi_agent_consensus",
            "agent_communication_cost",
            "agent_load_balance",
            "agent_cost_optimization",
            "bounded_autonomy_score",
        ]
        for eq_name in phase15_equations:
            assert registry.metadata[eq_name].phase == 15


class TestPhase15InvariantValidation:
    """Test Phase 15 equation invariant validation."""

    @pytest.fixture
    def registry(self):
        return SuperBrainEquationRegistry()

    def test_consensus_negative_score_invalid(self, registry):
        """Test that negative consensus score would be invalid."""
        # This should pass with valid inputs
        result = registry.execute(
            "multi_agent_consensus", {"agent_confidences": [-0.5, -0.3], "agreement_threshold": 0.6}
        )
        # Negative confidences result in negative score, which triggers invariant
        assert not result.invariants_valid

    def test_communication_negative_bandwidth_invalid(self, registry):
        """Test that negative bandwidth would be invalid."""
        # Negative message size would result in negative bandwidth
        result = registry.execute(
            "agent_communication_cost", {"message_size_bytes": -100, "agent_count": 5, "rounds": 1}
        )
        assert not result.invariants_valid

    def test_bounded_autonomy_negative_escalation_invalid(self, registry):
        """Test that negative escalation score would be invalid."""
        result = registry.execute(
            "bounded_autonomy_score", {"task_risk": -0.5, "agent_confidence": 0.5}
        )
        assert not result.invariants_valid


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
