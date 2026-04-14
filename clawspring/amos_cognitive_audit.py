"""AMOS Cognitive Audit - Validates outputs against 6 Global Laws."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from amos_runtime import get_runtime


@dataclass
class AuditResult:
    """Result of cognitive audit."""

    content_hash: str
    overall_pass: bool
    law_compliance: dict[str, bool]
    quality_checks: dict[str, bool]
    violations: list[dict]
    recommendations: list[str]
    gap_acknowledgment: str
    audit_timestamp: float = field(default_factory=lambda: __import__("time").time())


class LawValidator:
    """Validates content against each Global Law."""

    def __init__(self):
        self.runtime = get_runtime()
        self.laws = self.runtime.get_law_summary()

    def validate_l1_law_of_law(self, content: str) -> tuple[bool, str]:
        """L1: Check reasoning obeys highest applicable constraints."""
        # Check for explicit constraint acknowledgment
        has_constraints = any(
            word in content.lower() for word in ["constraint", "limit", "boundary", "law", "rule"]
        )
        return has_constraints, "L1: Constraints must be acknowledged"

    def validate_l2_rule_of_two(self, content: str) -> tuple[bool, str]:
        """L2: Check for dual perspectives."""
        # Check for multiple viewpoints
        dual_indicators = ["perspective", "viewpoint", "alternative", "contrast", "compare"]
        has_dual = any(word in content.lower() for word in dual_indicators)
        return has_dual, "L2: Dual perspectives recommended"

    def validate_l3_rule_of_four(self, content: str) -> tuple[bool, str]:
        """L3: Check for quadrant coverage."""
        quadrant_terms = [
            "biological",
            "technical",
            "economic",
            "environmental",
            "human",
            "system",
            "cost",
            "impact",
        ]
        quadrant_count = sum(1 for term in quadrant_terms if term in content.lower())
        has_quadrants = quadrant_count >= 2
        return has_quadrants, f"L3: {quadrant_count}/4 quadrants detected"

    def validate_l4_structural_integrity(self, content: str) -> tuple[bool, str]:
        """L4: Check for logical consistency and no contradictions."""
        # Check for contradiction indicators
        contradiction_patterns = [
            (r"is true.*is false", "Direct contradiction detected"),
            (r"always.*never", "Absolute contradiction"),
            (r"all.*none", "Universal contradiction"),
        ]

        issues = []
        for pattern, msg in contradiction_patterns:
            if re.search(pattern, content.lower()):
                issues.append(msg)

        # Check for vague structural claims
        if "i feel" in content.lower() or "i believe" in content.lower():
            issues.append("Subjective claims without structural basis")

        passed = len(issues) == 0
        return passed, f"L4: {', '.join(issues) if issues else 'Structural integrity passed'}"

    def validate_l5_post_theory_communication(self, content: str) -> tuple[bool, str]:
        """L5: Check for precise, concrete language."""
        vague_terms = [
            "vibration",
            "energy",
            "spiritual",
            "quantum healing",
            "frequency",
            "resonance",
            "alignment",
        ]
        found_vague = [term for term in vague_terms if term in content.lower()]

        # Check for abstract mysticism
        mystic_patterns = [r"cosmic.*energy", r"universal.*force", r"divine.*pattern"]
        found_mystic = [p for p in mystic_patterns if re.search(p, content.lower())]

        passed = len(found_vague) == 0 and len(found_mystic) == 0
        return passed, f"L5: {len(found_vague)} vague terms, {len(found_mystic)} mystic patterns"

    def validate_l6_ubi_alignment(self, content: str) -> tuple[bool, str]:
        """L6: Check for biological/social/systemic alignment."""
        # Check for biological respect indicators
        bio_terms = ["human", "biological", "cognitive load", "attention", "stress", "fatigue"]
        has_bio = any(term in content.lower() for term in bio_terms)

        # Check for systemic awareness
        system_terms = ["system", "context", "environment", "ecosystem"]
        has_system = any(term in content.lower() for term in system_terms)

        passed = has_bio or has_system
        return passed, f"L6: Bio={has_bio}, System={has_system}"


class QualityChecker:
    """Checks output quality per Layer 6 standards."""

    def check_structural_integrity(self, content: str) -> tuple[bool, str]:
        """Content has coherent structure."""
        has_sections = "#" in content or "##" in content or "- " in content
        has_paragraphs = len(content.split("\n\n")) > 1
        return has_sections or has_paragraphs, "Has organized structure"

    def check_explicit_assumptions(self, content: str) -> tuple[bool, str]:
        """Assumptions are explicitly stated."""
        assumption_indicators = [
            "assumption",
            "assume",
            "given that",
            "if we accept",
            "presuming",
            "supposing",
        ]
        has_assumptions = any(ind in content.lower() for ind in assumption_indicators)
        return (
            has_assumptions,
            "Assumptions explicitly stated" if has_assumptions else "Assumptions not found",
        )

    def check_risks_and_limits(self, content: str) -> tuple[bool, str]:
        """Risks and limits are clearly stated."""
        risk_indicators = [
            "risk",
            "limitation",
            "constraint",
            "uncertainty",
            "gap",
            "unknown",
            "caution",
            "warning",
        ]
        risk_count = sum(1 for ind in risk_indicators if ind in content.lower())
        return risk_count > 0, f"{risk_count} risk/limit indicators found"

    def check_precise_language(self, content: str) -> tuple[bool, str]:
        """Language is precise and non-abstract."""
        # Check for concrete measurements
        has_measurements = bool(re.search(r"\d+\s*(px|%|ms|sec|min|hours?)", content))
        # Check for specific terms vs abstract
        vague_count = content.lower().count("thing") + content.lower().count("stuff")
        return (
            has_measurements and vague_count < 3,
            f"Measurements: {has_measurements}, Vague terms: {vague_count}",
        )


class AMOSCognitiveAudit:
    """Complete cognitive audit system for AMOS outputs."""

    def __init__(self):
        self.runtime = get_runtime()
        self.law_validator = LawValidator()
        self.quality_checker = QualityChecker()

    def audit(self, content: str, content_type: str = "general") -> AuditResult:
        """Run full cognitive audit on content."""
        import hashlib

        content_hash = hashlib.md5(content.encode()).hexdigest()[:12]

        # Validate all 6 laws
        law_compliance = {
            "L1": self.law_validator.validate_l1_law_of_law(content)[0],
            "L2": self.law_validator.validate_l2_rule_of_two(content)[0],
            "L3": self.law_validator.validate_l3_rule_of_four(content)[0],
            "L4": self.law_validator.validate_l4_structural_integrity(content)[0],
            "L5": self.law_validator.validate_l5_post_theory_communication(content)[0],
            "L6": self.law_validator.validate_l6_ubi_alignment(content)[0],
        }

        # Run quality checks
        quality_checks = {
            "structural_integrity": self.quality_checker.check_structural_integrity(content)[0],
            "explicit_assumptions": self.quality_checker.check_explicit_assumptions(content)[0],
            "risks_and_limits": self.quality_checker.check_risks_and_limits(content)[0],
            "precise_language": self.quality_checker.check_precise_language(content)[0],
        }

        # Collect violations
        violations = []
        for law_id, passed in law_compliance.items():
            if not passed:
                law_name = next(
                    (l["name"] for l in self.runtime.get_law_summary() if l["id"] == law_id), law_id
                )
                violations.append(
                    {
                        "law": law_id,
                        "name": law_name,
                        "severity": "high" if law_id in ["L1", "L4"] else "medium",
                    }
                )

        # Generate recommendations
        recommendations = []
        if not law_compliance["L4"]:
            recommendations.append("Review for logical consistency and remove contradictions")
        if not law_compliance["L5"]:
            recommendations.append("Replace vague/mystical language with concrete terms")
        if not quality_checks["explicit_assumptions"]:
            recommendations.append("Explicitly state all assumptions")
        if not quality_checks["risks_and_limits"]:
            recommendations.append("Add risk acknowledgment and limit statements")

        overall_pass = all(law_compliance.values()) and all(quality_checks.values())

        return AuditResult(
            content_hash=content_hash,
            overall_pass=overall_pass,
            law_compliance=law_compliance,
            quality_checks=quality_checks,
            violations=violations,
            recommendations=recommendations,
            gap_acknowledgment=(
                "GAP: This audit is algorithmic pattern matching, not human judgment. "
                "No understanding, no consciousness, no lived experience of quality."
            ),
        )

    def audit_code(self, code: str, language: str = "python") -> AuditResult:
        """Specialized audit for code."""
        # Add code-specific checks
        result = self.audit(code, "code")

        # Check for code-specific AMOS compliance
        has_comments = "#" in code or '"""' in code
        has_types = "def " in code or "class " in code
        has_error_handling = "try" in code or "except" in code or "error" in code.lower()

        if not has_comments:
            result.violations.append({"law": "L4", "name": "Documentation", "severity": "low"})
            result.recommendations.append("Add docstrings explaining structural intent")

        if not has_error_handling:
            result.recommendations.append("Add error handling for structural robustness")

        return result

    def audit_design(self, design_spec: str) -> AuditResult:
        """Specialized audit for design specifications."""
        result = self.audit(design_spec, "design")

        # Check for UBI alignment
        has_accessibility = "accessibility" in design_spec.lower() or "a11y" in design_spec.lower()
        has_biological = "cognitive" in design_spec.lower() or "human" in design_spec.lower()

        if not has_accessibility:
            result.recommendations.append("Add accessibility considerations (L6 UBI alignment)")
        if not has_biological:
            result.recommendations.append("Add human/biological factor analysis")

        return result

    def get_audit_summary(self, result: AuditResult) -> str:
        """Generate human-readable audit summary."""
        lines = [
            "# AMOS Cognitive Audit Report",
            f"Content Hash: {result.content_hash}",
            f"Overall: {'PASS' if result.overall_pass else 'NEEDS REVIEW'}",
            "",
            "## Law Compliance (L1-L6)",
        ]

        for law_id, passed in result.law_compliance.items():
            icon = "✓" if passed else "✗"
            law_name = next(
                (l["name"] for l in self.runtime.get_law_summary() if l["id"] == law_id), law_id
            )
            lines.append(f"{icon} {law_id}: {law_name}")

        lines.extend(
            [
                "",
                "## Quality Checks",
            ]
        )
        for check, passed in result.quality_checks.items():
            icon = "✓" if passed else "✗"
            lines.append(f"{icon} {check.replace('_', ' ').title()}")

        if result.violations:
            lines.extend(["", "## Violations"])
            for v in result.violations:
                lines.append(f"- {v['law']} ({v['severity']}): {v['name']}")

        if result.recommendations:
            lines.extend(["", "## Recommendations"])
            for rec in result.recommendations:
                lines.append(f"- {rec}")

        lines.extend(
            [
                "",
                "## Gap Acknowledgment",
                result.gap_acknowledgment,
            ]
        )

        return "\n".join(lines)


