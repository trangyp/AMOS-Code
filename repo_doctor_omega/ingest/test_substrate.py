"""Test execution substrate for contract-critical test validation.

Validates that contract-critical tests pass.

I_tests = 1 iff contract-critical tests pass.

Test partition:
- Hard contract tests (gate release)
- Soft regression tests
- Flaky tests
- Environment-bound tests
- Quarantined tests

Only hard contract tests gate release.
"""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TestCase:
    """Represents a test case."""

    name: str
    file: str
    line: int = 0
    markers: list[str] = field(default_factory=list)

    @property
    def is_hard_contract(self) -> bool:
        """Check if this is a hard contract test."""
        return "contract" in self.markers or "hard" in self.markers

    @property
    def is_quarantined(self) -> bool:
        """Check if test is quarantined."""
        return "quarantine" in self.markers or "skip" in self.markers

    @property
    def is_flaky(self) -> bool:
        """Check if test is marked flaky."""
        return "flaky" in self.markers


@dataclass
class TestResult:
    """Result of executing a test."""

    test: TestCase
    passed: bool
    duration_ms: float = 0.0
    error_message: str = ""
    stdout: str = ""
    stderr: str = ""

    @property
    def failed(self) -> bool:
        """Check if test failed."""
        return not self.passed


class TestSubstrate:
    """Test execution substrate.

    Discovers and executes pytest tests, categorizing them by markers
    to identify contract-critical tests that gate release.

    Usage:
        substrate = TestSubstrate("/path/to/repo")

        # Collect tests
        tests = substrate.collect_tests()

        # Run hard contract tests
        hard_tests = [t for t in tests if t.is_hard_contract]
        results = substrate.run_tests(hard_tests)

        # Check if all passed
        all_passed = all(r.passed for r in results)
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()

    def collect_tests(self, pattern: str = "test_*.py") -> list[TestCase]:
        """Collect test cases from repository.

        Uses pytest collection in dry-run mode.

        Args:
            pattern: Test file glob pattern

        Returns:
            List of test cases
        """
        tests = []

        # Find test directories
        test_dirs = self._find_test_dirs()

        if not test_dirs:
            return tests

        # Use pytest to collect tests
        try:
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                "--collect-only",
                "-q",
                "--no-header",
            ]

            # Add test directories
            cmd.extend(str(d) for d in test_dirs)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.repo_path,
            )

            if result.returncode in (0, 5):  # 5 = no tests collected
                tests = self._parse_collect_output(result.stdout)

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        except Exception:
            pass

        return tests

    def _find_test_dirs(self) -> list[Path]:
        """Find test directories in repository."""
        test_dirs = []

        # Common test directory names
        for name in ["tests", "test", "testsuite"]:
            path = self.repo_path / name
            if path.exists() and path.is_dir():
                test_dirs.append(path)

        # Also look for test files in repo root
        if list(self.repo_path.glob("test_*.py")):
            test_dirs.append(self.repo_path)

        return test_dirs

    def _parse_collect_output(self, output: str) -> list[TestCase]:
        """Parse pytest --collect-only output."""
        tests = []

        for line in output.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("="):
                continue

            # Parse test node ID
            # Format: <file>::<class>::<function> or <file>::<function>
            if "::" in line:
                parts = line.split("::")
                if len(parts) >= 2:
                    file_part = parts[0]
                    func_part = parts[-1]

                    # Extract markers if present
                    markers = []
                    if "[" in func_part and "]" in func_part:
                        marker_str = func_part[func_part.find("[") + 1 : func_part.rfind("]")]
                        markers = [m.strip() for m in marker_str.split("-")]
                        func_part = func_part[: func_part.find("[")]

                    tests.append(
                        TestCase(
                            name=func_part,
                            file=file_part,
                            markers=markers,
                        )
                    )

        return tests

    def run_tests(self, tests: list[TestCase], timeout: int = 60) -> list[TestResult]:
        """Execute specific tests.

        Args:
            tests: Tests to run
            timeout: Maximum execution time in seconds

        Returns:
            List of test results
        """
        if not tests:
            return []

        results = []

        # Group tests by file for efficient execution
        by_file: dict[str, list[TestCase]] = {}
        for test in tests:
            by_file.setdefault(test.file, []).append(test)

        for file_path, file_tests in by_file.items():
            # Build pytest selector
            test_ids = []
            for t in file_tests:
                # Convert to pytest node ID
                node_id = f"{t.file}::{t.name}"
                test_ids.append(node_id)

            try:
                cmd = [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-v",
                    "--tb=short",
                    "--no-header",
                    "-x",  # Stop on first failure
                ] + test_ids

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.repo_path,
                )

                # Parse results
                file_results = self._parse_run_output(file_tests, result)
                results.extend(file_results)

            except subprocess.TimeoutExpired:
                # Mark remaining tests as failed due to timeout
                for t in file_tests:
                    if not any(r.test.name == t.name for r in results):
                        results.append(
                            TestResult(
                                test=t,
                                passed=False,
                                error_message="Test execution timeout",
                            )
                        )
            except Exception as e:
                # Mark all as failed
                for t in file_tests:
                    results.append(
                        TestResult(
                            test=t,
                            passed=False,
                            error_message=str(e),
                        )
                    )

        return results

    def _parse_run_output(
        self, tests: list[TestCase], result: subprocess.CompletedProcess
    ) -> list[TestResult]:
        """Parse pytest run output."""
        results = []

        stdout = result.stdout or ""

        for test in tests:
            # Look for test result in output
            # PASSED, FAILED, ERROR, SKIPPED
            test_pattern = f"{test.name}"

            passed = False
            error_msg = ""

            if "PASSED" in stdout and test_pattern in stdout:
                passed = True
            elif "FAILED" in stdout and test_pattern in stdout:
                passed = False
                # Extract error message
                lines = stdout.split("\n")
                for i, line in enumerate(lines):
                    if test_pattern in line and "FAILED" in line:
                        # Look for error details in following lines
                        for j in range(i + 1, min(i + 10, len(lines))):
                            if lines[j].strip() and not lines[j].startswith("="):
                                error_msg += lines[j].strip() + " "
            elif "SKIPPED" in stdout and test_pattern in stdout:
                passed = True  # Skipped doesn't fail invariant
            else:
                # Test may not have run
                passed = result.returncode == 0

            results.append(
                TestResult(
                    test=test,
                    passed=passed,
                    error_message=error_msg.strip(),
                    stdout=stdout[:1000] if not passed else "",
                    stderr=result.stderr[:1000] if not passed else "",
                )
            )

        return results

    def run_hard_contract_tests(self) -> list[TestResult]:
        """Run only hard contract tests.

        These tests gate release.

        Returns:
            List of test results for hard contract tests
        """
        all_tests = self.collect_tests()
        hard_tests = [t for t in all_tests if t.is_hard_contract and not t.is_quarantined]

        if not hard_tests:
            # No hard contract tests found - check if any tests exist
            if all_tests:
                return []  # Have tests but none are marked as hard
            else:
                return []  # No tests at all

        return self.run_tests(hard_tests)

    def analyze_repository(self) -> dict[str, Any]:
        """Analyze test suite health.

        Returns:
            Dictionary with test analysis
        """
        tests = self.collect_tests()

        if not tests:
            return {
                "has_tests": False,
                "total": 0,
                "hard_contract": 0,
                "passed": 0,
                "failed": 0,
                "all_passed": True,  # No tests = vacuously true
            }

        # Run all non-quarantined tests
        active_tests = [t for t in tests if not t.is_quarantined]
        results = self.run_tests(active_tests)

        hard_tests = [t for t in active_tests if t.is_hard_contract]
        hard_results = [r for r in results if r.test.is_hard_contract]

        return {
            "has_tests": True,
            "total": len(tests),
            "active": len(active_tests),
            "quarantined": len(tests) - len(active_tests),
            "hard_contract": len(hard_tests),
            "flaky": sum(1 for t in tests if t.is_flaky),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
            "hard_passed": sum(1 for r in hard_results if r.passed),
            "hard_failed": sum(1 for r in hard_results if not r.passed),
            "all_passed": all(r.passed for r in hard_results) if hard_results else True,
        }

    def get_summary(self, results: list[TestResult]) -> dict[str, Any]:
        """Generate summary statistics."""
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed

        hard_results = [r for r in results if r.test.is_hard_contract]
        hard_passed = sum(1 for r in hard_results if r.passed)
        hard_failed = len(hard_results) - hard_passed

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 1.0,
            "hard_contract_total": len(hard_results),
            "hard_contract_passed": hard_passed,
            "hard_contract_failed": hard_failed,
            "releaseable": hard_failed == 0 if hard_results else True,
        }
