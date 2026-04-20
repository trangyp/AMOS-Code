"""Bias Detector — Bias Detection & Mitigation

Detects and mitigates biases in data, decisions, and algorithms
ensuring fair and equitable outcomes.

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional


class BiasType(Enum):
    """Types of bias."""

    SELECTION_BIAS = "selection_bias"
    CONFIRMATION_BIAS = "confirmation_bias"
    ALGORITHMIC_BIAS = "algorithmic_bias"
    REPRESENTATION_BIAS = "representation_bias"
    MEASUREMENT_BIAS = "measurement_bias"
    SOCIAL_BIAS = "social_bias"


class BiasSeverity(Enum):
    """Severity of bias detected."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class BiasFinding:
    """A specific bias finding."""

    bias_type: BiasType
    description: str
    severity: BiasSeverity
    affected_groups: list[str]
    confidence: float  # 0.0 to 1.0
    evidence: dict[str, Any]


@dataclass
class BiasReport:
    """Report of bias analysis."""

    generated_at: datetime
    total_findings: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    findings: list[BiasFinding]
    recommendations: list[str]


@dataclass
class MitigationAction:
    """Bias mitigation action."""

    action_id: str
    bias_type: BiasType
    description: str
    applied_at: datetime
    effectiveness: float  # 0.0 to 1.0


class BiasDetector:
    """Detects and mitigates biases in AMOS operations.

    Analyzes data, decisions, and algorithms for various types
    of bias and provides mitigation strategies.
    """

    def __init__(self, sensitive_attributes: list[str] = None):
        self.findings: list[BiasFinding] = []
        self.mitigations: list[MitigationAction] = []
        self.sensitive_attributes = sensitive_attributes or [
            "gender",
            "race",
            "age",
            "religion",
            "nationality",
            "disability",
            "socioeconomic",
        ]

    def analyze_data(self, data: dict[str, Any], context: str = "general") -> BiasReport:
        """Analyze data for bias."""
        findings = []

        # Check for representation bias
        rep_finding = self._check_representation_bias(data)
        if rep_finding:
            findings.append(rep_finding)

        # Check for selection bias
        sel_finding = self._check_selection_bias(data)
        if sel_finding:
            findings.append(sel_finding)

        # Check for measurement bias
        meas_finding = self._check_measurement_bias(data)
        if meas_finding:
            findings.append(meas_finding)

        self.findings.extend(findings)
        return self._generate_report(findings)

    def _check_representation_bias(self, data: dict[str, Any]) -> Optional[BiasFinding]:
        """Check for representation bias in data distribution."""
        # Check if sensitive attributes are under-represented
        for attr in self.sensitive_attributes:
            if attr in data:
                values = data[attr] if isinstance(data[attr], list) else [data[attr]]
                if len(values) < 10:  # Small sample size
                    return BiasFinding(
                        bias_type=BiasType.REPRESENTATION_BIAS,
                        description=f"Small sample size for {attr}: {len(values)} samples",
                        severity=BiasSeverity.MEDIUM,
                        affected_groups=[attr],
                        confidence=0.7,
                        evidence={"sample_size": len(values), "attribute": attr},
                    )
        return None

    def _check_selection_bias(self, data: dict[str, Any]) -> Optional[BiasFinding]:
        """Check for selection bias in data collection."""
        # Check for missing data patterns that might indicate selection bias
        missing_count = sum(1 for v in data.values() if v is None or v == "")
        total_count = len(data)
        if total_count > 0 and missing_count / total_count > 0.3:  # >30% missing
            return BiasFinding(
                bias_type=BiasType.SELECTION_BIAS,
                description=f"High missing data rate: {missing_count}/{total_count} ({missing_count / total_count:.1%})",
                severity=BiasSeverity.HIGH,
                affected_groups=["data_collection"],
                confidence=0.6,
                evidence={"missing": missing_count, "total": total_count},
            )
        return None

    def _check_measurement_bias(self, data: dict[str, Any]) -> Optional[BiasFinding]:
        """Check for measurement bias in data values."""
        # Check for extreme outliers that might indicate measurement issues
        numeric_values = [v for v in data.values() if isinstance(v, (int, float))]
        if numeric_values:
            import statistics

            try:
                mean_val = statistics.mean(numeric_values)
                stdev_val = statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0
                # Check for values > 3 standard deviations
                outliers = [v for v in numeric_values if abs(v - mean_val) > 3 * stdev_val]
                if outliers:
                    return BiasFinding(
                        bias_type=BiasType.MEASUREMENT_BIAS,
                        description=f"Detected {len(outliers)} outliers in numeric data",
                        severity=BiasSeverity.LOW,
                        affected_groups=["measurement"],
                        confidence=0.5,
                        evidence={"outliers": len(outliers), "mean": mean_val, "stdev": stdev_val},
                    )
            except statistics.StatisticsError:
                pass
        return None

    def _generate_report(self, findings: list[BiasFinding]) -> BiasReport:
        """Generate a bias report."""
        critical = sum(1 for f in findings if f.severity == BiasSeverity.CRITICAL)
        high = sum(1 for f in findings if f.severity == BiasSeverity.HIGH)
        medium = sum(1 for f in findings if f.severity == BiasSeverity.MEDIUM)
        low = sum(1 for f in findings if f.severity == BiasSeverity.LOW)

        recommendations = self._generate_recommendations(findings)

        return BiasReport(
            generated_at=datetime.now(UTC),
            total_findings=len(findings),
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            findings=findings,
            recommendations=recommendations,
        )

    def _generate_recommendations(self, findings: list[BiasFinding]) -> list[str]:
        """Generate mitigation recommendations."""
        recommendations = []

        for finding in findings:
            if finding.bias_type == BiasType.REPRESENTATION_BIAS:
                recommendations.append("Collect more representative data samples")
            elif finding.bias_type == BiasType.SELECTION_BIAS:
                recommendations.append("Review data selection criteria for fairness")
            elif finding.bias_type == BiasType.MEASUREMENT_BIAS:
                recommendations.append("Validate measurement instruments across groups")

        return recommendations

    def apply_mitigation(self, bias_type: BiasType, description: str) -> MitigationAction:
        """Record a bias mitigation action."""
        action = MitigationAction(
            action_id=f"mit_{len(self.mitigations) + 1}",
            bias_type=bias_type,
            description=description,
            applied_at=datetime.now(UTC),
            effectiveness=0.0,  # To be evaluated
        )

        self.mitigations.append(action)
        return action

    def get_findings_by_type(self, bias_type: BiasType) -> list[BiasFinding]:
        """Get findings by bias type."""
        return [f for f in self.findings if f.bias_type == bias_type]

    def get_high_severity_findings(self) -> list[BiasFinding]:
        """Get high and critical severity findings."""
        return [
            f for f in self.findings if f.severity in [BiasSeverity.HIGH, BiasSeverity.CRITICAL]
        ]


if __name__ == "__main__":
    print("Bias Detector Module")
    print("=" * 50)

    detector = BiasDetector()
    print(f"Sensitive attributes tracked: {len(detector.sensitive_attributes)}")

    # Test analysis
    test_data = {"sample": "data"}
    report = detector.analyze_data(test_data)
    print(f"Findings: {report.total_findings}")

    print("Bias Detector ready")
