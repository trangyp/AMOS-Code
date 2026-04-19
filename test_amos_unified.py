#!/usr/bin/env python3
"""AMOS Unified Integration Test — Full Stack Validation

Tests the complete AMOS system from axioms to operational runtime:
1. Axiom validation (Ω → implementation compliance)
2. Runtime integration (v1-v5 + production)
3. Coherence Ω integration (human cognition + axioms)
4. End-to-end workflow validation
5. Performance and stress testing

Usage:
    python test_amos_unified.py              # Run all tests
    python test_amos_unified.py --quick      # Run quick tests only
    python test_amos_unified.py --layer axioms  # Test specific layer
    python test_amos_unified.py --report json   # Export JSON report

Exit codes:
    0 = All tests passed
    1 = Some tests failed
    2 = Critical system failure
"""

import argparse
import json
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TestLevel(Enum):
    """Test severity levels."""

    UNIT = "unit"
    INTEGRATION = "integration"
    END_TO_END = "end_to_end"
    STRESS = "stress"


class TestResult(Enum):
    """Test outcome."""

    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


@dataclass
class TestCase:
    """Single test case result."""

    name: str
    level: TestLevel
    result: TestResult
    duration_ms: float
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    traceback: str = None


@dataclass
class TestSuite:
    """Collection of test cases."""

    name: str
    cases: List[TestCase] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for c in self.cases if c.result == TestResult.PASS)

    @property
    def failed(self) -> int:
        return sum(1 for c in self.cases if c.result == TestResult.FAIL)

    @property
    def total(self) -> int:
        return len(self.cases)

    @property
    def duration_ms(self) -> float:
        return sum(c.duration_ms for c in self.cases)


