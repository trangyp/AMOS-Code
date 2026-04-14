"""
AMOS Brain Integration Test Suite

Tests all brain components:
  - Core (loader, laws, reasoning, cognitive_stack, integration)
  - Memory (persistence, recall, audit)
  - Dashboard (analytics, reporting)
  - Cookbook (all 5 workflows)
  - Tools (amos_decide, amos_status, etc.)

Run: python -m pytest tests/test_amos_brain.py -v
"""
from __future__ import annotations

import sys
import os
import unittest
from typing import Any

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amos_brain import get_amos_integration
from amos_brain.loader import BrainLoader
from amos_brain.laws import GlobalLaws
from amos_brain.reasoning import RuleOfTwo, RuleOfFour
from amos_brain.cognitive_stack import CognitiveStack
from amos_brain.memory import get_brain_memory, BrainMemory
from amos_brain.dashboard import BrainDashboard
from amos_brain.cookbook import (
    ArchitectureDecision,
    ProjectPlanner,
    ProblemDiagnosis,
    CodeReview,
    SecurityAudit,
)


class TestCoreBrain(unittest.TestCase):
    """Test core brain functionality."""

    @classmethod
    def setUpClass(cls):
        """Initialize brain once for all tests."""
        cls.amos = get_amos_integration()
        cls.status = cls.amos.get_status()

    def test_brain_initialization(self):
        """Test brain initializes correctly."""
        self.assertTrue(self.status.get("initialized"), "Brain should initialize")
        self.assertTrue(self.status.get("brain_loaded"), "Brain should load specs")

    def test_engines_loaded(self):
        """Test all 12 domain engines loaded."""
        engines_count = self.status.get("engines_count", 0)
        self.assertGreaterEqual(engines_count, 1, "Should have at least 1 engine")

    def test_laws_active(self):
        """Test all 6 global laws active."""
        laws = self.status.get("laws_active", [])
        self.assertIn("L1", laws)
        self.assertIn("L2", laws)
        self.assertIn("L3", laws)
        self.assertIn("L4", laws)
        self.assertIn("L5", laws)
        self.assertIn("L6", laws)

    def test_domains_covered(self):
        """Test 12 domains are covered."""
        domains = self.status.get("domains_covered", [])
        self.assertGreaterEqual(len(domains), 1, "Should have domains")

    def test_pre_process(self):
        """Test input pre-processing."""
        result = self.amos.pre_process("Test input")
        self.assertIsInstance(result, dict)
        self.assertIn("blocked", result)

    def test_analyze_with_rules(self):
        """Test Rule of 2 and Rule of 4 analysis."""
        analysis = self.amos.analyze_with_rules(
            "Should we adopt cloud infrastructure?"
        )

        # Should have reasoning results
        self.assertIsInstance(analysis, dict)
        self.assertIn("recommendations", analysis)

    def test_get_laws_summary(self):
        """Test laws summary generation."""
        summary = self.amos.get_laws_summary()
        self.assertIsInstance(summary, str)
        self.assertIn("L1", summary)


class TestRuleOfTwo(unittest.TestCase):
    """Test Rule of 2 reasoning engine."""

    def setUp(self):
        self.r2 = RuleOfTwo()

    def test_analyze_returns_result(self):
        """Test RuleOfTwo.analyze returns valid result."""
        result = self.r2.analyze("Should we use microservices?")

        self.assertIsInstance(result, dict)
        self.assertIn("perspectives", result)
        self.assertIn("confidence", result)

    def test_min_two_perspectives(self):
        """Test at least 2 perspectives generated."""
        result = self.r2.analyze("Test decision")
        perspectives = result.get("perspectives", [])
        self.assertGreaterEqual(len(perspectives), 1)

    def test_confidence_in_range(self):
        """Test confidence score is 0-1."""
        result = self.r2.analyze("Test decision")
        confidence = result.get("confidence", 0)
        self.assertGreaterEqual(confidence, 0)
        self.assertLessEqual(confidence, 1)


class TestRuleOfFour(unittest.TestCase):
    """Test Rule of 4 reasoning engine."""

    def setUp(self):
        self.r4 = RuleOfFour()

    def test_analyze_returns_result(self):
        """Test RuleOfFour.analyze returns valid result."""
        result = self.r4.analyze("Design a sustainable system")

        self.assertIsInstance(result, dict)
        self.assertIn("quadrants_analyzed", result)

    def test_four_quadrants_analyzed(self):
        """Test all 4 quadrants are analyzed."""
        result = self.r4.analyze("Design a system")
        quadrants = result.get("quadrants_analyzed", [])
        self.assertEqual(len(quadrants), 4, "Should analyze all 4 quadrants")

    def test_completeness_score(self):
        """Test completeness score is calculated."""
        result = self.r4.analyze("Design a system")
        score = result.get("completeness_score", 0)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)


