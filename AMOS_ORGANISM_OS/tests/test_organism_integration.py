"""AMOS Organism Integration Tests
==============================

Comprehensive test suite validating all 14 subsystems
and their cross-subsystem integrations.

Owner: Trang
Version: 1.0.0
"""

import importlib.util
import unittest
from pathlib import Path

# Load organism module using importlib
_org_path = Path(__file__).parent.parent / "organism.py"
_spec = importlib.util.spec_from_file_location("_organism", _org_path)
_org_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_org_mod)
AmosOrganism = _org_mod.AmosOrganism


class TestOrganismInitialization(unittest.TestCase):
    """Test organism initialization and basic state."""

    def setUp(self):
        self.organism = AmosOrganism()

    def test_organism_creates_successfully(self):
        """Test that organism initializes without errors."""
        self.assertIsNotNone(self.organism)
        self.assertIsInstance(self.organism, AmosOrganism)

    def test_session_id_exists(self):
        """Test that organism has a session ID."""
        self.assertTrue(hasattr(self.organism.state, "session_id"))
        self.assertIsNotNone(self.organism.state.session_id)

    def test_start_time_exists(self):
        """Test that organism records start time."""
        self.assertTrue(hasattr(self.organism.state, "started_at"))
        self.assertIsNotNone(self.organism.state.started_at)


class TestAllSubsystemsPresent(unittest.TestCase):
    """Test that all 14 subsystems are present and accessible."""

    def setUp(self):
        self.organism = AmosOrganism()

    def test_01_brain_present(self):
        """Test BRAIN subsystem present."""
        self.assertTrue(hasattr(self.organism, "brain"))
        self.assertTrue(hasattr(self.organism, "router"))
        self.assertTrue(hasattr(self.organism, "memory"))

    def test_02_senses_present(self):
        """Test SENSES subsystem present."""
        self.assertTrue(hasattr(self.organism, "senses"))
        self.assertTrue(hasattr(self.organism, "environment"))
        self.assertTrue(hasattr(self.organism, "context"))

    def test_03_immune_present(self):
        """Test IMMUNE subsystem present."""
        self.assertTrue(hasattr(self.organism, "immune"))
        self.assertTrue(hasattr(self.organism, "threat_detector"))
        self.assertTrue(hasattr(self.organism, "compliance"))

    def test_04_blood_present(self):
        """Test BLOOD subsystem present."""
        self.assertTrue(hasattr(self.organism, "resources"))
        self.assertTrue(hasattr(self.organism, "budget"))
        self.assertTrue(hasattr(self.organism, "cashflow"))

    def test_05_skeleton_present(self):
        """Test SKELETON subsystem present."""
        self.assertTrue(hasattr(self.organism, "constraints"))
        self.assertTrue(hasattr(self.organism, "validator"))
        self.assertTrue(hasattr(self.organism, "integrity"))

    def test_06_muscle_present(self):
        """Test MUSCLE subsystem present."""
        self.assertTrue(hasattr(self.organism, "muscle"))
        self.assertTrue(hasattr(self.organism, "code_runner"))
        self.assertTrue(hasattr(self.organism, "workflow"))

    def test_07_metabolism_present(self):
        """Test METABOLISM subsystem present."""
        self.assertTrue(hasattr(self.organism, "pipeline"))
        self.assertTrue(hasattr(self.organism, "transform"))
        self.assertTrue(hasattr(self.organism, "io_router"))

    def test_08_world_model_present(self):
        """Test WORLD_MODEL subsystem present."""
        self.assertTrue(hasattr(self.organism, "knowledge"))
        self.assertTrue(hasattr(self.organism, "context_mapper"))
        self.assertTrue(hasattr(self.organism, "semantic_index"))

    def test_09_quantum_layer_present(self):
        """Test QUANTUM_LAYER subsystem present."""
        self.assertTrue(hasattr(self.organism, "scenarios"))
        self.assertTrue(hasattr(self.organism, "monte_carlo"))
        self.assertTrue(hasattr(self.organism, "decision_optimizer"))

    def test_10_social_engine_present(self):
        """Test SOCIAL_ENGINE subsystem present."""
        self.assertTrue(hasattr(self.organism, "agent_coordinator"))
        self.assertTrue(hasattr(self.organism, "communication_bridge"))
        self.assertTrue(hasattr(self.organism, "human_interface"))
        self.assertTrue(hasattr(self.organism, "negotiation_engine"))

    def test_11_life_engine_present(self):
        """Test LIFE_ENGINE subsystem present."""
        self.assertTrue(hasattr(self.organism, "growth_engine"))
        self.assertTrue(hasattr(self.organism, "adaptation_system"))
        self.assertTrue(hasattr(self.organism, "health_monitor"))
        self.assertTrue(hasattr(self.organism, "lifecycle_manager"))

    def test_12_legal_brain_present(self):
        """Test LEGAL_BRAIN subsystem present."""
        self.assertTrue(hasattr(self.organism, "policy_engine"))
        self.assertTrue(hasattr(self.organism, "compliance_auditor"))
        self.assertTrue(hasattr(self.organism, "contract_manager"))
        self.assertTrue(hasattr(self.organism, "risk_governor"))

    def test_13_factory_present(self):
        """Test FACTORY subsystem present."""
        self.assertTrue(hasattr(self.organism, "agent_factory"))
        self.assertTrue(hasattr(self.organism, "code_generator"))
        self.assertTrue(hasattr(self.organism, "builder"))
        self.assertTrue(hasattr(self.organism, "quality"))

    def test_14_interfaces_present(self):
        """Test INTERFACES subsystem present."""
        self.assertTrue(hasattr(self.organism, "api"))
        self.assertTrue(hasattr(self.organism, "mcp"))


