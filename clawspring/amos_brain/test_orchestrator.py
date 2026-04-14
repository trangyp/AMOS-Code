#!/usr/bin/env python3
"""AMOS Ecosystem v2.8 - Automated Test Orchestrator.

Unifies all test suites (integration tests, health validator,
demo system) into single orchestrated execution with
consolidated reporting.
"""

import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

sys.path.insert(0, ".")
sys.path.insert(0, "clawspring")
sys.path.insert(0, "clawspring/amos_brain")


@dataclass
class TestSuiteResult:
    """Result from a test suite execution."""

    name: str
    passed: int
    failed: int
    skipped: int
    duration: float
    status: str
    output: str = ""


class TestOrchestrator:
    """Orchestrates all AMOS test suites."""

    def __init__(self):
        self.results: list[TestSuiteResult] = []
        self.start_time = time.time()

    def run_all_tests(self) -> dict[str, Any]:
        """Execute complete test orchestration."""
        print("\n" + "=" * 78)
        print(" " * 18 + "AMOS ECOSYSTEM v2.8")
        print(" " * 16 + "AUTOMATED TEST ORCHESTRATOR")
        print("=" * 78)
        print(f"\nStarted: {datetime.now().isoformat()}")
        print("Suites: 4 | Target: Production Readiness\n")

        # Suite 1: Integration Test Suite
        self._run_suite("Integration Test Suite", self._run_integration_suite)

        # Suite 2: System Health Validator
        self._run_suite("System Health Check", self._run_health_validator)

        # Suite 3: Complete System Demo
        self._run_suite("End-to-End Demo", self._run_complete_demo)

        # Suite 4: Module Import Check
        self._run_suite("Module Import Validation", self._run_import_checks)

        return self._generate_final_report()

    def _run_suite(self, name: str, test_fn) -> None:
        """Run a single test suite with timing."""
        print(f"\n{'─' * 78}")
        print(f"SUITE: {name}")
        print(f"{'─' * 78}")

        start = time.time()
        try:
            passed, failed, output = test_fn()
            duration = time.time() - start

            status = "PASS" if failed == 0 else "FAIL"
            self.results.append(
                TestSuiteResult(
                    name=name,
                    passed=passed,
                    failed=failed,
                    skipped=0,
                    duration=duration,
                    status=status,
                    output=output,
                )
            )

            print(f"  Status: {status}")
            print(f"  Passed: {passed}")
            print(f"  Failed: {failed}")
            print(f"  Duration: {duration:.2f}s")

        except Exception as e:
            duration = time.time() - start
            self.results.append(
                TestSuiteResult(
                    name=name,
                    passed=0,
                    failed=1,
                    skipped=0,
                    duration=duration,
                    status="ERROR",
                    output=str(e),
                )
            )
            print(f"  Status: ERROR - {str(e)[:60]}")

    def _run_integration_suite(self) -> tuple:
        """Run the 20-test integration suite."""
        try:
            from test_integration_suite import IntegrationTestSuite

            suite = IntegrationTestSuite()
            result = suite.run_all_tests()

            passed = result.get("passed", 0)
            failed = result.get("failed", 0)

            return passed, failed, f"Tests: {passed + failed}"
        except Exception as e:
            return 0, 1, str(e)

    def _run_health_validator(self) -> tuple:
        """Run system health validation."""
        try:
            from system_health_validator import SystemHealthValidator

            validator = SystemHealthValidator()
            result = validator.run_full_validation()

            healthy = result.get("healthy", 0)
            unhealthy = result.get("unhealthy", 0)
            degraded = result.get("degraded", 0)

            return healthy, unhealthy + degraded, f"Components: {healthy + unhealthy + degraded}"
        except Exception as e:
            return 0, 1, str(e)

    def _run_complete_demo(self) -> tuple:
        """Run the 7-phase complete demo."""
        try:
            from demo_complete_system import CompleteSystemDemo

            demo = CompleteSystemDemo()
            result = demo.run_full_demo()

            phases_complete = result.get("phases_complete", 0)
            total_phases = result.get("total_phases", 7)
            failed = total_phases - phases_complete

            return phases_complete, failed, f"Phases: {phases_complete}/{total_phases}"
        except Exception as e:
            return 0, 7, str(e)

    def _run_import_checks(self) -> tuple:
        """Validate all 31 modules can be imported."""
        modules = [
            "amos_cognitive_router",
            "engine_executor",
            "multi_agent_orchestrator",
            "cognitive_audit",
            "feedback_loop",
            "audit_exporter",
            "organism_bridge",
            "predictive_integration",
            "task_execution_integration",
            "master_orchestrator",
            "system_validator",
            "system_status",
            "deploy_amos",
            "benchmark",
            "lifecycle_manager",
            "plugin_system",
            "telemetry",
            "api_gateway",
            "workflow_integration",
            "ethics_integration",
            "unified_cli",
            "deep_integration",
            "resilience",
            "config_manager",
            "test_integration_suite",
            "demo_complete_system",
            "system_health_validator",
            "test_orchestrator",
        ]

        passed = 0
        failed = 0
        errors = []

        for module in modules:
            try:
                __import__(module)
                passed += 1
            except Exception as e:
                failed += 1
                errors.append(f"{module}: {str(e)[:30]}")

        return passed, failed, f"Modules: {passed}/{passed + failed}"

    def _generate_final_report(self) -> dict[str, Any]:
        """Generate final orchestrated test report."""
        duration = time.time() - self.start_time

        total_passed = sum(r.passed for r in self.results)
        total_failed = sum(r.failed for r in self.results)
        total_tests = total_passed + total_failed

        all_pass = all(r.status == "PASS" for r in self.results)
        any_fail = any(r.status == "FAIL" for r in self.results)

        if all_pass:
            overall_status = "PRODUCTION READY"
            emoji = "🎉"
        elif any_fail:
            overall_status = "REVIEW REQUIRED"
            emoji = "⚠️"
        else:
            overall_status = "PARTIAL"
            emoji = "⚡"

        print("\n" + "=" * 78)
        print("ORCHESTRATED TEST REPORT")
        print("=" * 78)

        print("\nExecution Summary:")
        print(f"  Total Suites: {len(self.results)}")
        print(f"  Total Passed: {total_passed}")
        print(f"  Total Failed: {total_failed}")
        print(f"  Duration: {duration:.2f}s")

        print("\nSuite Results:")
        for result in self.results:
            icon = "✓" if result.status == "PASS" else "✗"
            print(f"  {icon} {result.name:.<35} {result.status} ({result.duration:.1f}s)")

        print(f"\nOverall Status: {overall_status}")

        if all_pass:
            print(f"\n{emoji} ALL SYSTEMS OPERATIONAL")
            print(f"{emoji} PRODUCTION DEPLOYMENT APPROVED")
        else:
            print(f"\n{emoji} Issues detected - review required before deployment")

        print("=" * 78)

        return {
            "timestamp": datetime.now().isoformat(),
            "total_suites": len(self.results),
            "total_passed": total_passed,
            "total_failed": total_failed,
            "duration": duration,
            "status": overall_status,
            "production_ready": all_pass,
            "suite_results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "passed": r.passed,
                    "failed": r.failed,
                    "duration": r.duration,
                }
                for r in self.results
            ],
        }


def main():
    """Run orchestrated test execution."""
    orchestrator = TestOrchestrator()
    result = orchestrator.run_all_tests()

    # Return exit code
    return 0 if result["production_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
