"""I_pack = 1 iff build metadata describes the same runtime surface."""
from __future__ import annotations

from typing import Any

from .base import Invariant, InvariantResult, InvariantSeverity


class PackagingInvariant(Invariant):
    """Packaging integrity invariant."""

    def __init__(self):
        super().__init__("I_pack", InvariantSeverity.CRITICAL)

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check packaging integrity."""
        context = context or {}
        conflicts = context.get("metadata_conflicts", 0)
        unshipped = context.get("unshipped_modules", 0)
        broken = context.get("broken_console_scripts", 0)

        total = conflicts + unshipped + broken

        if total == 0:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=self.severity,
                message="Packaging metadata consistent",
            )

        return InvariantResult(
            name=self.name,
            passed=False,
            severity=self.severity,
            message=f"Packaging issues: {conflicts} conflicts, {unshipped} unshipped, {broken} broken",
            details={"conflicts": conflicts, "unshipped": unshipped, "broken": broken},
        )
