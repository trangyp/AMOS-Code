#!/usr/bin/env python3
"""
AMOS Equation Knowledge Bridge Test Suite
==========================================

Tests the equation knowledge graph and reasoning engine.
Validates integration with EXHAUSTIVE_EQUATIONS_INVARIANTS_ALL_LANGUAGES.md
"""

import sys
import unittest
from pathlib import Path

# Add 01_BRAIN to path
sys.path.insert(0, str(Path(__file__).parent / "AMOS_ORGANISM_OS" / "01_BRAIN"))

from equation_knowledge_bridge import (
    EquationCategory,
    EquationEntry,
    EquationKnowledgeGraph,
    EquationParser,
    InvariantType,
    LanguageProfile,
    build_equation_knowledge_base,
)


class TestEquationKnowledgeGraph(unittest.TestCase):
    """Test the knowledge graph structure."""

    def setUp(self):
        self.graph = EquationKnowledgeGraph()
        # Add test equations
        self.eq1 = EquationEntry(
            id="",
            name="Type Preservation",
            category=EquationCategory.TYPE_THEORY,
            latex_formula=r"\Gamma \vdash e : T",
            description="Well-typed programs never get stuck",
            language=None,
            invariants=["type_safety"],
            source_section="1.1",
            tags=["fundamental"],
        )
        self.eq2 = EquationEntry(
            id="",
            name="Rust Ownership",
            category=EquationCategory.MEMORY_SAFETY,
            latex_formula=r"(&mut T) \oplus (&T)",
            description="XOR of mutable and immutable references",
            language="rust",
            invariants=["memory_safety"],
            source_section="5.1",
            tags=["rust", "ownership"],
        )

    def test_add_equation(self):
        """Test adding equation to graph."""
        eq_id = self.graph.add_equation(self.eq1)
        self.assertIn(eq_id, self.graph.equations)
        self.assertEqual(self.graph.equations[eq_id].name, "Type Preservation")

    def test_category_index(self):
        """Test category indexing."""
        eq_id = self.graph.add_equation(self.eq1)
        self.assertIn(eq_id, self.graph.category_index[EquationCategory.TYPE_THEORY])

    def test_find_by_category(self):
        """Test finding equations by category."""
        self.graph.add_equation(self.eq1)
        self.graph.add_equation(self.eq2)

        type_eqs = self.graph.find_equations_by_category(EquationCategory.TYPE_THEORY)
        self.assertEqual(len(type_eqs), 1)
        self.assertEqual(type_eqs[0].name, "Type Preservation")

    def test_language_profile(self):
        """Test language profile creation."""
        lang = LanguageProfile(
            name="rust",
            paradigms=["systems", "functional"],
            type_system="affine",
            memory_model="ownership",
            concurrency_model="shared_nothing",
        )
        self.graph.add_language(lang)

        self.assertIn("rust", self.graph.languages)
        self.assertEqual(self.graph.languages["rust"].paradigms, ["systems", "functional"])


class TestEquationParser(unittest.TestCase):
    """Test parsing of exhaustive equation document."""

    def setUp(self):
        self.doc_path = Path(__file__).parent / "EXHAUSTIVE_EQUATIONS_INVARIANTS_ALL_LANGUAGES.md"
        self.parser = EquationParser(self.doc_path)

    def test_document_loaded(self):
        """Test that document is loaded."""
        if self.doc_path.exists():
            self.assertGreater(len(self.parser.content), 1000)
        else:
            self.skipTest("Document not found")

    def test_parse_creates_graph(self):
        """Test parsing creates valid graph."""
        if not self.doc_path.exists():
            self.skipTest("Document not found")

        graph = self.parser.parse()
        self.assertIsInstance(graph, EquationKnowledgeGraph)
        self.assertGreater(len(graph.equations), 0)

    def test_universal_equations_present(self):
        """Test universal equations are extracted."""
        if not self.doc_path.exists():
            self.skipTest("Document not found")

        graph = self.parser.parse()
        universal = [eq for eq in graph.equations.values() if eq.language is None]
        self.assertGreater(len(universal), 0)


class TestKnowledgeGraphSerialization(unittest.TestCase):
    """Test graph serialization and deserialization."""

    def setUp(self):
        self.graph = EquationKnowledgeGraph()
        self.eq = EquationEntry(
            id="",
            name="Test Equation",
            category=EquationCategory.LAMBDA_CALCULUS,
            latex_formula=r"\lambda x.x",
            description="Identity function",
            language=None,
        )
        self.graph.add_equation(self.eq)

        self.test_path = Path("/tmp/test_equation_graph.json")

    def test_to_json(self):
        """Test serialization to JSON."""
        self.graph.to_json(self.test_path)
        self.assertTrue(self.test_path.exists())

    def test_from_json(self):
        """Test deserialization from JSON."""
        self.graph.to_json(self.test_path)
        loaded = EquationKnowledgeGraph.from_json(self.test_path)

        self.assertEqual(len(loaded.equations), len(self.graph.equations))

    def tearDown(self):
        """Clean up test file."""
        if self.test_path.exists():
            self.test_path.unlink()


class TestInvariantTypes(unittest.TestCase):
    """Test invariant type classification."""

    def test_invariant_type_enum(self):
        """Test invariant type enum values."""
        self.assertEqual(InvariantType.TYPE_SAFETY.value, "type_safety")
        self.assertEqual(InvariantType.MEMORY_SAFETY.value, "memory_safety")
        self.assertEqual(InvariantType.CONCURRENCY_SAFETY.value, "concurrency_safety")


class TestBuildKnowledgeBase(unittest.TestCase):
    """Test the full knowledge base builder."""

    def test_build_knowledge_base(self):
        """Test building knowledge base from document."""
        doc_path = Path(__file__).parent / "EXHAUSTIVE_EQUATIONS_INVARIANTS_ALL_LANGUAGES.md"
        output_path = Path("/tmp/test_knowledge_graph.json")

        if not doc_path.exists():
            self.skipTest("Document not found")

        try:
            graph = build_equation_knowledge_base(doc_path, output_path)
            self.assertIsInstance(graph, EquationKnowledgeGraph)
            self.assertTrue(output_path.exists())
        finally:
            if output_path.exists():
                output_path.unlink()


def run_tests():
    """Run all tests with reporting."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestEquationKnowledgeGraph))
    suite.addTests(loader.loadTestsFromTestCase(TestEquationParser))
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledgeGraphSerialization))
    suite.addTests(loader.loadTestsFromTestCase(TestInvariantTypes))
    suite.addTests(loader.loadTestsFromTestCase(TestBuildKnowledgeBase))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print("EQUATION KNOWLEDGE BRIDGE - TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
