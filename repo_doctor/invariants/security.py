"""I_security = 1 iff no forbidden source-to-sink flow exists."""
from __future__ import annotations

from typing import Any

from .base import Invariant, InvariantResult, InvariantSeverity


class SecurityInvariant(Invariant):
    """Security flow invariant."""

    def __init__(self):
        super().__init__("I_security", InvariantSeverity.CRITICAL)

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check security integrity."""
        context = context or {}
        flow = context.get("security_flow_violations", 0)
        deps = context.get("disallowed_dependencies", 0)

        total = flow + deps

        if total == 0:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=self.severity,
                message="No security violations",
            )

        return InvariantResult(
            name=self.name,
            passed=False,
            severity=self.severity,
            message=f"Security issues: {flow} flow, {deps} dependencies",
            details={"flow_violations": flow, "bad_dependencies": deps},
        )
