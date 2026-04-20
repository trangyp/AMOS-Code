"""I_persist = 1 iff serialize -> deserialize preserves operational semantics."""

from typing import Any, Dict

from .base import Invariant, InvariantResult, InvariantSeverity


class PersistenceInvariant(Invariant):
    """Persistence roundtrip invariant."""

    def __init__(self):
        super().__init__("I_persist", InvariantSeverity.ERROR)

    def check(self, repo_path: str, context: Dict[str, Any] = None) -> InvariantResult:
        """Check persistence integrity."""
        context = context or {}
        roundtrip = context.get("roundtrip_failures", 0)
        schema = context.get("schema_field_losses", 0)
        poison = context.get("cache_poison_acceptance", 0)

        total = roundtrip + schema + poison

        if total == 0:
            return InvariantResult(
                name=self.name,
                passed=True,
                severity=self.severity,
                message="Persistence roundtrip valid",
            )

        return InvariantResult(
            name=self.name,
            passed=False,
            severity=self.severity,
            message=f"Persistence issues: {roundtrip} roundtrip, {schema} schema, {poison} poison",
            details={"roundtrip": roundtrip, "schema": schema, "poison": poison},
        )
