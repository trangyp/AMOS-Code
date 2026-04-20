"""Regulatory Scanner — Regulatory compliance monitoring

Scans for relevant regulations, compliance requirements,
and tracks regulatory changes affecting AMOS operations.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC, timedelta
from enum import Enum
from pathlib import Path
from typing import Any


class RegulationType(Enum):
    """Type of regulation."""

    DATA_PRIVACY = "data_privacy"
    AI_ETHICS = "ai_ethics"
    CYBERSECURITY = "cybersecurity"
    FINANCIAL = "financial"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    CONSUMER_PROTECTION = "consumer_protection"
    ENVIRONMENTAL = "environmental"
    LABOR = "labor"


class ComplianceLevel(Enum):
    """Compliance level for regulations."""

    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    COMPLIANT = "compliant"
    EXCEEDED = "exceeded"


class ImpactLevel(Enum):
    """Impact level of regulation."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Regulation:
    """A regulation or compliance requirement."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    regulation_type: RegulationType = RegulationType.AI_ETHICS
    jurisdiction: str = ""  # US, EU, Global, etc.
    description: str = ""
    effective_date: str = ""
    compliance_deadline: str = None
    requirements: list[str] = field(default_factory=list)
    impact_level: ImpactLevel = ImpactLevel.MEDIUM
    applicable: bool = True
    notes: str = ""
    source_url: str = ""
    last_updated: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "regulation_type": self.regulation_type.value,
            "impact_level": self.impact_level.value,
        }


@dataclass
class ComplianceAssessment:
    """Assessment of compliance with a regulation."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    regulation_id: str = ""
    compliance_level: ComplianceLevel = ComplianceLevel.NON_COMPLIANT
    gaps: list[str] = field(default_factory=list)
    actions_required: list[str] = field(default_factory=list)
    assessed_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    assessed_by: str = ""
    next_review: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "compliance_level": self.compliance_level.value,
        }


