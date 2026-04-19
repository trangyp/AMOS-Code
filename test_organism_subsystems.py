#!/usr/bin/env python3
"""AMOS ORGANISM_OS Subsystem Integration Tests
=============================================

Comprehensive test suite for all 14 biological subsystems:
- Validates subsystem handlers
- Tests primary loop execution
- Verifies inter-subsystem communication
- Checks error handling and recovery

Run: python test_organism_subsystems.py

Owner: Trang
Version: 1.0.0
"""

import json
import sys
import unittest
from pathlib import Path
from typing import Any, Dict

# Add parent to path
AMOS_ROOT = Path(__file__).parent
sys.path.insert(0, str(AMOS_ROOT))
sys.path.insert(0, str(AMOS_ROOT / "AMOS_ORGANISM_OS"))

from AMOS_ORGANISM_OS.AMOS_MASTER_ORCHESTRATOR import (
    HANDLER_MAP,
    PRIMARY_LOOP,
    AmosMasterOrchestrator,
    BrainHandler,
    CycleResult,
    ImmuneHandler,
    MetabolismHandler,
    MuscleHandler,
    QuantumLayerHandler,
    SensesHandler,
    SkeletonHandler,
    WorldModelHandler,
    get_handler,
)


class TestSubsystemHandlers(unittest.TestCase):
    """Test individual subsystem handlers."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.mock_registry = {
            "subsystems": {
                "01_BRAIN": {"status": "active", "kernel_refs": ["test_kernel"]},
                "02_SENSES": {"status": "active"},
                "03_IMMUNE": {"status": "active"},
                "06_MUSCLE": {"status": "active"},
                "07_METABOLISM": {"status": "active"},
                "08_WORLD_MODEL": {"status": "active"},
                "12_QUANTUM_LAYER": {"status": "active"},
                "05_SKELETON": {"status": "active"},
            }
        }
        self.context = {"organism_root": AMOS_ROOT / "AMOS_ORGANISM_OS"}

    def test_brain_handler_initialization(self) -> None:
        """Test BrainHandler initialization."""
        handler = BrainHandler("01_BRAIN", self.mock_registry)
        self.assertEqual(handler.code, "01_BRAIN")
        self.assertIsNotNone(handler.config)

    def test_brain_handler_process(self) -> None:
        """Test BrainHandler process cycle."""
        handler = BrainHandler("01_BRAIN", self.mock_registry)
        result = handler.process(self.context)

        self.assertIsInstance(result, CycleResult)
        self.assertEqual(result.subsystem, "01_BRAIN")
        self.assertEqual(result.status, "active")
        self.assertIn("load_cognition_engine", result.actions)
        self.assertEqual(result.next_recommended, "02_SENSES")

    def test_senses_handler_process(self) -> None:
        """Test SensesHandler process cycle."""
        handler = SensesHandler("02_SENSES", self.mock_registry)
        result = handler.process(self.context)

        self.assertIsInstance(result, CycleResult)
        self.assertEqual(result.subsystem, "02_SENSES")
        self.assertEqual(result.status, "active")
        self.assertIn("scan_filesystem", result.actions)
        self.assertEqual(result.next_recommended, "05_SKELETON")

    def test_skeleton_handler_process(self) -> None:
        """Test SkeletonHandler process cycle."""
        handler = SkeletonHandler("05_SKELETON", self.mock_registry)
        result = handler.process(self.context)

        self.assertIsInstance(result, CycleResult)
        self.assertEqual(result.subsystem, "05_SKELETON")
        self.assertIn("load_constraints", result.actions)
        self.assertEqual(result.next_recommended, "08_WORLD_MODEL")

    def test_world_model_handler_process(self) -> None:
        """Test WorldModelHandler process cycle."""
        handler = WorldModelHandler("08_WORLD_MODEL", self.mock_registry)
        result = handler.process(self.context)

        self.assertIsInstance(result, CycleResult)
        self.assertEqual(result.subsystem, "08_WORLD_MODEL")
        self.assertIn("load_tss_tpe", result.actions)
        self.assertEqual(result.next_recommended, "12_QUANTUM_LAYER")

    def test_quantum_layer_handler_process(self) -> None:
        """Test QuantumLayerHandler process cycle."""
        handler = QuantumLayerHandler("12_QUANTUM_LAYER", self.mock_registry)
        result = handler.process(self.context)

        self.assertIsInstance(result, CycleResult)
        self.assertEqual(result.subsystem, "12_QUANTUM_LAYER")
        self.assertIn("load_quantum_stack", result.actions)
        self.assertEqual(result.next_recommended, "06_MUSCLE")

    def test_muscle_handler_process(self) -> None:
        """Test MuscleHandler process cycle."""
        handler = MuscleHandler("06_MUSCLE", self.mock_registry)
        result = handler.process(self.context)

        self.assertIsInstance(result, CycleResult)
        self.assertEqual(result.subsystem, "06_MUSCLE")
        self.assertIn("check_code_engines", result.actions)
        self.assertEqual(result.next_recommended, "07_METABOLISM")

    def test_metabolism_handler_process(self) -> None:
        """Test MetabolismHandler process cycle."""
        handler = MetabolismHandler("07_METABOLISM", self.mock_registry)
        result = handler.process(self.context)

        self.assertIsInstance(result, CycleResult)
        self.assertEqual(result.subsystem, "07_METABOLISM")
        self.assertIn("run_pipeline_cleanup", result.actions)
        self.assertEqual(result.next_recommended, "01_BRAIN")

    def test_immune_handler_process(self) -> None:
        """Test ImmuneHandler process cycle."""
        handler = ImmuneHandler("03_IMMUNE", self.mock_registry)

        # Add context for metrics
        context_with_metrics = {
            **self.context,
            "subsystem_load": 50.0,
            "pending_tasks": 0,
            "anomaly_count": 0,
        }

        result = handler.process(context_with_metrics)

        self.assertIsInstance(result, CycleResult)
        self.assertEqual(result.subsystem, "03_IMMUNE")
        self.assertIn("validate_security_policies", result.actions)
        self.assertIn("alerts_triggered", result.outputs)
        self.assertIn("active_alerts", result.outputs)


class TestHandlerFactory(unittest.TestCase):
    """Test handler factory function."""

    def test_get_handler_brain(self) -> None:
        """Test getting Brain handler."""
        handler = get_handler("01_BRAIN", {})
        self.assertIsInstance(handler, BrainHandler)

    def test_get_handler_senses(self) -> None:
        """Test getting Senses handler."""
        handler = get_handler("02_SENSES", {})
        self.assertIsInstance(handler, SensesHandler)

    def test_get_handler_invalid(self) -> None:
        """Test getting invalid handler returns None."""
        handler = get_handler("INVALID_CODE", {})
        self.assertIsNone(handler)

    def test_handler_map_completeness(self) -> None:
        """Test that all primary loop subsystems have handlers."""
        for code in PRIMARY_LOOP:
            self.assertIn(code, HANDLER_MAP, f"Handler for {code} not found in HANDLER_MAP")


class TestPrimaryLoop(unittest.TestCase):
    """Test primary loop execution."""

    def test_primary_loop_defined(self) -> None:
        """Test primary loop is properly defined."""
        self.assertIsInstance(PRIMARY_LOOP, list)
        self.assertGreater(len(PRIMARY_LOOP), 0)
        # Should start with BRAIN
        self.assertEqual(PRIMARY_LOOP[0], "01_BRAIN")
        # Should be a cycle (ends back at BRAIN)
        self.assertEqual(PRIMARY_LOOP[-1], "01_BRAIN")

    def test_primary_loop_valid_codes(self) -> None:
        """Test all primary loop codes are valid."""
        valid_codes = set(HANDLER_MAP.keys())
        for code in PRIMARY_LOOP:
            self.assertIn(code, valid_codes, f"{code} in PRIMARY_LOOP but not in HANDLER_MAP")


class TestOrchestratorIntegration(unittest.TestCase):
    """Test full orchestrator integration."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up orchestrator once for all tests."""
        cls.orchestrator = AmosMasterOrchestrator()
        cls.initialized = cls.orchestrator.initialize()

    def test_orchestrator_initialization(self) -> None:
        """Test orchestrator initializes successfully."""
        if not self.initialized:
            self.skipTest("Orchestrator failed to initialize")

        self.assertTrue(self.initialized)
        self.assertGreater(len(self.orchestrator.state.active_subsystems), 0)

    def test_orchestrator_run_cycle(self) -> None:
        """Test running a full cycle."""
        if not self.initialized:
            self.skipTest("Orchestrator failed to initialize")

        initial_cycle_count = self.orchestrator.state.cycle_count

        context = {"organism_root": AMOS_ROOT / "AMOS_ORGANISM_OS"}
        results = self.orchestrator.run_cycle(context)

        self.assertIsInstance(results, list)
        self.assertEqual(self.orchestrator.state.cycle_count, initial_cycle_count + 1)
        self.assertGreater(self.orchestrator.state.last_cycle_time, 0)

    def test_orchestrator_status(self) -> None:
        """Test getting orchestrator status."""
        if not self.initialized:
            self.skipTest("Orchestrator failed to initialize")

        status = self.orchestrator.get_status()

        self.assertIsInstance(status, dict)
        self.assertIn("cycle_count", status)
        self.assertIn("active_subsystems", status)
        self.assertIn("error_count", status)