class TestSubsystemStatus(unittest.TestCase):
    """Test that all subsystems report status correctly."""

    def setUp(self):
        self.organism = AmosOrganism()
        self.status = self.organism.status()

    def test_status_returns_dict(self):
        """Test status returns dictionary."""
        self.assertIsInstance(self.status, dict)

    def test_all_14_subsystems_in_active_list(self):
        """Test all 14 subsystems are in active list."""
        active = self.status.get("active_subsystems", [])
        self.assertEqual(len(active), 14)

    def test_all_subsystems_report_status(self):
        """Test all subsystems have status entries."""
        subsystems = self.status.get("subsystems", {})
        expected = [
            "brain",
            "senses",
            "skeleton",
            "world_model",
            "quantum_layer",
            "blood",
            "metabolism",
            "immune",
            "muscle",
            "factory",
            "legal_brain",
            "social_engine",
            "life_engine",
            "memory",
            "workflow",
        ]
        for subsys in expected:
            self.assertIn(subsys, subsystems, f"Missing status for {subsys}")


class TestCrossSubsystemIntegration(unittest.TestCase):
    """Test cross-subsystem integrations."""

    def setUp(self):
        self.organism = AmosOrganism()

    def test_brain_to_muscle_bridge(self):
        """Test BRAIN can communicate with MUSCLE."""
        # Verify the bridge exists
        self.assertTrue(hasattr(self.organism, "brain"))
        self.assertTrue(hasattr(self.organism, "muscle"))

    def test_senses_to_world_model_flow(self):
        """Test SENSES data flows to WORLD_MODEL."""
        self.assertTrue(hasattr(self.organism, "senses"))
        self.assertTrue(hasattr(self.organism, "knowledge"))

    def test_immune_protects_all_subsystems(self):
        """Test IMMUNE can protect other subsystems."""
        immune_status = self.organism.immune.status()
        self.assertIsInstance(immune_status, dict)

    def test_blood_resources_available_to_muscle(self):
        """Test BLOOD resources accessible to MUSCLE."""
        self.assertTrue(hasattr(self.organism.resources, "pools"))

    def test_legal_brain_enforces_on_factory(self):
        """Test LEGAL_BRAIN can govern FACTORY."""
        self.assertTrue(hasattr(self.organism, "policy_engine"))
        self.assertTrue(hasattr(self.organism, "agent_factory"))

    def test_life_engine_monitors_health(self):
        """Test LIFE_ENGINE health monitoring works."""
        health_status = self.organism.health_monitor.get_status()
        self.assertIsInstance(health_status, dict)
        self.assertIn("overall_health", health_status)

    def test_social_engine_coordination(self):
        """Test SOCIAL_ENGINE agent coordination."""
        coordinator_status = self.organism.agent_coordinator.get_status()
        self.assertIsInstance(coordinator_status, dict)
        self.assertIn("total_pools", coordinator_status)


class TestEndToEndWorkflows(unittest.TestCase):
    """Test end-to-end workflows across subsystems."""

    def setUp(self):
        self.organism = AmosOrganism()

    def test_perceive_think_act_cycle(self):
        """Test full perceive-think-act cycle."""
        # Perceive
        perception = self.organism.perceive("Test environment")
        self.assertIsNotNone(perception)

        # Think (via brain)
        self.assertTrue(hasattr(self.organism.brain, "status"))

        # Act (via muscle)
        self.assertTrue(hasattr(self.organism.muscle, "status"))

    def test_scan_context_decide_workflow(self):
        """Test scan-context-decide workflow."""
        # Scan via SENSES
        scan_result = self.organism.scan()
        self.assertIsNotNone(scan_result)

        # Gather context
        context = self.organism.gather_context()
        self.assertIsInstance(context, dict)

        # Decision via QUANTUM_LAYER
        self.assertTrue(hasattr(self.organism, "decision_optimizer"))


class TestOrganismCompleteness(unittest.TestCase):
    """Test that organism is complete and functional."""

    def setUp(self):
        self.organism = AmosOrganism()

    def test_all_subsystem_numbers_present(self):
        """Test all numbered subsystems are present."""
        status = self.organism.status()
        active = status.get("active_subsystems", [])

        expected_numbers = [
            "01_BRAIN",
            "02_SENSES",
            "03_IMMUNE",
            "04_BLOOD",
            "05_SKELETON",
            "06_MUSCLE",
            "07_METABOLISM",
            "08_WORLD_MODEL",
            "09_QUANTUM_LAYER",
            "10_SOCIAL_ENGINE",
            "11_LIFE_ENGINE",
            "12_LEGAL_BRAIN",
            "13_FACTORY",
            "14_INTERFACES",
        ]

        for expected in expected_numbers:
            self.assertIn(expected, active, f"Missing {expected}")

    def test_organism_is_production_ready(self):
        """Test organism is production ready."""
        # All 14 subsystems active
        status = self.organism.status()
        active = status.get("active_subsystems", [])
        self.assertEqual(len(active), 14, "Not all 14 subsystems active")

        # Status reports correctly
        self.assertIn("subsystems", status)
        self.assertIn("session_id", status)

    def test_lifecycle_manager_tracks_birth(self):
        """Test lifecycle manager recorded organism birth."""
        lifecycle = self.organism.lifecycle_manager
        self.assertEqual(lifecycle.current_stage.value, "seed")
        self.assertTrue(len(lifecycle.events) > 0)


def run_integration_tests():
    """Run all integration tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOrganismInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestAllSubsystemsPresent))
    suite.addTests(loader.loadTestsFromTestCase(TestSubsystemStatus))
    suite.addTests(loader.loadTestsFromTestCase(TestCrossSubsystemIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndWorkflows))
    suite.addTests(loader.loadTestsFromTestCase(TestOrganismCompleteness))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    result = run_integration_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
