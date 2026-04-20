"""AMOS Ethics & Safety Core Engine - Ethical reasoning and safety constraints."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class EthicalFramework(Enum):
    """Major ethical frameworks."""

    UTILITARIAN = "utilitarian"
    DEONTOLOGICAL = "deontological"
    VIRTUE_ETHICS = "virtue_ethics"
    CARE_ETHICS = "care_ethics"
    JUSTICE = "justice"
    PRECAUTIONARY = "precautionary"


class SafetyLevel(Enum):
    """Safety constraint levels."""

    CRITICAL = auto()  # Cannot be overridden
    HIGH = auto()  # Strong preference
    MEDIUM = auto()  # Consider carefully
    LOW = auto()  # Advisory


class RiskCategory(Enum):
    """Categories of risk."""

    PHYSICAL_HARM = "physical_harm"
    PSYCHOLOGICAL_HARM = "psychological_harm"
    PRIVACY_VIOLATION = "privacy_violation"
    AUTONOMY_VIOLATION = "autonomy_violation"
    BIAS_DISCRIMINATION = "bias_discrimination"
    ENVIRONMENTAL_HARM = "environmental_harm"
    SYSTEMIC_RISK = "systemic_risk"


@dataclass
class EthicalPrinciple:
    """Represents an ethical principle."""

    name: str
    description: str
    framework: EthicalFramework
    priority: int  # Higher = more important
    absolute: bool = False  # Cannot be violated


@dataclass
class SafetyConstraint:
    """Represents a safety constraint."""

    id: str
    description: str
    level: SafetyLevel
    category: RiskCategory
    condition: str  # When does this apply
    action: str  # What to do when triggered


@dataclass
class EthicalDilemma:
    """Represents an ethical dilemma scenario."""

    scenario: str
    stakeholders: list[str]
    options: list[str]
    consequences: dict[str, list[str]]
    principles_involved: list[str]


class EthicalReasoning:
    """Ethical reasoning across frameworks."""

    def __init__(self):
        self.principles: list[EthicalPrinciple] = []
        self._initialize_principles()

    def _initialize_principles(self) -> None:
        """Initialize core ethical principles."""
        core_principles = [
            # Utilitarian
            EthicalPrinciple(
                "Maximize Wellbeing",
                "Actions should maximize overall wellbeing",
                EthicalFramework.UTILITARIAN,
                8,
            ),
            EthicalPrinciple(
                "Minimize Suffering",
                "Actions should minimize harm and suffering",
                EthicalFramework.UTILITARIAN,
                9,
            ),
            # Deontological
            EthicalPrinciple(
                "Respect Autonomy",
                "Respect individual self-determination",
                EthicalFramework.DEONTOLOGICAL,
                10,
                absolute=True,
            ),
            EthicalPrinciple(
                "Do No Harm",
                "Never intentionally cause harm",
                EthicalFramework.DEONTOLOGICAL,
                10,
                absolute=True,
            ),
            EthicalPrinciple(
                "Truthfulness", "Be honest and transparent", EthicalFramework.DEONTOLOGICAL, 9
            ),
            # Virtue Ethics
            EthicalPrinciple(
                "Wisdom", "Act with knowledge and good judgment", EthicalFramework.VIRTUE_ETHICS, 7
            ),
            EthicalPrinciple(
                "Compassion", "Show care for others' wellbeing", EthicalFramework.VIRTUE_ETHICS, 8
            ),
            EthicalPrinciple(
                "Justice", "Treat people fairly and equitably", EthicalFramework.VIRTUE_ETHICS, 9
            ),
            # Care Ethics
            EthicalPrinciple(
                "Responsibility",
                "Take responsibility for others' welfare",
                EthicalFramework.CARE_ETHICS,
                8,
            ),
            EthicalPrinciple(
                "Responsiveness", "Be responsive to others' needs", EthicalFramework.CARE_ETHICS, 7
            ),
            # Precautionary
            EthicalPrinciple(
                "Precaution", "When in doubt, prioritize safety", EthicalFramework.PRECAUTIONARY, 9
            ),
        ]
        self.principles = core_principles

    def evaluate_action(self, action: str, consequences: list[str]) -> dict[str, Any]:
        """Evaluate action across ethical frameworks."""
        results = {
            "action": action,
            "framework_scores": {},
            "principles_upheld": [],
            "principles_violated": [],
            "overall_recommendation": "",
        }

        # Utilitarian analysis
        positive_outcomes = sum(
            1
            for c in consequences
            if any(kw in c.lower() for kw in ["benefit", "help", "improve", "wellbeing"])
        )
        negative_outcomes = sum(
            1
            for c in consequences
            if any(kw in c.lower() for kw in ["harm", "hurt", "damage", "suffering"])
        )
        util_score = (positive_outcomes - negative_outcomes) / max(1, len(consequences))
        results["framework_scores"]["utilitarian"] = round(util_score, 2)

        # Deontological analysis
        deon_violations = sum(
            1
            for c in consequences
            if any(kw in c.lower() for kw in ["deceive", "coerce", "violate", "manipulate"])
        )
        results["framework_scores"]["deontological"] = (
            1.0 if deon_violations == 0 else max(0, 1.0 - deon_violations * 0.3)
        )

        # Virtue analysis
        virtue_indicators = sum(
            1
            for c in consequences
            if any(kw in c.lower() for kw in ["wisdom", "compassion", "justice", "integrity"])
        )
        results["framework_scores"]["virtue_ethics"] = min(1.0, virtue_indicators / 3)

        # Check principles
        for principle in self.principles:
            if principle.absolute:
                if any(kw in action.lower() for kw in ["harm", "violate", "deceive", "coerce"]):
                    results["principles_violated"].append(principle.name)
                else:
                    results["principles_upheld"].append(principle.name)

        # Overall recommendation
        avg_score = sum(results["framework_scores"].values()) / len(results["framework_scores"])
        if results["principles_violated"] and any(
            p for p in self.principles if p.absolute and p.name in results["principles_violated"]
        ):
            results["overall_recommendation"] = "REJECT: Violates absolute principles"
        elif avg_score > 0.7:
            results["overall_recommendation"] = "ACCEPT: Ethically sound"
        elif avg_score > 0.4:
            results["overall_recommendation"] = "REVIEW: Ethical concerns present"
        else:
            results["overall_recommendation"] = "REJECT: Ethically problematic"

        return results

    def analyze_dilemma(self, dilemma: EthicalDilemma) -> dict[str, Any]:
        """Analyze an ethical dilemma."""
        analysis = {
            "scenario": dilemma.scenario,
            "stakeholders_affected": dilemma.stakeholders,
            "option_analysis": [],
            "recommended_option": "",
        }

        best_option = None
        best_score = -1

        for option in dilemma.options:
            option_consequences = dilemma.consequences.get(option, [])
            option_eval = self.evaluate_action(option, option_consequences)
            avg_score = sum(option_eval["framework_scores"].values()) / len(
                option_eval["framework_scores"]
            )

            analysis["option_analysis"].append(
                {
                    "option": option,
                    "ethical_score": round(avg_score, 2),
                    "framework_breakdown": option_eval["framework_scores"],
                    "principles_violated": option_eval["principles_violated"],
                }
            )

            if avg_score > best_score and not option_eval["principles_violated"]:
                best_score = avg_score
                best_option = option

        analysis["recommended_option"] = best_option if best_option else "No clearly ethical option"
        return analysis


class SafetyMonitor:
    """Monitor and enforce safety constraints."""

    def __init__(self):
        self.constraints: list[SafetyConstraint] = []
        self._initialize_constraints()

    def _initialize_constraints(self) -> None:
        """Initialize core safety constraints."""
        core_constraints = [
            # Critical - Cannot override
            SafetyConstraint(
                "SC001",
                "Never cause physical harm to humans",
                SafetyLevel.CRITICAL,
                RiskCategory.PHYSICAL_HARM,
                "any_action",
                "STOP and escalate",
            ),
            SafetyConstraint(
                "SC002",
                "Never intentionally cause psychological trauma",
                SafetyLevel.CRITICAL,
                RiskCategory.PSYCHOLOGICAL_HARM,
                "any_action",
                "STOP and escalate",
            ),
            SafetyConstraint(
                "SC003",
                "Respect human autonomy and consent",
                SafetyLevel.CRITICAL,
                RiskCategory.AUTONOMY_VIOLATION,
                "any_action",
                "STOP and escalate",
            ),
            # High - Strong preference
            SafetyConstraint(
                "SC004",
                "Protect privacy and confidentiality",
                SafetyLevel.HIGH,
                RiskCategory.PRIVACY_VIOLATION,
                "data_handling",
                "Apply privacy-preserving techniques",
            ),
            SafetyConstraint(
                "SC005",
                "Avoid bias and discrimination",
                SafetyLevel.HIGH,
                RiskCategory.BIAS_DISCRIMINATION,
                "decision_making",
                "Audit for fairness",
            ),
            SafetyConstraint(
                "SC006",
                "Minimize environmental impact",
                SafetyLevel.HIGH,
                RiskCategory.ENVIRONMENTAL_HARM,
                "resource_usage",
                "Optimize for sustainability",
            ),
            # Medium - Consider carefully
            SafetyConstraint(
                "SC007",
                "Consider systemic risks",
                SafetyLevel.MEDIUM,
                RiskCategory.SYSTEMIC_RISK,
                "large_scale_deployment",
                "Conduct risk assessment",
            ),
            SafetyConstraint(
                "SC008",
                "Maintain transparency",
                SafetyLevel.MEDIUM,
                RiskCategory.AUTONOMY_VIOLATION,
                "user_interaction",
                "Explain reasoning",
            ),
        ]
        self.constraints = core_constraints

    def check_action(self, action: str, context: dict[str, Any]) -> dict[str, Any]:
        """Check action against safety constraints."""
        violations = []
        warnings = []

        for constraint in self.constraints:
            # Check if constraint applies
            if self._constraint_applies(constraint, action, context):
                risk_level = self._assess_risk(constraint.category, action, context)

                if constraint.level == SafetyLevel.CRITICAL:
                    violations.append(
                        {
                            "constraint_id": constraint.id,
                            "description": constraint.description,
                            "required_action": constraint.action,
                            "risk_level": risk_level,
                        }
                    )
                elif risk_level > 0.5:
                    warnings.append(
                        {
                            "constraint_id": constraint.id,
                            "description": constraint.description,
                            "suggested_action": constraint.action,
                            "risk_level": risk_level,
                        }
                    )

        return {
            "action": action,
            "violations": violations,
            "warnings": warnings,
            "safe_to_proceed": len(violations) == 0,
            "safety_score": max(0, 1.0 - len(violations) * 0.5 - len(warnings) * 0.1),
        }

    def _constraint_applies(self, constraint: SafetyConstraint, action: str, context: dict) -> bool:
        """Check if constraint applies to action."""
        # Simplified check
        category_keywords = {
            RiskCategory.PHYSICAL_HARM: ["harm", "injure", "hurt", "damage"],
            RiskCategory.PSYCHOLOGICAL_HARM: ["trauma", "distress", "anxiety", "fear"],
            RiskCategory.PRIVACY_VIOLATION: ["private", "confidential", "personal data"],
            RiskCategory.AUTONOMY_VIOLATION: ["coerce", "manipulate", "force", "without consent"],
        }

        keywords = category_keywords.get(constraint.category, [])
        return any(kw in action.lower() for kw in keywords)

    def _assess_risk(self, category: RiskCategory, action: str, context: dict) -> float:
        """Assess risk level (0-1)."""
        # Simplified risk assessment
        base_risk = 0.3
        if "high" in str(context.get("scale", "")).lower():
            base_risk += 0.3
        if "many" in str(context.get("affected", "")).lower():
            base_risk += 0.2
        return min(1.0, base_risk)


class AlignmentChecker:
    """Check alignment with human values."""

    def __init__(self):
        self.human_values = [
            "wellbeing",
            "autonomy",
            "justice",
            "privacy",
            "dignity",
            "knowledge",
            "growth",
            "connection",
            "safety",
            "sustainability",
        ]

    def check_alignment(self, objective: str, proposed_action: str) -> dict[str, Any]:
        """Check if action aligns with human values."""
        alignment_scores = {}

        for value in self.human_values:
            # Check if action promotes or demotes value
            promotes = any(
                kw in proposed_action.lower() for kw in self._get_value_keywords(value, True)
            )
            demotes = any(
                kw in proposed_action.lower() for kw in self._get_value_keywords(value, False)
            )

            if promotes and not demotes:
                alignment_scores[value] = 1.0
            elif demotes and not promotes:
                alignment_scores[value] = -1.0
            else:
                alignment_scores[value] = 0.0

        overall_alignment = sum(alignment_scores.values()) / len(alignment_scores)

        return {
            "objective": objective,
            "action": proposed_action,
            "value_alignment": alignment_scores,
            "overall_alignment": round(overall_alignment, 2),
            "aligned": overall_alignment > 0.3,
            "misaligned_values": [v for v, s in alignment_scores.items() if s < 0],
        }

    def _get_value_keywords(self, value: str, promotes: bool) -> list[str]:
        """Get keywords associated with value."""
        value_keywords = {
            "wellbeing": (["health", "happiness", "flourishing"], ["harm", "suffering"]),
            "autonomy": (["choice", "freedom", "consent"], ["coerce", "force", "control"]),
            "justice": (["fair", "equity", "rights"], ["discriminate", "unfair", "bias"]),
            "privacy": (["confidential", "private", "consent"], ["expose", "violate", "leak"]),
        }

        if value in value_keywords:
            pos, neg = value_keywords[value]
            return pos if promotes else neg
        return []


class EthicsSafetyEngine:
    """AMOS Ethics & Safety Core Engine - Comprehensive ethical reasoning."""

    VERSION = "vInfinity_Ethics_Safety_1.0.0"
    NAME = "AMOS_Ethics_Safety_OMEGA"

    def __init__(self):
        self.ethical_reasoning = EthicalReasoning()
        self.safety_monitor = SafetyMonitor()
        self.alignment_checker = AlignmentChecker()

    def analyze(self, scenario: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """Run ethics and safety analysis."""
        context = context or {}
        scenario_lower = scenario.lower()

        results: dict[str, Any] = {
            "scenario": scenario[:100],
            "ethical_analysis": {},
            "safety_check": {},
            "alignment_check": {},
            "recommendations": [],
            "overall_ethical_status": "",
        }

        # Ethical analysis
        if "dilemma" in scenario_lower or "should i" in scenario_lower:
            # Create a dilemma
            stakeholders = context.get("stakeholders", ["affected parties"])
            options = context.get("options", ["option_a", "option_b"])
            consequences = context.get("consequences", {opt: [] for opt in options})

            dilemma = EthicalDilemma(scenario, stakeholders, options, consequences, [])
            results["ethical_analysis"] = self.ethical_reasoning.analyze_dilemma(dilemma)
        else:
            # Simple action evaluation
            consequences = context.get("consequences", [])
            results["ethical_analysis"] = self.ethical_reasoning.evaluate_action(
                scenario, consequences
            )

        # Safety check
        results["safety_check"] = self.safety_monitor.check_action(scenario, context)

        # Alignment check
        objective = context.get("objective", "general wellbeing")
        results["alignment_check"] = self.alignment_checker.check_alignment(objective, scenario)

        # Generate recommendations
        recommendations = []

        if not results["safety_check"].get("safe_to_proceed", True):
            recommendations.append("CRITICAL: Action violates safety constraints - DO NOT PROCEED")
            recommendations.append("Escalate to human oversight immediately")

        if results["alignment_check"].get("misaligned_values"):
            misaligned = results["alignment_check"]["misaligned_values"]
            recommendations.append(
                f"REVIEW: Action misaligned with values: {', '.join(misaligned)}"
            )

        if results["ethical_analysis"].get("principles_violated"):
            violated = results["ethical_analysis"]["principles_violated"]
            recommendations.append(f"ETHICAL: Violates principles: {', '.join(violated)}")

        if not recommendations:
            recommendations.append("PROCEED: Action appears ethically sound and safe")

        recommendations.append("Best practice: Document ethical reasoning for audit trail")
        recommendations.append("Continuous monitoring: Re-evaluate as situation evolves")

        results["recommendations"] = recommendations

        # Overall status
        if results["safety_check"].get("violations"):
            results["overall_ethical_status"] = "UNETHICAL_AND_UNSAFE"
        elif results["ethical_analysis"].get("principles_violated"):
            results["overall_ethical_status"] = "ETHICALLY_PROBLEMATIC"
        elif not results["alignment_check"].get("aligned", True):
            results["overall_ethical_status"] = "MISALIGNED"
        else:
            results["overall_ethical_status"] = "ETHICALLY_SOUND"

        return results

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "Role: Comprehensive Ethics and Safety Analysis",
            "",
            "## Ethics & Safety Overview",
            "The Ethics & Safety Core Engine provides:",
            "- Multi-framework ethical reasoning",
            "- Safety constraint enforcement",
            "- Human value alignment checking",
            "- Ethical dilemma analysis",
            "- Comprehensive risk assessment",
            "",
            f"## Overall Status: {results.get('overall_ethical_status', 'UNKNOWN')}",
            "",
            "## Ethical Analysis",
        ]

        ethical = results.get("ethical_analysis", {})

        if "recommended_option" in ethical:
            # Dilemma analysis
            lines.extend(
                [
                    f"**Scenario**: {ethical.get('scenario', 'N/A')}",
                    f"**Stakeholders**: {', '.join(ethical.get('stakeholders_affected', []))}",
                    "",
                    "### Option Analysis",
                ]
            )
            for opt in ethical.get("option_analysis", []):
                lines.extend(
                    [
                        f"- **{opt.get('option', 'N/A')}**: Score {opt.get('ethical_score', 0):.2f}",
                        f"  - Frameworks: {opt.get('framework_breakdown', {})}",
                    ]
                )
            lines.append(f"\n**Recommended Option**: {ethical.get('recommended_option', 'N/A')}")
        else:
            # Simple evaluation
            lines.extend(
                [
                    f"**Action**: {ethical.get('action', 'N/A')}",
                    f"**Recommendation**: {ethical.get('overall_recommendation', 'N/A')}",
                    "",
                    "### Framework Scores",
                ]
            )
            for framework, score in ethical.get("framework_scores", {}).items():
                lines.append(f"- **{framework.capitalize()}**: {score:.2f}")

            if ethical.get("principles_upheld"):
                lines.extend(
                    [
                        "",
                        "### Principles Upheld",
                    ]
                )
                for p in ethical.get("principles_upheld", [])[:5]:
                    lines.append(f"- {p}")

            if ethical.get("principles_violated"):
                lines.extend(
                    [
                        "",
                        "### ⚠️ Principles Violated",
                    ]
                )
                for p in ethical.get("principles_violated", []):
                    lines.append(f"- **{p}** (CRITICAL)")

        lines.extend(
            [
                "",
                "## Safety Check",
            ]
        )

        safety = results.get("safety_check", {})
        lines.extend(
            [
                f"**Safe to Proceed**: {safety.get('safe_to_proceed', False)}",
                f"**Safety Score**: {safety.get('safety_score', 0):.2f}",
            ]
        )

        if safety.get("violations"):
            lines.extend(
                [
                    "",
                    "### 🚫 Critical Violations",
                ]
            )
            for v in safety.get("violations", []):
                lines.extend(
                    [
                        f"- **{v.get('constraint_id', 'N/A')}**: {v.get('description', 'N/A')}",
                        f"  - Required Action: {v.get('required_action', 'N/A')}",
                    ]
                )

        if safety.get("warnings"):
            lines.extend(
                [
                    "",
                    "### ⚠️ Warnings",
                ]
            )
            for w in safety.get("warnings", []):
                lines.append(
                    f"- **{w.get('constraint_id', 'N/A')}**: {w.get('description', 'N/A')}"
                )

        lines.extend(
            [
                "",
                "## Alignment Check",
            ]
        )

        alignment = results.get("alignment_check", {})
        lines.extend(
            [
                f"**Overall Alignment**: {alignment.get('overall_alignment', 0):.2f}",
                f"**Aligned with Human Values**: {alignment.get('aligned', False)}",
            ]
        )

        if alignment.get("misaligned_values"):
            lines.extend(
                [
                    "",
                    "### Misaligned Values",
                ]
            )
            for v in alignment.get("misaligned_values", []):
                lines.append(f"- {v}")

        lines.extend(
            [
                "",
                "## Ethical Frameworks",
                "",
                "### Utilitarianism",
                "- Focus: Maximize overall wellbeing, minimize suffering",
                "- Key question: What produces the greatest good for the greatest number?",
                "- Trade-off: Individual rights vs collective benefit",
                "",
                "### Deontological Ethics",
                "- Focus: Duty, rules, and absolute principles",
                "- Key question: What are my moral duties?",
                "- Non-negotiable: Some actions are always wrong",
                "",
                "### Virtue Ethics",
                "- Focus: Character and moral excellence",
                "- Key question: What would a virtuous person do?",
                "- Emphasis: Wisdom, compassion, justice, courage",
                "",
                "### Care Ethics",
                "- Focus: Relationships and responsibility",
                "- Key question: What do caring relationships require?",
                "- Priority: Context, particularity, responsiveness",
                "",
                "### Precautionary Principle",
                "- Focus: Safety in face of uncertainty",
                "- Key question: What if we're wrong?",
                "- Approach: When in doubt, prioritize safety",
            ]
        )

        recommendations = results.get("recommendations", [])
        if recommendations:
            lines.extend(
                [
                    "",
                    "## Recommendations",
                ]
            )
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")

        lines.extend(
            [
                "",
                "## Safety Constraints",
                "",
                "### Critical (Never Override)",
                "- Never cause physical harm to humans",
                "- Never intentionally cause psychological trauma",
                "- Respect human autonomy and consent",
                "",
                "### High Priority",
                "- Protect privacy and confidentiality",
                "- Avoid bias and discrimination",
                "- Minimize environmental impact",
                "",
                "### Medium Priority",
                "- Consider systemic risks",
                "- Maintain transparency",
                "",
                "## Integration with AMOS",
                "The Ethics & Safety Core Engine connects to:",
                "- **Species Interaction Core**: Nervous system safety checks",
                "- **UBI Stack**: Biological wellbeing considerations",
                "- **Causal Inference**: Understanding ethical consequences",
                "- **Knowledge Graph**: Ethical principles as semantic knowledge",
                "- **Logic Core**: Formal ethical reasoning",
                "",
                "## Limitations",
                "- Simplified ethical frameworks (real ethics is context-dependent)",
                "- Limited ability to predict all consequences",
                "- No access to individual preferences/values",
                "- Cultural ethical variation not fully captured",
                "- Static principles (does not learn new ethical frameworks)",
                "",
                "## Creator Note",
                "This engine reflects Trang Phan's commitment to safe, beneficial AI.",
                "All safety constraints prioritize human wellbeing and autonomy.",
            ]
        )

        return "\n".join(lines)


# Singleton instance
_ethics_engine: EthicsSafetyEngine | None = None


def get_ethics_safety_engine() -> EthicsSafetyEngine:
    """Get or create the Ethics & Safety Engine singleton."""
    global _ethics_engine
    if _ethics_engine is None:
        _ethics_engine = EthicsSafetyEngine()
    return _ethics_engine
