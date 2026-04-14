"""Risk Governor — Risk Assessment & Governance

Assesses and governs risk for all organism activities.
Provides risk scoring, mitigation recommendations, and governance.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class RiskLevel(Enum):
    """Level of risk."""

    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    MINIMAL = 1
    UNKNOWN = 0


class RiskCategory(Enum):
    """Category of risk."""

    SECURITY = "security"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    LEGAL = "legal"
    REPUTATIONAL = "reputational"
    TECHNICAL = "technical"


@dataclass
class RiskAssessment:
    """Risk assessment for an activity or system."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    target: str = ""
    category: RiskCategory = RiskCategory.OPERATIONAL
    risk_level: RiskLevel = RiskLevel.UNKNOWN
    probability: float = 0.0  # 0-1
    impact: float = 0.0  # 0-1
    score: float = 0.0  # calculated: probability * impact * 100
    mitigations: list[str] = field(default_factory=list)
    residual_risk: RiskLevel = RiskLevel.UNKNOWN
    assessed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    assessor: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "category": self.category.value,
            "risk_level": self.risk_level.value,
            "residual_risk": self.residual_risk.value,
        }


class RiskGovernor:
    """Governs risk assessment and management.

    Provides risk scoring, assessment tracking, and governance
    recommendations for all organism activities.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        self.assessments: dict[str, RiskAssessment] = {}
        self.risk_thresholds: dict[RiskLevel, float] = {
            RiskLevel.CRITICAL: 0.9,
            RiskLevel.HIGH: 0.7,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.LOW: 0.3,
            RiskLevel.MINIMAL: 0.1,
        }

        self._load_assessments()

    def assess_risk(
        self,
        target: str,
        category: RiskCategory,
        probability: float,
        impact: float,
        mitigations: Optional[list[str]] = None,
        assessor: str = "system",
    ) -> RiskAssessment:
        """Assess risk for a target activity."""
        score = probability * impact * 100

        # Determine risk level
        if score >= 90:
            level = RiskLevel.CRITICAL
        elif score >= 70:
            level = RiskLevel.HIGH
        elif score >= 50:
            level = RiskLevel.MEDIUM
        elif score >= 30:
            level = RiskLevel.LOW
        else:
            level = RiskLevel.MINIMAL

        # Calculate residual risk based on mitigations
        mitigation_effectiveness = len(mitigations or []) * 0.15
        residual_score = max(0, score * (1 - mitigation_effectiveness))

        if residual_score >= 90:
            residual = RiskLevel.CRITICAL
        elif residual_score >= 70:
            residual = RiskLevel.HIGH
        elif residual_score >= 50:
            residual = RiskLevel.MEDIUM
        elif residual_score >= 30:
            residual = RiskLevel.LOW
        else:
            residual = RiskLevel.MINIMAL

        assessment = RiskAssessment(
            target=target,
            category=category,
            risk_level=level,
            probability=probability,
            impact=impact,
            score=score,
            mitigations=mitigations or [],
            residual_risk=residual,
            assessor=assessor,
        )

        self.assessments[assessment.id] = assessment
        self._save_assessments()
        return assessment

    def evaluate_action_risk(
        self,
        action_type: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Evaluate risk of taking an action."""
        # Base risk by action type
        base_risks = {
            "code_execution": (0.3, 0.6, RiskCategory.TECHNICAL),
            "file_deletion": (0.2, 0.9, RiskCategory.OPERATIONAL),
            "external_api": (0.4, 0.5, RiskCategory.SECURITY),
            "data_modification": (0.3, 0.7, RiskCategory.OPERATIONAL),
            "auto_deploy": (0.5, 0.6, RiskCategory.TECHNICAL),
        }

        prob, impact, category = base_risks.get(action_type, (0.3, 0.5, RiskCategory.OPERATIONAL))

        # Adjust based on context
        if context.get("production", False):
            impact *= 1.5
        if context.get("validated", False):
            prob *= 0.7
        if context.get("tested", False):
            prob *= 0.8

        # Cap values
        prob = min(1.0, prob)
        impact = min(1.0, impact)

        assessment = self.assess_risk(
            target=action_type,
            category=category,
            probability=prob,
            impact=impact,
            mitigations=context.get("mitigations", []),
        )

        return {
            "assessment_id": assessment.id,
            "risk_level": assessment.risk_level.value,
            "risk_name": assessment.risk_level.name,
            "score": assessment.score,
            "residual_risk": assessment.residual_risk.value,
            "approved": assessment.residual_risk.value < RiskLevel.HIGH.value,
        }

    def get_risk_summary(self) -> dict[str, Any]:
        """Get summary of all risk assessments."""
        if not self.assessments:
            return {"status": "no_assessments"}

        by_category: dict[str, list[RiskAssessment]] = {}
        for a in self.assessments.values():
            cat = a.category.value
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(a)

        summary = {
            "total_assessments": len(self.assessments),
            "by_category": {
                cat: {
                    "count": len(assessments),
                    "avg_score": sum(a.score for a in assessments) / len(assessments),
                    "high_risk": sum(1 for a in assessments if a.risk_level.value >= 4),
                }
                for cat, assessments in by_category.items()
            },
        }

        return summary

    def _load_assessments(self):
        """Load assessments from disk."""
        assessments_file = self.data_dir / "risk_assessments.json"
        if assessments_file.exists():
            try:
                data = json.loads(assessments_file.read_text())
                for a_data in data.get("assessments", []):
                    assessment = RiskAssessment(
                        id=a_data["id"],
                        target=a_data["target"],
                        category=RiskCategory(a_data["category"]),
                        risk_level=RiskLevel(a_data["risk_level"]),
                        probability=a_data["probability"],
                        impact=a_data["impact"],
                        score=a_data["score"],
                        mitigations=a_data.get("mitigations", []),
                        residual_risk=RiskLevel(a_data["residual_risk"]),
                        assessed_at=a_data.get("assessed_at", ""),
                        assessor=a_data.get("assessor", ""),
                    )
                    self.assessments[assessment.id] = assessment
            except Exception as e:
                print(f"[RISK] Error loading assessments: {e}")

    def _save_assessments(self):
        """Save assessments to disk."""
        assessments_file = self.data_dir / "risk_assessments.json"
        data = {
            "assessments": [a.to_dict() for a in self.assessments.values()],
            "saved_at": datetime.utcnow().isoformat(),
        }
        assessments_file.write_text(json.dumps(data, indent=2))

    def list_assessments(self) -> list[dict[str, Any]]:
        """List all risk assessments."""
        return [a.to_dict() for a in self.assessments.values()]

    def get_status(self) -> dict[str, Any]:
        """Get governor status."""
        summary = self.get_risk_summary()
        critical = sum(1 for a in self.assessments.values() if a.risk_level == RiskLevel.CRITICAL)
        high = sum(1 for a in self.assessments.values() if a.risk_level == RiskLevel.HIGH)

        return {
            **summary,
            "critical_risks": critical,
            "high_risks": high,
            "risk_categories": [c.value for c in RiskCategory],
        }


_GOVERNOR: Optional[RiskGovernor] = None


def get_risk_governor(data_dir: Optional[Path] = None) -> RiskGovernor:
    """Get or create global risk governor."""
    global _GOVERNOR
    if _GOVERNOR is None:
        _GOVERNOR = RiskGovernor(data_dir)
    return _GOVERNOR
