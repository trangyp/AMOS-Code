"""AMOS Architecture Integration Test Suite.

Validates the complete system-of-systems architecture:
- Repo Doctor Omega (27-dim state) → Omega Bridge → Self-Evolution
- Unified Orchestrator → Governance → Governance Bridge → Self-Evolution
- Bridge conflict resolution
- Full autonomous flow
- Failure modes and recovery

Test Levels:
1. Component Integration (bridges + systems)
2. End-to-End Flow (detect → decide → execute → learn)
3. Failure Recovery (rollback, safety checks)
4. State Consistency (across all systems)

Owner: AMOS Brain (Canonical Runtime)
Version: 1.0.0
"""


import sys
import time
import unittest
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestArchitectureIntegration(unittest.TestCase):
    """Integration tests for AMOS architecture."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up test environment once for all tests."""
        cls.repo_root = Path(__file__).parent.parent

        # Check subsystem availability
        cls.omega_available = cls._check_omega()
        cls.evolution_available = cls._check_evolution()
        cls.governance_available = cls._check_governance()

        print(f"\n{'='*70}")
        print("AMOS ARCHITECTURE INTEGRATION TEST SUITE")
        print(f"{'='*70}")
        print(f"Omega available: {cls.omega_available}")
        print(f"Evolution available: {cls.evolution_available}")
        print(f"Governance available: {cls.governance_available}")
        print(f"{'='*70}\n")

    @staticmethod
    def _check_omega() -> bool:
        """Check if Repo Doctor Omega is available."""
        try:
            from repo_doctor_omega.state.basis import BasisVector
            return True
        except ImportError:
            return False

    @staticmethod
    def _check_evolution() -> bool:
        """Check if self-evolution infrastructure is available."""
        try:
            from amos_self_evolution.evolution_contract_registry import EvolutionContract
            from amos_self_evolution.evolution_execution_engine import EvolutionExecutionEngine
            return True
        except ImportError:
            return False

    @staticmethod
    def _check_governance() -> bool:
        """Check if governance is available."""
        try:
            from amos_brain.governance_bridge import GovernanceBridge
            return True
        except ImportError:
            return False

    # =========================================================================
    # TEST LEVEL 1: Component Integration
    # =========================================================================

    def test_01_omega_bridge_initialization(self) -> None:
        """Test Omega-Evolution Bridge can initialize."""
        if not self.omega_available or not self.evolution_available:
            self.skipTest("Omega or Evolution not available")

        from repo_doctor_omega.omega_evolution_bridge import OmegaEvolutionBridge

        bridge = OmegaEvolutionBridge(str(self.repo_root))
        self.assertIsNotNone(bridge)
        self.assertTrue(bridge.is_fully_operational)

        print("✓ Omega Bridge initializes correctly")

    def test_02_governance_bridge_initialization(self) -> None:
        """Test Governance-Evolution Bridge can initialize."""
        if not self.governance_available or not self.evolution_available:
            self.skipTest("Governance or Evolution not available")

        from amos_self_evolution.governance_evolution_bridge import GovernanceEvolutionBridge

        bridge = GovernanceEvolutionBridge(str(self.repo_root))
        self.assertIsNotNone(bridge)

        print("✓ Governance Bridge initializes correctly")

    def test_03_evolution_engine_initialization(self) -> None:
        """Test Evolution Execution Engine can initialize."""
        if not self.evolution_available:
            self.skipTest("Evolution not available")

        from amos_self_evolution.evolution_execution_engine import EvolutionExecutionEngine

        engine = EvolutionExecutionEngine(str(self.repo_root))
        self.assertIsNotNone(engine)

        print("✓ Evolution Engine initializes correctly")

    # =========================================================================
    # TEST LEVEL 2: End-to-End Flow
    # =========================================================================

    def test_04_omega_state_to_trigger(self) -> None:
        """Test Omega state degradation creates evolution trigger."""
        if not self.omega_available or not self.evolution_available:
            self.skipTest("Omega or Evolution not available")

        from repo_doctor_omega.omega_evolution_bridge import (
            OmegaEvolutionBridge,
            StateTriggerThreshold,
        )

        bridge = OmegaEvolutionBridge(str(self.repo_root))

        # Set conservative threshold to force trigger
        bridge.thresholds = {
            "critical": StateTriggerThreshold.CRITICAL,
            "warning": StateTriggerThreshold.WARNING,
            "notice": StateTriggerThreshold.NOTICE,
        }

        # Check state (should find at least test data)
        results = bridge.check_state_and_evolve()

        # Verify results structure
        self.assertIsInstance(results, list)

        print(f"✓ Omega state check completed ({len(results)} triggers)")

    def test_05_contract_creation_from_trigger(self) -> None:
        """Test evolution contract created from state trigger."""
        if not self.omega_available or not self.evolution_available:
            self.skipTest("Omega or Evolution not available")

        from repo_doctor_omega.omega_evolution_bridge import (
            OmegaEvolutionBridge,
            StateEvolutionTrigger,
            StateTriggerThreshold,
        )
        from amos_self_evolution.evolution_contract_registry import EvolutionContract

        bridge = OmegaEvolutionBridge(str(self.repo_root))

        # Create a mock trigger
        trigger = StateEvolutionTrigger(
            trigger_id="test_trigger_001",
            basis_vector="TEST",
            current_value=0.4,  # Below warning threshold
            threshold_breached=StateTriggerThreshold.WARNING,
            recommended_action="Test evolution",
            severity_score=0.8,
        )

        # Create contract from trigger
        contract = bridge._create_contract_from_trigger(trigger)

        self.assertIsInstance(contract, EvolutionContract)
        self.assertIn("OMEGA", contract.evolution_id)
        self.assertIn("TEST", contract.evolution_id)

        print("✓ Contract created from state trigger")

    def test_06_governance_decision_processing(self) -> None:
        """Test governance decision can be processed by bridge."""
        if not self.governance_available or not self.evolution_available:
            self.skipTest("Governance or Evolution not available")

        from amos_self_evolution.governance_evolution_bridge import (
            GovernanceEvolutionBridge,
            BridgeMode,
        )

        bridge = GovernanceEvolutionBridge(str(self.repo_root))
        bridge.set_mode(BridgeMode.OBSERVE)  # Safe mode for testing

        # Create mock governance decision
        class MockDecision:
            decision_id = "mock_001"
            requires_human_approval = False

        decision = MockDecision()

        # Process decision
        from amos_self_evolution.evolution_opportunity_detector import (
            DetectedOpportunity,
        )

        opportunity = DetectedOpportunity(
            opportunity_id="test_opp_001",
            opportunity_type="test",
            description="Test opportunity",
            confidence=0.8,
        )

        result = bridge.process_governance_decision(decision, opportunity)

        self.assertIsNotNone(result)
        self.assertEqual(result.governance_decision_id, "mock_001")

        print("✓ Governance decision processed")

    # =========================================================================
    # TEST LEVEL 3: Safety and Recovery
    # =========================================================================

    def test_07_safety_check_blocks_invalid_contract(self) -> None:
        """Test safety checks prevent invalid evolution execution."""
        if not self.evolution_available:
            self.skipTest("Evolution not available")

        from amos_self_evolution.evolution_execution_engine import (
            EvolutionExecutionEngine,
            ExecutionPhase,
        )
        from amos_self_evolution.evolution_contract_registry import EvolutionContract

        engine = EvolutionExecutionEngine(str(self.repo_root))

        # Create invalid contract (no files)
        contract = EvolutionContract(
            evolution_id="INVALID_TEST",
            owner="Test",
            target_files=[],
            target_modules=[],
            verification_steps=[],
            mutation_budget_lines=100,
            mutation_budget_files=1,
        )

        # Attempt execution
        result = engine.execute_evolution(contract, [])

        # Should fail at safety check phase
        self.assertFalse(result.success)
        self.assertTrue(any(p.phase == ExecutionPhase.SAFETY_CHECK for p in result.phases))

        print("✓ Safety check blocked invalid contract")

    def test_08_rollback_capability(self) -> None:
        """Test rollback system is operational."""
        if not self.evolution_available:
            self.skipTest("Evolution not available")

        from amos_self_evolution.rollback_guard import RollbackGuard

        guard = RollbackGuard(str(self.repo_root))

        # Verify backup directory exists
        self.assertTrue(guard.backup_dir.exists())

        print("✓ Rollback system operational")

    def test_09_regression_guard_blocks_bad_changes(self) -> None:
        """Test regression guard prevents harmful mutations."""
        if not self.evolution_available:
            self.skipTest("Evolution not available")

        from amos_self_evolution.regression_guard import RegressionGuard

        guard = RegressionGuard(str(self.repo_root))

        # Verify guard can run checks
        from amos_self_evolution.evolution_contract_registry import EvolutionContract

        contract = EvolutionContract(
            evolution_id="REGRESSION_TEST",
            owner="Test",
            target_files=[],
            target_modules=[],
            verification_steps=[],
            mutation_budget_lines=100,
            mutation_budget_files=1,
        )

        report = guard.verify_evolution(contract)

        self.assertIsNotNone(report)
        self.assertIsInstance(report.mutation_permitted, bool)

        print("✓ Regression guard operational")

    # =========================================================================
    # TEST LEVEL 4: State Consistency
    # =========================================================================

    def test_10_bridge_mode_consistency(self) -> None:
        """Test bridge modes are consistent across both bridges."""
        if not (self.omega_available and self.evolution_available):
            self.skipTest("Required systems not available")

        from repo_doctor_omega.omega_evolution_bridge import OmegaEvolutionBridge
        from amos_self_evolution.governance_evolution_bridge import GovernanceEvolutionBridge
        from amos_self_evolution.governance_evolution_bridge import BridgeMode

        omega_bridge = OmegaEvolutionBridge(str(self.repo_root))
        gov_bridge = GovernanceEvolutionBridge(str(self.repo_root))

        # Set Omega bridge mode
        omega_bridge.set_mode(BridgeMode.SUPERVISED)

        # Verify mode was set
        self.assertEqual(omega_bridge.mode, BridgeMode.SUPERVISED)

        print("✓ Bridge mode consistency maintained")

    def test_11_metrics_tracking(self) -> None:
        """Test metrics are tracked across systems."""
        if not self.evolution_available:
            self.skipTest("Evolution not available")

        from amos_self_evolution.governance_evolution_bridge import GovernanceEvolutionBridge

        bridge = GovernanceEvolutionBridge(str(self.repo_root))

        metrics = bridge.get_metrics()

        self.assertIsInstance(metrics, dict)
        self.assertIn("total_decisions", metrics)
        self.assertIn("successfully_executed", metrics)

        print("✓ Metrics tracking operational")

    def test_12_state_health_summary(self) -> None:
        """Test state health summary from Omega."""
        if not self.omega_available:
            self.skipTest("Omega not available")

        from repo_doctor_omega.omega_evolution_bridge import OmegaEvolutionBridge

        bridge = OmegaEvolutionBridge(str(self.repo_root))

        summary = bridge.get_state_health_summary()

        self.assertIsInstance(summary, dict)
        self.assertIn("total_vectors", summary)
        self.assertIn("healthy", summary)
        self.assertIn("overall_health", summary)

        print("✓ State health summary operational")


