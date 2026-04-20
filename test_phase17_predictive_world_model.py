"""Phase 17: Predictive World Model with Recursive Self-Improvement Tests (2026)."""

from amos_predictive_world_model import (
    HorizonStrategy,
    PredictiveWorldModel,
    Reflection,
    SimulatedState,
    SimulationError,
    SimulationResult,
    create_predictive_world_model,
)
from amos_unified_cognitive_substrate import get_cognitive_substrate


class TestPhase17PredictiveWorldModel:
    """Test Phase 17: Predictive World Model."""

    def setup_method(self):
        """Setup before each test."""
        self.model = create_predictive_world_model()
        self.substrate = get_cognitive_substrate()
        self.model.connect_to_substrate(self.substrate)

    def test_model_creation(self):
        """Test world model creation."""
        assert self.model is not None
        assert self.model.max_horizon == 10
        assert self.model.horizon_strategy == HorizonStrategy.CONFIDENCE_DECAY

    def test_horizon_strategies(self):
        """Test different horizon strategies."""
        strategies = [
            HorizonStrategy.FIXED,
            HorizonStrategy.CONFIDENCE_DECAY,
            HorizonStrategy.UNCERTAINTY_DRIVEN,
            HorizonStrategy.RECURSIVE,
        ]

        for strategy in strategies:
            model = PredictiveWorldModel(horizon_strategy=strategy)
            assert model.horizon_strategy == strategy

    def test_simulate_future(self):
        """Test future simulation."""
        initial_state = self.substrate.get_state()
        actions = [{"classical": {"set": {"x": 1}}}, {"classical": {"set": {"y": 2}}}]

        result = self.model.simulate_future(initial_state.__dict__, actions, target_horizon=2)

        assert isinstance(result, SimulationResult)
        assert result.horizon > 0
        assert result.horizon <= 2
        assert result.final_confidence >= 0
        assert result.computational_cost > 0

    def test_simulation_trajectory(self):
        """Test simulation trajectory generation."""
        initial_state = self.substrate.get_state()
        actions = [{"classical": {"set": {"test": 1}}}]

        result = self.model.simulate_future(initial_state.__dict__, actions, target_horizon=1)

        assert len(result.trajectory) > 0

        for state in result.trajectory:
            assert isinstance(state, SimulatedState)
            assert state.confidence >= 0
            assert state.confidence <= 1
            assert state.uncertainty >= 0

    def test_evaluate_simulation(self):
        """Test simulation evaluation."""
        initial_state = self.substrate.get_state()
        actions = [{"classical": {"set": {"x": 1}}}]

        simulation = self.model.simulate_future(initial_state.__dict__, actions, target_horizon=1)

        # Mock actual future (slightly different from prediction)
        actual_future = [{"amosl_state": {"x": 1}, "step_count": 1}]

        errors = self.model.evaluate_simulation(simulation, actual_future)

        assert isinstance(errors, list)
        for error in errors:
            assert isinstance(error, SimulationError)
            assert "state_diff" in error.error_metrics

    def test_reflect_on_simulation(self):
        """Test meta-cognitive reflection."""
        initial_state = self.substrate.get_state()
        actions = [{"classical": {"set": {"x": 1}}}]

        simulation = self.model.simulate_future(initial_state.__dict__, actions, target_horizon=1)

        actual_future = [{"amosl_state": {"x": 1}, "step_count": 1}]
        errors = self.model.evaluate_simulation(simulation, actual_future)

        reflection = self.model.reflect_on_simulation(simulation, errors)

        assert isinstance(reflection, Reflection)
        assert reflection.reflection_id is not None
        assert reflection.timestamp > 0
        assert reflection.root_cause is not None

    def test_improve_world_model(self):
        """Test world model self-improvement."""
        # Create a reflection that should trigger improvements
        reflection = Reflection(
            reflection_id="test_refl_001",
            timestamp=0.0,
            simulation_id="test_sim_001",
            error_type="transition_error",
            root_cause="high_complexity",
            confidence_assessment="overconfident",
            what_went_wrong="State transition mismatch",
            what_was_missing=["state_variables"],
            what_worked_well=["maintained_horizon"],
            recommended_adjustments=["adjust_transition_weights"],
            confidence_delta=-0.2,
        )

        initial_weights = self.model.transition_weights.copy()

        improvements = self.model.improve_world_model(reflection)

        # Check that improvements were generated
        assert isinstance(improvements, list)

        # Check that weights were adjusted
        if improvements:
            assert self.model.transition_weights != initial_weights

    def test_full_recursive_loop(self):
        """Test full recursive self-improvement loop."""
        initial_state = self.substrate.get_state()
        actions = [{"classical": {"set": {"x": 1}}}]
        actual_future = [{"amosl_state": {"x": 1}, "step_count": 1}]

        result = self.model.full_recursive_loop(initial_state.__dict__, actions, actual_future)

        assert "simulation" in result
        assert "errors" in result
        assert "reflection" in result
        assert "improvements" in result
        assert "learning_summary" in result

        summary = result["learning_summary"]
        assert summary["total_simulations"] > 0
        assert summary["total_reflections"] > 0

    def test_learning_statistics(self):
        """Test learning statistics retrieval."""
        stats = self.model.get_learning_statistics()

        assert "status" in stats

        # Run one loop to generate data
        initial_state = self.substrate.get_state()
        actions = [{"classical": {"set": {"x": 1}}}]
        actual_future = [{"amosl_state": {"x": 1}, "step_count": 1}]

        self.model.full_recursive_loop(initial_state.__dict__, actions, actual_future)

        stats = self.model.get_learning_statistics()

        assert "total_simulations" in stats
        assert "total_reflections" in stats
        assert "total_improvements" in stats
        assert "current_parameters" in stats

    def test_confidence_decay(self):
        """Test that confidence decays over simulation steps."""
        confidences = []

        for step in range(5):
            conf = self.model._calculate_confidence(step, 5)
            confidences.append(conf)

        # Confidence should generally decrease (or stay same)
        for i in range(1, len(confidences)):
            assert confidences[i] <= confidences[i - 1] + 0.01  # Small tolerance

    def test_uncertainty_growth(self):
        """Test that uncertainty grows over simulation steps."""
        uncertainties = []

        for step in range(5):
            unc = self.model._calculate_uncertainty(step, 5)
            uncertainties.append(unc)

        # Uncertainty should generally increase
        for i in range(1, len(uncertainties)):
            assert uncertainties[i] >= uncertainties[i - 1] - 0.01  # Small tolerance


def run_tests():
    """Run all Phase 17 tests."""
    test_class = TestPhase17PredictiveWorldModel()

    tests = [
        ("Model Creation", test_class.test_model_creation),
        ("Horizon Strategies", test_class.test_horizon_strategies),
        ("Simulate Future", test_class.test_simulate_future),
        ("Simulation Trajectory", test_class.test_simulation_trajectory),
        ("Evaluate Simulation", test_class.test_evaluate_simulation),
        ("Reflect on Simulation", test_class.test_reflect_on_simulation),
        ("Improve World Model", test_class.test_improve_world_model),
        ("Full Recursive Loop", test_class.test_full_recursive_loop),
        ("Learning Statistics", test_class.test_learning_statistics),
        ("Confidence Decay", test_class.test_confidence_decay),
        ("Uncertainty Growth", test_class.test_uncertainty_growth),
    ]

    passed = 0
    failed = 0

    print("=" * 70)
    print("Phase 17: Predictive World Model - Test Suite")
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
