"""I_history = 1 iff structural transitions over commits remain localizable."""

from __future__ import annotations

from typing import Any

from .base import Invariant, InvariantResult, InvariantSeverity


class HistoryInvariant(Invariant):
    """Temporal/history integrity invariant."""

    def __init__(self):
        super().__init__("I_history", InvariantSeverity.WARNING)

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check history integrity."""
        context = context or {}
        unlocalized = context.get("unlocalized_flips", 0)
        impossible = context.get("impossible_merges", 0)

        total = unlocalized + impossible

        if total == 0:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=self.severity,
                message="History is coherent",
            )

        return InvariantResult(
            name=self.name,
            passed=False,
            severity=self.severity,
            message=f"History issues: {unlocalized} unlocalized, {impossible} impossible",
            details={"unlocalized": unlocalized, "impossible": impossible},
        )
