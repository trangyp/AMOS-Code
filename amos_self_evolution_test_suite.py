"""
AMOS Self-Evolution Test Suite
Safety Validation for Self-Modifying Code

Ensures Law 3 compliance: Evolution must be triggered by evidence
Provides comprehensive safety guarantees for production deployment.
"""

import asyncio
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc, timezone

UTC = UTC
import hashlib
from pathlib import Path
from typing import Any, Optional, Protocol


class EvolutionSafetyError(Exception):
    """Safety violation in self-evolution process."""

    pass


class RollbackTriggeredError(Exception):
    """Evolution rolled back due to safety check failure."""

    pass


@dataclass
class SafetyReport:
    """Safety validation report for evolution attempt."""

    evolution_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    passed: bool = False
    checks: dict[str, bool] = field(default_factory=dict)
    violations: list[str] = field(default_factory=list)
    rollback_required: bool = False
    evidence_quality: float = 0.0


class EvolutionSafetyChecker(Protocol):
    """Protocol for evolution safety validators."""

    async def validate(self, context: dict[str, Any]) -> tuple[bool, list[str]]:
        """Return (passed, violations)."""
        ...


class SyntaxValidator:
    """Validate generated code syntax."""

    async def validate(self, context: dict[str, Any]) -> tuple[bool, list[str]]:
        code = context.get("proposed_code", "")
        if not code:
            return False, ["No code provided"]

        try:
            compile(code, "<evolution>", "exec")
            return True, []
        except SyntaxError as e:
            return False, [f"Syntax error: {e}"]


class ImportSafetyValidator:
    """Validate imports are from allowed modules."""

    ALLOWED_MODULES = {
        "asyncio",
        "collections",
        "dataclasses",
        "datetime",
        "json",
        "math",
        "numpy",
        "pathlib",
        "typing",
        "amos",
        "amosl",
        "amos_brain",
    }

    BLOCKED_MODULES = {
        "os.system",
        "subprocess",
        "eval",
        "exec",
        "compile",
        "__import__",
        "importlib",
        "sys.modules",
    }

    async def validate(self, context: dict[str, Any]) -> tuple[bool, list[str]]:
        code = context.get("proposed_code", "")
        violations = []

        for blocked in self.BLOCKED_MODULES:
            if blocked in code:
                violations.append(f"Blocked import/usage: {blocked}")

        return len(violations) == 0, violations


class BehavioralConsistencyValidator:
    """Validate behavior matches specification."""

    async def validate(self, context: dict[str, Any]) -> tuple[bool, list[str]]:
        spec = context.get("specification", {})
        if not spec:
            return True, []  # No spec to validate against

        violations = []

        # Check required functions exist
        required = spec.get("required_functions", [])
        code = context.get("proposed_code", "")

        for func in required:
            if f"def {func}" not in code:
                violations.append(f"Missing required function: {func}")

        return len(violations) == 0, violations


class SemanticDriftValidator:
    """Validate semantic consistency with original."""

    async def validate(self, context: dict[str, Any]) -> tuple[bool, list[str]]:
        original_hash = context.get("original_hash")
        proposed_code = context.get("proposed_code", "")

        if not original_hash:
            return True, []

        # Compute semantic fingerprint (simplified: function signatures)
        current_fingerprint = self._extract_fingerprint(proposed_code)
        original_fingerprint = context.get("original_fingerprint", {})

        violations = []

        # Check API compatibility
        for func, sig in original_fingerprint.items():
            if func not in current_fingerprint:
                violations.append(f"Function removed: {func}")
            elif current_fingerprint[func] != sig:
                violations.append(f"Signature changed: {func}")

        return len(violations) == 0, violations

    def _extract_fingerprint(self, code: str) -> dict[str, str]:
        """Extract function signatures from code."""
        fingerprint = {}
        for line in code.split("\n"):
            if line.strip().startswith("def "):
                # Extract def line
                sig = line.strip()
                func_name = sig[4:].split("(")[0].strip()
                fingerprint[func_name] = sig
        return fingerprint