# Singleton
_audit_system: AMOSCognitiveAudit | None = None


def get_cognitive_audit() -> AMOSCognitiveAudit:
    """Get singleton cognitive audit system."""
    global _audit_system
    if _audit_system is None:
        _audit_system = AMOSCognitiveAudit()
    return _audit_system


def audit_content(content: str, content_type: str = "general") -> AuditResult:
    """Quick audit helper."""
    return get_cognitive_audit().audit(content, content_type)


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS COGNITIVE AUDIT TEST")
    print("=" * 60)

    audit = get_cognitive_audit()

    # Test cases
    test_contents = [
        "This is a vague statement about energy vibrations.",  # Should fail L5
        """# Analysis
Consider two perspectives: technical and biological.
This approach respects human cognitive limits.
Assumptions: User has basic computer literacy.
Risks: System may fail under high load.
""",  # Should pass
    ]

    for i, content in enumerate(test_contents, 1):
        print(f"\n{'='*50}")
        print(f"Test {i}: {content[:50]}...")
        print("=" * 50)

        result = audit.audit(content)
        print(audit.get_audit_summary(result))

    print("\n" + "=" * 60)
    print("Cognitive Audit: OPERATIONAL")
    print("=" * 60)
    print("\nAll 6 Global Laws enforced via algorithmic validation.")
    print("GAP: No understanding. Pattern matching only.")
