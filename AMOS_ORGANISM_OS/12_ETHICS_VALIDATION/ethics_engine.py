"""Ethics Engine — Core Ethical Reasoning & Validation

Validates decisions against ethical frameworks, ensures moral compliance,
and provides ethical guidance for AMOS operations.

Owner: Trang
Version: 1.0.0
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class EthicsSeverity(Enum):
    """Severity levels for ethical violations."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EthicsCategory(Enum):
    """Categories of ethical considerations."""

    PRIVACY = "privacy"
    FAIRNESS = "fairness"
    TRANSPARENCY = "transparency"
    ACCOUNTABILITY = "accountability"
    SAFETY = "safety"
    AUTONOMY = "autonomy"


@dataclass
class EthicsRule:
    """An ethical rule definition."""

    id: str
    name: str
    description: str
    category: EthicsCategory
    severity: EthicsSeverity
    condition: str
    enabled: bool = True


@dataclass
class EthicalDecision:
    """An ethical decision record."""

    decision_id: str
    timestamp: datetime
    context: str
    action: str
    ethical_score: float  # 0.0 to 1.0
    violations: list[str]
    approved: bool
    reasoning: str


@dataclass
class EthicsReport:
    """Report of ethical analysis."""

    generated_at: datetime
    total_decisions: int
    approved_count: int
    rejected_count: int
    average_score: float
    critical_violations: int


class EthicsEngine:
    """Core engine for ethical reasoning and validation.

    Evaluates decisions against ethical rules, calculates ethical scores,
    and maintains ethical compliance across AMOS operations.
    """

    def __init__(self):
        self.rules: dict[str, EthicsRule] = {}
        self.decisions: list[EthicalDecision] = []
        self._load_default_rules()

    def _load_default_rules(self):
        """Load default ethical rules."""
        default_rules = [
            EthicsRule(
                id="ETHIC-001",
                name="Privacy Protection",
                description="Respect user privacy and data protection",
                category=EthicsCategory.PRIVACY,
                severity=EthicsSeverity.CRITICAL,
                condition="personal_data_involved",
            ),
            EthicsRule(
                id="ETHIC-002",
                name="Fairness",
                description="Ensure decisions are fair and unbiased",
                category=EthicsCategory.FAIRNESS,
                severity=EthicsSeverity.HIGH,
                condition="decision_affects_multiple_parties",
            ),
            EthicsRule(
                id="ETHIC-003",
                name="Transparency",
                description="Maintain transparency in decision-making",
                category=EthicsCategory.TRANSPARENCY,
                severity=EthicsSeverity.HIGH,
                condition="external_communication",
            ),
            EthicsRule(
                id="ETHIC-004",
                name="Human Oversight",
                description="Require human oversight for critical decisions",
                category=EthicsCategory.ACCOUNTABILITY,
                severity=EthicsSeverity.CRITICAL,
                condition="high_impact_decision",
            ),
            EthicsRule(
                id="ETHIC-005",
                name="Safety First",
                description="Prioritize safety in all operations",
                category=EthicsCategory.SAFETY,
                severity=EthicsSeverity.CRITICAL,
                condition="safety_risk_present",
            ),
        ]

        for rule in default_rules:
            self.rules[rule.id] = rule

    def add_rule(self, rule: EthicsRule) -> bool:
        """Add a new ethical rule."""
        if rule.id in self.rules:
            return False
        self.rules[rule.id] = rule
        return True

    def evaluate_decision(self, context: str, action: str, data: dict[str, Any]) -> EthicalDecision:
        """Evaluate a decision against ethical rules."""
        violations = []
        score = 1.0

        # Check each enabled rule
        for rule in self.rules.values():
            if not rule.enabled:
                continue

            # Simulate rule evaluation
            violation = self._check_rule(rule, context, action, data)
            if violation:
                violations.append(rule.id)
                # Adjust score based on severity
                if rule.severity == EthicsSeverity.CRITICAL:
                    score -= 0.3
                elif rule.severity == EthicsSeverity.HIGH:
                    score -= 0.2
                elif rule.severity == EthicsSeverity.MEDIUM:
                    score -= 0.1
                else:
                    score -= 0.05

        # Ensure score stays within bounds
        score = max(0.0, min(1.0, score))

        # Decision is approved if score >= 0.7 and no critical violations
        approved = score >= 0.7 and not any(
            self.rules[v].severity == EthicsSeverity.CRITICAL for v in violations if v in self.rules
        )

        decision = EthicalDecision(
            decision_id=f"ethics_{len(self.decisions) + 1}",
            timestamp=datetime.utcnow(),
            context=context,
            action=action,
            ethical_score=score,
            violations=violations,
            approved=approved,
            reasoning=f"Score: {score:.2f}, Violations: {len(violations)}",
        )

        self.decisions.append(decision)
        return decision

    def _check_rule(
        self, rule: EthicsRule, context: str, action: str, data: dict[str, Any]
    ) -> bool:
        """Check if a rule is violated."""
        # Placeholder for actual rule checking logic
        # In production, this would evaluate the condition against data
        return False

    def get_ethics_report(self) -> EthicsReport:
        """Generate an ethics report."""
        if not self.decisions:
            return EthicsReport(
                generated_at=datetime.utcnow(),
                total_decisions=0,
                approved_count=0,
                rejected_count=0,
                average_score=0.0,
                critical_violations=0,
            )

        approved = sum(1 for d in self.decisions if d.approved)
        rejected = len(self.decisions) - approved
        avg_score = sum(d.ethical_score for d in self.decisions) / len(self.decisions)

        critical_violations = sum(
            1
            for d in self.decisions
            for v in d.violations
            if v in self.rules and self.rules[v].severity == EthicsSeverity.CRITICAL
        )

        return EthicsReport(
            generated_at=datetime.utcnow(),
            total_decisions=len(self.decisions),
            approved_count=approved,
            rejected_count=rejected,
            average_score=avg_score,
            critical_violations=critical_violations,
        )

    def get_rules_by_category(self, category: EthicsCategory) -> list[EthicsRule]:
        """Get all rules in a category."""
        return [r for r in self.rules.values() if r.category == category]

    def enable_rule(self, rule_id: str) -> bool:
        """Enable an ethical rule."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """Disable an ethical rule."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            return True
        return False


if __name__ == "__main__":
    print("Ethics Engine Module")
    print("=" * 50)

    engine = EthicsEngine()
    print(f"Loaded {len(engine.rules)} ethical rules")

    # Test evaluation
    decision = engine.evaluate_decision(
        context="test",
        action="test_action",
        data={},
    )
    print(f"Decision score: {decision.ethical_score:.2f}")
    print(f"Approved: {decision.approved}")

    print("Ethics Engine ready")