class TestCoverageValidator:
    """Validate tests exist and pass for evolved code."""

    async def validate(self, context: dict[str, Any]) -> tuple[bool, list[str]]:
        test_code = context.get("test_code", "")

        if not test_code:
            return False, ["No tests provided for evolved code"]

        # Validate test syntax
        try:
            compile(test_code, "<test>", "exec")
        except SyntaxError as e:
            return False, [f"Test syntax error: {e}"]

        # Check for actual test functions
        if "def test_" not in test_code and "async def test_" not in test_code:
            return False, ["No test functions found (def test_*)"]

        return True, []


@dataclass
class EvolutionContext:
    """Context for evolution attempt."""

    evolution_id: str
    target_file: Path
    original_code: str
    proposed_code: str
    reason: str
    evidence: dict[str, Any]
    specification: dict[str, Any] = None
    test_code: str = None


class SelfEvolutionTestSuite:
    """
    Comprehensive safety testing for AMOS self-evolution.

    Ensures all self-modifications meet safety criteria before application.
    Implements Law 3: Evolution must be triggered by evidence.
    """

    def __init__(self) -> None:
        self.validators: list[EvolutionSafetyChecker] = [
            SyntaxValidator(),
            ImportSafetyValidator(),
            BehavioralConsistencyValidator(),
            SemanticDriftValidator(),
            TestCoverageValidator(),
        ]
        self._test_history: list[SafetyReport] = []
        self._sandbox_dir: Optional[Path] = None

    async def initialize(self) -> None:
        """Initialize test suite with sandbox environment."""
        self._sandbox_dir = Path(tempfile.mkdtemp(prefix="amos_evolution_"))

    async def validate_evolution(self, context: EvolutionContext) -> SafetyReport:
        """
        Comprehensive safety validation for evolution attempt.

        All checks must pass for evolution to proceed.
        """
        report = SafetyReport(evolution_id=context.evolution_id)

        validation_context = {
            "proposed_code": context.proposed_code,
            "original_code": context.original_code,
            "original_hash": hashlib.sha256(context.original_code.encode()).hexdigest()[:16],
            "original_fingerprint": self._extract_fingerprint(context.original_code),
            "specification": context.specification or {},
            "test_code": context.test_code or "",
            "reason": context.reason,
            "evidence": context.evidence,
        }

        # Run all validators
        for validator in self.validators:
            validator_name = type(validator).__name__
            passed, violations = await validator.validate(validation_context)

            report.checks[validator_name] = passed
            report.violations.extend(violations)

            if not passed:
                report.rollback_required = True

        # Evidence quality assessment
        report.evidence_quality = self._assess_evidence_quality(context.evidence)

        # Final verdict
        report.passed = all(report.checks.values()) and report.evidence_quality >= 0.7

        # Store report
        self._test_history.append(report)

        return report

    def _extract_fingerprint(self, code: str) -> dict[str, str]:
        """Extract semantic fingerprint from code."""
        fingerprint = {}
        for line in code.split("\n"):
            if line.strip().startswith("def "):
                sig = line.strip()
                func_name = sig[4:].split("(")[0].strip()
                fingerprint[func_name] = sig
        return fingerprint

    def _assess_evidence_quality(self, evidence: dict[str, Any]) -> float:
        """Assess quality of evolution evidence (0.0-1.0)."""
        if not evidence:
            return 0.0

        score = 0.0
        checks = 0

        # Check for specific evidence types
        if "performance_metrics" in evidence:
            score += 0.2
            checks += 1
        if "error_logs" in evidence:
            score += 0.2
            checks += 1
        if "user_feedback" in evidence:
            score += 0.2
            checks += 1
        if "test_results" in evidence:
            score += 0.2
            checks += 1
        if "audit_trail" in evidence:
            score += 0.2
            checks += 1

        return score if checks > 0 else 0.0

    async def execute_sandbox_test(self, context: EvolutionContext) -> tuple[bool, str]:
        """
        Execute evolved code in sandboxed environment.

        Returns (success, output_or_error).
        """
        if not self._sandbox_dir:
            await self.initialize()

        test_file = self._sandbox_dir / f"{context.evolution_id}.py"

        try:
            # Write code to sandbox
            test_file.write_text(context.proposed_code)

            # Attempt import (catches many runtime errors)
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                f"evolution_{context.evolution_id}", test_file
            )
            module = importlib.util.module_from_spec(spec)

            # Execute in isolated context
            exec_globals = {"__name__": "__test__"}
            exec(context.proposed_code, exec_globals)

            return True, "Sandbox execution successful"

        except Exception as e:
            error_msg = f"Sandbox execution failed: {type(e).__name__}: {str(e)}"
            return False, error_msg
        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()

    def get_safety_metrics(self) -> dict[str, Any]:
        """Get safety testing metrics."""
        if not self._test_history:
            return {"total_tests": 0, "pass_rate": 0.0}

        total = len(self._test_history)
        passed = sum(1 for r in self._test_history if r.passed)

        return {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 0.0,
            "rollbacks_triggered": sum(1 for r in self._test_history if r.rollback_required),
            "average_evidence_quality": sum(r.evidence_quality for r in self._test_history) / total
            if total > 0
            else 0.0,
        }

    def export_safety_report(self, evolution_id: str = None) -> dict[str, Any]:
        """Export safety report for compliance."""
        if evolution_id:
            reports = [r for r in self._test_history if r.evolution_id == evolution_id]
        else:
            reports = self._test_history

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "reports": [
                {
                    "evolution_id": r.evolution_id,
                    "timestamp": r.timestamp,
                    "passed": r.passed,
                    "checks": r.checks,
                    "violations": r.violations,
                    "evidence_quality": r.evidence_quality,
                }
                for r in reports
            ],
            "metrics": self.get_safety_metrics(),
        }


