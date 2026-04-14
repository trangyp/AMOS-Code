"""I_status = 1 iff every reported status label is logically implied by actual state."""
from __future__ import annotations

from typing import Any

from .base import Invariant, InvariantResult, InvariantSeverity


class StatusInvariant(Invariant):
    """Status truth invariant."""

    def __init__(self):
        super().__init__("I_status", InvariantSeverity.ERROR)

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check status truthfulness."""
        context = context or {}
        false_init = context.get("false_initialized", 0)
        false_enabled = context.get("false_enabled", 0)
        false_healthy = context.get("false_healthy", 0)
        false_active = context.get("false_active", 0)

        total = false_init + false_enabled + false_healthy + false_active

        if total == 0:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=self.severity,
                message="Status claims are truthful",
            )

        return InvariantResult(
            name=self.name,
            passed=False,
            severity=self.severity,
            message=f"Status lies: {false_init} init, {false_enabled} enabled, {false_healthy} healthy, {false_active} active",
            details={
                "false_init": false_init,
                "false_enabled": false_enabled,
                "false_healthy": false_healthy,
                "false_active": false_active,
            },
        )
