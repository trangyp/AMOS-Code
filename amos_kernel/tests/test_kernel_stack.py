"""
Kernel Stack Tests

Test the kernel-first architecture:
    ULK → DeterministicCore → UniversalState → SelfObserver → RepairExecutor
"""

import pytest

from amos_kernel import (
    DeterministicCore,
    KernelContract,
    RepairExecutor,
    SelfObserver,
    UniversalLawKernel,
    UniversalStateModel,
    initialize_kernel,
)
from amos_kernel.contracts import CORE_INVARIANTS


class TestUniversalLawKernel:
    """Test L0 - Universal Law Kernel"""

    def test_singleton(self):
        """UL K is singleton."""
        ulk1 = UniversalLawKernel()
        ulk2 = UniversalLawKernel()
        assert ulk1 is ulk2

    def test_core_invariants_loaded(self):
        """Core invariants are loaded."""
        ulk = UniversalLawKernel()
        assert len(ulk._invariants) == len(CORE_INVARIANTS)

    def test_validate_empty_state(self):
        """Validation handles empty state."""
        ulk = UniversalLawKernel()
        from amos_kernel.L2_universal_state_model import StateTensor

        state = StateTensor()
        action = {"type": "test"}

        result = ulk.validate_invariants(state, action)
        assert result.validated_by == "ULK"

    def test_contradiction_score_no_contradictions(self):
        """No contradictions = score 0."""
        ulk = UniversalLawKernel()
        from amos_kernel.L2_universal_state_model import StateTensor

        state = StateTensor()
        score = ulk.contradiction_score(state)
        assert score == 0.0

    def test_quadrant_integrity_computed(self):
        """Quadrant integrity is computed."""
        ulk = UniversalLawKernel()
        from amos_kernel.L2_universal_state_model import StateTensor

        state = StateTensor()
        integrity = ulk.quadrant_integrity(state)

        assert 0.0 <= integrity.overall_score <= 1.0
        assert hasattr(integrity, "code")
        assert hasattr(integrity, "build")
        assert hasattr(integrity, "operational")
        assert hasattr(integrity, "environment")


class TestDeterministicCore:
    """Test L1 - Deterministic Core"""

    def test_singleton(self):
        """DeterministicCore is singleton."""
        core1 = DeterministicCore()
        core2 = DeterministicCore()
        assert core1 is core2

    def test_transition_creates_record(self):
        """Transition creates history record."""
        core = DeterministicCore()
        initial_count = len(core.get_transition_history())

        state = {"canonical_hash": "abc123"}
        inputs = {"test": "input"}
        constraints = {}

        result = core.transition(state, inputs, constraints)
        assert result.success

        new_count = len(core.get_transition_history())
        assert new_count == initial_count + 1

    def test_predict_returns_prediction(self):
        """Predict returns prediction object."""
        core = DeterministicCore()

        state = {"canonical_hash": "abc123"}
        inputs = {"test": "input"}

        prediction = core.predict(state, inputs)
        assert prediction.expected_state_hash is not None
        assert 0.0 <= prediction.confidence <= 1.0

    def test_compare_match(self):
        """Compare detects matches."""
        core = DeterministicCore()

        from amos_kernel.L1_deterministic_core import Prediction

        prediction = Prediction("hash123", 0.9, "deterministic")
        observation = {"canonical_hash": "hash123"}

        result = core.compare(prediction, observation)
        assert result["match"] is True


