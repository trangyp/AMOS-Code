"""I_runtime = 1 iff shells, wrappers, servers, and bridges commute."""

from typing import Any, Dict

from .base import Invariant, InvariantResult, InvariantSeverity


class RuntimeInvariant(Invariant):
    """Runtime behavior invariant."""

    def __init__(self):
        super().__init__("I_runtime", InvariantSeverity.ERROR)

    def check(self, repo_path: str, context: Dict[str, Any] = None) -> InvariantResult:
        """Check runtime integrity."""
        context = context or {}
        shell = context.get("shell_promise_violations", 0)
        wrapper = context.get("wrapper_runtime_mismatches", 0)
        schema = context.get("server_schema_mismatches", 0)

        total = shell + wrapper + schema

        if total == 0:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=self.severity,
                message="Runtime surfaces commute",
            )

        return InvariantResult(
            name=self.name,
            passed=False,
            severity=self.severity,
            message=f"Runtime issues: {shell} shell, {wrapper} wrapper, {schema} schema",
            details={"shell": shell, "wrapper": wrapper, "schema": schema},
        )