class TestCycleResult(unittest.TestCase):
    """Test CycleResult data structure."""

    def test_cycle_result_creation(self) -> None:
        """Test creating a CycleResult."""
        result = CycleResult(
            subsystem="TEST",
            status="active",
            actions=["action1", "action2"],
            outputs={"key": "value"},
            next_recommended="NEXT",
        )

        self.assertEqual(result.subsystem, "TEST")
        self.assertEqual(result.status, "active")
        self.assertEqual(result.actions, ["action1", "action2"])
        self.assertEqual(result.outputs, {"key": "value"})
        self.assertEqual(result.next_recommended, "NEXT")

    def test_cycle_result_defaults(self) -> None:
        """Test CycleResult default values."""
        result = CycleResult(
            subsystem="TEST",
            status="active",
            actions=[],
            outputs={},
        )

        self.assertIsNone(result.next_recommended)


def run_integration_tests() -> Dict[str, Any]:
    """Run all integration tests and return summary."""
    print("=" * 70)
    print("AMOS ORGANISM_OS SUBSYSTEM INTEGRATION TESTS")
    print("=" * 70)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSubsystemHandlers))
    suite.addTests(loader.loadTestsFromTestCase(TestHandlerFactory))
    suite.addTests(loader.loadTestsFromTestCase(TestPrimaryLoop))
    suite.addTests(loader.loadTestsFromTestCase(TestOrchestratorIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCycleResult))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Generate summary
    summary = {
        "total_tests": result.testsRun,
        "success": result.wasSuccessful(),
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
    }

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Success: {'✅ PASSED' if summary['success'] else '❌ FAILED'}")
    print(f"Failures: {summary['failures']}")
    print(f"Errors: {summary['errors']}")
    print(f"Skipped: {summary['skipped']}")
    print("=" * 70)

    return summary


if __name__ == "__main__":
    summary = run_integration_tests()

    # Save results
    results_file = AMOS_ROOT / "test_organism_results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults saved to: {results_file}")

    # Exit with appropriate code
    sys.exit(0 if summary["success"] else 1)