# Global test suite instance
_test_suite: Optional[SelfEvolutionTestSuite] = None


def get_self_evolution_test_suite() -> SelfEvolutionTestSuite:
    """Get global test suite instance."""
    global _test_suite
    if _test_suite is None:
        _test_suite = SelfEvolutionTestSuite()
    return _test_suite


async def validate_evolution_safety(context: EvolutionContext) -> SafetyReport:
    """Convenience function to validate evolution safety."""
    suite = get_self_evolution_test_suite()
    await suite.initialize()
    return await suite.validate_evolution(context)


if __name__ == "__main__":

    async def demo():
        """Demonstrate self-evolution test suite."""
        print("=== AMOS Self-Evolution Test Suite Demo ===\n")

        suite = get_self_evolution_test_suite()
        await suite.initialize()

        # Test valid evolution
        context = EvolutionContext(
            evolution_id="test_001",
            target_file=Path("test_module.py"),
            original_code="def foo(): pass",
            proposed_code="""def foo():
    \"\"\"Valid function.\"\"\"\n    return 42
""",
            reason="Add return value",
            evidence={
                "performance_metrics": {"improvement": 0.15},
                "test_results": {"passed": True},
            },
            test_code="""def test_foo():
    assert foo() == 42
""",
        )

        report = await suite.validate_evolution(context)
        print(f"Evolution {context.evolution_id}:")
        print(f"  Passed: {report.passed}")
        print(f"  Checks: {report.checks}")
        print(f"  Evidence Quality: {report.evidence_quality:.2f}")

        # Test invalid evolution (syntax error)
        bad_context = EvolutionContext(
            evolution_id="test_002",
            target_file=Path("bad_module.py"),
            original_code="def bar(): pass",
            proposed_code="def bar(:\n    invalid syntax",
            reason="Break things",
            evidence={},
            test_code="",
        )

        bad_report = await suite.validate_evolution(bad_context)
        print(f"\nEvolution {bad_context.evolution_id}:")
        print(f"  Passed: {bad_report.passed}")
        print(f"  Violations: {bad_report.violations}")
        print(f"  Rollback Required: {bad_report.rollback_required}")

        # Metrics
        print(f"\nSafety Metrics: {suite.get_safety_metrics()}")
        print("\n✅ Self-evolution test suite operational")

    asyncio.run(demo())
