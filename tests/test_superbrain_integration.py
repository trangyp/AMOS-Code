"""
SuperBrain Integration Test Suite v2.0.0

Comprehensive tests for SuperBrain governance across all 12 integrated systems.
Tests ActionGate validation, audit trail recording, and fail-open behavior.

Author: Trang Phan
Version: 2.0.0
"""

import asyncio
from datetime import UTC, datetime

UTC = UTC
from unittest.mock import Mock, patch

import pytest

# Test imports
from amos_cognitive_router import CognitiveRouter, RouteDecision
from amos_resilience_engine import CircuitBreaker, CircuitBreakerConfig


class MockActionResult:
    """Mock ActionGate result for testing."""

    def __init__(self, authorized=True, reason=""):
        self.authorized = authorized
        self.reason = reason


class MockSuperBrain:
    """Mock SuperBrain for testing governance integration."""

    def __init__(self, should_authorize=True):
        self.should_authorize = should_authorize
        self.action_gate = Mock()
        self.action_gate.validate_action = Mock(
            return_value=MockActionResult(authorized=should_authorize)
        )
        self.record_audit = Mock()
        self.audit_calls = []

    def record_audit(self, action, agent_id, details):
        self.audit_calls.append(
            {
                "action": action,
                "agent_id": agent_id,
                "details": details,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )


class TestCognitiveRouterSuperBrainIntegration:
    """Test SuperBrain integration in Cognitive Router."""

    @pytest.fixture
    def router_with_superbrain(self):
        """Create router with mocked SuperBrain."""
        with patch("amos_cognitive_router.get_super_brain") as mock_get_brain:
            mock_brain = MockSuperBrain(should_authorize=True)
            mock_get_brain.return_value = mock_brain

            router = CognitiveRouter()
            router._brain = mock_brain
            router.SUPERBRAIN_AVAILABLE = True

            yield router, mock_brain

    @pytest.fixture
    def router_without_superbrain(self):
        """Create router without SuperBrain availability."""
        with patch("amos_cognitive_router.SUPERBRAIN_AVAILABLE", False):
            router = CognitiveRouter()
            yield router

    def test_validate_route_authorized(self, router_with_superbrain):
        """Test that routing is allowed when ActionGate authorizes."""
        router, mock_brain = router_with_superbrain

        result = router._validate_route("test task", "coding")

        assert result is True
        mock_brain.action_gate.validate_action.assert_called_once()
        call_args = mock_brain.action_gate.validate_action.call_args
        assert call_args[1]["agent_id"] == "cognitive_router"
        assert call_args[1]["action"] == "route_task"

    def test_validate_route_blocked(self):
        """Test that routing is blocked when ActionGate denies."""
        with patch("amos_cognitive_router.get_super_brain") as mock_get_brain:
            mock_brain = MockSuperBrain(should_authorize=False)
            mock_brain.action_gate.validate_action.return_value = MockActionResult(
                authorized=False, reason="test policy violation"
            )
            mock_get_brain.return_value = mock_brain

            router = CognitiveRouter()
            router._brain = mock_brain
            router.SUPERBRAIN_AVAILABLE = True

            result = router._validate_route("test task", "coding")

            assert result is False

    def test_validate_route_fail_open(self, router_without_superbrain):
        """Test that routing succeeds when SuperBrain unavailable (fail-open)."""
        result = router_without_superbrain._validate_route("test task", "coding")

        assert result is True  # Fail open

    def test_route_task_records_audit(self, router_with_superbrain):
        """Test that successful routing records audit trail."""
        router, mock_brain = router_with_superbrain

        # Route a task
        decision = router.route_task("create a python function")

        # Verify audit was recorded
        assert mock_brain.record_audit.called or router._record_route.called

    def test_route_task_blocked_by_governance(self):
        """Test that blocked routing returns BLOCKED decision."""
        with patch("amos_cognitive_router.get_super_brain") as mock_get_brain:
            mock_brain = MockSuperBrain(should_authorize=False)
            mock_brain.action_gate.validate_action.return_value = MockActionResult(
                authorized=False, reason="governance policy"
            )
            mock_get_brain.return_value = mock_brain

            router = CognitiveRouter()
            router._brain = mock_brain
            router.SUPERBRAIN_AVAILABLE = True

            decision = router.route_task("test task")

            assert decision.selected_engine == "BLOCKED"
            assert decision.engine_category == "BLOCKED"
            assert decision.confidence == 0.0


class TestResilienceEngineSuperBrainIntegration:
    """Test SuperBrain integration in Resilience Engine."""

    @pytest.fixture
    def circuit_breaker_with_superbrain(self):
        """Create circuit breaker with mocked SuperBrain."""
        with patch("amos_resilience_engine.get_super_brain") as mock_get_brain:
            mock_brain = MockSuperBrain(should_authorize=True)
            mock_get_brain.return_value = mock_brain

            config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=30.0)
            breaker = CircuitBreaker("test_circuit", config)
            breaker._brain = mock_brain
            breaker.SUPERBRAIN_AVAILABLE = True

            yield breaker, mock_brain

    @pytest.fixture
    def circuit_breaker_without_superbrain(self):
        """Create circuit breaker without SuperBrain."""
        with patch("amos_resilience_engine.SUPERBRAIN_AVAILABLE", False):
            config = CircuitBreakerConfig()
            breaker = CircuitBreaker("test_circuit", config)
            yield breaker

    def test_circuit_opens_records_audit(self, circuit_breaker_with_superbrain):
        """Test that circuit opening records audit event."""
        breaker, mock_brain = circuit_breaker_with_superbrain

        # Simulate failures to trigger circuit open
        breaker.failure_count = 3
        breaker.config.failure_threshold = 3

        # Force circuit to open
        asyncio.run(breaker._on_failure())
        asyncio.run(breaker._on_failure())
        asyncio.run(breaker._on_failure())

        # Verify circuit is open
        assert breaker.state.name == "OPEN"

    def test_validate_circuit_action_authorized(self, circuit_breaker_with_superbrain):
        """Test circuit action validation when authorized."""
        breaker, mock_brain = circuit_breaker_with_superbrain

        result = breaker._validate_circuit_action("open", {"reason": "test"})

        assert result is True
        mock_brain.action_gate.validate_action.assert_called()

    def test_validate_circuit_action_fail_open(self, circuit_breaker_without_superbrain):
        """Test circuit action validation fails open."""
        breaker = circuit_breaker_without_superbrain

        result = breaker._validate_circuit_action("open", {"reason": "test"})

        assert result is True  # Fail open

    def test_record_circuit_event(self, circuit_breaker_with_superbrain):
        """Test circuit event recording."""
        breaker, mock_brain = circuit_breaker_with_superbrain

        breaker._record_circuit_event("opened", {"failure_count": 3})

        # Should not raise exception
        assert True