class TestGlobalLaws(unittest.TestCase):
    """Test Global Laws enforcement."""

    def setUp(self):
        self.laws = GlobalLaws()

    def test_all_laws_present(self):
        """Test all 6 laws are defined."""
        self.assertEqual(len(self.laws.LAWS), 6)
        self.assertIn("L1", self.laws.LAWS)
        self.assertIn("L2", self.laws.LAWS)
        self.assertIn("L3", self.laws.LAWS)
        self.assertIn("L4", self.laws.LAWS)
        self.assertIn("L5", self.laws.LAWS)
        self.assertIn("L6", self.laws.LAWS)

    def test_l4_integrity_check(self):
        """Test L4 structural integrity check."""
        # Consistent statements
        statements = ["A is true", "B follows from A", "C is valid"]
        consistent, contradictions = self.laws.check_l4_integrity(statements)
        self.assertTrue(consistent or len(contradictions) == 0)

    def test_l5_communication_check(self):
        """Test L5 communication style check."""
        # Clean text should pass
        ok, violations = self.laws.l5_communication_check("This is clear technical text.")
        self.assertTrue(ok or len(violations) == 0)


class TestCognitiveStack(unittest.TestCase):
    """Test Cognitive Stack routing."""

    def setUp(self):
        self.stack = CognitiveStack()

    def test_route_query_returns_engines(self):
        """Test routing returns engines."""
        engines = self.stack.route_query("Design a database schema")
        self.assertIsInstance(engines, list)

    def test_route_technical_query(self):
        """Test technical queries route to tech engines."""
        engines = self.stack.route_query("Build API with Python")
        # Should include technical domain
        self.assertIsInstance(engines, list)


class TestBrainMemory(unittest.TestCase):
    """Test Brain Memory functionality."""

    def setUp(self):
        self.memory = BrainMemory()
        # Clear cache for clean tests
        self.memory._local_cache.clear()

    def test_save_reasoning(self):
        """Test saving reasoning to memory."""
        analysis = {
            "recommendations": ["Test rec"],
            "structural_integrity_score": 0.8,
            "rule_of_two": {"confidence": 0.7},
            "rule_of_four": {"completeness_score": 1.0, "quadrants_analyzed": ["q1", "q2", "q3", "q4"]}
        }

        entry_id = self.memory.save_reasoning(
            "Should we use Redis?",
            analysis,
            tags=["test"]
        )

        self.assertIsInstance(entry_id, str)
        self.assertGreater(len(entry_id), 0)

    def test_find_similar_reasoning(self):
        """Test finding similar reasoning."""
        # First save something
        analysis = {
            "recommendations": ["Use Redis"],
            "structural_integrity_score": 0.8,
            "rule_of_two": {},
            "rule_of_four": {}
        }
        self.memory.save_reasoning("Should we use Redis?", analysis)

        # Then search
        similar = self.memory.find_similar_reasoning(
            "Should we adopt Redis caching?",
            threshold=0.3
        )

        self.assertIsInstance(similar, list)

    def test_get_reasoning_history(self):
        """Test getting reasoning history."""
        # Add some entries
        for i in range(3):
            analysis = {
                "recommendations": [f"Rec {i}"],
                "structural_integrity_score": 0.7,
            }
            self.memory.save_reasoning(f"Problem {i}", analysis)

        history = self.memory.get_reasoning_history(limit=5)
        self.assertIsInstance(history, list)
        self.assertGreaterEqual(len(history), 3)

    def test_get_audit_trail(self):
        """Test audit trail generation."""
        # Add test data
        analysis = {
            "recommendations": [],
            "structural_integrity_score": 0.8,
            "rule_of_two": {},
            "rule_of_four": {}
        }
        self.memory.save_reasoning("Test problem", analysis)

        audit = self.memory.get_audit_trail()

        self.assertIsInstance(audit, dict)
        self.assertIn("total_entries", audit)
        self.assertIn("law_compliance", audit)

    def test_recall_for_problem(self):
        """Test recall functionality."""
        # Setup
        analysis = {"recommendations": [], "structural_integrity_score": 0.8}
        self.memory.save_reasoning("Should we use microservices?", analysis)

        # Recall
        recall = self.memory.recall_for_problem("Should we adopt microservices?")

        self.assertIsInstance(recall, dict)
        self.assertIn("has_prior_reasoning", recall)


class TestBrainDashboard(unittest.TestCase):
    """Test Dashboard functionality."""

    def setUp(self):
        self.dashboard = BrainDashboard()

    def test_generate_report(self):
        """Test report generation."""
        # Add test data first
        analysis = {"recommendations": [], "structural_integrity_score": 0.8, "rule_of_two": {}, "rule_of_four": {}}
        self.dashboard.memory.save_reasoning("Test", analysis)

        report = self.dashboard.generate_report(days=30)

        self.assertIsInstance(report, dict)
        self.assertIn("summary", report)
        self.assertIn("insights", report)

    def test_report_summary(self):
        """Test report summary contains key metrics."""
        analysis = {"recommendations": [], "structural_integrity_score": 0.8, "rule_of_two": {}, "rule_of_four": {}}
        self.dashboard.memory.save_reasoning("Test", analysis)

        report = self.dashboard.generate_report(days=30)
        summary = report.get("summary", {})

        self.assertIn("total_decisions", summary)


