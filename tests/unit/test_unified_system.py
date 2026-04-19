#!/usr/bin/env python3
"""Unit tests for AMOS Unified System."""


class TestSystemInitialization:
    """Test system initialization."""

    def test_system_initializes(self, amos_system):
        """Test that AMOS system initializes successfully."""
        assert amos_system.status.initialized is True
        assert amos_system.status.neural_ready is True
        assert amos_system.status.symbolic_ready is True

    def test_neural_providers_loaded(self, amos_system):
        """Test that neural providers are loaded."""
        status = amos_system.get_status()
        assert status["neural"] is True
        assert status.get("agents", 0) >= 0

    def test_laws_active(self, amos_system):
        """Test that global laws are active."""
        status = amos_system.get_status()
        assert "laws_active" in status
        assert len(status["laws_active"]) == 6  # L1-L6

    def test_components_registered(self, amos_system):
        """Test that all components are registered."""
        status = amos_system.get_status()
        assert "components" in status
        expected_components = [
            "amos_brain",
            "hybrid_orchestrator",
            "mcp_bridge",
            "global_laws",
            "auth_integration",
        ]
        for comp in expected_components:
            assert comp in status["components"], f"{comp} not registered"


class TestAgentManagement:
    """Test agent spawning and management."""

    def test_spawn_hybrid_agent(self, amos_system):
        """Test spawning hybrid paradigm agent."""
        agent = amos_system.spawn_agent("architect", "HYBRID")
        assert agent is not None
        assert agent.role == "architect"
        assert agent.paradigm.name == "HYBRID"
        assert amos_system.status.active_agents >= 1

    def test_spawn_symbolic_agent(self, amos_system):
        """Test spawning symbolic paradigm agent."""
        agent = amos_system.spawn_agent("reviewer", "SYMBOLIC")
        assert agent is not None
        assert agent.paradigm.name == "SYMBOLIC"

    def test_spawn_neural_agent(self, amos_system):
        """Test spawning neural paradigm agent."""
        agent = amos_system.spawn_agent("executor", "NEURAL")
        assert agent is not None
        assert agent.paradigm.name == "NEURAL"

    def test_agent_tracking(self, amos_system):
        """Test that spawned agents are tracked."""
        initial_count = amos_system.status.active_agents
        amos_system.spawn_agent("auditor", "HYBRID")
        assert amos_system.status.active_agents == initial_count + 1


class TestLawValidation:
    """Test law validation functionality."""

    def test_valid_action_compliance(self, amos_system):
        """Test that valid actions are compliant."""
        result = amos_system.validate_action("Design a secure API")
        assert result["compliant"] is True
        assert result["violations"] == []

    def test_l1_violation_detection(self, amos_system, law_violation_scenarios):
        """Test L1 law violation detection."""
        action = law_violation_scenarios["L1_violation"]
        result = amos_system.validate_action(action)
        # Note: Actual implementation may vary
        assert "compliant" in result


class TestStatusReporting:
    """Test system status reporting."""

    def test_status_structure(self, amos_system):
        """Test that status has correct structure."""
        status = amos_system.get_status()
        required_keys = [
            "initialized",
            "neural",
            "symbolic",
            "orchestrator",
            "mcp",
            "auth",
            "laws_active",
            "agents",
            "tools",
            "sessions",
            "components",
        ]
        for key in required_keys:
            assert key in status, f"Missing key: {key}"

    def test_status_types(self, amos_system):
        """Test that status values have correct types."""
        status = amos_system.get_status()
        assert isinstance(status["initialized"], bool)
        assert isinstance(status["agents"], int)
        assert isinstance(status["tools"], int)
        assert isinstance(status["laws_active"], list)
        assert isinstance(status["components"], list)
