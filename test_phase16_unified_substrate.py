"""Phase 16: Unified Cognitive Substrate Integration Tests (2026)."""

from amos_unified_cognitive_substrate import (
    ReasoningMode,
    get_cognitive_substrate,
    reset_cognitive_substrate,
)


class TestPhase16UnifiedSubstrate:
    """Test Phase 16: Unified Cognitive Substrate."""

    def setup_method(self):
        """Reset substrate before each test."""
        reset_cognitive_substrate()
        self.substrate = get_cognitive_substrate()

    def test_mathematical_reasoning(self):
        """Test mathematical reasoning via equation bridge."""
        result = self.substrate.reason_mathematical(
            "multi_agent_consensus",
            {"agent_confidences": [0.8, 0.9, 0.7], "agreement_threshold": 0.6},
        )

        assert result.mode == ReasoningMode.MATHEMATICAL
        assert result.confidence > 0
        assert result.execution_time_ms > 0
        assert "consensus_score" in result.result["result"]

    def test_causal_reasoning(self):
        """Test causal reasoning for root cause analysis."""
        result = self.substrate.reason_causal(
            "bug_rate", {"complexity": 15.5, "test_coverage": 0.45, "tech_debt": "high"}
        )

        assert result.mode == ReasoningMode.CAUSAL
        assert result.confidence > 0
        assert len(result.result["root_causes"]) > 0

    def test_hybrid_reasoning(self):
        """Test hybrid reasoning combining multiple modalities."""
        result = self.substrate.reason_hybrid(
            "optimize system performance", {"complexity": 100, "budget": 1000}
        )

        assert result.mode == ReasoningMode.HYBRID
        assert result.confidence >= 0

    def test_state_persistence(self):
        """Test that substrate state persists across operations."""
        # Execute mathematical reasoning
        self.substrate.reason_mathematical(
            "agent_cost_optimization",
            {
                "task_complexity": 1000,
                "frontier_cost_per_token": 0.01,
                "midtier_cost_per_token": 0.003,
                "small_cost_per_token": 0.001,
            },
        )

        # Execute causal reasoning
        self.substrate.reason_causal("performance", {"complexity": 10})

        # Check state
        state = self.substrate.get_state()
        assert len(state.equation_cache) >= 1
        assert len(state.causal_graph) >= 1

    def test_equation_integration(self):
        """Test integration with Phase 15 multi-agent equations."""
        # Test consensus
        result = self.substrate.reason_mathematical(
            "multi_agent_consensus",
            {"agent_confidences": [0.9, 0.85, 0.8], "agreement_threshold": 0.6},
        )

        assert result.invariant_violations == []
        assert result.used_equations == ["multi_agent_consensus"]

        # Test load balancing
        result = self.substrate.reason_mathematical(
            "agent_load_balance",
            {
                "task_complexity": 100,
                "agent_capacities": [50, 75, 100],
                "agent_costs": [1.0, 0.8, 0.6],
            },
        )

        assert "optimal_agent" in result.result["result"]

    def test_phase15_bounded_autonomy(self):
        """Test Phase 15 bounded autonomy equation integration."""
        result = self.substrate.reason_mathematical(
            "bounded_autonomy_score",
            {"task_risk": 0.7, "agent_confidence": 0.6, "governance_level": "strict"},
        )

        assert "escalation_score" in result.result["result"]
        assert "requires_oversight" in result.result["result"]

    def test_explain_state(self):
        """Test state explanation generation."""
        # Populate some state
        self.substrate.reason_mathematical(
            "agent_communication_cost", {"message_size_bytes": 1024, "agent_count": 5, "rounds": 3}
        )

        explanation = self.substrate.explain_state()
        assert "Substrate State" in explanation
        assert "Equation cache" in explanation

    def test_singleton_pattern(self):
        """Test that substrate is a singleton."""
        substrate1 = get_cognitive_substrate()
        substrate2 = get_cognitive_substrate()

        assert substrate1 is substrate2

    def test_step_execution(self):
        """Test substrate step execution."""
        initial_step = self.substrate.get_state().step_count

        self.substrate.step({"classical": {"set": {"x": 1}}})

        new_step = self.substrate.get_state().step_count
        assert new_step == initial_step + 1


def run_tests():
    """Run all Phase 16 tests."""
    test_class = TestPhase16UnifiedSubstrate()

    tests = [
        ("Mathematical Reasoning", test_class.test_mathematical_reasoning),
        ("Causal Reasoning", test_class.test_causal_reasoning),
        ("Hybrid Reasoning", test_class.test_hybrid_reasoning),
        ("State Persistence", test_class.test_state_persistence),
        ("Equation Integration", test_class.test_equation_integration),
        ("Bounded Autonomy", test_class.test_phase15_bounded_autonomy),
        ("State Explanation", test_class.test_explain_state),
        ("Singleton Pattern", test_class.test_singleton_pattern),
        ("Step Execution", test_class.test_step_execution),
    ]

    passed = 0
    failed = 0

    print("=" * 70)
    print("Phase 16: Unified Cognitive Substrate - Test Suite")
    print("=" * 70)

    for name, test in tests:
        try:
            test_class.setup_method()
            test()
            print(f"  PASS: {name}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {name} - {e}")
            failed += 1

    print("=" * 70)
    print(f"Results: {passed}/{passed + failed} tests passed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
