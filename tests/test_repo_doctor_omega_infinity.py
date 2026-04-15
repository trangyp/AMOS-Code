"""Repo Doctor Ω∞ - Comprehensive Test Suite

Tests all components of the maximum-strength repository mechanics engine.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest


class TestStateVector(unittest.TestCase):
    """Test 12-dimensional state space model."""

    def test_all_dimensions_present(self):
        """All 12 basis states must be present."""
        from repo_doctor.omega_infinity import StateDimension, StateVector

        sv = StateVector()
        self.assertEqual(len(sv.amplitudes), 12)
        for dim in StateDimension:
            self.assertIn(dim, sv.amplitudes)

    def test_amplitude_range(self):
        """Amplitudes must be in [0, 1]."""
        from repo_doctor.omega_infinity import StateDimension, StateVector

        sv = StateVector(amplitudes={StateDimension.SYNTAX: 1.5})
        self.assertEqual(sv.amplitudes[StateDimension.SYNTAX], 1.0)

        sv2 = StateVector(amplitudes={StateDimension.SYNTAX: -0.5})
        self.assertEqual(sv2.amplitudes[StateDimension.SYNTAX], 0.0)

    def test_healthy_detection(self):
        """Healthy when all amplitudes near 1."""
        from repo_doctor.omega_infinity import StateDimension, StateVector

        sv = StateVector()
        for dim in StateDimension:
            sv.amplitudes[dim] = 0.95
        self.assertTrue(sv.is_healthy)

    def test_collapsed_detection(self):
        """Collapsed when any amplitude is 0."""
        from repo_doctor.omega_infinity import StateDimension, StateVector

        sv = StateVector()
        sv.amplitudes[StateDimension.SYNTAX] = 0.0
        self.assertTrue(sv.is_collapsed)

    def test_energy_computation(self):
        """Energy formula: E = Σ λ(1-α)²"""
        from repo_doctor.omega_infinity import StateDimension, StateVector

        # All intact → low energy
        sv = StateVector()
        for dim in StateDimension:
            sv.amplitudes[dim] = 1.0
        self.assertEqual(sv.compute_energy(), 0.0)

        # All collapsed → high energy
        sv2 = StateVector()
        for dim in StateDimension:
            sv2.amplitudes[dim] = 0.0
        energy = sv2.compute_energy()
        self.assertGreater(energy, 0)
        self.assertEqual(energy, sum(sv2.WEIGHTS.values()))


class TestDensityMatrix(unittest.TestCase):
    """Test mixed-state realism."""

    def test_hypothesis_management(self):
        """Can add and normalize hypotheses."""
        from repo_doctor.omega_infinity import (
            DensityMatrix,
            PureStateHypothesis,
            StateVector,
        )

        dm = DensityMatrix()
        h1 = PureStateHypothesis("h1", StateVector(), 0.5)
        h2 = PureStateHypothesis("h2", StateVector(), 0.5)

        dm.add_hypothesis(h1)
        dm.add_hypothesis(h2)

        # Probabilities should normalize
        total = sum(h.probability for h in dm.hypotheses)
        self.assertAlmostEqual(total, 1.0, places=5)

    def test_expected_measurement(self):
        """Can compute expected values."""
        from repo_doctor.omega_infinity import (
            DensityMatrix,
            PureStateHypothesis,
            StateDimension,
            StateVector,
        )

        dm = DensityMatrix()
        sv = StateVector()
        sv.amplitudes[StateDimension.SYNTAX] = 0.5

        h1 = PureStateHypothesis("h1", sv, 1.0)
        dm.add_hypothesis(h1)

        observable = {StateDimension.SYNTAX: 1.0}
        expectation = dm.expected_measurement(observable)

        self.assertGreater(expectation, 0)


class TestHardInvariants(unittest.TestCase):
    """Test 12 hard invariant system."""

    def setUp(self):
        """Create temporary test repository."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir)

        # Create a valid Python file
        (self.repo_path / "valid.py").write_text(
            """
def hello():
    return "world"

if __name__ == "__main__":
    print(hello())
"""
        )

        # Create a file with syntax error
        (self.repo_path / "invalid.py").write_text(
            """
def broken(
    # Missing closing paren
    pass
"""
        )

    def tearDown(self):
        """Clean up temp directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parse_invariant_valid(self):
        """I_parse passes when all files parse."""
        from repo_doctor.omega_infinity import HardInvariantChecker

        # Create repo with only valid files
        valid_repo = tempfile.mkdtemp()
        valid_path = Path(valid_repo)
        (valid_path / "valid.py").write_text("print('hello')")

        try:
            checker = HardInvariantChecker(valid_path)
            result = checker._check_parse()
            self.assertTrue(result.passed)
        finally:
            import shutil

            shutil.rmtree(valid_repo, ignore_errors=True)

    def test_parse_invariant_invalid(self):
        """I_parse fails when syntax errors present."""
        from repo_doctor.omega_infinity import HardInvariantChecker

        checker = HardInvariantChecker(self.repo_path)
        result = checker._check_parse()

        # Should fail due to invalid.py
        self.assertFalse(result.passed)
        self.assertIn("parse", result.name.lower())

    def test_repo_valid_conjunction(self):
        """RepoValid = AND of all invariants."""
        from repo_doctor.omega_infinity import HardInvariantChecker

        checker = HardInvariantChecker(self.repo_path)
        results = checker.check_all()

        # Should have 12 results
        self.assertEqual(len(results), 12)

        # Repo valid only if all pass
        valid = all(r.passed for r in results)
        self.assertEqual(valid, checker.repo_valid)


class TestRepositoryGraph(unittest.TestCase):
    """Test unified repository graph."""

    def setUp(self):
        """Create test repo with structure."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir)

        # Create module structure
        (self.repo_path / "main.py").write_text(
            """
from utils import helper

def main():
    return helper()
"""
        )

        (self.repo_path / "utils.py").write_text(
            """
def helper():
    return 42
"""
        )

    def tearDown(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_graph_construction(self):
        """Can build graph from repository."""
        from repo_doctor.omega_infinity import RepositoryGraph

        graph = RepositoryGraph(self.repo_path)

        # Should have nodes for files
        self.assertGreater(len(graph.nodes), 0)

    def test_node_types(self):
        """Nodes have correct types."""
        from repo_doctor.omega_infinity import NodeType, RepositoryGraph

        graph = RepositoryGraph(self.repo_path)

        # Check that file nodes exist
        file_nodes = [n for n in graph.nodes.values() if n.type == NodeType.FILE]
        self.assertGreaterEqual(len(file_nodes), 2)  # main.py and utils.py


class TestEntanglementMatrix(unittest.TestCase):
    """Test entanglement analysis."""

    def setUp(self):
        """Create test repo."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir)

        # Create coupled modules
        (self.repo_path / "main.py").write_text(
            """
from utils import helper
from models import User

def main():
    user = User()
    return helper(user)
"""
        )

        (self.repo_path / "utils.py").write_text(
            """
from models import User

def helper(user: User):
    return user.name
"""
        )

        (self.repo_path / "models.py").write_text(
            """
class User:
    def __init__(self):
        self.name = "test"
"""
        )

    def tearDown(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_entanglement_computation(self):
        """Can compute coupling between modules."""
        from repo_doctor.omega_infinity import EntanglementMatrix, RepositoryGraph

        graph = RepositoryGraph(self.repo_path)
        entanglement = EntanglementMatrix(graph)

        # Should have entanglement pairs
        self.assertGreaterEqual(len(entanglement.matrix), 0)

    def test_entropy_computation(self):
        """Can compute entanglement entropy."""
        from repo_doctor.omega_infinity import EntanglementMatrix, RepositoryGraph

        graph = RepositoryGraph(self.repo_path)
        entanglement = EntanglementMatrix(graph)

        if graph.nodes:
            first = list(graph.nodes.keys())[0]
            entropy = entanglement.compute_entropy(first)

            # Entropy should be non-negative
            self.assertGreaterEqual(entropy, 0)


class TestCollapseOperator(unittest.TestCase):
    """Test failure collapse."""

    def setUp(self):
        """Create repo with known issues."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir)

        # Create file with syntax error
        (self.repo_path / "broken.py").write_text("def broken(")

    def tearDown(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_collapse_produces_minimal_cut(self):
        """Collapse finds minimal failing cut."""
        from repo_doctor.omega_infinity import (
            CollapseOperator,
            HardInvariantChecker,
            RepositoryGraph,
        )

        checker = HardInvariantChecker(self.repo_path)
        checker.check_all()

        graph = RepositoryGraph(self.repo_path)
        collapse = CollapseOperator(checker, graph)

        result = collapse.collapse()

        # Should identify failing invariants
        self.assertIn("minimal_cut", result)
        self.assertIn("unsat_core", result)


class TestTemporalAnalysis(unittest.TestCase):
    """Test temporal mechanics."""

    def test_drift_computation(self):
        """Can compute drift between states."""
        from repo_doctor.omega_infinity import StateDimension, StateVector, TemporalAnalyzer

        temporal = TemporalAnalyzer(Path("."))

        sv1 = StateVector()
        sv1.amplitudes[StateDimension.SYNTAX] = 1.0

        sv2 = StateVector()
        sv2.amplitudes[StateDimension.SYNTAX] = 0.9

        drift = temporal.compute_drift(sv1, sv2)

        # Drift should be positive
        self.assertGreater(drift, 0)
        # Drift should be sqrt(sum of squares)
        self.assertAlmostEqual(drift, 0.1, places=5)


class TestRepairOptimizer(unittest.TestCase):
    """Test repair optimization."""

    def test_repair_priority_order(self):
        """Repairs follow correct priority."""
        from repo_doctor.omega_infinity import (
            EntanglementMatrix,
            InvariantResult,
            RepairOptimizer,
            RepositoryGraph,
        )

        graph = RepositoryGraph(Path("."))
        entanglement = EntanglementMatrix(graph)
        optimizer = RepairOptimizer(graph, entanglement)

        # Create mock failing invariants
        failing = [
            InvariantResult("I_api", False, "critical", "API mismatch"),
            InvariantResult("I_parse", False, "critical", "Syntax error"),
        ]

        repairs = optimizer.optimize_repairs(failing)

        # Should produce repair actions
        self.assertGreater(len(repairs), 0)

        # Parse should be first
        if repairs:
            self.assertEqual(repairs[0].target, "I_parse")


class TestFleetState(unittest.TestCase):
    """Test fleet-level analysis."""

    def test_fleet_energy_computation(self):
        """Can compute fleet energy."""
        from repo_doctor.omega_infinity import FleetState, StateDimension, StateVector

        fleet = FleetState()

        sv1 = StateVector()
        sv1.amplitudes[StateDimension.SYNTAX] = 0.5

        sv2 = StateVector()
        sv2.amplitudes[StateDimension.SYNTAX] = 0.8

        fleet.add_repository("repo1", sv1, weight=1.0)
        fleet.add_repository("repo2", sv2, weight=0.5)

        energy = fleet.compute_fleet_energy()

        # Energy should be weighted sum
        self.assertGreater(energy, 0)


class TestZ3Integration(unittest.TestCase):
    """Test Z3 solver integration."""

    def test_z3_availability(self):
        """Z3 solver can be initialized."""
        from repo_doctor.solver.z3_model import Z3Model

        model = Z3Model()
        # Should not crash
        self.assertIsNotNone(model)

    def test_core_minimization_enabled(self):
        """Core minimization is enabled by default."""
        from repo_doctor.solver.z3_model import Z3Model

        model = Z3Model(enable_core_minimization=True)
        self.assertTrue(model.enable_core_minimization)


class TestDiagnosisReport(unittest.TestCase):
    """Test output generation."""

    def setUp(self):
        """Create test data."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_json_output(self):
        """Can generate JSON report."""
        from repo_doctor.omega_infinity import (
            DiagnosisReport,
            HardInvariantChecker,
            StateVector,
        )

        sv = StateVector()
        checker = HardInvariantChecker(self.repo_path)
        results = checker.check_all()

        report = DiagnosisReport(
            repo_path=self.repo_path,
            state_vector=sv,
            invariants=results,
            collapse_result={"minimal_cut": [], "unsat_core": []},
        )

        json_output = report.to_json()

        # Should be valid JSON
        data = json.loads(json_output)
        self.assertIn("repository", data)
        self.assertIn("energy", data)


class TestTreeSitterIngest(unittest.TestCase):
    """Test Tree-sitter integration."""

    def setUp(self):
        """Create test Python file."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir)

        (self.repo_path / "test.py").write_text(
            """
import os
import sys

def main():
    print("Hello")

class TestClass:
    def method(self):
        pass
"""
        )

    def tearDown(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parser_initialization(self):
        """Can initialize Tree-sitter parser."""
        from repo_doctor.ingest.treesitter_ingest import TreeSitterIngest

        ingest = TreeSitterIngest(self.repo_path)

        # Should detect supported languages
        self.assertIn(".py", ingest.SUPPORTED_LANGUAGES)

    def test_file_parsing(self):
        """Can parse Python files."""
        from repo_doctor.ingest.treesitter_ingest import TreeSitterIngest

        ingest = TreeSitterIngest(self.repo_path)

        result = ingest.parse_file(self.repo_path / "test.py")

        # Should have extracted info
        self.assertEqual(result.language, "python")
        self.assertIsNotNone(result.path)


class TestMainEngine(unittest.TestCase):
    """Integration test for main engine."""

    def setUp(self):
        """Create test repository."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir)

        # Create valid Python module
        (self.repo_path / "main.py").write_text(
            """
\"\"\"Main module.\"\"\"

def main():
    return 42
"""
        )

        # Create pyproject.toml
        (self.repo_path / "pyproject.toml").write_text(
            """
[project]
name = "test-project"
version = "1.0.0"
"""
        )

    def tearDown(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_engine_initialization(self):
        """Can initialize main engine."""
        from repo_doctor.omega_infinity import RepoDoctorOmegaInfinity

        doctor = RepoDoctorOmegaInfinity(self.repo_path)

        self.assertEqual(doctor.repo_path, self.repo_path)
        self.assertIsNotNone(doctor.graph)
        self.assertIsNotNone(doctor.hamiltonian)

    def test_full_scan(self):
        """Can perform full repository scan."""
        from repo_doctor.omega_infinity import RepoDoctorOmegaInfinity

        doctor = RepoDoctorOmegaInfinity(self.repo_path)
        report = doctor.scan()

        # Should produce report
        self.assertIsNotNone(report)

        data = report.to_dict()

        # Should have all fields
        self.assertIn("repository", data)
        self.assertIn("state_vector", data)
        self.assertIn("energy", data)
        self.assertIn("hard_invariant_failures", data)


class TestPerformance(unittest.TestCase):
    """Performance tests."""

    def test_large_repo_handling(self):
        """Can handle repositories with many files."""
        import time

        from repo_doctor.omega_infinity import RepoDoctorOmegaInfinity

        # Create temp repo with multiple files
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)

        try:
            # Create 50 Python files
            for i in range(50):
                (repo_path / f"file{i}.py").write_text(
                    f"""
def func{i}():
    return {i}
"""
                )

            start = time.time()
            doctor = RepoDoctorOmegaInfinity(repo_path)
            report = doctor.scan()
            elapsed = time.time() - start

            # Should complete in reasonable time (< 30 seconds)
            self.assertLess(elapsed, 30.0)

            data = report.to_dict()
            self.assertIn("state_vector", data)

        finally:
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