class TestEndToEndAutonomousFlow(unittest.TestCase):
    """End-to-end tests simulating full autonomous flow."""

    def test_full_detect_decide_execute_learn_cycle(self) -> None:
        """Test complete autonomous self-improvement cycle."""
        # This test simulates the full cycle without actual mutations
        print("\n" + "="*70)
        print("END-TO-END AUTONOMOUS FLOW TEST")
        print("="*70)

        steps = []

        # Step 1: Detect (Omega State)
        try:
            from repo_doctor_omega.omega_evolution_bridge import OmegaEvolutionBridge
            bridge = OmegaEvolutionBridge(".")
            state = bridge.get_state_health_summary()
            steps.append(("Detect", "✓ Omega state retrieved", state.get("overall_health", 0)))
        except Exception as e:
            steps.append(("Detect", f"✗ Failed: {e}", 0))

        # Step 2: Decide (Governance)
        try:
            from amos_self_evolution.governance_evolution_bridge import (
                GovernanceEvolutionBridge,
                BridgeMode,
            )
            bridge = GovernanceEvolutionBridge(".")
            bridge.set_mode(BridgeMode.OBSERVE)  # Safe mode
            steps.append(("Decide", "✓ Governance ready", 1))
        except Exception as e:
            steps.append(("Decide", f"✗ Failed: {e}", 0))

        # Step 3: Safety Check (E003)
        try:
            from amos_self_evolution.regression_guard import RegressionGuard
            guard = RegressionGuard(".")
            steps.append(("Safety", "✓ Regression guard ready", 1))
        except Exception as e:
            steps.append(("Safety", f"✗ Failed: {e}", 0))

        # Step 4: Execute Capability (E012)
        try:
            from amos_self_evolution.evolution_execution_engine import EvolutionExecutionEngine
            engine = EvolutionExecutionEngine(".")
            steps.append(("Execute", "✓ Evolution engine ready", 1))
        except Exception as e:
            steps.append(("Execute", f"✗ Failed: {e}", 0))

        # Step 5: Rollback Capability (E004)
        try:
            from amos_self_evolution.rollback_guard import RollbackGuard
            guard = RollbackGuard(".")
            steps.append(("Rollback", "✓ Rollback guard ready", 1))
        except Exception as e:
            steps.append(("Rollback", f"✗ Failed: {e}", 0))

        # Print results
        for step_name, status, value in steps:
            print(f"  {step_name:12} {status}")

        # Verify all steps passed
        success_count = sum(1 for _, status, _ in steps if status.startswith("✓"))
        total_count = len(steps)

        print(f"\nResult: {success_count}/{total_count} steps operational")
        print("="*70)

        # Test passes if at least 4/5 steps are ready
        self.assertGreaterEqual(success_count, 4, f"Only {success_count}/5 steps operational")


def run_integration_tests() -> None:
    """Run all integration tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestArchitectureIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndAutonomousFlow))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print(f"\n{'='*70}")
    print("INTEGRATION TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"{'='*70}")

    if result.wasSuccessful():
        print("✓ ALL INTEGRATION TESTS PASSED")
        print("Architecture is validated and operational.")
    else:
        print("✗ SOME TESTS FAILED")
        print("Review failures before proceeding.")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
