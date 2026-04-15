"""
I_api = 1 iff [A_public, A_runtime] = 0

Public contract commutator - detects drift between claimed and actual API.
"""

from __future__ import annotations

from typing import Any

from .base import Invariant, InvariantResult, InvariantSeverity


class APIInvariant(Invariant):
    """
    API contract invariant.
    Public claims must match runtime reality.
    """

    def __init__(self):
        super().__init__("I_api", InvariantSeverity.CRITICAL)

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check API contract commutator."""
        context = context or {}

        # Check for contract drift
        public_claims = context.get("public_api_claims", set())
        runtime_reality = context.get("runtime_api", set())

        # Compute commutator: [A_public, A_runtime] = A_p * A_r - A_r * A_p
        # For sets, this is symmetric difference
        drift = public_claims.symmetric_difference(runtime_reality)

        if not drift:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=self.severity,
                message="Public API commutes with runtime reality",
            )

        return InvariantResult(
            name=self.name,
            passed=False,
            severity=self.severity,
            message=f"API contract drift: {len(drift)} mismatches",
            details={
                "missing_in_runtime": list(public_claims - runtime_reality),
                "extra_in_runtime": list(runtime_reality - public_claims),
            },
        )
