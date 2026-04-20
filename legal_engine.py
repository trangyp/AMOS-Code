"""Legal Engine stub for compatibility."""

from typing import Any


class LegalRule:
    """Represents a legal rule."""

    def __init__(self, name: str, condition: str, action: str):
        self.name = name
        self.condition = condition
        self.action = action


class LegalEngine:
    """Engine for legal reasoning."""

    def __init__(self):
        self.rules: list[LegalRule] = []

    def add_rule(self, rule: LegalRule) -> None:
        """Add legal rule."""
        self.rules.append(rule)

    def evaluate(self, facts: dict[str, Any]) -> list[LegalRule]:
        """Evaluate facts against rules."""
        return []


__all__ = ["LegalRule", "LegalEngine"]