class RegulatoryScanner:
    """Scans and monitors regulatory landscape.

    Tracks regulations, assesses compliance, and
    alerts on regulatory changes.
    """

    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.regulations: list[Regulation] = []
        self.assessments: list[ComplianceAssessment] = []

        self._load_data()

        # Initialize with sample regulations if empty
        if not self.regulations:
            self._init_sample_regulations()

    def _load_data(self):
        """Load regulatory data from disk."""
        data_file = self.data_dir / "regulations.json"
        if data_file.exists():
            try:
                data = json.loads(data_file.read_text())
                for r_data in data.get("regulations", []):
                    reg = Regulation(
                        id=r_data["id"],
                        title=r_data["title"],
                        regulation_type=RegulationType(r_data["regulation_type"]),
                        jurisdiction=r_data.get("jurisdiction", ""),
                        description=r_data.get("description", ""),
                        effective_date=r_data.get("effective_date", ""),
                        compliance_deadline=r_data.get("compliance_deadline"),
                        requirements=r_data.get("requirements", []),
                        impact_level=ImpactLevel(r_data["impact_level"]),
                        applicable=r_data.get("applicable", True),
                        notes=r_data.get("notes", ""),
                        source_url=r_data.get("source_url", ""),
                        last_updated=r_data["last_updated"],
                    )
                    self.regulations.append(reg)

                for a_data in data.get("assessments", []):
                    assessment = ComplianceAssessment(
                        id=a_data["id"],
                        regulation_id=a_data["regulation_id"],
                        compliance_level=ComplianceLevel(a_data["compliance_level"]),
                        gaps=a_data.get("gaps", []),
                        actions_required=a_data.get("actions_required", []),
                        assessed_at=a_data["assessed_at"],
                        assessed_by=a_data.get("assessed_by", ""),
                        next_review=a_data.get("next_review", ""),
                    )
                    self.assessments.append(assessment)
            except Exception as e:
                print(f"[REGULATORY] Error loading data: {e}")

    def save(self):
        """Save regulatory data to disk."""
        data_file = self.data_dir / "regulations.json"
        data = {
            "saved_at": datetime.now(UTC).isoformat(),
            "regulations": [r.to_dict() for r in self.regulations],
            "assessments": [a.to_dict() for a in self.assessments],
        }
        data_file.write_text(json.dumps(data, indent=2))

    def _init_sample_regulations(self):
        """Initialize with sample regulations."""
        samples = [
            Regulation(
                title="GDPR Data Protection",
                regulation_type=RegulationType.DATA_PRIVACY,
                jurisdiction="EU",
                description="General Data Protection Regulation for EU citizens",
                effective_date="2018-05-25",
                requirements=[
                    "Obtain consent for data processing",
                    "Provide data portability",
                    "Enable right to erasure",
                    "Maintain data breach notification",
                ],
                impact_level=ImpactLevel.HIGH,
            ),
            Regulation(
                title="AI Ethics Guidelines",
                regulation_type=RegulationType.AI_ETHICS,
                jurisdiction="Global",
                description="Guidelines for ethical AI development",
                effective_date="2023-01-01",
                requirements=[
                    "Ensure transparency in AI decisions",
                    "Prevent bias in training data",
                    "Maintain human oversight",
                    "Respect privacy and autonomy",
                ],
                impact_level=ImpactLevel.HIGH,
            ),
            Regulation(
                title="Software License Compliance",
                regulation_type=RegulationType.INTELLECTUAL_PROPERTY,
                jurisdiction="Global",
                description="Compliance with open source and proprietary licenses",
                effective_date="2020-01-01",
                requirements=[
                    "Track all dependencies and licenses",
                    "Comply with license terms",
                    "Attribute original authors",
                ],
                impact_level=ImpactLevel.MEDIUM,
            ),
        ]

        self.regulations.extend(samples)
        self.save()

    def add_regulation(self, regulation: Regulation) -> Regulation:
        """Add a new regulation."""
        self.regulations.append(regulation)
        self.save()
        return regulation

    def get_regulation(self, reg_id: str) -> Regulation:
        """Get a regulation by ID."""
        for reg in self.regulations:
            if reg.id == reg_id:
                return reg
        return None

    def assess_compliance(
        self,
        regulation_id: str,
        level: ComplianceLevel,
        gaps: list[str],
        actions: list[str],
    ) -> ComplianceAssessment:
        """Record a compliance assessment."""
        reg = self.get_regulation(regulation_id)
        if not reg:
            return None

        # Calculate next review date
        next_review = (datetime.now(UTC) + timedelta(days=90)).isoformat()

        assessment = ComplianceAssessment(
            regulation_id=regulation_id,
            compliance_level=level,
            gaps=gaps,
            actions_required=actions,
            next_review=next_review,
        )
        self.assessments.append(assessment)
        self.save()
        return assessment

    def get_upcoming_deadlines(self, days: int = 30) -> list[dict[str, Any]]:
        """Get regulations with upcoming compliance deadlines."""
        cutoff = (datetime.now(UTC) + timedelta(days=days)).isoformat()

        upcoming = []
        for reg in self.regulations:
            if reg.applicable and reg.compliance_deadline and reg.compliance_deadline < cutoff:
                upcoming.append(
                    {
                        "regulation": reg.to_dict(),
                        "days_until": (
                            datetime.fromisoformat(reg.compliance_deadline) - datetime.now(UTC)
                        ).days,
                    }
                )

        return sorted(upcoming, key=lambda x: x["days_until"])

    def get_compliance_summary(self) -> dict[str, Any]:
        """Get overall compliance summary."""
        by_level = {
            "compliant": 0,
            "partial": 0,
            "non_compliant": 0,
        }

        # Count latest assessment per regulation
        latest = {}
        for a in self.assessments:
            if a.regulation_id not in latest or a.assessed_at > latest[a.regulation_id].assessed_at:
                latest[a.regulation_id] = a

        for a in latest.values():
            l = a.compliance_level.value
            if l in by_level:
                by_level[l] += 1

        total_applicable = len([r for r in self.regulations if r.applicable])

        return {
            "total_regulations": len(self.regulations),
            "applicable_regulations": total_applicable,
            "assessed": len(latest),
            "by_compliance_level": by_level,
            "overall_compliance_rate": by_level["compliant"] / total_applicable
            if total_applicable > 0
            else 0,
            "high_impact_regulations": len(
                [r for r in self.regulations if r.impact_level == ImpactLevel.HIGH and r.applicable]
            ),
        }

    def get_applicable_regulations(
        self,
        jurisdiction: str = None,
        reg_type: RegulationType = None,
    ) -> list[dict[str, Any]]:
        """Get applicable regulations."""
        regs = [r for r in self.regulations if r.applicable]

        if jurisdiction:
            regs = [r for r in regs if r.jurisdiction == jurisdiction]

        if reg_type:
            regs = [r for r in regs if r.regulation_type == reg_type]

        return [r.to_dict() for r in regs]

    def check_action_compliance(self, action_description: str) -> dict[str, Any]:
        """Check if an action might violate regulations."""
        risks = []

        # Check for data privacy risks
        privacy_keywords = ["personal data", "user data", "private information"]
        if any(kw in action_description.lower() for kw in privacy_keywords):
            privacy_regs = [
                r for r in self.regulations if r.regulation_type == RegulationType.DATA_PRIVACY
            ]
            for reg in privacy_regs:
                risks.append(f"Potential GDPR/privacy impact - review {reg.title}")

        # Check for AI ethics risks
        ai_keywords = ["automated decision", "AI model", "algorithmic"]
        if any(kw in action_description.lower() for kw in ai_keywords):
            ethics_regs = [
                r for r in self.regulations if r.regulation_type == RegulationType.AI_ETHICS
            ]
            for reg in ethics_regs:
                risks.append(f"AI ethics consideration - review {reg.title}")

        return {
            "action": action_description,
            "risk_count": len(risks),
            "risks": risks,
            "requires_review": len(risks) > 0,
        }


# Global instance
_SCANNER: RegulatoryScanner = None


def get_regulatory_scanner(data_dir: Path = None) -> RegulatoryScanner:
    """Get or create global regulatory scanner."""
    global _SCANNER
    if _SCANNER is None:
        _SCANNER = RegulatoryScanner(data_dir)
    return _SCANNER


if __name__ == "__main__":
    print("Regulatory Scanner (11_LEGAL_BRAIN)")
    print("=" * 40)

    scanner = get_regulatory_scanner()

    print(f"\nRegulations tracked: {len(scanner.regulations)}")

    print("\nCompliance Summary:")
    summary = scanner.get_compliance_summary()
    print(f"  Total regulations: {summary['total_regulations']}")
    print(f"  High impact: {summary['high_impact_regulations']}")

    print("\nApplicable regulations:")
    for reg in scanner.get_applicable_regulations():
        print(f"  - {reg['title']} ({reg['jurisdiction']})")
