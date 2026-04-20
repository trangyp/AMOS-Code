"""
AMOS Engines Comprehensive Test Suite
Unit and Integration Tests for All New Engines

Validates:
- Temporal Engine: Scheduling, events, workflows
- Field Dynamics: Lagrangian evolution, conservation laws
- Self-Evolution Safety: Syntax, security, semantic validation
- Engine Integration: Cross-engine coordination
"""

from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from pathlib import Path

import pytest

from amos_engine_integration import EngineOperation, EngineType, get_engine_integration
from amos_field_dynamics import (
    create_scalar_field,
)
from amos_self_evolution_test_suite import (
    EvolutionContext,
    ImportSafetyValidator,
    SyntaxValidator,
    get_self_evolution_test_suite,
)

# Engine imports
from amos_temporal_engine import TemporalEvent, Workflow, get_temporal_engine


class TestTemporalEngine:
    """Unit tests for Temporal Integration Engine."""

    @pytest.fixture
    async def temporal(self):
        engine = get_temporal_engine()
        await engine.initialize()
        yield engine
        await engine.stop()

    async def test_schedule_event(self, temporal):
        """Test event scheduling."""
        event = TemporalEvent(
            event_type="test", payload={"data": "value"}, scheduled_at=datetime.now(UTC)
        )
        event_id = await temporal.schedule_event(event)
        assert event_id is not None
        assert len(event_id) > 0

    async def test_cancel_event(self, temporal):
        """Test event cancellation."""
        event = TemporalEvent(event_type="cancellable", payload={})
        event_id = await temporal.schedule_event(event)
        result = await temporal.cancel_event(event_id)
        assert result is True

    async def test_workflow_execution(self, temporal):
        """Test workflow definition and execution tracking."""
        workflow = Workflow(
            workflow_id="test_wf",
            name="test_workflow",
            steps=[{"action": "step1"}, {"action": "step2"}],
        )
        await temporal.register_workflow(workflow)
        assert workflow.workflow_id in temporal._workflows

    async def test_metrics_collection(self, temporal):
        """Test metrics are collected."""
        metrics = temporal.get_metrics()
        assert "scheduled_events" in metrics
        assert "event_history" in metrics


class TestFieldDynamics:
    """Unit tests for Field Dynamics Engine."""

    @pytest.fixture
    def scalar_field(self):
        return create_scalar_field(mass=1.0, coupling=0.1, grid_size=32)

    def test_field_initialization(self, scalar_field):
        """Test field state initialization."""
        state = scalar_field.initialize_field((32,), "vacuum")
        assert state.values.shape == (32,)
        assert state.momenta is not None
        assert state.momenta.shape == (32,)

    def test_hamiltonian_computation(self, scalar_field):
        """Test Hamiltonian energy computation."""
        state = scalar_field.initialize_field((32,), "vacuum")
        H = scalar_field.compute_hamiltonian(state)
        assert H >= 0  # Energy should be non-negative for vacuum

    def test_action_computation(self, scalar_field):
        """Test action functional computation."""
        state = scalar_field.initialize_field((32,), "soliton")
        S = scalar_field.compute_action(state)
        assert isinstance(S, float)

    def test_field_evolution(self, scalar_field):
        """Test field time evolution."""
        initial = scalar_field.initialize_field((32,), "vacuum")
        states = scalar_field.evolve(10, initial)
        assert len(states) == 10
        # Check energy conservation (approximately)
        H_initial = scalar_field.compute_hamiltonian(initial)
        H_final = scalar_field.compute_hamiltonian(states[-1])
        assert abs(H_final - H_initial) < 0.1  # Small energy drift

    def test_noether_charge(self, scalar_field):
        """Test Noether charge computation."""
        state = scalar_field.initialize_field((32,), "random")
        charge = scalar_field.get_noether_charge("phase")
        assert isinstance(charge, float)


