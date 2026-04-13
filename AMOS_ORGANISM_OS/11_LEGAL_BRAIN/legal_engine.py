#!/usr/bin/env python3
"""
AMOS Legal Engine (11_LEGAL_BRAIN)
====================================

Legal compliance, governance enforcement, and risk assessment.
Ensures all actions comply with legal constraints and operator governance.

Owner: Trang
Version: 1.0.0
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class ComplianceRule:
    """A compliance rule to check against."""
    id: str
    category: str  # legal, governance, ethical, technical
    description: str
    check_type: str  # regex, keyword, pattern, custom
    check_value: Any
    severity: str  # info, warning, error, critical
    enabled: bool = True


@dataclass
class ComplianceCheck:
    """Result of a compliance check."""
    rule_id: str
    passed: bool
    severity: str
    message: str
    timestamp: str


@dataclass
class RiskAssessment:
    """Risk assessment for an action or document."""
    id: str
    target: str
    risk_level: str  # low, medium, high, critical
    risk_factors: List[str]
    mitigations: List[str]
    assessed_at: str


class LegalEngine:
    """
    Legal Brain subsystem - compliance and governance enforcement.
    Validates actions against legal rules and operator governance.
    """

    def __init__(self, organism_root: Path) -> None:
        self.root = organism_root
        self.legal_dir = organism_root / "11_LEGAL_BRAIN"
        self.data_dir = self.legal_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.rules: List[ComplianceRule] = []
        self.checks: List[ComplianceCheck] = []
        self.risk_assessments: List[RiskAssessment] = []

        self._load_operator_profile()
        self._load_rules()
        self._load_state()

    def _load_operator_profile(self) -> None:
        """Load operator governance preferences."""
        profile_path = self.root / "operator_profile_trang.json"
        if profile_path.exists():
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    self.operator_profile = json.load(f)
            except Exception:
                self.operator_profile = {}
        else:
            self.operator_profile = {}

    def _load_rules(self) -> None:
        """Load default compliance rules."""
        default_rules = [
            ComplianceRule(
                id="LEGAL_001",
                category="legal",
                description="No IP infringement in generated code",
                check_type="keyword",
                check_value=["copyright", "trademark", "proprietary"],
                severity="critical"
            ),
            ComplianceRule(
                id="LEGAL_002",
                category="legal",
                description="Respect software licenses",
                check_type="keyword",
                check_value=["GPL violation", "license breach"],
                severity="error"
            ),
            ComplianceRule(
                id="GOV_001",
                category="governance",
                description="Trang's explicit consent required for external sharing",
                check_type="pattern",
                check_value=r"share.*external|publish.*public",
                severity="error"
            ),
            ComplianceRule(
                id="GOV_002",
                category="governance",
                description="No deletion of core canon files",
                check_type="keyword",
                check_value=["delete canon", "remove canon", "overwrite canon"],
                severity="critical"
            ),
            ComplianceRule(
                id="ETHIC_001",
                category="ethical",
                description="No harmful code generation",
                check_type="keyword",
                check_value=["malware", "virus", "exploit", "hack"],
                severity="critical"
            ),
            ComplianceRule(
                id="TECH_001",
                category="technical",
                description="Python 3.9+ compatibility required",
                check_type="keyword",
                check_value=["python 3.8", "python 3.7", "python 2"],
                severity="warning"
            ),
        ]

        self.rules.extend(default_rules)

        # Load custom rules from file if exists
        rules_file = self.data_dir / "custom_rules.json"
        if rules_file.exists():
            try:
                with open(rules_file, 'r', encoding='utf-8') as f:
                    custom_rules = json.load(f)
                    for r in custom_rules:
                        self.rules.append(ComplianceRule(**r))
            except Exception as e:
                print(f"[LEGAL] Error loading rules: {e}")

    def _load_state(self) -> None:
        """Load previous checks and assessments."""
        state_file = self.data_dir / "legal_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for check_data in data.get("checks", []):
                    self.checks.append(ComplianceCheck(**check_data))

                for risk_data in data.get("risk_assessments", []):
                    self.risk_assessments.append(RiskAssessment(**risk_data))

            except Exception as e:
                print(f"[LEGAL] Error loading state: {e}")

    def _save_state(self) -> None:
        """Save checks and assessments to disk."""
        state_file = self.data_dir / "legal_state.json"

        data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "check_count": len(self.checks),
            "risk_count": len(self.risk_assessments),
            "checks": [
                {
                    "rule_id": c.rule_id,
                    "passed": c.passed,
                    "severity": c.severity,
                    "message": c.message,
                    "timestamp": c.timestamp
                }
                for c in self.checks[-100:]  # Keep last 100
            ],
            "risk_assessments": [
                {
                    "id": r.id,
                    "target": r.target,
                    "risk_level": r.risk_level,
                    "risk_factors": r.risk_factors,
                    "mitigations": r.mitigations,
                    "assessed_at": r.assessed_at
                }
                for r in self.risk_assessments[-50:]
            ]
        }

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def check_compliance(
        self,
        content: str,
        context: str = "general"
    ) -> List[ComplianceCheck]:
        """Check content against all compliance rules."""
        results: List[ComplianceCheck] = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            passed = self._check_rule(content, rule)

            check = ComplianceCheck(
                rule_id=rule.id,
                passed=passed,
                severity=rule.severity if not passed else "info",
                message=f"{'PASS' if passed else 'FAIL'}: {rule.description}",
                timestamp=datetime.utcnow().isoformat() + "Z"
            )

            results.append(check)
            self.checks.append(check)

        self._save_state()
        return results

    def _check_rule(self, content: str, rule: ComplianceRule) -> bool:
        """Check content against a single rule."""
        content_lower = content.lower()

        if rule.check_type == "keyword":
            keywords = rule.check_value
            if isinstance(keywords, list):
                return not any(kw.lower() in content_lower for kw in keywords)
            return keywords.lower() not in content_lower

        elif rule.check_type == "regex":
            pattern = rule.check_value
            return not re.search(pattern, content, re.IGNORECASE)

        elif rule.check_type == "pattern":
            pattern = rule.check_value
            return not re.search(pattern, content, re.IGNORECASE)

        return True

    def assess_risk(
        self,
        target: str,
        action_type: str,
        parameters: Dict[str, Any]
    ) -> RiskAssessment:
        """Assess risk of an action."""
        risk_factors: List[str] = []
        mitigations: List[str] = []

        # Assess based on action type
        if action_type == "code_generation":
            if parameters.get("external_libs"):
                risk_factors.append("External dependencies introduce supply chain risk")
                mitigations.append("Pin dependency versions")
                mitigations.append("Audit external packages")

            if parameters.get("file_operations"):
                risk_factors.append("File operations can cause data loss")
                mitigations.append("Create backups before modifications")

        elif action_type == "data_sharing":
            risk_factors.append("Data sharing may violate privacy policies")
            mitigations.append("Anonymize data before sharing")
            mitigations.append("Get explicit consent from data owner")

        elif action_type == "execution":
            risk_factors.append("Code execution carries security risk")
            mitigations.append("Run in sandboxed environment")
            mitigations.append("Review code before execution")

        # Determine risk level
        factor_count = len(risk_factors)
        if factor_count >= 3:
            risk_level = "high"
        elif factor_count >= 1:
            risk_level = "medium"
        else:
            risk_level = "low"

        assessment = RiskAssessment(
            id=f"RISK_{len(self.risk_assessments) + 1:04d}",
            target=target,
            risk_level=risk_level,
            risk_factors=risk_factors,
            mitigations=mitigations,
            assessed_at=datetime.utcnow().isoformat() + "Z"
        )

        self.risk_assessments.append(assessment)
        self._save_state()

        return assessment

    def validate_governance(self, action: str, params: Dict) -> Dict[str, Any]:
        """Validate action against operator governance rules."""
        profile = self.operator_profile
        governance = profile.get("governance", {}) if isinstance(profile, dict) else {}
        restricted = governance.get("restricted_actions", [])
        comms = governance.get("communication_preferences", {})

        # Check if action is restricted
        is_restricted = any(r in action.lower() for r in restricted)

        # Check permission level
        permissions = governance.get("permissions", {})
        needs_approval = (
            permissions.get("can_override_safety") is False and
            action in ["execute", "deploy", "share_external"]
        )

        return {
            "action": action,
            "allowed": not is_restricted,
            "needs_approval": needs_approval,
            "requires_consent": "share" in action.lower(),
            "communication_style": communication.get("style", "formal"),
            "reasoning_preference": governance.get("reasoning_preferences", {}).get("style", "pragmatic")
        }

    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance status report."""
        # Get recent checks
        recent_checks = self.checks[-50:]

        passed = sum(1 for c in recent_checks if c.passed)
        failed = len(recent_checks) - passed

        # Group by severity
        by_severity: Dict[str, int] = {}
        for check in recent_checks:
            if not check.passed:
                sev = check.severity
                by_severity[sev] = by_severity.get(sev, 0) + 1

        return {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_checks": len(recent_checks),
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / len(recent_checks) if recent_checks else 0,
            "failures_by_severity": by_severity,
            "active_rules": len([r for r in self.rules if r.enabled]),
            "total_risk_assessments": len(self.risk_assessments)
        }

    def get_status(self) -> Dict[str, Any]:
        """Get legal engine status."""
        return {
            "status": "operational",
            "active_rules": len([r for r in self.rules if r.enabled]),
            "total_checks_performed": len(self.checks),
            "total_risk_assessments": len(self.risk_assessments),
            "recent_pass_rate": self._calculate_recent_pass_rate(),
            "operator_governance_loaded": bool(self.operator_profile)
        }

    def _calculate_recent_pass_rate(self) -> float:
        """Calculate pass rate for recent checks."""
        recent = self.checks[-100:]
        if not recent:
            return 1.0
        passed = sum(1 for c in recent if c.passed)
        return passed / len(recent)


