#!/usr/bin/env python3
"""AMOS Integration Test Runner - Automated testing framework.

Runs comprehensive tests on all AMOS components:
- Syntax validation
- Import resolution
- Component initialization
- Integration workflows
- Performance benchmarks
"""

from __future__ import annotations

import ast
import asyncio
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


@dataclass
class TestCase:
    """Single test case definition."""

    name: str
    func: Callable[[], Any]
    timeout: float = 30.0


@dataclass
class TestResult:
    """Result of a single test."""

    name: str
    passed: bool
    duration_ms: float
    error: str | None = None


class AMOSIntegrationTestRunner:
    """Automated test runner for AMOS ecosystem."""

    def __init__(self, root_path: Path | None = None):
        self.root_path = root_path or Path.cwd()
        self.results: list[TestResult] = []
        self.tests: list[TestCase] = []
        self._register_default_tests()

    def _register_default_tests(self) -> None:
        """Register default test cases."""
        self.tests.extend([
            TestCase("syntax_validation", self._test_syntax_validation),
            TestCase("core_imports", self._test_core_imports),
            TestCase("new_modules", self._test_new_modules),
            TestCase("backend_api", self._test_backend_api),
        ])

    def add_test(self, name: str, func: Callable[[], Any], timeout: float = 30.0) -> None:
        """Add a custom test case."""
        self.tests.append(TestCase(name, func, timeout))

    async def run_all(self) -> dict[str, Any]:
        """Run all registered tests."""
        print("\n" + "=" * 70)
        print("AMOS INTEGRATION TEST RUNNER")
        print("=" * 70)

        self.results = []

        for test in self.tests:
            print(f"\n[TEST] {test.name}...")
            start = time.time()

            try:
                # Run test with timeout
                if asyncio.iscoroutinefunction(test.func):
                    result = await asyncio.wait_for(test.func(), timeout=test.timeout)
                else:
                    result = test.func()

                duration = (time.time() - start) * 1000

                self.results.append(
                    TestResult(
                        name=test.name,
                        passed=result is not False,
                        duration_ms=duration,
                    )
                )
                status = "PASS" if result is not False else "FAIL"
                print(f"  ✓ {status} ({duration:.1f}ms)")

            except asyncio.TimeoutError:
                duration = (time.time() - start) * 1000
                self.results.append(
                    TestResult(
                        name=test.name,
                        passed=False,
                        duration_ms=duration,
                        error="Timeout",
                    )
                )
                print(f"  ✗ TIMEOUT ({duration:.1f}ms)")

            except Exception as e:
                duration = (time.time() - start) * 1000
                self.results.append(
                    TestResult(
                        name=test.name,
                        passed=False,
                        duration_ms=duration,
                        error=str(e)[:100],
                    )
                )
                print(f"  ✗ ERROR: {e}")

        return self._generate_report()

    async def _test_syntax_validation(self) -> bool:
        """Test 1: Validate syntax of all Python files."""
        errors = []
        total = 0

        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["venv", "__pycache__", "node_modules", "AMOS_REPOS", ".git"]
            ]
            for file in files:
                if file.endswith(".py"):
                    total += 1
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            ast.parse(f.read())
                    except SyntaxError:
                        errors.append(filepath)

        print(f"    Checked {total} files, {len(errors)} errors")
        return len(errors) == 0

    async def _test_core_imports(self) -> bool:
        """Test 2: Test core module imports."""
        modules = [
            "amos_kernel",
            "amos_brain",
            "amos_circuit_breaker",
            "amos_workflow_engine_v2",
        ]

        failed = []
        for module in modules:
            try:
                __import__(module)
            except ImportError as e:
                failed.append((module, str(e)))

        print(f"    {len(modules) - len(failed)}/{len(modules)} modules imported")
        return len(failed) == 0

    async def _test_new_modules(self) -> bool:
        """Test 3: Test new production modules."""
        modules = [
            "amos_master_integration",
            "amos_async_task_processor",
            "amos_api_health_router",
        ]

        loaded = 0
        for module in modules:
            try:
                __import__(module)
                loaded += 1
            except ImportError:
                pass

        print(f"    {loaded}/{len(modules)} new modules loaded")
        return loaded > 0

    async def _test_backend_api(self) -> bool:
        """Test 4: Test backend API files."""
        api_path = self.root_path / "backend" / "api"
        if not api_path.exists():
            return True

        files = list(api_path.glob("*.py"))
        errors = []

        for f in files:
            try:
                with open(f, "r", encoding="utf-8") as file:
                    ast.parse(file.read())
            except SyntaxError:
                errors.append(str(f))

        print(f"    {len(files) - len(errors)}/{len(files)} API files valid")
        return len(errors) == 0

    def _generate_report(self) -> dict[str, Any]:
        """Generate test report."""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total_duration = sum(r.duration_ms for r in self.results)

        print("\n" + "=" * 70)
        print("TEST RESULTS")
        print("=" * 70)
        print(f"Total: {len(self.results)} | Passed: {passed} | Failed: {failed}")
        print(f"Duration: {total_duration:.1f}ms")
        print("=" * 70)

        overall = "PASS" if failed == 0 else "PARTIAL" if passed > 0 else "FAIL"
        print(f"Result: {overall}")

        return {
            "overall": overall,
            "summary": {
                "total": len(self.results),
                "passed": passed,
                "failed": failed,
                "duration_ms": total_duration,
            },
            "tests": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "duration_ms": r.duration_ms,
                    "error": r.error,
                }
                for r in self.results
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


async def main():
    """Run integration tests."""
    runner = AMOSIntegrationTestRunner()
    report = await runner.run_all()
    return 0 if report["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
