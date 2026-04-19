"""Legal Engine stub for compatibility."""

from typing import Any, Dict, List


class LegalRule:
    """Represents a legal rule."""

    def __init__(self, name: str, condition: str, action: str):
        self.name = name
        self.condition = condition
        self.action = action


class LegalEngine:
    """Engine for legal reasoning."""

    def __init__(self):
        self.rules: List[LegalRule] = []

    def add_rule(self, rule: LegalRule) -> None:
        """Add legal rule."""
        self.rules.append(rule)

    def evaluate(self, facts: Dict[str, Any]) -> List[LegalRule]:
        """Evaluate facts against rules."""
        return []


__all__ = ["LegalRule", "LegalEngine"]