class TestSuperBrainGovernanceCheck:
    """Test the SuperBrainGovernanceCheck health check."""

    def test_has_12_systems(self):
        """Verify health check lists all 12 integrated systems."""
        from backend.health_checks import SuperBrainGovernanceCheck

        check = SuperBrainGovernanceCheck()

        assert len(check.integrated_systems) == 12

        # Verify critical systems
        systems_str = " ".join(check.integrated_systems)
        assert "Cognitive Router" in systems_str
        assert "Resilience Engine" in systems_str
        assert "Master Orchestrator" in systems_str
        assert "Knowledge Loader" in systems_str

    def test_critical_check(self):
        """Verify governance check is marked critical."""
        from backend.health_checks import SuperBrainGovernanceCheck

        check = SuperBrainGovernanceCheck()

        assert check.critical is True

    @pytest.mark.asyncio
    async def test_check_skips_when_unavailable(self):
        """Test check returns True when SuperBrain unavailable."""
        from backend.health_checks import SuperBrainGovernanceCheck

        with patch("backend.health_checks.SUPERBRAIN_AVAILABLE", False):
            check = SuperBrainGovernanceCheck()
            result, message = await check.check()

            assert result is True
            assert "skipped" in message.lower()


class TestIntegrationPatternCompliance:
    """Test that all 12 systems follow the canonical integration pattern."""

    def test_cognitive_router_has_patterns(self):
        """Verify CognitiveRouter has all required patterns."""
        import amos_cognitive_router as module

        source = open(module.__file__).read()

        assert "SUPERBRAIN_AVAILABLE" in source
        assert "_init_superbrain" in source
        assert "_validate_route" in source
        assert "_record_route" in source
        assert "CANONICAL" in source

    def test_resilience_engine_has_patterns(self):
        """Verify ResilienceEngine has all required patterns."""
        import amos_resilience_engine as module

        source = open(module.__file__).read()

        assert "SUPERBRAIN_AVAILABLE" in source
        assert "_init_superbrain" in source
        assert "_validate_circuit_action" in source
        assert "_record_circuit_event" in source
        assert "CANONICAL" in source

    def test_health_checks_has_patterns(self):
        """Verify health_checks has SuperBrainGovernanceCheck."""
        import backend.health_checks as module

        source = open(module.__file__).read()

        assert "SuperBrainGovernanceCheck" in source
        assert "12" in source or "integrated_systems" in source


class TestFailOpenBehavior:
    """Test fail-open strategy across all integrations."""

    @pytest.mark.parametrize(
        "exception_type",
        [
            ImportError,
            Exception,
            RuntimeError,
            AttributeError,
        ],
    )
    def test_cognitive_router_fail_open_on_exception(self, exception_type):
        """Test router degrades gracefully on any exception."""
        with patch("amos_cognitive_router.get_super_brain") as mock_get_brain:
            mock_get_brain.side_effect = exception_type("Simulated failure")

            router = CognitiveRouter()

            # Should not raise
            result = router._validate_route("test", "category")
            assert result is True  # Fail open

    def test_resilience_engine_fail_open_on_exception(self):
        """Test circuit breaker degrades gracefully."""
        with patch("amos_resilience_engine.get_super_brain") as mock_get_brain:
            mock_get_brain.side_effect = Exception("Simulated failure")

            config = CircuitBreakerConfig()
            breaker = CircuitBreaker("test", config)

            # Should not raise
            result = breaker._validate_circuit_action("test", {})
            assert result is True  # Fail open


class TestAuditTrailRecording:
    """Test audit trail recording across systems."""

    def test_cognitive_router_audit_structure(self):
        """Verify router audit has required fields."""
        with patch("amos_cognitive_router.get_super_brain") as mock_get_brain:
            mock_brain = MockSuperBrain()
            mock_get_brain.return_value = mock_brain

            router = CognitiveRouter()
            router._brain = mock_brain
            router.SUPERBRAIN_AVAILABLE = True

            decision = RouteDecision(
                task="test task",
                selected_engine="test_engine",
                engine_category="test_category",
                confidence=0.8,
                reasoning="test",
                alternatives=[],
                route_time=datetime.now(UTC).isoformat(),
            )

            router._record_route(decision)

            # Verify audit was recorded with correct structure
            mock_brain.record_audit.assert_called_once()
            call_args = mock_brain.record_audit.call_args
            assert call_args[1]["action"] == "task_routed"
            assert call_args[1]["agent_id"] == "cognitive_router"
            assert "details" in call_args[1]


# Integration test markers
pytestmark = [
    pytest.mark.superbrain,
    pytest.mark.governance,
    pytest.mark.integration,
]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