class TestUniversalStateModel:
    """Test L2 - Universal State Model"""

    def test_singleton(self):
        """StateModel is singleton."""
        model1 = UniversalStateModel()
        model2 = UniversalStateModel()
        assert model1 is model2

    def test_normalize_creates_tensor(self):
        """Normalize creates StateTensor."""
        model = UniversalStateModel()

        raw = {"system_load": 50.0, "health_score": 0.9}
        tensor = model.normalize(raw)

        assert tensor.mu is not None
        assert tensor.nu is not None
        assert tensor.alpha is not None
        assert tensor.beta is not None
        assert tensor.canonical_hash != ""

    def test_project_deterministic(self):
        """Deterministic projection works."""
        model = UniversalStateModel()

        tensor = model.normalize({"system_load": 50.0})
        projection = model.project(tensor, "deterministic")

        assert "state_hash" in projection

    def test_integrity_computed(self):
        """Integrity is computed for tensor."""
        model = UniversalStateModel()

        tensor = model.normalize({"system_load": 50.0})
        integrity = model.integrity(tensor)

        assert 0.0 <= integrity.overall <= 1.0


class TestSelfObserver:
    """Test L4 - Self Observer"""

    def test_singleton(self):
        """SelfObserver is singleton."""
        obs1 = SelfObserver()
        obs2 = SelfObserver()
        assert obs1 is obs2

    def test_detect_drift_empty(self):
        """Drift detection on clean state."""
        observer = SelfObserver()
        from amos_kernel.L2_universal_state_model import StateTensor

        state = StateTensor()
        drift_reports = observer.detect_drift(state)

        # No drift in empty state
        assert len(drift_reports) == 0

    def test_structural_audit(self):
        """Structural audit produces report."""
        observer = SelfObserver()
        from amos_kernel.L2_universal_state_model import StateTensor

        state = StateTensor()
        audit = observer.structural_audit(state)

        assert "tensor_integrity" in audit
        assert "projection_coverage" in audit
        assert "timestamp" in audit


class TestRepairExecutor:
    """Test L5 - Repair Executor"""

    def test_singleton(self):
        """RepairExecutor is singleton."""
        exec1 = RepairExecutor()
        exec2 = RepairExecutor()
        assert exec1 is exec2

    def test_simulate_returns_result(self):
        """Simulation returns result."""
        repair = RepairExecutor()
        from amos_kernel.L5_repair_executor import RepairPlan

        plan = RepairPlan(
            plan_id="test-001",
            repair_type="codemod",
            target="test.py",
            changes=[{"type": "codemod", "file": "test.py", "mods": []}],
            validation_chain=["SelfObserver", "ULK"],
            priority="low",
        )

        result = repair.simulate(plan)
        assert result.success

    def test_validation_chain_check(self):
        """Validation chain must be satisfied."""
        repair = RepairExecutor()
        from amos_kernel.L5_repair_executor import RepairPlan

        # Invalid plan (no ULK)
        plan = RepairPlan(
            plan_id="test-002",
            repair_type="codemod",
            target="test.py",
            changes=[],
            validation_chain=["SelfObserver"],  # Missing ULK
            priority="low",
        )

        result = repair.apply(plan)
        assert not result.success


class TestKernelContract:
    """Test Kernel Contract Integration"""

    def test_initialize_all_layers(self):
        """Initialize creates all layers."""
        result = initialize_kernel()

        assert result.success
        assert result.value.all_ready
        assert result.value.ulk_ready
        assert result.value.deterministic_core_ready
        assert result.value.state_model_ready
        assert result.value.self_observer_ready
        assert result.value.repair_executor_ready

    def test_validate_runtime_path(self):
        """Runtime path validation works."""
        contract = KernelContract()
        contract.initialize()

        context = {"paths": {"claimed": "a", "actual": "a"}}
        result = contract.validate_runtime_path("cli", context)

        assert result.success


class TestKernelChain:
    """Test the full kernel chain"""

    def test_full_chain_initialization(self):
        """Full chain initializes in order."""
        result = initialize_kernel()
        assert result.success

        # Verify order by checking all layers exist
        ulk = UniversalLawKernel()
        core = DeterministicCore()
        state = UniversalStateModel()
        observer = SelfObserver()
        repair = RepairExecutor()

        assert ulk._initialized
        assert core._initialized
        assert state._initialized
        assert observer._initialized
        assert repair._initialized


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
