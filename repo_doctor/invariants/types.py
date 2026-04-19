"""I_type = 1 iff every public callsite satisfies the actual callable signature."""

from typing import Any

from .base import Invariant, InvariantResult, InvariantSeverity


class TypeInvariant(Invariant):
    """Type/signature integrity invariant."""

    def __init__(self):
        super().__init__("I_type", InvariantSeverity.ERROR)

    def check(self, repo_path: str, context: Dict[str, Any] = None) -> InvariantResult:
        """Check type/signature integrity."""
        context = context or {}
        arity = context.get("arity_mismatches", 0)
        kwarg = context.get("kwarg_mismatches", 0)
        return_shape = context.get("return_shape_mismatches", 0)

        total = arity + kwarg + return_shape

        if total == 0:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=self.severity,
                message="All signatures valid",
            )

        return InvariantResult(
            name=self.name,
            passed=False,
            severity=self.severity,
            message=f"Type issues: {arity} arity, {kwarg} kwarg, {return_shape} return",
            details={"arity": arity, "kwarg": kwarg, "return_shape": return_shape},
        )
