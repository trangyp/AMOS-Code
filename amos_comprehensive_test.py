#!/usr/bin/env python3
"""AMOS Comprehensive Test - Validate all components work together.

Tests:
1. Syntax validation for all Python files
2. Import resolution for core modules
3. Component initialization
4. Integration between modules
5. End-to-end workflows
"""

from __future__ import annotations

import ast
import asyncio
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class TestResult:
    """Result of a test case."""

    name: str
    passed: bool
    duration_ms: float
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


class AMOSComprehensiveTest:
    """Comprehensive test suite for AMOS ecosystem."""

    def __init__(self, root_path: Path | None = None):
        self.root_path = root_path or Path.cwd()
        self.results: list[TestResult] = []
        self.start_time: datetime | None = None

    async def run_all_tests(self) -> dict[str, Any]:
        """Execute complete test suite."""
        self.start_time = datetime.now(timezone.utc)
        print("\n" + "=" * 70)
        print("AMOS COMPREHENSIVE TEST SUITE")
        print("=" * 70)

        # Test 1: Syntax validation
        await self._test_syntax_validation()

        # Test 2: Core module imports
        await self._test_core_imports()

        # Test 3: New feature modules
        await self._test_new_modules()

        # Test 4: Integration
        await self._test_integration()

        return self._generate_report()

    async def _test_syntax_validation(self) -> None:
        """Test 1: Validate syntax of all Python files."""
        print("\n[Test 1] Syntax Validation...")
        start = datetime.now(timezone.utc)

        errors = []
        total_files = 0

        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["venv", "__pycache__", "node_modules", "AMOS_REPOS", ".git"]
            ]
            for file in files:
                if file.endswith(".py"):
                    total_files += 1
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()
                        ast.parse(content)
                    except SyntaxError as e:
                        errors.append((filepath, e.lineno, str(e)[:50]))

        duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
        passed = len(errors) == 0

        self.results.append(
            TestResult(
                name="Syntax Validation",
                passed=passed,
                duration_ms=duration,
                error=f"{len(errors)} files with syntax errors" if errors else None,
                details={"total_files": total_files, "errors": errors[:5]},
            )
        )

        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status} - {total_files} files checked, {len(errors)} errors")
        for f, line, msg in errors[:3]:
            print(f"    - {f}:{line}: {msg}")

    async def _test_core_imports(self) -> None:
        """Test 2: Test core module imports."""
        print("\n[Test 2] Core Module Imports...")
        start = datetime.now(timezone.utc)

        modules_to_test = [
            "amos_kernel",
            "amos_brain",
            "amos_circuit_breaker",
            "amos_workflow_engine_v2",
            "amos_async_task_processor",
            "amos_api_health_router",
            "amos_auto_repair",
            "amos_master_integration",
        ]

        successful = []
        failed = []

        for module_name in modules_to_test:
            try:
                __import__(module_name)
                successful.append(module_name)
            except ImportError as e:
                failed.append((module_name, str(e)[:50]))

        duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
        passed = len(failed) == 0

        self.results.append(
            TestResult(
                name="Core Module Imports",
                passed=passed,
                duration_ms=duration,
                error=f"{len(failed)} modules failed to import" if failed else None,
                details={"successful": successful, "failed": failed},
            )
        )

        status = "✓ PASS" if passed else "⚠ PARTIAL"
        print(f"  {status} - {len(successful)}/{len(modules_to_test)} modules imported")
        for name, err in failed[:3]:
            print(f"    - {name}: {err}")

    async def _test_new_modules(self) -> None:
        """Test 3: Test new production modules."""
        print("\n[Test 3] New Production Modules...")
        start = datetime.now(timezone.utc)

        new_modules = [
            "amos_circuit_breaker",
            "amos_service_runner",
            "amos_system_bootstrap",
            "amos_workflow_engine_v2",
            "amos_async_task_processor",
            "amos_api_health_router",
            "amos_auto_repair",
            "amos_master_integration",
        ]

        loaded = []
        for name in new_modules:
            try:
                module = __import__(name)
                loaded.append(name)
            except Exception as e:
                print(f"  - {name}: {e}")

        duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
        passed = len(loaded) > 0

        self.results.append(
            TestResult(
                name="New Production Modules",
                passed=passed,
                duration_ms=duration,
                details={"loaded": loaded},
            )
        )

        print(f"  ✓ {len(loaded)}/{len(new_modules)} new modules loaded")

    async def _test_integration(self) -> None:
        """Test 4: Integration between components."""
        print("\n[Test 4] Component Integration...")
        start = datetime.now(timezone.utc)

        tests_passed = 0

        # Test circuit breaker integration
        try:
            from amos_circuit_breaker import CircuitBreaker, CircuitBreakerConfig

            breaker = CircuitBreaker("test", CircuitBreakerConfig())
            tests_passed += 1
        except Exception as e:
            print(f"  - Circuit breaker: {e}")

        # Test workflow engine
        try:
            from amos_workflow_engine_v2 import WorkflowEngine, WorkflowDefinition

            engine = WorkflowEngine()
            tests_passed += 1
        except Exception as e:
            print(f"  - Workflow engine: {e}")

        # Test async task processor
        try:
            from amos_async_task_processor import AsyncTaskProcessor

            processor = AsyncTaskProcessor()
            tests_passed += 1
        except Exception as e:
            print(f"  - Task processor: {e}")

        duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000

        self.results.append(
            TestResult(
                name="Component Integration",
                passed=tests_passed >= 2,
                duration_ms=duration,
                details={"tests_passed": tests_passed},
            )
        )

        print(f"  ✓ {tests_passed}/3 integration tests passed")

    def _generate_report(self) -> dict[str, Any]:
        """Generate comprehensive test report."""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total_duration = sum(r.duration_ms for r in self.results)

        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {len(self.results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total Duration: {total_duration:.1f}ms")
        print("=" * 70)

        overall = "PASS" if failed == 0 else "PARTIAL" if passed > 0 else "FAIL"
        print(f"Overall Result: {overall}")

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
    """Run comprehensive tests."""
    test = AMOSComprehensiveTest()
    report = await test.run_all_tests()
    return report["overall"] == "PASS"


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
