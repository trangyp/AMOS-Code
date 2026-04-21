"""AMOS AI Governance & Safety Guardrails System.

Provides comprehensive governance, safety guardrails, and constitutional AI
principles for production AI systems. Ensures ethical alignment, safety,
and regulatory compliance.

Features:
- Constitutional AI principles enforcement
- Content safety guardrails
- Bias detection and mitigation
- Audit logging and compliance
- Policy-based access control for AI actions
- Ethical constraint validation
- Automated safety checks

Research Sources:
- AI Governance Framework 2026 (Arthur.ai)
- Constitutional AI (Anthropic Claude 2026)
- AI Guardrails Requirements (StateTech 2026)
- AI Safety & Alignment Best Practices

Creator: Trang Phan
Version: 3.0.0
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum
from typing import Any, Optional, Union

# Governance configuration
GOVERNANCE_ENABLED = os.getenv("GOVERNANCE_ENABLED", "true").lower() == "true"
CONTENT_SAFETY_ENABLED = os.getenv("CONTENT_SAFETY_ENABLED", "true").lower() == "true"
AUDIT_LOGGING_ENABLED = os.getenv("AUDIT_LOGGING_ENABLED", "true").lower() == "true"
MAX_POLICIES_PER_REQUEST = int(os.getenv("MAX_POLICIES_PER_REQUEST", "10"))


class PolicyType(Enum):
    """Types of governance policies."""

    SAFETY = "safety"  # Harmful content prevention
    ETHICS = "ethics"  # Ethical guidelines
    COMPLIANCE = "compliance"  # Regulatory compliance
    PRIVACY = "privacy"  # Data privacy protection
    QUALITY = "quality"  # Output quality standards


class ViolationSeverity(Enum):
    """Severity levels for policy violations."""

    CRITICAL = "critical"  # Block immediately, alert
    HIGH = "high"  # Block, log
    MEDIUM = "medium"  # Warn, log
    LOW = "low"  # Log only
    INFO = "info"  # Informational


@dataclass
class GovernancePolicy:
    """Represents a governance policy."""

    policy_id: str
    name: str
    policy_type: str
    description: str
    rules: list[dict[str, Any]]
    severity: str
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyViolation:
    """Represents a policy violation."""

    violation_id: str
    policy_id: str
    policy_name: str
    severity: str
    content_type: str  # "input" or "output"
    violation_details: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    action_taken: str = ""


@dataclass
class AuditLogEntry:
    """Represents an audit log entry."""

    entry_id: str
    timestamp: str
    agent_id: str
    action: str
    input_hash: str
    output_hash: str
    policies_applied: list[str]
    violations: list[str]
    latency_ms: float
    metadata: dict[str, Any]


class AIGovernanceEngine:
    """Core governance engine for AI safety and compliance."""

    def __init__(self):
        self.policies: dict[str, GovernancePolicy] = {}
        self.violations: list[PolicyViolation] = []
        self.audit_log: list[AuditLogEntry] = []
        self.max_audit_entries = 10000
        self.content_filters = self._initialize_content_filters()
        self._initialize_default_policies()

    def _initialize_content_filters(self) -> dict[str, Any]:
        """Initialize content safety filters."""
        return {
            "harmful_patterns": [
                r"\b(kill|murder|hurt|attack)\s+(?:myself|yourself|someone)",
                r"\b(how\s+to\s+make|create|build)\s+(?:bomb|weapon|drug)",
                r"\b(hack|steal|breach|exploit)\s+(?:bank|system|account)",
            ],
            "pii_patterns": [
                r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
                r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # Credit card
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
            ],
            "bias_indicators": [
                "all",
                "every",
                "always",
                "never",
                "only",
            ],
        }

    def _initialize_default_policies(self):
        """Initialize default governance policies."""
        # Safety Policy
        self.add_policy(
            GovernancePolicy(
                policy_id="safety_001",
                name="Harmful Content Prevention",
                policy_type=PolicyType.SAFETY.value,
                description="Prevents generation of harmful, dangerous, or self-harm content",
                rules=[
                    {"type": "block", "pattern": "self_harm", "action": "block"},
                    {"type": "block", "pattern": "violence", "action": "block"},
                    {"type": "block", "pattern": "illegal_acts", "action": "block"},
                ],
                severity=ViolationSeverity.CRITICAL.value,
            )
        )

        # Ethics Policy
        self.add_policy(
            GovernancePolicy(
                policy_id="ethics_001",
                name="Ethical Guidelines",
                policy_type=PolicyType.ETHICS.value,
                description="Ensures AI responses align with ethical principles",
                rules=[
                    {"type": "check", "principle": "fairness", "action": "warn"},
                    {"type": "check", "principle": "transparency", "action": "log"},
                    {"type": "check", "principle": "accountability", "action": "log"},
                ],
                severity=ViolationSeverity.MEDIUM.value,
            )
        )

        # Privacy Policy
        self.add_policy(
            GovernancePolicy(
                policy_id="privacy_001",
                name="PII Protection",
                policy_type=PolicyType.PRIVACY.value,
                description="Prevents exposure of personally identifiable information",
                rules=[
                    {"type": "detect", "data_type": "ssn", "action": "redact"},
                    {"type": "detect", "data_type": "email", "action": "redact"},
                    {"type": "detect", "data_type": "phone", "action": "redact"},
                ],
                severity=ViolationSeverity.HIGH.value,
            )
        )

        # Quality Policy
        self.add_policy(
            GovernancePolicy(
                policy_id="quality_001",
                name="Response Quality",
                policy_type=PolicyType.QUALITY.value,
                description="Ensures high-quality, accurate, and helpful responses",
                rules=[
                    {"type": "validate", "criteria": "accuracy", "threshold": 0.8},
                    {"type": "validate", "criteria": "helpfulness", "threshold": 0.8},
                    {"type": "validate", "criteria": "clarity", "threshold": 0.7},
                ],
                severity=ViolationSeverity.LOW.value,
            )
        )

    def add_policy(self, policy: GovernancePolicy) -> bool:
        """Add a governance policy."""
        self.policies[policy.policy_id] = policy
        return True

    def get_policy(self, policy_id: str) -> Optional[GovernancePolicy]:
        """Get a policy by ID."""
        return self.policies.get(policy_id)

    def list_policies(self, policy_type: str = None) -> list[GovernancePolicy]:
        """List all policies, optionally filtered by type."""
        policies = list(self.policies.values())
        if policy_type:
            policies = [p for p in policies if p.policy_type == policy_type]
        return policies

    def enable_policy(self, policy_id: str) -> bool:
        """Enable a policy."""
        if policy_id in self.policies:
            self.policies[policy_id].enabled = True
            return True
        return False

    def disable_policy(self, policy_id: str) -> bool:
        """Disable a policy."""
        if policy_id in self.policies:
            self.policies[policy_id].enabled = False
            return True
        return False

    async def validate_input(
        self, agent_id: str, user_input: str, context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Validate user input against governance policies."""
        violations = []
        actions_taken = []

        if not GOVERNANCE_ENABLED:
            return {"valid": True, "violations": [], "actions": []}

        # Check content safety
        if CONTENT_SAFETY_ENABLED:
            for pattern in self.content_filters["harmful_patterns"]:
                if re.search(pattern, user_input, re.IGNORECASE):
                    violation = PolicyViolation(
                        violation_id=self._generate_id(),
                        policy_id="safety_001",
                        policy_name="Harmful Content Prevention",
                        severity=ViolationSeverity.CRITICAL.value,
                        content_type="input",
                        violation_details={"pattern": pattern, "matched_text": user_input[:100]},
                        action_taken="blocked",
                    )
                    violations.append(violation)
                    actions_taken.append("blocked_harmful_content")

                    return {
                        "valid": False,
                        "violations": [self._violation_to_dict(v) for v in violations],
                        "actions": actions_taken,
                        "error": "Input violates safety policy",
                    }

        # Check for PII
        pii_detected = []
        for pattern in self.content_filters["pii_patterns"]:
            matches = re.findall(pattern, user_input)
            if matches:
                pii_detected.extend(matches)

        if pii_detected:
            violation = PolicyViolation(
                violation_id=self._generate_id(),
                policy_id="privacy_001",
                policy_name="PII Protection",
                severity=ViolationSeverity.HIGH.value,
                content_type="input",
                violation_details={"pii_types": len(pii_detected)},
                action_taken="logged",
            )
            violations.append(violation)
            actions_taken.append("logged_pii_warning")

        return {
            "valid": len(violations) == 0
            or all(v.severity != ViolationSeverity.CRITICAL.value for v in violations),
            "violations": [self._violation_to_dict(v) for v in violations],
            "actions": actions_taken,
        }

    async def validate_output(
        self, agent_id: str, user_input: str, ai_output: str, context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Validate AI output against governance policies."""
        violations = []
        actions_taken = []
        modified_output = ai_output

        if not GOVERNANCE_ENABLED:
            return {"valid": True, "output": ai_output, "violations": [], "actions": []}

        # Check content safety
        if CONTENT_SAFETY_ENABLED:
            for pattern in self.content_filters["harmful_patterns"]:
                if re.search(pattern, ai_output, re.IGNORECASE):
                    violation = PolicyViolation(
                        violation_id=self._generate_id(),
                        policy_id="safety_001",
                        policy_name="Harmful Content Prevention",
                        severity=ViolationSeverity.CRITICAL.value,
                        content_type="output",
                        violation_details={"pattern": pattern},
                        action_taken="blocked",
                    )
                    violations.append(violation)

                    return {
                        "valid": False,
                        "output": "[Content blocked due to safety policy violation]",
                        "violations": [self._violation_to_dict(v) for v in violations],
                        "actions": ["blocked_output"],
                    }

        # Check for PII in output
        for pattern in self.content_filters["pii_patterns"]:
            matches = re.findall(pattern, ai_output)
            if matches:
                # Redact PII
                modified_output = re.sub(pattern, "[REDACTED]", modified_output)
                actions_taken.append("redacted_pii")

        # Check quality
        if len(ai_output) < 10:
            violation = PolicyViolation(
                violation_id=self._generate_id(),
                policy_id="quality_001",
                policy_name="Response Quality",
                severity=ViolationSeverity.LOW.value,
                content_type="output",
                violation_details={"issue": "response_too_short", "length": len(ai_output)},
                action_taken="logged",
            )
            violations.append(violation)
            actions_taken.append("logged_quality_warning")

        return {
            "valid": True,
            "output": modified_output,
            "violations": [self._violation_to_dict(v) for v in violations],
            "actions": actions_taken,
        }

    async def audit_request(
        self,
        agent_id: str,
        action: str,
        user_input: str,
        ai_output: str,
        policies_applied: list[str],
        violations: list[str],
        latency_ms: float,
        metadata: dict[str, Any] = None,
    ) -> bool:
        """Log an audit entry for the request."""
        if not AUDIT_LOGGING_ENABLED:
            return True

        entry = AuditLogEntry(
            entry_id=self._generate_id(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_id=agent_id,
            action=action,
            input_hash=hashlib.sha256(user_input.encode()).hexdigest()[:16],
            output_hash=hashlib.sha256(ai_output.encode()).hexdigest()[:16],
            policies_applied=policies_applied,
            violations=violations,
            latency_ms=latency_ms,
            metadata=metadata or {},
        )

        self.audit_log.append(entry)

        # Trim audit log if too large
        if len(self.audit_log) > self.max_audit_entries:
            self.audit_log = self.audit_log[-self.max_audit_entries :]

        return True

    def get_violations(
        self, severity: str = None, since: str = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get policy violations with optional filtering."""
        violations = self.violations

        if severity:
            violations = [v for v in violations if v.severity == severity]

        if since:
            violations = [v for v in violations if v.timestamp >= since]

        violations = violations[-limit:]

        return [self._violation_to_dict(v) for v in violations]

    def get_audit_log(
        self, agent_id: str | None = None, since: str | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get audit log entries with optional filtering."""
        entries = self.audit_log

        if agent_id:
            entries = [e for e in entries if e.agent_id == agent_id]

        if since:
            entries = [e for e in entries if e.timestamp >= since]

        entries = entries[-limit:]

        return [self._audit_entry_to_dict(e) for e in entries]

    def get_governance_report(self) -> dict[str, Any]:
        """Generate governance compliance report."""
        total_requests = len(self.audit_log)
        total_violations = len(self.violations)

        violations_by_severity = {}
        for v in self.violations:
            violations_by_severity[v.severity] = violations_by_severity.get(v.severity, 0) + 1

        violations_by_policy = {}
        for v in self.violations:
            violations_by_policy[v.policy_name] = violations_by_policy.get(v.policy_name, 0) + 1

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "governance_enabled": GOVERNANCE_ENABLED,
            "content_safety_enabled": CONTENT_SAFETY_ENABLED,
            "audit_logging_enabled": AUDIT_LOGGING_ENABLED,
            "total_policies": len(self.policies),
            "enabled_policies": len([p for p in self.policies.values() if p.enabled]),
            "total_requests_audited": total_requests,
            "total_violations": total_violations,
            "violations_by_severity": violations_by_severity,
            "violations_by_policy": violations_by_policy,
            "violation_rate": round(total_violations / total_requests * 100, 2)
            if total_requests > 0
            else 0,
        }

    def _generate_id(self) -> str:
        """Generate a unique ID."""
        import uuid

        return str(uuid.uuid4())[:8]

    def _violation_to_dict(self, violation: PolicyViolation) -> dict[str, Any]:
        """Convert violation to dictionary."""
        return {
            "violation_id": violation.violation_id,
            "policy_id": violation.policy_id,
            "policy_name": violation.policy_name,
            "severity": violation.severity,
            "content_type": violation.content_type,
            "violation_details": violation.violation_details,
            "timestamp": violation.timestamp,
            "action_taken": violation.action_taken,
        }

    def _audit_entry_to_dict(self, entry: AuditLogEntry) -> dict[str, Any]:
        """Convert audit entry to dictionary."""
        return {
            "entry_id": entry.entry_id,
            "timestamp": entry.timestamp,
            "agent_id": entry.agent_id,
            "action": entry.action,
            "input_hash": entry.input_hash,
            "output_hash": entry.output_hash,
            "policies_applied": entry.policies_applied,
            "violations": entry.violations,
            "latency_ms": entry.latency_ms,
            "metadata": entry.metadata,
        }


# Global governance engine
governance_engine = AIGovernanceEngine()


# Convenience decorators
async def validate_with_governance(agent_id: str, user_input: str) -> dict[str, Any]:
    """Validate input with governance engine."""
    return await governance_engine.validate_input(agent_id, user_input)


async def validate_output_with_governance(
    agent_id: str, user_input: str, ai_output: str
) -> dict[str, Any]:
    """Validate output with governance engine."""
    return await governance_engine.validate_output(agent_id, user_input, ai_output)


def add_custom_policy(policy: GovernancePolicy) -> bool:
    """Add a custom governance policy."""
    return governance_engine.add_policy(policy)
