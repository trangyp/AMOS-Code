#!/usr/bin/env python3
"""
AMOS Unified Equation System Test Suite
=======================================

Comprehensive integration tests for all equation systems:
- SuperBrain Equation Bridge (33 domains, 145+ equations)
- Equation Knowledge Bridge (PL theory, 400+ equations)
- Invariant Verification Engine (neural-symbolic)
- Automated Remediation Engine (self-healing)
- Unified Equation API (central hub)
"""

import sys
import unittest
from pathlib import Path

# Add all paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS"))
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS" / "01_BRAIN"))
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS" / "03_IMMUNE"))
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS" / "06_MUSCLE"))
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS" / "15_KNOWLEDGE_CORE"))


class TestSuperBrainIntegration(unittest.TestCase):
    """Test SuperBrain equation bridge integration."""

    def test_superbrain_import(self):
        """Test SuperBrain can be imported."""
        try:
            from amos_superbrain_equation_bridge import Domain, MathematicalPattern

            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"SuperBrain import failed: {e}")

    def test_domains_available(self):
        """Test all 33 domains are available."""
        try:
            from amos_superbrain_equation_bridge import Domain

            domains = list(Domain)
            self.assertGreaterEqual(len(domains), 33, "Should have 33+ domains")
        except ImportError:
            self.skipTest("SuperBrain not available")

    def test_mathematical_patterns(self):
        """Test mathematical patterns are defined."""
        try:
            from amos_superbrain_equation_bridge import MathematicalPattern

            patterns = list(MathematicalPattern)
            self.assertGreater(len(patterns), 0, "Should have patterns defined")
        except ImportError:
            self.skipTest("SuperBrain not available")


class TestKnowledgeBridge(unittest.TestCase):
    """Test equation knowledge bridge."""

    def test_knowledge_bridge_import(self):
        """Test knowledge bridge can be imported."""
        try:
            from equation_knowledge_bridge import EquationKnowledgeBridge

            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Knowledge bridge import failed: {e}")

    def test_graph_construction(self):
        """Test knowledge graph can be built."""
        try:
            from equation_knowledge_bridge import EquationKnowledgeBridge

            bridge = EquationKnowledgeBridge()
            self.assertIsNotNone(bridge.graph)
        except ImportError:
            self.skipTest("Knowledge bridge not available")

    def test_equation_query(self):
        """Test equation querying."""
        try:
            from equation_knowledge_bridge import EquationKnowledgeBridge

            bridge = EquationKnowledgeBridge()
            equations = bridge.get_equations_by_language("python")
            self.assertIsInstance(equations, list)
        except ImportError:
            self.skipTest("Knowledge bridge not available")


class TestInvariantVerification(unittest.TestCase):
    """Test invariant verification engine."""

    def test_verification_engine_import(self):
        """Test verification engine can be imported."""
        try:
            from invariant_verification_engine import InvariantVerificationEngine

            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Verification engine import failed: {e}")

    def test_code_verification(self):
        """Test code verification works."""
        try:
            from invariant_verification_engine import InvariantVerificationEngine

            engine = InvariantVerificationEngine()
            code = "def f(): pass"
            results = engine.verify_code(code, "python")
            self.assertIsInstance(results, list)
        except ImportError:
            self.skipTest("Verification engine not available")

    def test_mutable_default_detection(self):
        """Test mutable default argument detection."""
        try:
            from invariant_verification_engine import (
                InvariantCategory,
                InvariantVerificationEngine,
            )

            engine = InvariantVerificationEngine()
            code = "def f(items=[]): items.append(1); return items"
            results = engine.verify_code(code, "python")
            memory_results = [r for r in results if r.category == InvariantCategory.MEMORY_SAFETY]
            self.assertTrue(len(memory_results) > 0, "Should detect memory safety issues")
        except ImportError:
            self.skipTest("Verification engine not available")