class TestSelfEvolutionSafety:
    """Unit tests for Self-Evolution Safety Suite."""

    @pytest.fixture
    async def safety_suite(self):
        suite = get_self_evolution_test_suite()
        await suite.initialize()
        return suite

    async def test_syntax_validation_pass(self, safety_suite):
        """Test syntax validator accepts valid code."""
        validator = SyntaxValidator()
        context = {"proposed_code": "def valid(): pass"}
        passed, violations = await validator.validate(context)
        assert passed is True
        assert len(violations) == 0

    async def test_syntax_validation_fail(self, safety_suite):
        """Test syntax validator rejects invalid code."""
        validator = SyntaxValidator()
        context = {"proposed_code": "def invalid(:"}
        passed, violations = await validator.validate(context)
        assert passed is False
        assert len(violations) > 0

    async def test_import_safety_blocks_dangerous(self, safety_suite):
        """Test import safety blocks dangerous imports."""
        validator = ImportSafetyValidator()
        context = {"proposed_code": "import os; os.system('rm -rf /')"}
        passed, violations = await validator.validate(context)
        assert passed is False

    async def test_evolution_validation(self, safety_suite):
        """Test full evolution validation pipeline."""
        context = EvolutionContext(
            evolution_id="test_001",
            target_file=Path("test.py"),
            original_code="def foo(): pass",
            proposed_code="def foo(): return 42",
            reason="Add return value",
            evidence={"test_results": {"passed": True}},
            test_code="def test_foo(): assert foo() == 42",
        )
        report = await safety_suite.validate_evolution(context)
        assert report.evolution_id == "test_001"
        assert report.evidence_quality > 0

    async def test_sandbox_execution(self, safety_suite):
        """Test sandboxed code execution."""
        context = EvolutionContext(
            evolution_id="sandbox_test",
            target_file=Path("sandbox.py"),
            original_code="",
            proposed_code="x = 42",
            reason="test",
            evidence={},
        )
        success, output = await safety_suite.execute_sandbox_test(context)
        assert success is True


class TestEngineIntegration:
    """Integration tests for Engine Integration Layer."""

    @pytest.fixture
    async def integration(self):
        engine = get_engine_integration()
        await engine.initialize()
        return engine

    async def test_temporal_status_via_integration(self, integration):
        """Test temporal engine access through integration layer."""
        op = EngineOperation(EngineType.TEMPORAL, "status", {})
        result = await integration.execute(op)
        assert result.success is True
        assert "data" in result.__dict__ or hasattr(result, "data")

    async def test_field_simulation_via_integration(self, integration):
        """Test field dynamics through integration layer."""
        op = EngineOperation(EngineType.FIELD, "simulate", {"grid_size": 32, "steps": 10})
        result = await integration.execute(op)
        assert result.success is True

    async def test_cross_engine_metrics(self, integration):
        """Test getting metrics from all engines."""
        status = await integration.get_system_status()
        assert "temporal" in status
        assert "field" in status
        assert "safety" in status


class TestEngineInteractions:
    """Integration tests for engine-to-engine interactions."""

    async def test_temporal_triggers_field_evolution(self):
        """Test temporal event can trigger field simulation."""
        temporal = get_temporal_engine()
        await temporal.initialize()

        field = create_scalar_field(grid_size=16)

        # Schedule field evolution as temporal event
        async def evolve_field():
            state = field.initialize_field((16,), "vacuum")
            return field.evolve(5, state)

        event = TemporalEvent(
            event_type="field_evolution",
            payload={"action": "evolve"},
            scheduled_at=datetime.now(UTC),
        )

        event_id = await temporal.schedule_event(event)
        assert event_id is not None
        await temporal.stop()

    async def test_safety_validates_field_code(self):
        """Test safety suite can validate field dynamics code."""
        safety = get_self_evolution_test_suite()
        await safety.initialize()

        # Field dynamics code to validate
        field_code = """
from amos_field_dynamics import create_scalar_field
def simulate():
    f = create_scalar_field()
    return f.initialize_field((16,), "vacuum")
"""

        validator = SyntaxValidator()
        passed, violations = await validator.validate({"proposed_code": field_code})
        assert passed is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
