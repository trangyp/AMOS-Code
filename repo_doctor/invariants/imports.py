"""
I_import = 1 iff every claimed symbol import resolves

Covers: internal imports, package exports, entrypoint imports, docs/demo/test imports
"""
from __future__ import annotations

from typing import Any

from .base import Invariant, InvariantResult, InvariantSeverity


class ImportInvariant(Invariant):
    """
    Import resolution invariant.
    All imports must resolve to real symbols.
    """

    def __init__(self):
        super().__init__("I_import", InvariantSeverity.CRITICAL)

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check import resolution."""
        context = context or {}
        unresolved = context.get("unresolved_imports", 0)
        public_fails = context.get("public_import_failures", 0)
        entrypoint_fails = context.get("entrypoint_import_failures", 0)

        total_fails = unresolved + public_fails + entrypoint_fails

        if total_fails == 0:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=self.severity,
                message="All imports resolve",
            )

        return InvariantResult(
            name=self.name,
            passed=False,
            severity=self.severity,
            message=f"Import failures: {unresolved} unresolved, {public_fails} public, {entrypoint_fails} entrypoint",
            details={
                "unresolved": unresolved,
                "public_failures": public_fails,
                "entrypoint_failures": entrypoint_fails,
            },
        )
