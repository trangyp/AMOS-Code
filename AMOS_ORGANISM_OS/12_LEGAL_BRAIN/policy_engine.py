"""Policy Engine — Policy Management & Enforcement

Manages organizational policies, rules, and enforcement mechanisms.
Provides policy validation and compliance checking.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class PolicyStatus(Enum):
    """Status of a policy."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    DEPRECATED = "deprecated"


class EnforcementLevel(Enum):
    """Level of policy enforcement."""

    STRICT = "strict"  # Block on violation
    MODERATE = "moderate"  # Warn on violation
    PERMISSIVE = "permissive"  # Log only


@dataclass
class PolicyRule:
    """A single rule within a policy."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    condition: str = ""  # Expression or pattern
    action: str = ""  # allow, deny, warn, log
    severity: int = 1  # 1-5

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Policy:
    """A policy containing multiple rules."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    category: str = ""  # security, privacy, operational, legal
    rules: List[PolicyRule] = field(default_factory=list)
    status: PolicyStatus = PolicyStatus.DRAFT
    enforcement: EnforcementLevel = EnforcementLevel.MODERATE
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "status": self.status.value,
            "enforcement": self.enforcement.value,
            "rules": [r.to_dict() for r in self.rules],
        }


class PolicyEngine:
    """Manages and enforces organizational policies.

    Provides policy definition, storage, validation,
    and enforcement mechanisms.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        self.policies: Dict[str, Policy] = {}
        self.violations: List[dict[str, Any]] = []

        self._load_policies()
        self._init_default_policies()

    def _init_default_policies(self):
        """Create default policies if none exist."""
        if self.policies:
            return

        # Security policy
        security = Policy(
            name="Security Policy",
            description="Basic security requirements",
            category="security",
            status=PolicyStatus.ACTIVE,
            enforcement=EnforcementLevel.STRICT,
            rules=[
                PolicyRule(
                    name="No Hardcoded Secrets",
                    description="Detect hardcoded passwords/tokens",
                    condition="contains(password|secret|token|key)",
                    action="deny",
                    severity=5,
                ),
                PolicyRule(
                    name="Input Validation",
                    description="Validate all external inputs",
                    condition="unvalidated_input",
                    action="warn",
                    severity=4,
                ),
            ],
        )
        self.policies[security.id] = security

        # Privacy policy
        privacy = Policy(
            name="Privacy Policy",
            description="Data privacy and protection",
            category="privacy",
            status=PolicyStatus.ACTIVE,
            enforcement=EnforcementLevel.STRICT,
            rules=[
                PolicyRule(
                    name="PII Protection",
                    description="Protect personally identifiable information",
                    condition="contains_pii",
                    action="deny",
                    severity=5,
                ),
            ],
        )
        self.policies[privacy.id] = privacy

        # Operational policy
        operational = Policy(
            name="Operational Policy",
            description="Operational guidelines",
            category="operational",
            status=PolicyStatus.ACTIVE,
            enforcement=EnforcementLevel.MODERATE,
            rules=[
                PolicyRule(
                    name="Resource Limits",
                    description="Stay within resource budgets",
                    condition="exceeds_budget",
                    action="warn",
                    severity=3,
                ),
            ],
        )
        self.policies[operational.id] = operational

        self.save()

    def create_policy(
        self,
        name: str,
        description: str = "",
        category: str = "",
        enforcement: EnforcementLevel = EnforcementLevel.MODERATE,
    ) -> Policy:
        """Create a new policy."""
        policy = Policy(
            name=name,
            description=description,
            category=category,
            enforcement=enforcement,
        )
        self.policies[policy.id] = policy
        self.save()
        return policy

    def add_rule(
        self,
        policy_id: str,
        name: str,
        description: str = "",
        condition: str = "",
        action: str = "warn",
        severity: int = 1,
    ) -> Optional[PolicyRule]:
        """Add a rule to a policy."""
        policy = self.policies.get(policy_id)
        if not policy:
            return None

        rule = PolicyRule(
            name=name,
            description=description,
            condition=condition,
            action=action,
            severity=severity,
        )
        policy.rules.append(rule)
        policy.updated_at = datetime.now(UTC).isoformat()
        self.save()
        return rule

    def evaluate_action(
        self,
        action_type: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Evaluate an action against all active policies."""
        violations = []
        allowed = True

        for policy in self.policies.values():
            if policy.status != PolicyStatus.ACTIVE:
                continue

            for rule in policy.rules:
                # Simple pattern matching for demo
                if self._check_condition(rule.condition, context):
                    violation = {
                        "policy_id": policy.id,
                        "policy_name": policy.name,
                        "rule_id": rule.id,
                        "rule_name": rule.name,
                        "severity": rule.severity,
                        "action": rule.action,
                    }
                    violations.append(violation)

                    # Apply enforcement
                    if rule.action == "deny":
                        allowed = False
                    elif rule.action == "warn":
                        pass  # Allow but flagged

        # Record violations
        if violations:
            self.violations.append(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "action_type": action_type,
                    "violations": violations,
                }
            )

        return {
            "allowed": allowed,
            "violations": violations,
            "max_severity": max((v["severity"] for v in violations), default=0),
        }

    def _check_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Check if context matches condition pattern."""
        # Simplified condition checking
        if condition == "contains(password|secret|token|key)":
            content = str(context.get("content", "")).lower()
            return any(word in content for word in ["password", "secret", "token", "key"])

        if condition == "unvalidated_input":
            return not context.get("validated", True)

        if condition == "contains_pii":
            content = str(context.get("content", "")).lower()
            pii_patterns = ["ssn", "email", "phone", "address", "name"]
            return any(p in content for p in pii_patterns)

        if condition == "exceeds_budget":
            return context.get("cost", 0) > context.get("budget", float("inf"))

        return False

    def _load_policies(self):
        """Load policies from disk."""
        policies_file = self.data_dir / "policies.json"
        if policies_file.exists():
            try:
                data = json.loads(policies_file.read_text())
                for p_data in data.get("policies", []):
                    policy = Policy(
                        id=p_data["id"],
                        name=p_data["name"],
                        description=p_data.get("description", ""),
                        category=p_data.get("category", ""),
                        status=PolicyStatus(p_data["status"]),
                        enforcement=EnforcementLevel(p_data["enforcement"]),
                        created_at=p_data.get("created_at", ""),
                        updated_at=p_data.get("updated_at", ""),
                    )
                    policy.rules = [PolicyRule(**r) for r in p_data.get("rules", [])]
                    self.policies[policy.id] = policy
            except Exception as e:
                print(f"[POLICY] Error loading policies: {e}")

    def save(self):
        """Save policies to disk."""
        policies_file = self.data_dir / "policies.json"
        data = {
            "policies": [p.to_dict() for p in self.policies.values()],
            "saved_at": datetime.now(UTC).isoformat(),
        }
        policies_file.write_text(json.dumps(data, indent=2))

    def list_policies(self) -> List[dict[str, Any]]:
        """List all policies."""
        return [p.to_dict() for p in self.policies.values()]

    def get_status(self) -> Dict[str, Any]:
        """Get engine status."""
        active = sum(1 for p in self.policies.values() if p.status == PolicyStatus.ACTIVE)
        total_rules = sum(len(p.rules) for p in self.policies.values())

        return {
            "total_policies": len(self.policies),
            "active_policies": active,
            "total_rules": total_rules,
            "total_violations": len(self.violations),
            "enforcement_levels": [e.value for e in EnforcementLevel],
        }


_ENGINE: Optional[PolicyEngine] = None


def get_policy_engine(data_dir: Optional[Path] = None) -> PolicyEngine:
    """Get or create global policy engine."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = PolicyEngine(data_dir)
    return _ENGINE
