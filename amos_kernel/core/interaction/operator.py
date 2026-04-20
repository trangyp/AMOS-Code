"""Interaction operator - combines internal and external state"""

from .types import InteractionResult


class InteractionOperator:
    """Applies interaction between internal and external state representations."""

    def apply(self, internal: dict, external: dict) -> InteractionResult:
        """Merge internal and external into interaction result."""
        has_internal = bool(internal)
        has_external = bool(external)

        merged = {
            "internal": internal,
            "external": external,
            "emergence": {
                "coupling_strength": 1.0 if (has_internal and has_external) else 0.0,
                "difference": abs(len(internal) - len(external)),
                "union_keys": list(set(internal.keys()) | set(external.keys())),
                "intersection_keys": list(set(internal.keys()) & set(external.keys())),
            },
        }

        return InteractionResult(data=merged)

    def extract_feedback(self, interaction: InteractionResult) -> dict[str, float]:
        """Extract feedback signals from interaction result."""
        if interaction.feedback:
            return interaction.feedback
        return {
            "coupling_strength": interaction.coupling_strength,
            "error_signal": 0.0,
        }