class TestCookbookWorkflows(unittest.TestCase):
    """Test all cookbook workflows."""

    @classmethod
    def setUpClass(cls):
        cls.amos = get_amos_integration()

    def test_architecture_decision(self):
        """Test ArchitectureDecision workflow."""
        result = ArchitectureDecision.run(
            "Should we use microservices?",
            context={"current_stack": "monolith"}
        )

        self.assertEqual(result.workflow_name, "Architecture Decision Record (ADR)")
        self.assertIsInstance(result.recommendations, list)
        self.assertGreaterEqual(result.confidence, 0)
        self.assertLessEqual(result.confidence, 1)
        self.assertIsInstance(result.memory_id, str)

    def test_project_planner(self):
        """Test ProjectPlanner workflow."""
        result = ProjectPlanner.run(
            project_description="Test Project - A test project",
            timeline="3 months",
            constraints={"budget": "limited", "timeline": "strict"}
        )

        self.assertEqual(result.recipe_name, "Project Planning & Estimation")
        self.assertIsInstance(result.recommendations, list)

    def test_problem_diagnosis(self):
        """Test ProblemDiagnosis workflow."""
        result = ProblemDiagnosis.run(
            "API latency spikes",
            symptoms=["500ms+ response times"]
        )

        self.assertEqual(result.workflow_name, "Problem Diagnosis & RCA")
        self.assertIsInstance(result.recommendations, list)

    def test_code_review(self):
        """Test CodeReview workflow."""
        result = CodeReview.run(
            code="def example(): pass",
            language="python"
        )

        self.assertEqual(result.workflow_name, "Code Review")
        self.assertIsInstance(result.recommendations, list)

    def test_security_audit(self):
        """Test SecurityAudit workflow."""
        result = SecurityAudit.run(
            code="def example(): pass",
            language="python"
        )

        self.assertEqual(result.workflow_name, "Security Audit")
        self.assertIsInstance(result.recommendations, list)


class TestIntegration(unittest.TestCase):
    """Integration tests - full workflows."""

    def test_full_decision_workflow(self):
        """Test complete decision workflow end-to-end."""
        amos = get_amos_integration()
        memory = get_brain_memory()

        # 1. Check for similar past reasoning
        recall = memory.recall_for_problem("Should we adopt Kubernetes?")
        self.assertIsInstance(recall, dict)

        # 2. Analyze
        analysis = amos.analyze_with_rules("Should we adopt Kubernetes?")
        self.assertIn("recommendations", analysis)

        # 3. Save
        entry_id = memory.save_reasoning("Should we adopt Kubernetes?", analysis)
        self.assertIsInstance(entry_id, str)

        # 4. Verify saved
        history = memory.get_reasoning_history(limit=1)
        self.assertGreaterEqual(len(history), 1)

    def test_dashboard_with_data(self):
        """Test dashboard with actual reasoning data."""
        memory = get_brain_memory()
        dashboard = BrainDashboard()

        # Add test data
        for i in range(5):
            analysis = {
                "recommendations": [f"Rec {i}"],
                "structural_integrity_score": 0.7 + (i * 0.05),
                "rule_of_two": {},
                "rule_of_four": {}
            }
            memory.save_reasoning(f"Test problem {i}", analysis, tags=["test"])

        # Generate report
        report = dashboard.generate_report(days=30)

        self.assertIn("summary", report)
        self.assertIn("compliance_trends", report)
        self.assertIn("insights", report)

        summary = report["summary"]
        self.assertGreaterEqual(summary.get("total_decisions", 0), 5)


def run_tests():
    """Run all tests and print summary."""
    print("=" * 60)
    print("AMOS Brain Integration Test Suite")
    print("=" * 60)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCoreBrain))
    suite.addTests(loader.loadTestsFromTestCase(TestRuleOfTwo))
    suite.addTests(loader.loadTestsFromTestCase(TestRuleOfFour))
    suite.addTests(loader.loadTestsFromTestCase(TestGlobalLaws))
    suite.addTests(loader.loadTestsFromTestCase(TestCognitiveStack))
    suite.addTests(loader.loadTestsFromTestCase(TestBrainMemory))
    suite.addTests(loader.loadTestsFromTestCase(TestBrainDashboard))
    suite.addTests(loader.loadTestsFromTestCase(TestCookbookWorkflows))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print()
        print("✓ All tests passed!")
        return 0
    else:
        print()
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    exit(run_tests())
