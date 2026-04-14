"""IMMUNE SYSTEM — Core safety and validation engine for AMOS.

The immune system acts as a gatekeeper for all organism actions.
It validates, audits, and can block potentially harmful operations.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable


class RiskLevel(Enum):
    SAFE = "safe"  # No risk, auto-approve
    LOW = "low"  # Minimal risk, log only
    MEDIUM = "medium"  # Moderate risk, notify
    HIGH = "high"  # Significant risk, require approval
    CRITICAL = "critical"  # Severe risk, block without override


class ActionType(Enum):
    READ = "read"  # File reads, non-destructive
    WRITE = "write"  # File writes, destructive
    EXECUTE = "execute"  # Code/command execution
    NETWORK = "network"  # Network operations
    DELETE = "delete"  # File deletion
    SYSTEM = "system"  # System-level operations


@dataclass
class SafetyPolicy:
    """A safety policy rule."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    action_types: list[ActionType] = field(default_factory=list)
    allowed: bool = True
    requires_approval: bool = False
    risk_level: RiskLevel = RiskLevel.SAFE
    conditions: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class AuditLog:
    """An audit log entry."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    action: str = ""
    action_type: ActionType = ActionType.READ
    target: str = ""
    source: str = ""
    risk_level: RiskLevel = RiskLevel.SAFE
    decision: str = ""  # approved, blocked, pending
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "action_type": self.action_type.value,
            "risk_level": self.risk_level.value,
        }


@dataclass
class ValidationResult:
    """Result of a validation check."""

    approved: bool = False
    risk_level: RiskLevel = RiskLevel.SAFE
    reason: str = ""
    requires_approval: bool = False
    audit_log_id: str = ""


class ImmuneSystem:
    """The immune system validates all actions before execution.

    Responsibilities:
    - Validate actions against safety policies
    - Detect threats and anomalies
    - Maintain audit logs
    - Enforce compliance rules
    - Block dangerous operations
    """

    AUDIT_DIR = Path(__file__).parent / "audit_logs"

    # Dangerous patterns that should be blocked
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf\s+/",
        r"rm\s+-rf\s+/\*",
        r"dd\s+if=/dev/zero",
        r":\(\)\s*{\s*:\|:&\s*};:",
        r"mkfs\.",
        r">\s*/dev/sda",
        r"mv\s+/\s+/dev/null",
        r"chmod\s+-R\s+777\s+/",
        r"chown\s+-R",
        r"sudo\s+rm",
    ]

    def __init__(self):
        self._policies: list[SafetyPolicy] = []
        self._audit_logs: list[AuditLog] = []
        self._threat_history: list[dict] = []
        self._validators: dict[ActionType, Callable] = {}
        self.AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        self._setup_default_policies()
        self._register_validators()

    def _setup_default_policies(self):
        """Set up default safety policies."""
        self._policies = [
            SafetyPolicy(
                name="read_only",
                description="Read operations are safe",
                action_types=[ActionType.READ],
                allowed=True,
                requires_approval=False,
                risk_level=RiskLevel.SAFE,
            ),
            SafetyPolicy(
                name="write_caution",
                description="Write operations require caution",
                action_types=[ActionType.WRITE],
                allowed=True,
                requires_approval=True,
                risk_level=RiskLevel.MEDIUM,
                conditions={"max_size_mb": 100},
            ),
            SafetyPolicy(
                name="execute_restricted",
                description="Execution is restricted",
                action_types=[ActionType.EXECUTE],
                allowed=True,
                requires_approval=True,
                risk_level=RiskLevel.HIGH,
            ),
            SafetyPolicy(
                name="delete_protected",
                description="Deletion requires explicit approval",
                action_types=[ActionType.DELETE],
                allowed=True,
                requires_approval=True,
                risk_level=RiskLevel.HIGH,
            ),
            SafetyPolicy(
                name="system_blocked",
                description="System operations are blocked",
                action_types=[ActionType.SYSTEM],
                allowed=False,
                requires_approval=False,
                risk_level=RiskLevel.CRITICAL,
            ),
        ]

    def _register_validators(self):
        """Register validators for each action type."""
        self._validators = {
            ActionType.READ: self._validate_read,
            ActionType.WRITE: self._validate_write,
            ActionType.EXECUTE: self._validate_execute,
            ActionType.DELETE: self._validate_delete,
            ActionType.NETWORK: self._validate_network,
            ActionType.SYSTEM: self._validate_system,
        }

    def validate(
        self,
        action: str,
        action_type: ActionType,
        target: str = "",
        source: str = "",
        metadata: dict = None,
    ) -> ValidationResult:
        """Validate an action before execution."""
        # Determine risk level
        risk = self._assess_risk(action, action_type, target)

        # Find applicable policies
        policies = [p for p in self._policies if action_type in p.action_types]

        # Default deny if no policies
        if not policies:
            result = ValidationResult(
                approved=False,
                risk_level=RiskLevel.CRITICAL,
                reason="No policy found for action type",
            )
        else:
            # Check if any policy blocks
            blocking = [p for p in policies if not p.allowed]
            if blocking:
                result = ValidationResult(
                    approved=False,
                    risk_level=risk,
                    reason=f"Blocked by policy: {blocking[0].name}",
                )
            else:
                # Check if approval required
                needs_approval = any(p.requires_approval for p in policies)
                result = ValidationResult(
                    approved=not needs_approval,
                    risk_level=risk,
                    requires_approval=needs_approval,
                    reason="Approved with caution" if needs_approval else "Approved",
                )

        # Run type-specific validator
        validator = self._validators.get(action_type)
        if validator:
            validator_result = validator(action, target)
            if not validator_result.approved:
                result = validator_result

        # Log the decision
        log = AuditLog(
            action=action,
            action_type=action_type,
            target=target,
            source=source,
            risk_level=result.risk_level,
            decision="approved" if result.approved else "blocked",
            reason=result.reason,
            metadata=metadata or {},
        )
        self._audit_logs.append(log)
        self._persist_audit(log)
        result.audit_log_id = log.id

        return result

    def _assess_risk(self, action: str, action_type: ActionType, target: str) -> RiskLevel:
        """Assess the risk level of an action."""
        # Check for dangerous patterns in execute actions
        if action_type == ActionType.EXECUTE:
            import re

            for pattern in self.DANGEROUS_PATTERNS:
                if re.search(pattern, action, re.IGNORECASE):
                    return RiskLevel.CRITICAL

        # Check target sensitivity
        sensitive_paths = ["/etc", "/sys", "/proc", "/dev", "~/.ssh", ".env"]
        if any(s in target for s in sensitive_paths):
            return RiskLevel.HIGH

        # Default based on action type
        risk_map = {
            ActionType.READ: RiskLevel.SAFE,
            ActionType.WRITE: RiskLevel.MEDIUM,
            ActionType.EXECUTE: RiskLevel.HIGH,
            ActionType.DELETE: RiskLevel.HIGH,
            ActionType.NETWORK: RiskLevel.MEDIUM,
            ActionType.SYSTEM: RiskLevel.CRITICAL,
        }
        return risk_map.get(action_type, RiskLevel.MEDIUM)

    def _validate_read(self, action: str, target: str) -> ValidationResult:
        """Validate read operations."""
        return ValidationResult(approved=True, risk_level=RiskLevel.SAFE)

    def _validate_write(self, action: str, target: str) -> ValidationResult:
        """Validate write operations."""
        # Check if file exists (overwrite warning)
        if Path(target).exists():
            return ValidationResult(
                approved=True,
                requires_approval=True,
                risk_level=RiskLevel.MEDIUM,
                reason="File exists - will overwrite",
            )
        return ValidationResult(
            approved=True,
            requires_approval=False,
            risk_level=RiskLevel.LOW,
        )

    def _validate_execute(self, action: str, target: str) -> ValidationResult:
        """Validate execute operations."""
        import re

        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, action, re.IGNORECASE):
                return ValidationResult(
                    approved=False,
                    risk_level=RiskLevel.CRITICAL,
                    reason=f"Dangerous pattern detected: {pattern}",
                )
        return ValidationResult(
            approved=True,
            requires_approval=True,
            risk_level=RiskLevel.HIGH,
        )

    def _validate_delete(self, action: str, target: str) -> ValidationResult:
        """Validate delete operations."""
        if not Path(target).exists():
            return ValidationResult(
                approved=False,
                risk_level=RiskLevel.LOW,
                reason="Target does not exist",
            )
        return ValidationResult(
            approved=True,
            requires_approval=True,
            risk_level=RiskLevel.HIGH,
            reason="Deletion requires approval",
        )

    def _validate_network(self, action: str, target: str) -> ValidationResult:
        """Validate network operations."""
        return ValidationResult(
            approved=True,
            requires_approval=True,
            risk_level=RiskLevel.MEDIUM,
        )

    def _validate_system(self, action: str, target: str) -> ValidationResult:
        """Validate system operations."""
        return ValidationResult(
            approved=False,
            risk_level=RiskLevel.CRITICAL,
            reason="System operations are blocked by default",
        )

    def _persist_audit(self, log: AuditLog):
        """Persist audit log to disk."""
        filepath = self.AUDIT_DIR / f"{log.id}.json"
        filepath.write_text(json.dumps(log.to_dict(), indent=2))

    def get_audit_logs(
        self,
        action_type: ActionType = None,
        risk_level: RiskLevel = None,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Get audit logs with filtering."""
        logs = self._audit_logs
        if action_type:
            logs = [l for l in logs if l.action_type == action_type]
        if risk_level:
            logs = [l for l in logs if l.risk_level == risk_level]
        return logs[-limit:]

    def add_policy(self, policy: SafetyPolicy):
        """Add a new safety policy."""
        self._policies.append(policy)

    def remove_policy(self, policy_id: str) -> bool:
        """Remove a policy by ID."""
        for i, p in enumerate(self._policies):
            if p.id == policy_id:
                self._policies.pop(i)
                return True
        return False

    def status(self) -> dict[str, Any]:
        """Get immune system status."""
        risk_counts = {r: 0 for r in RiskLevel}
        for log in self._audit_logs:
            risk_counts[log.risk_level] += 1

        return {
            "total_policies": len(self._policies),
            "total_audit_logs": len(self._audit_logs),
            "by_risk_level": {k.value: v for k, v in risk_counts.items()},
            "policies": [p.name for p in self._policies],
        }
