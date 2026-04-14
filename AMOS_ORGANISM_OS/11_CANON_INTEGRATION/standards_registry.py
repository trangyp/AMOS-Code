"""Standards Registry — Standards & Compliance Tracking

Maintains registry of industry standards, compliance requirements,
and tracks AMOS compliance status.

Owner: Trang
Version: 1.0.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class StandardType(Enum):
    """Types of standards."""

    ISO = "iso"
    IEEE = "ieee"
    W3C = "w3c"
    IETF = "ietf"
    INDUSTRY = "industry"
    INTERNAL = "internal"


class ComplianceStatus(Enum):
    """Compliance status levels."""

    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"
    PENDING_REVIEW = "pending_review"


@dataclass
class Standard:
    """Standard definition."""

    id: str
    name: str
    standard_type: StandardType
    version: str
    description: str
    requirements: list[str]
    reference_url: Optional[str] = None
    effective_date: Optional[datetime] = None


@dataclass
class ComplianceRecord:
    """Compliance record for a standard."""

    standard_id: str
    status: ComplianceStatus
    assessed_at: datetime
    assessed_by: str
    notes: str
    evidence: dict[str, Any] = field(default_factory=dict)
    next_review_date: Optional[datetime] = None


class StandardsRegistry:
    """Registry of standards and compliance tracking.

    Manages standard definitions, tracks compliance status,
    and generates compliance reports.
    """

    def __init__(self):
        self.standards: dict[str, Standard] = {}
        self.compliance_records: dict[str, ComplianceRecord] = {}
        self._load_default_standards()

    def _load_default_standards(self):
        """Load default standards."""
        default_standards = [
            Standard(
                id="STD-001",
                name="ISO 27001",
                standard_type=StandardType.ISO,
                version="2013",
                description="Information Security Management",
                requirements=["Risk assessment", "Security controls", "Monitoring"],
            ),
            Standard(
                id="STD-002",
                name="ISO 9001",
                standard_type=StandardType.ISO,
                version="2015",
                description="Quality Management Systems",
                requirements=["Quality policy", "Process approach", "Continuous improvement"],
            ),
            Standard(
                id="STD-003",
                name="AMOS Canonical Standards",
                standard_type=StandardType.INTERNAL,
                version="1.0",
                description="AMOS internal canonical requirements",
                requirements=["Deterministic execution", "Auditability", "Human confirmation"],
            ),
        ]

        for standard in default_standards:
            self.standards[standard.id] = standard

    def register_standard(self, standard: Standard) -> bool:
        """Register a new standard."""
        if standard.id in self.standards:
            return False
        self.standards[standard.id] = standard
        return True

    def assess_compliance(
        self,
        standard_id: str,
        status: ComplianceStatus,
        assessed_by: str,
        notes: str = "",
        evidence: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Record a compliance assessment."""
        if standard_id not in self.standards:
            return False

        record = ComplianceRecord(
            standard_id=standard_id,
            status=status,
            assessed_at=datetime.utcnow(),
            assessed_by=assessed_by,
            notes=notes,
            evidence=evidence or {},
        )

        self.compliance_records[standard_id] = record
        return True

    def get_compliance_status(self, standard_id: str) -> Optional[ComplianceStatus]:
        """Get compliance status for a standard."""
        if standard_id not in self.compliance_records:
            return None
        return self.compliance_records[standard_id].status

    def get_standard(self, standard_id: str) -> Optional[Standard]:
        """Get a standard definition."""
        return self.standards.get(standard_id)

    def list_standards(self, standard_type: Optional[StandardType] = None) -> list[Standard]:
        """List all standards, optionally filtered by type."""
        standards = list(self.standards.values())
        if standard_type:
            standards = [s for s in standards if s.standard_type == standard_type]
        return standards

    def get_compliance_summary(self) -> dict[str, int]:
        """Get summary of compliance status across all standards."""
        summary = {
            "total": len(self.standards),
            "compliant": 0,
            "partial": 0,
            "non_compliant": 0,
            "not_applicable": 0,
            "pending_review": 0,
            "not_assessed": 0,
        }

        for standard_id in self.standards:
            if standard_id in self.compliance_records:
                status = self.compliance_records[standard_id].status
                if status == ComplianceStatus.COMPLIANT:
                    summary["compliant"] += 1
                elif status == ComplianceStatus.PARTIAL:
                    summary["partial"] += 1
                elif status == ComplianceStatus.NON_COMPLIANT:
                    summary["non_compliant"] += 1
                elif status == ComplianceStatus.NOT_APPLICABLE:
                    summary["not_applicable"] += 1
                elif status == ComplianceStatus.PENDING_REVIEW:
                    summary["pending_review"] += 1
            else:
                summary["not_assessed"] += 1

        return summary

    def get_non_compliant_standards(self) -> list[Standard]:
        """Get all standards that are not fully compliant."""
        non_compliant = []
        for standard_id, record in self.compliance_records.items():
            if record.status in [ComplianceStatus.NON_COMPLIANT, ComplianceStatus.PARTIAL]:
                standard = self.standards.get(standard_id)
                if standard:
                    non_compliant.append(standard)
        return non_compliant


if __name__ == "__main__":
    print("Standards Registry Module")
    print("=" * 50)

    registry = StandardsRegistry()
    print(f"Loaded {len(registry.standards)} standards")

    # Assess compliance
    registry.assess_compliance(
        "STD-001",
        ComplianceStatus.COMPLIANT,
        "System",
        "All security controls implemented",
    )

    registry.assess_compliance(
        "STD-002",
        ComplianceStatus.PARTIAL,
        "System",
        "Some quality processes need improvement",
    )

    summary = registry.get_compliance_summary()
    print("\nCompliance Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("\nStandards Registry ready")