class TestUnifiedAPI(unittest.TestCase):
    """Test unified equation API."""

    def test_api_import(self):
        """Test unified API can be imported."""
        try:
            from unified_equation_api import UnifiedEquationAPI

            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Unified API import failed: {e}")

    def test_api_initialization(self):
        """Test API initialization."""
        try:
            from unified_equation_api import UnifiedEquationAPI

            api = UnifiedEquationAPI()
            self.assertIsNotNone(api)
        except ImportError:
            self.skipTest("Unified API not available")

    def test_dashboard_data(self):
        """Test dashboard data retrieval."""
        try:
            from unified_equation_api import UnifiedEquationAPI

            api = UnifiedEquationAPI()
            data = api.get_dashboard_data()
            self.assertIn("total_equations", data)
            self.assertIn("sources_active", data)
        except ImportError:
            self.skipTest("Unified API not available")

    def test_code_verification_via_api(self):
        """Test code verification through unified API."""
        try:
            from unified_equation_api import UnifiedEquationAPI

            api = UnifiedEquationAPI()
            code = "def f(): pass"
            result = api.verify_code(code, "python")
            self.assertIn("summary", result)
        except ImportError:
            self.skipTest("Unified API not available")


class TestRemediationEngine(unittest.TestCase):
    """Test automated remediation engine."""

    def test_remediation_import(self):
        """Test remediation engine can be imported."""
        try:
            from automated_remediation_engine import AutomatedRemediationEngine

            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Remediation engine import failed: {e}")

    def test_remediation_initialization(self):
        """Test remediation engine initialization."""
        try:
            from automated_remediation_engine import AutomatedRemediationEngine

            engine = AutomatedRemediationEngine()
            self.assertIsNotNone(engine)
        except ImportError:
            self.skipTest("Remediation engine not available")


class TestIntegrationLayer(unittest.TestCase):
    """Test Master Orchestrator integration."""

    def test_handler_import(self):
        """Test equation handler can be imported."""
        try:
            from equation_integration_handler import EquationIntegrationHandler

            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Handler import failed: {e}")

    def test_handler_process(self):
        """Test handler process cycle."""
        try:
            from equation_integration_handler import EquationIntegrationHandler

            handler = EquationIntegrationHandler()
            handler.initialize()
            result = handler.process({})
            self.assertIsNotNone(result)
        except ImportError:
            self.skipTest("Handler not available")


class TestSelfHealingOrchestrator(unittest.TestCase):
    """Test self-healing orchestrator."""

    def test_orchestrator_import(self):
        """Test orchestrator can be imported."""
        try:
            import AMOS_SELF_HEALING_ORCHESTRATOR

            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Orchestrator import failed: {e}")

    def test_orchestrator_status(self):
        """Test orchestrator status."""
        try:
            from AMOS_SELF_HEALING_ORCHESTRATOR import SelfHealingOrchestrator

            orch = SelfHealingOrchestrator()
            status = orch.get_system_status()
            self.assertIn("health", status)
        except ImportError:
            self.skipTest("Orchestrator not available")


class TestEndToEnd(unittest.TestCase):
    """End-to-end integration tests."""

    def test_full_pipeline(self):
        """Test full equation → verification → remediation pipeline."""
        try:
            from automated_remediation_engine import AutomatedRemediationEngine
            from unified_equation_api import UnifiedEquationAPI

            # Step 1: Initialize systems
            api = UnifiedEquationAPI()
            remediation = AutomatedRemediationEngine()

            # Step 2: Get status
            status = api.get_dashboard_data()
            self.assertEqual(status["health"], "operational")

            # Step 3: Verify problematic code
            bad_code = "def f(items=[]): items.append(1); return items"
            result = api.verify_code(bad_code, "python")
            self.assertIn("summary", result)

            # Step 4: Attempt remediation
            record = remediation.remediate(bad_code, "python", auto_apply=False)
            self.assertIsNotNone(record)

        except ImportError as e:
            self.skipTest(f"Components not available: {e}")


def run_all_tests():
    """Run the complete test suite."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSuperBrainIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledgeBridge))
    suite.addTests(loader.loadTestsFromTestCase(TestInvariantVerification))
    suite.addTests(loader.loadTestsFromTestCase(TestUnifiedAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestRemediationEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestSelfHealingOrchestrator))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEnd))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
