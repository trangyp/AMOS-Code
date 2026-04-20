"""Phase 18: Meta-Learning Control Layer Tests (2026)."""

from amos_meta_learning_controller import (
    ExplorationPolicy,
    ImprovementAttempt,
    ImprovementStrategy,
    MetaLearningController,
    MetaStrategy,
    create_meta_learning_controller,
)


class TestPhase18MetaLearning:
    """Test Phase 18: Meta-Learning Control Layer."""

    def setup_method(self):
        """Setup before each test."""
        self.controller = create_meta_learning_controller()

    def test_controller_creation(self):
        """Test meta-learning controller creation."""
        assert self.controller is not None
        assert len(self.controller.meta_strategies) == 3
        assert self.controller.exploration_policy == ExplorationPolicy.UCB

    def test_exploration_policies(self):
        """Test different exploration policies."""
        policies = [
            ExplorationPolicy.GREEDY,
            ExplorationPolicy.EPSILON_GREEDY,
            ExplorationPolicy.UCB,
            ExplorationPolicy.THOMPSON,
        ]

        for policy in policies:
            controller = MetaLearningController(exploration_policy=policy)
            assert controller.exploration_policy == policy

    def test_record_improvement_attempt(self):
        """Test recording improvement attempts."""
        initial_count = len(self.controller.improvement_history)

        attempt = self.controller.record_improvement_attempt(
            strategy=ImprovementStrategy.CONSERVATIVE,
            target_component="world_model",
            improvement_type="parameter_adjustment",
            success=True,
            validation_score=0.8,
            computation_cost=100.0,
            system_state_before={"step": 0},
            system_state_after={"step": 1},
            side_effects=[],
        )

        assert isinstance(attempt, ImprovementAttempt)
        assert len(self.controller.improvement_history) == initial_count + 1
        assert attempt.success is True

    def test_strategy_confidence_update(self):
        """Test that strategy confidence updates after attempts."""
        initial_confidence = self.controller.strategy_confidence.get(
            ImprovementStrategy.CONSERVATIVE.name, 0.5
        )

        self.controller.record_improvement_attempt(
            strategy=ImprovementStrategy.CONSERVATIVE,
            target_component="test",
            improvement_type="test",
            success=True,
            validation_score=0.9,
            computation_cost=100.0,
            system_state_before={},
            system_state_after={},
            side_effects=[],
        )

        new_confidence = self.controller.strategy_confidence.get(
            ImprovementStrategy.CONSERVATIVE.name, 0.5
        )

        # Confidence should increase after successful attempt
        assert new_confidence >= initial_confidence

    def test_select_improvement_strategy(self):
        """Test strategy selection."""
        strategy, meta_strategy, confidence = self.controller.select_improvement_strategy(
            current_context="production_environment",
            available_components=["world_model"],
            system_state={},
        )

        assert isinstance(strategy, ImprovementStrategy)
        assert isinstance(meta_strategy, MetaStrategy)
        assert 0 <= confidence <= 1

    def test_analyze_improvement_patterns(self):
        """Test improvement pattern analysis."""
        # Record some attempts first
        for i in range(5):
            self.controller.record_improvement_attempt(
                strategy=ImprovementStrategy.CONSERVATIVE,
                target_component="test",
                improvement_type="test",
                success=i % 2 == 0,
                validation_score=0.7,
                computation_cost=100.0,
                system_state_before={},
                system_state_after={},
                side_effects=[],
            )

        patterns = self.controller.analyze_improvement_patterns()

        assert "total_attempts" in patterns
        assert patterns["total_attempts"] == 5
        assert "overall_success_rate" in patterns
        assert 0 <= patterns["overall_success_rate"] <= 1

    def test_transfer_knowledge(self):
        """Test cross-domain knowledge transfer."""
        # Setup source domain
        self.controller.domain_knowledge["source_domain"] = type(
            "DomainKnowledge",
            (),
            {"successful_strategies": ["conservative_param_adjust"], "transferred_from": []},
        )()

        transferred = self.controller.transfer_knowledge("source_domain", "target_domain")

        # Check that strategies were transferred
        assert isinstance(transferred, list)
        # A new adapted strategy should be created
        assert (
            len(
                [
                    s
                    for s in self.controller.meta_strategies.values()
                    if "target_domain" in s.strategy_id
                ]
            )
            > 0
        )

    def test_get_acceleration_metrics(self):
        """Test acceleration metrics retrieval."""
        metrics = self.controller.get_acceleration_metrics()

        assert "improvement_velocity" in metrics
        assert "learning_efficiency" in metrics
        assert "acceleration_factor" in metrics
        assert "exploration_rate" in metrics
        assert "total_improvements" in metrics
        assert "active_strategies" in metrics

    def test_recommendations(self):
        """Test improvement recommendations."""
        # Add some history
        for i in range(3):
            self.controller.record_improvement_attempt(
                strategy=ImprovementStrategy.CONSERVATIVE,
                target_component="test",
                improvement_type="test",
                success=True,
                validation_score=0.8,
                computation_cost=100.0,
                system_state_before={},
                system_state_after={},
                side_effects=[],
            )

        recommendations = self.controller.recommend_next_improvements(n_recommendations=3)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        for rec in recommendations:
            assert "type" in rec
            assert "rationale" in rec

    def test_ucb_score(self):
        """Test UCB score calculation."""
        strategy = self.controller.meta_strategies["conservative_param_adjust"]

        score = self.controller._ucb_score(strategy)

        assert score > 0
        # Score should include exploration bonus
        assert score >= self.controller.strategy_confidence.get(strategy.strategy_id, 0.5)

    def test_thompson_sample(self):
        """Test Thompson sampling."""
        strategies = list(self.controller.meta_strategies.values())

        chosen = self.controller._thompson_sample(strategies)

        assert chosen in strategies

    def test_acceleration_metrics_update(self):
        """Test that acceleration metrics update over time."""
        initial_velocity = self.controller.improvement_velocity

        # Record multiple attempts
        for i in range(10):
            self.controller.record_improvement_attempt(
                strategy=ImprovementStrategy.CONSERVATIVE,
                target_component="test",
                improvement_type="test",
                success=True,
                validation_score=0.8,
                computation_cost=100.0,
                system_state_before={"step": i},
                system_state_after={"step": i + 1},
                side_effects=[],
            )

        # Velocity should be calculated after enough attempts
        assert self.controller.improvement_velocity > 0
        assert len(self.controller.improvement_history) == 10


def run_tests():
    """Run all Phase 18 tests."""
    test_class = TestPhase18MetaLearning()

    tests = [
        ("Controller Creation", test_class.test_controller_creation),
        ("Exploration Policies", test_class.test_exploration_policies),
        ("Record Improvement Attempt", test_class.test_record_improvement_attempt),
        ("Strategy Confidence Update", test_class.test_strategy_confidence_update),
        ("Select Improvement Strategy", test_class.test_select_improvement_strategy),
        ("Analyze Improvement Patterns", test_class.test_analyze_improvement_patterns),
        ("Transfer Knowledge", test_class.test_transfer_knowledge),
        ("Get Acceleration Metrics", test_class.test_get_acceleration_metrics),
        ("Recommendations", test_class.test_recommendations),
        ("UCB Score", test_class.test_ucb_score),
        ("Thompson Sample", test_class.test_thompson_sample),
        ("Acceleration Metrics Update", test_class.test_acceleration_metrics_update),
    ]

    passed = 0
    failed = 0

    print("=" * 70)
    print("Phase 18: Meta-Learning Control Layer - Test Suite")
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
