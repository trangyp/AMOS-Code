"""Kernel Core Tests - Unit tests for kernel-first architecture"""

import unittest

from amos_kernel.core.law import UniversalLawKernel
from amos_kernel.core.state import TensorState
from amos_kernel.workflows import WorkflowResult, get_workflow_engine


class TestUniversalLawKernel(unittest.TestCase):
    """Test law validation across all 7 invariants."""

    def setUp(self):
        self.law = UniversalLawKernel()

    def test_coherence_invariant(self):
        """Test coherence check passes for valid state."""
        result = self.law.validate_invariants(
            biological={"load": 0.5},
            cognitive={"focus": 0.8},
            system={"cpu": 0.3},
            environment={"risk": 0.1},
        )
        self.assertTrue(result.passed)
        self.assertLess(result.collapse_risk, 0.5)

    def test_drift_detection(self):
        """Test drift detection for anomalous state."""
        result = self.law.validate_invariants(
            biological={"load": 0.99},
            cognitive={"focus": 0.01},
            system={"cpu": 0.99},
            environment={"risk": 0.9},
        )
        self.assertGreater(result.collapse_risk, 0.5)

    def test_seven_invariants_checked(self):
        """Verify all 7 invariants are validated."""
        result = self.law.validate_invariants(
            biological={"load": 0.5},
            cognitive={"focus": 0.8},
            system={"cpu": 0.3},
            environment={"risk": 0.1},
        )
        self.assertEqual(len(result.details), 7)
        self.assertIn("coherence", result.details)
        self.assertIn("stability", result.details)


class TestTensorState(unittest.TestCase):
    """Test tensor state normalization and integrity."""

    def setUp(self):
        self.state = TensorState()

    def test_normalization(self):
        """Test state normalization produces valid tensors."""
        raw = {
            "biological": {"load": 1.0, "fatigue": 0.5},
            "cognitive": {"focus": 0.8, "stress": 0.2},
            "system": {"cpu": 0.3, "memory": 0.4},
            "environment": {"risk": 0.1, "temperature": 0.5},
        }
        normalized = self.state.normalize(raw)
        self.assertIn("biological", normalized)
        self.assertIn("cognitive", normalized)

    def test_integrity_calculation(self):
        """Test integrity score calculation."""
        tensor = {
            "biological": [0.5, 0.3],
            "cognitive": [0.8, 0.2],
        }
        integrity = self.state.calculate_integrity(tensor)
        self.assertGreaterEqual(integrity.score, 0.0)
        self.assertLessEqual(integrity.score, 1.0)


class TestWorkflowEngine(unittest.TestCase):
    """Test workflow execution through kernel."""

    def setUp(self):
        self.engine = get_workflow_engine()

    def test_workflow_execution(self):
        """Test basic workflow execution."""
        result = self.engine.execute(
            workflow_id="test-workflow",
            raw_input={
                "biological": {"load": 0.5},
                "cognitive": {"focus": 0.8},
                "system": {"cpu": 0.3},
                "environment": {"risk": 0.1},
            },
        )
        self.assertIsInstance(result, WorkflowResult)
        self.assertEqual(result.workflow_id, "test-workflow")
        self.assertGreater(len(result.steps), 0)

    def test_law_validation_in_workflow(self):
        """Test law validation occurs during workflow."""
        result = self.engine.execute(
            workflow_id="law-test",
            raw_input={
                "biological": {"load": 0.5},
                "cognitive": {"focus": 0.8},
                "system": {"cpu": 0.3},
                "environment": {"risk": 0.1},
            },
            validate_laws=True,
        )
        self.assertTrue(result.law_validation.passed)


class TestEquationExecutor(unittest.TestCase):
    """Test equation execution through kernel."""

    def test_sigmoid_execution(self):
        """Test sigmoid equation executes."""
        from amos_kernel.equations import get_executor

        executor = get_executor()
        result = executor.execute("sigmoid", {"x": 0.0})
        self.assertTrue(result.success)
        self.assertAlmostEqual(result.result, 0.5, places=2)

    def test_softmax_execution(self):
        """Test softmax equation executes."""
        from amos_kernel.equations import get_executor

        executor = get_executor()
        result = executor.execute("softmax", {"logits": [1.0, 2.0, 3.0]})
        self.assertTrue(result.success)
        self.assertEqual(len(result.result), 3)


if __name__ == "__main__":
    unittest.main()
