"""Repair verification - extracted from amos_brain/equation_bridge_integration.py"""

from .types import VerificationResult


def verify(simulation_result: dict) -> VerificationResult:
    """Verify repair simulation result."""
    passed = bool(simulation_result.get("safe"))
    return VerificationResult(
        passed=passed,
        messages=["simulation passed"] if passed else ["simulation failed"],
    )


def verify_repairs(plan: "RepairPlan") -> VerificationResult:
    """Verify a repair plan is safe to execute."""
    if not plan.safe:
        return VerificationResult(passed=False, messages=["Plan contains unsafe actions"])

    if not plan.actions:
        return VerificationResult(passed=True, messages=["No repairs needed"])

    return VerificationResult(passed=True, messages=[f"{len(plan.actions)} repairs verified safe"])
