"""Test suite for repo_doctor package.

Tests the deterministic repository diagnostic system.
Converted to unittest format to avoid pytest plugin conflicts.
"""

import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from repo_doctor import (
    InvariantEngine,
    RepoStateVector,
    SensorResult,
    SensorSuite,
    StateDimension,
)


class TestRepoStateVector(unittest.TestCase):
    """Test the quantum state-space model."""

    def test_initialization(self):
        """Test that state vector initializes correctly."""
        state = RepoStateVector()

        # All dimensions should be 1.0 initially
        for dim in StateDimension:
            self.assertEqual(state.values[dim], 1.0)

    def test_energy_calculation(self):
        """Test energy calculation formula."""
        state = RepoStateVector()

        # Perfect state has 0 energy
        self.assertEqual(state.energy(), 0.0)

        # Degraded state has positive energy
        state.values[StateDimension.SYNTAX] = 0.5
        self.assertGreater(state.energy(), 0.0)

    def test_score_calculation(self):
        """Test repository score calculation."""
        state = RepoStateVector()

        # Perfect state scores 100
        self.assertEqual(state.score(), 100)

        # Failed parse should deduct 20 points
        state.values[StateDimension.SYNTAX] = 0.0
        self.assertEqual(state.score(), 80)

    def test_releaseable_check(self):
        """Test releaseable status."""
        state = RepoStateVector()

        # Perfect state is releaseable
        releaseable, blockers = state.is_releaseable()
        self.assertTrue(releaseable)

        # Failed hard-fail dimension blocks release
        state.values[StateDimension.PACKAGING] = 0.0
        releaseable, blockers = state.is_releaseable()
        self.assertFalse(releaseable)
        self.assertIn(StateDimension.PACKAGING, blockers)


class TestInvariantEngine(unittest.TestCase):
    """Test the hard invariant engine."""

    def test_empty_repo(self):
        """Test scanning empty repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = InvariantEngine(tmpdir)
            state, results = engine.run_all()

            # Empty repo should fail packaging invariant
            packaging_result = next(r for r in results if r.dimension == StateDimension.PACKAGING)
            self.assertFalse(packaging_result.passed)

    def test_valid_repo(self):
        """Test scanning valid repository structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)

            # Create minimal valid structure
            (repo / "pyproject.toml").write_text(
                """
[project]
name = "test-repo"
version = "0.1.0"
"""
            )
            (repo / "test_repo").mkdir()
            (repo / "test_repo" / "__init__.py").write_text("# Test package")

            engine = InvariantEngine(repo)
            state, results = engine.run_all()

            # Should pass packaging with valid pyproject.toml
            packaging_result = next(r for r in results if r.dimension == StateDimension.PACKAGING)
            self.assertTrue(packaging_result.passed)


class TestSensorSuite(unittest.TestCase):
    """Test external tool sensors."""

    def test_sensor_availability(self):
        """Test that sensor suite checks tool availability."""
        with tempfile.TemporaryDirectory() as tmpdir:
            suite = SensorSuite(tmpdir)
            available = suite.get_available_tools()

            # List should contain available tool names
            self.assertIsInstance(available, list)

    def test_sensor_execution(self):
        """Test running all sensors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            suite = SensorSuite(tmpdir)
            results = suite.run_all()

            # Should return results for all sensors
            self.assertEqual(len(results), 4)  # pip-audit, ruff, pyright, deptry

            # Each result should be a SensorResult
            for result in results:
                self.assertIsInstance(result, SensorResult)
                self.assertTrue(hasattr(result, "tool_name"))
                self.assertTrue(hasattr(result, "available"))
                self.assertTrue(hasattr(result, "passed"))


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components."""

    def test_full_scan_workflow(self):
        """Test complete scan workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)

            # Create realistic repo structure
            (repo / "pyproject.toml").write_text(
                """
[project]
name = "integration-test"
version = "0.1.0"
description = "Test repository"

[project.scripts]
cli = "test_pkg:main"
"""
            )
            pkg = repo / "test_pkg"
            pkg.mkdir()
            (pkg / "__init__.py").write_text(
                """
def main():
    return 0
"""
            )

            # Run invariants
            engine = InvariantEngine(repo)
            state, results = engine.run_all()

            # Run sensors
            suite = SensorSuite(repo)
            sensor_results = suite.run_all()

            # Verify workflow completed
            self.assertIsNotNone(_state)
            self.assertGreater(len(results), 0)
            self.assertEqual(len(sensor_results), 4)

            # Valid repo should be releaseable
            releaseable, blockers = state.is_releaseable()
            self.assertTrue(releaseable)


def main():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRepoStateVector))
    suite.addTests(loader.loadTestsFromTestCase(TestInvariantEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestSensorSuite))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