class AMOSUnifiedTest:
    """Unified integration test for complete AMOS stack.

    Test Layers:
    1. Axioms (Ω) — Validate formal specification
    2. Omega Runtime — Test executable axiom implementation
    3. Validator — Test theory→practice bridge
    4. Core v1-v3 — Test cognitive, memory, time, energy
    5. v4 Economic — Test persistence, resource allocation
    6. v5 Civilization — Test strategic layers
    7. Coherence Ω — Test human cognition integration
    8. End-to-End — Test complete workflows
    """

    def __init__(self, verbose: bool = False, quick: bool = False):
        self.verbose = verbose
        self.quick = quick
        self.suites: List[TestSuite] = []
        self.start_time: datetime = None
        self.end_time: datetime = None

    # ========================================================================
    # LAYER 1: AXIOM TESTS (Ω)
    # ========================================================================

    def test_axioms(self) -> TestSuite:
        """Test 32 Ω axioms are well-formed and consistent."""
        suite = TestSuite(name="Omega Axioms")

        try:
            # Test axiom file exists and is parseable
            with open("OMEGA_AXIOMS.md") as f:
                content = f.read()

            suite.cases.append(
                TestCase(
                    name="axiom_file_readable",
                    level=TestLevel.UNIT,
                    result=TestResult.PASS,
                    duration_ms=1.0,
                    message="OMEGA_AXIOMS.md is readable",
                    details={"size_chars": len(content)},
                )
            )

            # Check for key axiom sections
            key_axioms = [
                "Axiom 1: Substrate Partition",
                "Axiom 4: State Stratification",
                "Axiom 10: Commit",
                "Axiom 21: Multi-Regime",
                "Final Governing Equation",
            ]

            for axiom in key_axioms:
                present = axiom in content
                suite.cases.append(
                    TestCase(
                        name=f"axiom_present_{axiom.replace(' ', '_')[:30]}",
                        level=TestLevel.UNIT,
                        result=TestResult.PASS if present else TestResult.FAIL,
                        duration_ms=0.1,
                        message=f"{axiom} {'found' if present else 'MISSING'}",
                    )
                )

        except Exception as e:
            suite.cases.append(
                TestCase(
                    name="axiom_file_access",
                    level=TestLevel.UNIT,
                    result=TestResult.ERROR,
                    duration_ms=0,
                    message=f"Failed to read axioms: {str(e)}",
                    traceback=traceback.format_exc(),
                )
            )

        return suite

    # ========================================================================
    # LAYER 2: OMEGA RUNTIME TESTS
    # ========================================================================

    def test_omega_runtime(self) -> TestSuite:
        """Test executable axiom implementation (amos_omega.py)."""
        suite = TestSuite(name="Omega Runtime")

        try:
            from amos_omega import Action, AMOSOmega, State, Substrate

            # Test initialization
            start = time.time()
            omega = AMOSOmega()
            init_time = (time.time() - start) * 1000

            suite.cases.append(
                TestCase(
                    name="omega_init",
                    level=TestLevel.UNIT,
                    result=TestResult.PASS,
                    duration_ms=init_time,
                    message="AMOSOmega initialized successfully",
                )
            )

            # Test substrate detection (Axiom 1)
            state = State(classical={"x": 1.0}, identity="test")
            substrates = omega.substrate_of(state)

            suite.cases.append(
                TestCase(
                    name="axiom_1_substrate_detection",
                    level=TestLevel.UNIT,
                    result=TestResult.PASS
                    if Substrate.CLASSICAL in substrates
                    else TestResult.FAIL,
                    duration_ms=1.0,
                    message=f"Detected substrates: {[s.name for s in substrates]}",
                )
            )

            # Test state stratification (Axiom 4)
            components = omega.decompose_state(state)
            suite.cases.append(
                TestCase(
                    name="axiom_4_stratification",
                    level=TestLevel.UNIT,
                    result=TestResult.PASS if len(components) > 0 else TestResult.FAIL,
                    duration_ms=1.0,
                    message=f"State decomposed into {len(components)} components",
                )
            )

            # Test runtime step (Axiom 29)
            action = Action(
                name="test_action",
                substrate=Substrate.CLASSICAL,
                effect={"x": 1.0},
                energy_cost=0.1,
            )

            start = time.time()
            new_state = omega.runtime_step(state, action, {})
            step_time = (time.time() - start) * 1000

            suite.cases.append(
                TestCase(
                    name="axiom_29_runtime_step",
                    level=TestLevel.INTEGRATION,
                    result=TestResult.PASS if new_state is not None else TestResult.FAIL,
                    duration_ms=step_time,
                    message="Runtime step executed" if new_state else "Runtime step FAILED",
                )
            )

            # Test ledger recording (Axiom 12)
            ledger = omega.get_ledger()
            suite.cases.append(
                TestCase(
                    name="axiom_12_ledger",
                    level=TestLevel.INTEGRATION,
                    result=TestResult.PASS if len(ledger) > 0 else TestResult.FAIL,
                    duration_ms=1.0,
                    message=f"Ledger has {len(ledger)} entries",
                )
            )

        except ImportError as e:
            suite.cases.append(
                TestCase(
                    name="omega_import",
                    level=TestLevel.UNIT,
                    result=TestResult.ERROR,
                    duration_ms=0,
                    message=f"Failed to import amos_omega: {str(e)}",
                )
            )
        except Exception as e:
            suite.cases.append(
                TestCase(
                    name="omega_runtime_error",
                    level=TestLevel.UNIT,
                    result=TestResult.ERROR,
                    duration_ms=0,
                    message=f"Runtime error: {str(e)}",
                    traceback=traceback.format_exc(),
                )
            )

        return suite

    # ========================================================================
    # LAYER 3: VALIDATOR TESTS
    # ========================================================================

    def test_validator(self) -> TestSuite:
        """Test axiom validator (amos_axiom_validator.py)."""
        suite = TestSuite(name="Axiom Validator")

        try:
            from amos_axiom_validator import AxiomValidator, ValidationLevel
            from amos_omega import State

            validator = AxiomValidator()

            # Test valid state validation
            valid_state = State(
                classical={"value": 1.0, "energy": 100.0}, identity="test_agent", time=0.0
            )

            start = time.time()
            report = validator.validate_state(valid_state)
            val_time = (time.time() - start) * 1000

            suite.cases.append(
                TestCase(
                    name="validator_valid_state",
                    level=TestLevel.INTEGRATION,
                    result=TestResult.PASS if report.is_valid() else TestResult.FAIL,
                    duration_ms=val_time,
                    message=f"Valid state validation: {len(report.checks)} checks",
                )
            )

            # Test invalid state detection
            invalid_state = State()  # Empty state
            report_invalid = validator.validate_state(invalid_state)

            suite.cases.append(
                TestCase(
                    name="validator_invalid_state",
                    level=TestLevel.INTEGRATION,
                    result=TestResult.PASS if not report_invalid.is_valid() else TestResult.FAIL,
                    duration_ms=1.0,
                    message="Invalid state correctly rejected",
                )
            )

            # Test JSON export
            json_str = report.to_json()
            suite.cases.append(
                TestCase(
                    name="validator_json_export",
                    level=TestLevel.UNIT,
                    result=TestResult.PASS if len(json_str) > 0 else TestResult.FAIL,
                    duration_ms=1.0,
                    message=f"JSON export: {len(json_str)} chars",
                )
            )

        except ImportError as e:
            suite.cases.append(
                TestCase(
                    name="validator_import",
                    level=TestLevel.UNIT,
                    result=TestResult.ERROR,
                    duration_ms=0,
                    message=f"Failed to import validator: {str(e)}",
                )
            )
        except Exception as e:
            suite.cases.append(
                TestCase(
                    name="validator_error",
                    level=TestLevel.UNIT,
                    result=TestResult.ERROR,
                    duration_ms=0,
                    message=f"Validator error: {str(e)}",
                    traceback=traceback.format_exc(),
                )
            )

        return suite

    # ========================================================================
    # LAYER 4: COHERENCE Ω TESTS
    # ========================================================================

    def test_coherence_omega(self) -> TestSuite:
        """Test coherence Ω integration."""
        suite = TestSuite(name="Coherence Omega")

        try:
            from amos_coherence_omega import CoherenceOmega

            coh_omega = CoherenceOmega()

            # Test message processing
            start = time.time()
            result = coh_omega.process_message("I'm feeling overwhelmed with work", validate=True)
            proc_time = (time.time() - start) * 1000

            suite.cases.append(
                TestCase(
                    name="coherence_process_message",
                    level=TestLevel.INTEGRATION,
                    result=TestResult.PASS if result.is_valid else TestResult.FAIL,
                    duration_ms=proc_time,
                    message=f"Processing: {result.coherence_result.detected_state.name}",
                )
            )

            # Test Master Law compliance
            suite.cases.append(
                TestCase(
                    name="master_law_compliance",
                    level=TestLevel.INTEGRATION,
                    result=TestResult.PASS if result.master_law_compliant else TestResult.FAIL,
                    duration_ms=1.0,
                    message=f"Master Law: {'COMPLIANT' if result.master_law_compliant else 'VIOLATION'}",
                )
            )

            # Test axiom satisfaction
            for axiom, satisfied in result.axioms_satisfied.items():
                suite.cases.append(
                    TestCase(
                        name=f"coherence_axiom_{axiom}",
                        level=TestLevel.UNIT,
                        result=TestResult.PASS if satisfied else TestResult.FAIL,
                        duration_ms=0.1,
                        message=f"{axiom}: {'✓' if satisfied else '✗'}",
                    )
                )

            # Test compliance stats
            stats = coh_omega.get_compliance_stats()
            suite.cases.append(
                TestCase(
                    name="compliance_stats",
                    level=TestLevel.UNIT,
                    result=TestResult.PASS,
                    duration_ms=1.0,
                    message=f"Stats: {stats['total']} interactions, {stats['rate']:.0%} compliant",
                )
            )

        except ImportError as e:
            suite.cases.append(
                TestCase(
                    name="coherence_import",
                    level=TestLevel.UNIT,
                    result=TestResult.ERROR,
                    duration_ms=0,
                    message=f"Failed to import coherence Ω: {str(e)}",
                )
            )
        except Exception as e:
            suite.cases.append(
                TestCase(
                    name="coherence_error",
                    level=TestLevel.UNIT,
                    result=TestResult.ERROR,
                    duration_ms=0,
                    message=f"Coherence error: {str(e)}",
                    traceback=traceback.format_exc(),
                )
            )

        return suite

    # ========================================================================
    # LAYER 5: CORE v1-v3 TESTS (if available)
    # ========================================================================

    def test_core_systems(self) -> TestSuite:
        """Test core AMOS systems."""
        suite = TestSuite(name="Core Systems")

        systems_to_test = [
            ("amos_core", "Core Cognitive"),
            ("amos_memory", "Memory System"),
            ("amos_time", "Time Engine"),
            ("amos_energy", "Energy System"),
        ]

        for module_name, system_name in systems_to_test:
            try:
                __import__(module_name)
                suite.cases.append(
                    TestCase(
                        name=f"import_{module_name}",
                        level=TestLevel.UNIT,
                        result=TestResult.PASS,
                        duration_ms=1.0,
                        message=f"{system_name} imported successfully",
                    )
                )
            except ImportError:
                suite.cases.append(
                    TestCase(
                        name=f"import_{module_name}",
                        level=TestLevel.UNIT,
                        result=TestResult.SKIP,
                        duration_ms=0,
                        message=f"{system_name} not available (optional)",
                    )
                )

        return suite

    # ========================================================================
    # LAYER 6: END-TO-END WORKFLOW
    # ========================================================================

    def test_end_to_end(self) -> TestSuite:
        """Test complete end-to-end workflow."""
        suite = TestSuite(name="End-to-End Workflow")

        if self.quick:
            suite.cases.append(
                TestCase(
                    name="e2e_skipped",
                    level=TestLevel.END_TO_END,
                    result=TestResult.SKIP,
                    duration_ms=0,
                    message="Skipped in quick mode",
                )
            )
            return suite

        try:
            # Full workflow: Axioms → Omega → Coherence

            from amos_axiom_validator import AxiomValidator
            from amos_coherence_omega import CoherenceOmega
            from amos_omega import Action, AMOSOmega, Substrate

            start = time.time()

            # 1. Initialize all systems
            omega = AMOSOmega()
            coh_omega = CoherenceOmega()
            validator = AxiomValidator()

            init_time = (time.time() - start) * 1000

            # 2. Process human message through coherence
            msg_start = time.time()
            coherence_result = coh_omega.process_message(
                "I need help making a complex decision", validate=True
            )
            msg_time = (time.time() - msg_start) * 1000

            suite.cases.append(
                TestCase(
                    name="e2e_human_message",
                    level=TestLevel.END_TO_END,
                    result=TestResult.PASS if coherence_result.is_valid else TestResult.FAIL,
                    duration_ms=msg_time,
                    message=f"Human→Coherence→Ω: {coherence_result.coherence_result.intervention_mode.name}",
                )
            )

            # 3. Convert to Omega state and run runtime step
            omega_state = coherence_result.omega_state
            action = Action(
                name="coh_decision_support",
                substrate=Substrate.HYBRID,
                effect={"decision_clarity": 0.2},
                energy_cost=0.5,
            )

            runtime_start = time.time()
            new_state = omega.runtime_step(omega_state, action, {})
            runtime_time = (time.time() - runtime_start) * 1000

            suite.cases.append(
                TestCase(
                    name="e2e_runtime_step",
                    level=TestLevel.END_TO_END,
                    result=TestResult.PASS if new_state is not None else TestResult.FAIL,
                    duration_ms=runtime_time,
                    message="Runtime step with coherence-derived state",
                )
            )

            # 4. Validate final state
            val_start = time.time()
            final_report = validator.validate_state(new_state)
            val_time = (time.time() - val_start) * 1000

            suite.cases.append(
                TestCase(
                    name="e2e_final_validation",
                    level=TestLevel.END_TO_END,
                    result=TestResult.PASS if final_report.is_valid() else TestResult.FAIL,
                    duration_ms=val_time,
                    message="Final state validation",
                )
            )

            # 5. Check ledger integrity
            ledger = omega.get_ledger()
            suite.cases.append(
                TestCase(
                    name="e2e_ledger_integrity",
                    level=TestLevel.END_TO_END,
                    result=TestResult.PASS if len(ledger) >= 1 else TestResult.FAIL,
                    duration_ms=1.0,
                    message=f"Ledger contains {len(ledger)} entries",
                )
            )

            total_time = (time.time() - start) * 1000
            suite.cases.append(
                TestCase(
                    name="e2e_total_time",
                    level=TestLevel.END_TO_END,
                    result=TestResult.PASS,
                    duration_ms=total_time,
                    message=f"Total E2E time: {total_time:.1f}ms",
                )
            )

        except Exception as e:
            suite.cases.append(
                TestCase(
                    name="e2e_error",
                    level=TestLevel.END_TO_END,
                    result=TestResult.ERROR,
                    duration_ms=0,
                    message=f"E2E workflow failed: {str(e)}",
                    traceback=traceback.format_exc(),
                )
            )

        return suite

    # ========================================================================
    # RUN ALL TESTS
    # ========================================================================

    def run_all(self) -> List[TestSuite]:
        """Execute complete test suite."""
        self.start_time = datetime.now(timezone.utc)

        print("=" * 70)
        print("AMOS Unified Integration Test")
        print("=" * 70)
        print(f"Mode: {'QUICK' if self.quick else 'FULL'}")
        print(f"Started: {self.start_time.isoformat()}")
        print()

        # Run all test layers
        test_methods = [
            self.test_axioms,
            self.test_omega_runtime,
            self.test_validator,
            self.test_coherence_omega,
            self.test_core_systems,
            self.test_end_to_end,
        ]

        for test_method in test_methods:
            try:
                suite = test_method()
                self.suites.append(suite)

                # Print progress
                status = "✓" if suite.failed == 0 else "✗"
                print(f"{status} {suite.name}: {suite.passed}/{suite.total} passed")

                if self.verbose and suite.failed > 0:
                    for case in suite.cases:
                        if case.result in (TestResult.FAIL, TestResult.ERROR):
                            print(f"    ✗ {case.name}: {case.message}")

            except Exception as e:
                print(f"✗ {test_method.__name__}: CRASH - {str(e)}")
                if self.verbose:
                    traceback.print_exc()

        self.end_time = datetime.now(timezone.utc)

        return self.suites

    def generate_report(self, format: str = "text") -> str:
        """Generate test report."""
        if format == "json":
            report = {
                "timestamp": self.end_time.isoformat() if self.end_time else None,
                "duration_ms": sum(s.duration_ms for s in self.suites),
                "summary": {
                    "total_suites": len(self.suites),
                    "total_cases": sum(s.total for s in self.suites),
                    "total_passed": sum(s.passed for s in self.suites),
                    "total_failed": sum(s.failed for s in self.suites),
                },
                "suites": [
                    {
                        "name": s.name,
                        "passed": s.passed,
                        "failed": s.failed,
                        "total": s.total,
                        "duration_ms": s.duration_ms,
                        "cases": [
                            {
                                "name": c.name,
                                "level": c.level.value,
                                "result": c.result.value,
                                "duration_ms": c.duration_ms,
                                "message": c.message,
                            }
                            for c in s.cases
                        ],
                    }
                    for s in self.suites
                ],
            }
            return json.dumps(report, indent=2)

        # Text format
        lines = []
        lines.append("=" * 70)
        lines.append("AMOS Unified Test Report")
        lines.append("=" * 70)
        lines.append("")

        total_cases = sum(s.total for s in self.suites)
        total_passed = sum(s.passed for s in self.suites)
        total_failed = sum(s.failed for s in self.suites)
        total_time = sum(s.duration_ms for s in self.suites)

        lines.append(f"Total Suites: {len(self.suites)}")
        lines.append(f"Total Cases: {total_cases}")
        lines.append(f"Passed: {total_passed}")
        lines.append(f"Failed: {total_failed}")
        lines.append(
            f"Success Rate: {total_passed / total_cases:.1%}" if total_cases > 0 else "N/A"
        )
        lines.append(f"Total Time: {total_time:.1f}ms")
        lines.append("")

        for suite in self.suites:
            status = "✓" if suite.failed == 0 else "✗"
            lines.append(f"{status} {suite.name}")
            for case in suite.cases:
                icon = {
                    TestResult.PASS: "✓",
                    TestResult.FAIL: "✗",
                    TestResult.SKIP: "○",
                    TestResult.ERROR: "!",
                }.get(case.result, "?")
                lines.append(f"  {icon} {case.name}: {case.message[:50]}")

        lines.append("")
        lines.append("=" * 70)

        return "\n".join(lines)

    def get_exit_code(self) -> int:
        """Get exit code based on test results."""
        total_failed = sum(s.failed for s in self.suites)
        total_errors = sum(
            sum(1 for c in s.cases if c.result == TestResult.ERROR) for s in self.suites
        )

        if total_errors > 0:
            return 2  # Critical failure
        if total_failed > 0:
            return 1  # Some tests failed
        return 0  # All passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AMOS Unified Integration Test")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--report", choices=["text", "json"], default="text", help="Report format")
    parser.add_argument("--layer", help="Test specific layer only")

    args = parser.parse_args()

    # Run tests
    tester = AMOSUnifiedTest(verbose=args.verbose, quick=args.quick)
    tester.run_all()

    # Generate report
    report = tester.generate_report(format=args.report)
    print("\n" + report)

    # Exit with appropriate code
    sys.exit(tester.get_exit_code())


if __name__ == "__main__":
    main()
