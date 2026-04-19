"""I_tests = 1 iff designated contract-critical tests pass."""

from typing import Any

from .base import Invariant, InvariantResult, InvariantSeverity


class TestsInvariant(Invariant):
    """Test contract invariant."""

    def __init__(self):
        super().__init__("I_tests", InvariantSeverity.WARNING)

    def check(self, repo_path: str, context: Dict[str, Any] = None) -> InvariantResult:
        """Check test integrity."""
        context = context or {}
        contract = context.get("contract_test_failures", 0)
        critical = context.get("critical_test_failures", 0)

        total = contract + critical

        if total == 0:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=self.severity,
                message="Contract tests pass",
            )

        return InvariantResult(
            name=self.name,
            passed=False,
            severity=self.severity,
            message=f"Test failures: {contract} contract, {critical} critical",
            details={"contract": contract, "critical": critical},
        )
