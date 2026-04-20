"""Rule Validator — Business rule validation for AMOS."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from enum import Enum
from typing import Any


class RuleType(Enum):
    REQUIRED = "required"
    FORBIDDEN = "forbidden"
    CONDITIONAL = "conditional"
    CUSTOM = "custom"


class ValidationOutcome(Enum):
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    WARNING = "warning"


@dataclass
class Rule:
    """A validation rule."""

    id: str
    name: str
    rule_type: RuleType
    condition: str
    message: str
    severity: str = "error"
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class ValidationResult:
    """Result of rule validation."""

    rule_id: str
    outcome: ValidationOutcome
    target: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class RuleValidator:
    """Validates business and operational rules."""

    def __init__(self):
        self._rules: dict[str, Rule] = {}
        self._history: list[ValidationResult] = []
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default rules."""
        defaults = [
            Rule(
                id="no_main_in_modules",
                name="No main blocks in modules",
                rule_type=RuleType.FORBIDDEN,
                condition="if __name__ == '__main__' in .py file",
                message="Library modules should not contain main blocks",
                severity="warning",
            ),
            Rule(
                id="has_docstring",
                name="Public functions need docstrings",
                rule_type=RuleType.REQUIRED,
                condition="def.*: requires docstring",
                message="Public functions should have docstrings",
                severity="warning",
            ),
        ]
        for r in defaults:
            self._rules[r.id] = r

    def add_rule(self, rule: Rule) -> str:
        """Add a new rule."""
        self._rules[rule.id] = rule
        return rule.id

    def validate(self, target: str, context: dict[str, Any] = None) -> list[ValidationResult]:
        """Validate target against all enabled rules."""
        results = []
        ctx = context or {}

        for rule in self._rules.values():
            if not rule.enabled:
                continue

            result = self._check_rule(rule, target, ctx)
            results.append(result)
            self._history.append(result)

        return results

    def _check_rule(self, rule: Rule, target: str, context: dict[str, Any]) -> ValidationResult:
        """Check a single rule."""
        # Simple rule checking - can be extended
        if rule.rule_type == RuleType.REQUIRED:
            # Check if required condition is met
            passed = self._check_required(rule, target, context)
        elif rule.rule_type == RuleType.FORBIDDEN:
            # Check if forbidden condition is present
            passed = not self._check_forbidden(rule, target, context)
        else:
            passed = True

        return ValidationResult(
            rule_id=rule.id,
            outcome=ValidationOutcome.PASS if passed else ValidationOutcome.FAIL,
            target=target,
            message=rule.message if not passed else "",
            details={"rule_type": rule.rule_type.value},
        )

    def _check_required(self, rule: Rule, target: str, context: dict[str, Any]) -> bool:
        """Check required condition."""
        # Simplified implementation
        return True

    def _check_forbidden(self, rule: Rule, target: str, context: dict[str, Any]) -> bool:
        """Check if forbidden condition exists."""
        # Simplified implementation
        return False

    def status(self) -> dict[str, Any]:
        """Get validator status."""
        failures = [r for r in self._history if r.outcome == ValidationOutcome.FAIL]
        return {
            "total_rules": len(self._rules),
            "enabled_rules": sum(1 for r in self._rules.values() if r.enabled),
            "total_validations": len(self._history),
            "total_failures": len(failures),
        }