def main() -> int:
    """CLI for Legal Engine."""
    print("=" * 50)
    print("AMOS Legal Engine (11_LEGAL_BRAIN)")
    print("=" * 50)

    organism_root = Path(__file__).parent.parent
    engine = LegalEngine(organism_root)

    # Test compliance checking
    print("\nTesting compliance check...")
    test_content = """
    This is a test code snippet for analysis.
    It uses standard Python libraries only.
    No external dependencies required.
    """

    results = engine.check_compliance(test_content, "code_review")

    print(f"\nChecked against {len(results)} rules:")
    for r in results:
        status = "✓" if r.passed else "✗"
        print(f"  {status} [{r.rule_id}] {r.severity}: {r.message}")

    # Test risk assessment
    print("\nTesting risk assessment...")
    risk = engine.assess_risk(
        "test_module.py",
        "code_generation",
        {"external_libs": ["requests"], "file_operations": True}
    )

    print(f"Risk Level: {risk.risk_level.upper()}")
    print(f"Factors: {len(risk.risk_factors)}")
    for factor in risk.risk_factors:
        print(f"  - {factor}")

    # Test governance validation
    print("\nTesting governance validation...")
    gov = engine.validate_governance("share_external", {"data": "test"})
    print(f"Action allowed: {gov['allowed']}")
    print(f"Needs approval: {gov['needs_approval']}")
    print(f"Requires consent: {gov['requires_consent']}")

    # Show status
    print("\nLegal Engine Status:")
    status = engine.get_status()
    print(f"  Active rules: {status['active_rules']}")
    print(f"  Total checks: {status['total_checks_performed']}")
    print(f"  Pass rate: {status['recent_pass_rate']:.1%}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
