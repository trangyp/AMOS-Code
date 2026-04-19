"""I_entry = 1 iff every launcher points to a real runnable target."""

from typing import Any

from .base import Invariant, InvariantResult, InvariantSeverity


class EntrypointInvariant(Invariant):
    """Entrypoint integrity invariant."""

    def __init__(self):
        super().__init__("I_entry", InvariantSeverity.CRITICAL)

    def check(self, repo_path: str, context: Dict[str, Any] = None) -> InvariantResult:
        """Check entrypoint integrity."""
        context = context or {}
        missing = context.get("missing_entrypoints", 0)
        wrong = context.get("wrong_target_entrypoints", 0)
        unimplemented = context.get("unimplemented_transports", 0)

        total = missing + wrong + unimplemented

        if total == 0:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=self.severity,
                message="All entrypoints valid",
            )

        return InvariantResult(
            name=self.name,
            passed=False,
            severity=self.severity,
            message=f"Entrypoint failures: {missing} missing, {wrong} wrong, {unimplemented} unimplemented",
            details={"missing": missing, "wrong": wrong, "unimplemented": unimplemented},
        )
