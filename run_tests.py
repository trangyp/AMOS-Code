#!/usr/bin/env python3
"""AMOS Test Runner v1.0.0
=========================

Convenient test runner with multiple execution modes.

Usage:
  python run_tests.py                    # Run all tests
  python run_tests.py --unit             # Run unit tests only
  python run_tests.py --integration      # Run integration tests
  python run_tests.py --law              # Run law compliance tests
  python run_tests.py --security         # Run security tests
  python run_tests.py --coverage         # Run with coverage report
  python run_tests.py --ci               # CI mode (all tests + coverage)

Author: Trang Phan
Version: 1.0.0
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> int:
    """Run a command and return exit code."""
    print(f"\n{'=' * 70}")
    print(f"Running: {description}")
    print(f"{'=' * 70}")

    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="AMOS Testing Framework Runner")

    parser.add_argument("--unit", "-u", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", "-i", action="store_true", help="Run integration tests")
    parser.add_argument("--law", "-l", action="store_true", help="Run law compliance tests")
    parser.add_argument("--security", "-s", action="store_true", help="Run security tests")
    parser.add_argument("--coverage", "-c", action="store_true", help="Run with coverage report")
    parser.add_argument("--ci", action="store_true", help="CI mode (comprehensive testing)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    print("=" * 70)
    print("AMOS COGNITIVE OPERATING SYSTEM - TEST RUNNER v1.0.0")
    print("=" * 70)

    # Determine test path
    if args.unit:
        test_path = "tests/unit/"
        description = "Unit Tests"
    elif args.integration:
        test_path = "tests/integration/"
        description = "Integration Tests"
    elif args.law:
        test_path = "tests/law/"
        description = "Law Compliance Tests"
    elif args.security:
        test_path = "tests/security/"
        description = "Security Tests"
    elif args.ci:
        test_path = "tests/"
        description = "Full CI Test Suite"
    else:
        test_path = "tests/"
        description = "All Tests"

    # Build pytest command
    cmd = ["python", "-m", "pytest", test_path, "-v"]

    if args.coverage or args.ci:
        cmd.extend(["--cov=.", "--cov-report=term-missing"])

    if args.ci:
        cmd.extend(["--tb=short", "--strict-markers"])

    # Run tests
    exit_code = run_command(cmd, description)

    # Summary
    print(f"\n{'=' * 70}")
    if exit_code == 0:
        print("✓ ALL TESTS PASSED")
    else:
        print(f"✗ TESTS FAILED (exit code: {exit_code})")
    print(f"{'=' * 70}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
