"""Compliance Engine — Regulatory and policy compliance."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ComplianceRule:
    """A compliance rule."""

    id: str
    name: str
    description: str
    category: str  # data_retention, privacy, security, audit
    check: str  # The check to perform
    required: bool = True


class ComplianceEngine:
    """Checks compliance with regulations and policies."""

    def __init__(self):
        self._rules: list[ComplianceRule] = []
        self._violations: list[dict] = []
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Set up default compliance rules."""
        self._rules = [
            ComplianceRule(
                id="rule_1",
                name="audit_logging",
                description="All actions must be logged",
                category="audit",
                check="audit_log_exists",
            ),
            ComplianceRule(
                id="rule_2",
                name="no_secrets_in_logs",
                description="No API keys or passwords in logs",
                category="security",
                check="no_secrets",
            ),
            ComplianceRule(
                id="rule_3",
                name="data_minimization",
                description="Only necessary data should be collected",
                category="privacy",
                check="minimal_data",
            ),
        ]

    def check_compliance(
        self,
        action: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Check if an action complies with rules."""
        violations = []

        # Check for secrets in action
        if "api_key" in action.lower() or "password" in action.lower():
            violations.append(
                {
                    "rule": "no_secrets_in_logs",
                    "severity": "high",
                    "description": "Potential secret detected in action",
                }
            )

        # Check audit log
        if not context.get("audit_logged"):
            violations.append(
                {
                    "rule": "audit_logging",
                    "severity": "medium",
                    "description": "Action not properly audited",
                }
            )

        if violations:
            self._violations.append(
                {
                    "action": action,
                    "violations": violations,
                    "timestamp": context.get("timestamp"),
                }
            )

        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "rules_checked": len(self._rules),
        }

    def add_rule(self, rule: ComplianceRule):
        """Add a compliance rule."""
        self._rules.append(rule)

    def status(self) -> dict[str, Any]:
        """Get compliance status."""
        return {
            "total_rules": len(self._rules),
            "total_violations": len(self._violations),
            "compliance_rate": (1.0 - len(self._violations) / max(len(self._rules), 1)),
        }
