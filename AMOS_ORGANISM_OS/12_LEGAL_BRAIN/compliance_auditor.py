"""Compliance Auditor — Compliance Checking & Reporting

Audits actions and configurations for compliance with
policies, regulations, and standards.
"""

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class ComplianceLevel(Enum):
    """Level of compliance."""

    FULL = "full"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"


class AuditType(Enum):
    """Type of audit."""

    SECURITY = "security"
    PRIVACY = "privacy"
    OPERATIONAL = "operational"
    LEGAL = "legal"
    COMPREHENSIVE = "comprehensive"


@dataclass
class AuditFinding:
    """A single audit finding."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    category: str = ""
    severity: int = 1  # 1-5
    description: str = ""
    recommendation: str = ""
    reference: str = ""  # Policy/regulation reference

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuditResult:
    """Result of a compliance audit."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    audit_type: AuditType = AuditType.COMPREHENSIVE
    target: str = ""
    compliance_level: ComplianceLevel = ComplianceLevel.UNKNOWN
    score: float = 0.0  # 0-100
    findings: list[AuditFinding] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    duration_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "audit_type": self.audit_type.value,
            "compliance_level": self.compliance_level.value,
            "findings": [f.to_dict() for f in self.findings],
        }


class ComplianceAuditor:
    """Performs compliance audits and generates reports.

    Checks configurations, actions, and states against
    compliance requirements and policies.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        self.audit_history: list[AuditResult] = []
        self.compliance_standards: dict[str, dict[str, Any]] = {}

        self._init_default_standards()

    def _init_default_standards(self):
        """Initialize default compliance standards."""
        self.compliance_standards = {
            "security_baseline": {
                "description": "Basic security requirements",
                "requirements": [
                    "authentication_required",
                    "access_controls",
                    "encryption_at_rest",
                ],
            },
            "privacy_gdpr": {
                "description": "GDPR privacy requirements",
                "requirements": [
                    "data_minimization",
                    "purpose_limitation",
                    "consent_management",
                    "right_to_deletion",
                ],
            },
            "operational_sla": {
                "description": "Operational SLA requirements",
                "requirements": [
                    "uptime_99_9",
                    "response_time_1s",
                    "backup_daily",
                ],
            },
        }

    def audit(
        self,
        target: str,
        audit_type: AuditType = AuditType.COMPREHENSIVE,
        context: dict[str, Any] = None,
    ) -> AuditResult:
        """Perform a compliance audit."""
        start_time = datetime.now(UTC)

        findings = []
        score = 100.0

        # Perform checks based on audit type
        if audit_type in (AuditType.SECURITY, AuditType.COMPREHENSIVE):
            security_findings = self._audit_security(context)
            findings.extend(security_findings)

        if audit_type in (AuditType.PRIVACY, AuditType.COMPREHENSIVE):
            privacy_findings = self._audit_privacy(context)
            findings.extend(privacy_findings)

        if audit_type in (AuditType.OPERATIONAL, AuditType.COMPREHENSIVE):
            operational_findings = self._audit_operational(context)
            findings.extend(operational_findings)

        # Calculate score based on findings
        for finding in findings:
            score -= finding.severity * 5  # Deduct points

        score = max(0.0, min(100.0, score))

        # Determine compliance level
        if score >= 90:
            level = ComplianceLevel.FULL
        elif score >= 70:
            level = ComplianceLevel.PARTIAL
        else:
            level = ComplianceLevel.NON_COMPLIANT

        duration = (datetime.now(UTC) - start_time).total_seconds()

        result = AuditResult(
            audit_type=audit_type,
            target=target,
            compliance_level=level,
            score=score,
            findings=findings,
            duration_seconds=duration,
        )

        self.audit_history.append(result)
        return result

    def _audit_security(self, context: dict[str, Any]) -> list[AuditFinding]:
        """Perform security audit."""
        findings = []

        # Check authentication
        if not context or not context.get("authentication_enabled", False):
            findings.append(
                AuditFinding(
                    category="security",
                    severity=5,
                    description="Authentication not enabled",
                    recommendation="Enable authentication for all access",
                    reference="security_baseline:authentication_required",
                )
            )

        # Check access controls
        if not context or not context.get("access_controls", False):
            findings.append(
                AuditFinding(
                    category="security",
                    severity=4,
                    description="Access controls not configured",
                    recommendation="Implement role-based access control",
                    reference="security_baseline:access_controls",
                )
            )

        return findings

    def _audit_privacy(self, context: dict[str, Any]) -> list[AuditFinding]:
        """Perform privacy audit."""
        findings = []

        # Check data minimization
        if context and context.get("collects_pii", False):
            if not context.get("pii_protection", False):
                findings.append(
                    AuditFinding(
                        category="privacy",
                        severity=5,
                        description="PII collected without protection",
                        recommendation="Implement PII encryption and access controls",
                        reference="privacy_gdpr:data_minimization",
                    )
                )

        return findings

    def _audit_operational(self, context: dict[str, Any]) -> list[AuditFinding]:
        """Perform operational audit."""
        findings = []

        # Check backups
        if not context or not context.get("backups_enabled", False):
            findings.append(
                AuditFinding(
                    category="operational",
                    severity=3,
                    description="Backups not enabled",
                    recommendation="Enable daily automated backups",
                    reference="operational_sla:backup_daily",
                )
            )

        return findings

    def get_audit_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent audit history."""
        return [a.to_dict() for a in self.audit_history[-limit:]]

    def get_compliance_report(self) -> dict[str, Any]:
        """Generate comprehensive compliance report."""
        if not self.audit_history:
            return {"status": "no_audits_performed"}

        latest = self.audit_history[-1]
        avg_score = sum(a.score for a in self.audit_history) / len(self.audit_history)

        return {
            "latest_audit": latest.to_dict(),
            "total_audits": len(self.audit_history),
            "average_score": round(avg_score, 2),
            "standards_checked": list(self.compliance_standards.keys()),
        }

    def get_status(self) -> dict[str, Any]:
        """Get auditor status."""
        return {
            "total_audits": len(self.audit_history),
            "standards": list(self.compliance_standards.keys()),
            "audit_types": [t.value for t in AuditType],
            "latest_score": self.audit_history[-1].score if self.audit_history else None,
        }


_AUDITOR: Optional[ComplianceAuditor] = None


def get_compliance_auditor(data_dir: Optional[Path] = None) -> ComplianceAuditor:
    """Get or create global compliance auditor."""
    global _AUDITOR
    if _AUDITOR is None:
        _AUDITOR = ComplianceAuditor(data_dir)
    return _AUDITOR
