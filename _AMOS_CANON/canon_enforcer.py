#!/usr/bin/env python3
"""Canon Enforcer - Enforces canonical rules and standards."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable
from collections.abc import Callable as CallableType

from .canon_core import CanonCore, CanonRule, CanonPriority

logger = logging.getLogger(__name__)

@dataclass
class Violation:
    rule_id: str
    timestamp: str
    context: str
    details: str
    severity: CanonPriority

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "timestamp": self.timestamp,
            "context": self.context,
            "details": self.details,
            "severity": self.severity.value,
        }

@dataclass
class EnforcementResult:
    rule_id: str
    passed: bool
    violation: Violation | None = None
    remediated: bool = False
    message: str = ""

class CanonEnforcer:
    def __init__(self, core: CanonCore | None = None):
        self._core = core or CanonCore()
        self._violations: list[Violation] = []
        self._handlers: dict[str, CallableType[..., EnforcementResult]] = {}

    def register_handler(self, rule_id: str, handler: CallableType[..., EnforcementResult]) -> None:
        self._handlers[rule_id] = handler

    def enforce(self, rule_id: str, context: Any, auto_remediate: bool = False) -> EnforcementResult:
        rule = self._core.get_rule(rule_id)
        if not rule:
            return EnforcementResult(
                rule_id=rule_id,
                passed=False,
                message=f"Rule {rule_id} not found",
            )
        if not rule.enabled:
            return EnforcementResult(
                rule_id=rule_id,
                passed=True,
                message="Rule disabled",
            )
        handler = self._handlers.get(rule_id)
        if handler:
            result = handler(context)
        else:
            result = self._default_enforce(rule, context)
        if not result.passed and result.violation:
            self._violations.append(result.violation)
            if auto_remediate and rule.auto_remediate:
                result.remediated = self._attempt_remediation(rule, context)
        return result

    def _default_enforce(self, rule: CanonRule, context: Any) -> EnforcementResult:
        passed = True
        message = "Default enforcement passed"
        if not passed:
            violation = Violation(
                rule_id=rule.id,
                timestamp=datetime.now(timezone.utc).isoformat(),
                context=str(context),
                details=f"Rule {rule.id} violated",
                severity=rule.priority,
            )
            return EnforcementResult(
                rule_id=rule.id,
                passed=False,
                violation=violation,
                message=message,
            )
        return EnforcementResult(
            rule_id=rule.id,
            passed=True,
            message=message,
        )

    def _attempt_remediation(self, rule: CanonRule, context: Any) -> bool:
        logger.info(f"Attempting remediation for rule {rule.id}")
        return False

    def enforce_all(self, context: Any, category: Any = None, auto_remediate: bool = False) -> list[EnforcementResult]:
        from .canon_core import CanonCategory
        rules = self._core.list_rules(category=category)
        results = []
        for rule in rules:
            if rule.enabled:
                result = self.enforce(rule.id, context, auto_remediate)
                results.append(result)
        return results

    def get_violations(self, severity: CanonPriority | None = None, limit: int = 100) -> list[Violation]:
        violations = self._violations
        if severity:
            violations = [v for v in violations if v.severity == severity]
        return violations[-limit:]

    def clear_violations(self) -> None:
        self._violations.clear()

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_violations": len(self._violations),
            "by_severity": {
                p.value: len([v for v in self._violations if v.severity == p])
                for p in CanonPriority
            },
            "registered_handlers": len(self._handlers),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
