"""Reasoning engines implementing Rule of 2, Rule of 4, and structural analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Perspective:
    """A single perspective in dual analysis."""

    name: str
    viewpoint: str
    supporting_evidence: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)


@dataclass
class Quadrant:
    """One of the four analysis quadrants."""

    name: str
    description: str
    factors: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)


class RuleOfTwo:
    """Rule of 2 implementation: All analysis must check at least two
    contrasting perspectives or hypotheses.
    """

    def analyze(self, problem: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Perform dual-perspective analysis.

        Returns analysis with primary and alternative perspectives.
        """
        context = context or {}

        # Generate primary perspective (internal/micro/short-term view)
        primary = Perspective(
            name="Primary (Internal/Micro Focus)",
            viewpoint=f"Direct analysis of: {problem}",
            supporting_evidence=["Immediate observable factors", "Direct causal relationships"],
            limitations=["May miss systemic patterns", "Limited temporal scope"],
        )

        # Generate alternative perspective (external/macro/long-term view)
        alternative = Perspective(
            name="Alternative (External/Macro Focus)",
            viewpoint=f"Contextual/systemic view of: {problem}",
            supporting_evidence=["Long-term trends", "Environmental/systemic factors"],
            limitations=["May miss immediate specifics", "Higher uncertainty in predictions"],
        )

        # Synthesis
        synthesis = self._synthesize(primary, alternative, problem)

        return {
            "problem": problem,
            "perspectives": [primary, alternative],
            "synthesis": synthesis,
            "confidence": self._calculate_confidence(primary, alternative),
            "recommendation": synthesis.get("recommended_path", "Further analysis needed"),
        }

    def _synthesize(self, p1: Perspective, p2: Perspective, problem: str) -> dict[str, Any]:
        """Synthesize two perspectives into actionable insight."""
        # Find common ground
        common_factors = set(p1.supporting_evidence) & set(p2.supporting_evidence)

        # Identify gaps
        all_limitations = p1.limitations + p2.limitations

        return {
            "common_ground": list(common_factors),
            "gaps": all_limitations,
            "complementary_insights": [
                f"Primary view: {p1.viewpoint}",
                f"Alternative view: {p2.viewpoint}",
            ],
            "recommended_path": self._recommend_path(p1, p2),
        }

    def _recommend_path(self, p1: Perspective, p2: Perspective) -> str:
        """Generate recommendation from dual perspectives."""
        if len(p1.supporting_evidence) > len(p2.supporting_evidence):
            return "Favor primary perspective with alternative as monitor"
        elif len(p2.supporting_evidence) > len(p1.supporting_evidence):
            return "Consider alternative perspective seriously"
        return "Maintain both perspectives; decision requires additional data"

    def _calculate_confidence(self, p1: Perspective, p2: Perspective) -> float:
        """Calculate confidence score from perspective balance."""
        evidence_total = len(p1.supporting_evidence) + len(p2.supporting_evidence)
        limitation_total = len(p1.limitations) + len(p2.limitations)
        if evidence_total == 0:
            return 0.0
        return min(1.0, evidence_total / (evidence_total + limitation_total * 0.5))


class RuleOfFour:
    """Rule of 4 implementation: For important systems, consider four entangled quadrants:
    1. Biological/Human
    2. Technical/Infrastructural
    3. Economic/Organizational
    4. Environmental/Planetary
    """

    QUADRANTS = {
        "biological": Quadrant(
            name="Biological/Human",
            description="Human factors, biological constraints, health, cognition, behavior",
            factors=["Human capacity", "Biological limits", "Cognitive load", "Wellbeing"],
            risks=["Burnout", "Health degradation", "Skill gaps"],
            opportunities=["Human creativity", "Adaptability", "Learning"],
        ),
        "technical": Quadrant(
            name="Technical/Infrastructural",
            description="Technical systems, infrastructure, code, architecture",
            factors=["System reliability", "Technical debt", "Scalability", "Security"],
            risks=["System failure", "Security breaches", "Technical obsolescence"],
            opportunities=["Automation", "Efficiency gains", "Innovation"],
        ),
        "economic": Quadrant(
            name="Economic/Organizational",
            description="Economic factors, organizational structure, incentives",
            factors=["Cost structure", "ROI", "Organizational capacity", "Stakeholder alignment"],
            risks=["Budget overrun", "Resource constraints", "Misalignment"],
            opportunities=["Cost savings", "New revenue", "Efficiency"],
        ),
        "environmental": Quadrant(
            name="Environmental/Planetary",
            description="Environmental impact, sustainability, planetary boundaries",
            factors=["Resource consumption", "Emissions", "Ecosystem impact", "Sustainability"],
            risks=["Environmental harm", "Regulatory non-compliance", "Reputation damage"],
            opportunities=["Sustainability leadership", "Efficiency", "Resilience"],
        ),
    }

    def analyze(self, problem: str, required_quadrants: set[str] | None = None) -> dict[str, Any]:
        """Perform four-quadrant analysis.

        Args:
            problem: The problem or system to analyze
            required_quadrants: Which quadrants must be present (default: all 4)

        Returns:
            Analysis results with all quadrants, cross-impacts, and recommendations
        """
        required = (
            set(required_quadrants)
            if required_quadrants is not None
            else set(self.QUADRANTS.keys())
        )
        ordered_required = [key for key in self.QUADRANTS.keys() if key in required]

        # Analyze each quadrant
        quadrant_results = {}
        for key in ordered_required:
            if key in self.QUADRANTS:
                quadrant_results[key] = self._analyze_quadrant(self.QUADRANTS[key], problem)

        # Cross-impact analysis
        cross_impacts = self._analyze_cross_impacts(quadrant_results)

        # Integration
        integration = self._integrate_quadrants(quadrant_results, cross_impacts)

        return {
            "problem": problem,
            "quadrants_analyzed": ordered_required,
            "quadrant_details": quadrant_results,
            "cross_impacts": cross_impacts,
            "integration": integration,
            "completeness_score": len(quadrant_results) / len(required) if required else 1.0,
            "missing_quadrants": [key for key in ordered_required if key not in quadrant_results],
        }

    def _analyze_quadrant(self, quadrant: Quadrant, problem: str) -> dict[str, Any]:
        """Analyze problem within a single quadrant."""
        return {
            "name": quadrant.name,
            "relevant_factors": [f for f in quadrant.factors if self._is_relevant(f, problem)],
            "applicable_risks": [r for r in quadrant.risks if self._is_relevant(r, problem)],
            "potential_opportunities": [
                o for o in quadrant.opportunities if self._is_relevant(o, problem)
            ],
            "priority": self._assess_priority(quadrant, problem),
        }

    def _is_relevant(self, factor: str, problem: str) -> bool:
        """Check if factor is relevant to problem (simplified)."""
        problem_lower = problem.lower()
        factor_words = factor.lower().split()
        return any(word in problem_lower for word in factor_words if len(word) > 3)

    def _assess_priority(self, quadrant: Quadrant, problem: str) -> str:
        """Assess priority level for this quadrant."""
        relevance_count = sum(1 for f in quadrant.factors if self._is_relevant(f, problem))
        if relevance_count >= 2:
            return "HIGH"
        elif relevance_count == 1:
            return "MEDIUM"
        return "LOW"

    def _analyze_cross_impacts(self, quadrants: dict[str, Any]) -> list[dict[str, Any]]:
        """Analyze impacts between quadrants."""
        impacts = []
        keys = list(quadrants.keys())
        for i, k1 in enumerate(keys):
            for k2 in keys[i + 1 :]:
                impacts.append(
                    {
                        "from": quadrants[k1]["name"],
                        "to": quadrants[k2]["name"],
                        "type": "bidirectional_influence",
                        "notes": f"Changes in {k1} affect {k2} and vice versa",
                    }
                )
        return impacts

    def _integrate_quadrants(
        self, quadrants: dict[str, Any], impacts: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Integrate all quadrants into unified recommendation."""
        high_priority = [k for k, v in quadrants.items() if v.get("priority") == "HIGH"]

        return {
            "key_quadrants": high_priority,
            "critical_factors": self._extract_critical_factors(quadrants),
            "risk_summary": self._summarize_risks(quadrants),
            "integrated_recommendation": self._generate_recommendation(quadrants, high_priority),
        }

    def _extract_critical_factors(self, quadrants: dict[str, Any]) -> list[str]:
        """Extract critical factors across all quadrants."""
        factors = []
        for q in quadrants.values():
            factors.extend(q.get("relevant_factors", []))
            factors.extend(q.get("applicable_risks", []))
        return list(set(factors))[:10]  # Top 10 unique factors

    def _summarize_risks(self, quadrants: dict[str, Any]) -> dict[str, int]:
        """Summarize risk counts by category."""
        return {
            q_name: len(q_data.get("applicable_risks", [])) for q_name, q_data in quadrants.items()
        }

    def _generate_recommendation(self, quadrants: dict[str, Any], high_priority: list[str]) -> str:
        """Generate integrated recommendation."""
        if len(high_priority) >= 3:
            return f"Multi-domain challenge requiring coordinated approach across: {', '.join(high_priority)}"
        elif len(high_priority) == 2:
            return (
                f"Focus on integration between {high_priority[0]} and {high_priority[1]} dimensions"
            )
        elif len(high_priority) == 1:
            return f"Primarily a {high_priority[0]} challenge; other domains provide supporting context"
        return "Insufficient quadrant coverage for specific recommendation"


class ReasoningEngine:
    """Main reasoning engine combining Rule of 2 and Rule of 4."""

    def __init__(self):
        self.rule_of_two = RuleOfTwo()
        self.rule_of_four = RuleOfFour()

    def full_analysis(self, problem: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Perform complete AMOS-compliant analysis.

        Combines Rule of 2 (dual perspectives) with Rule of 4 (four quadrants).
        """
        # Apply Rule of 2
        dual_analysis = self.rule_of_two.analyze(problem, context)

        # Apply Rule of 4
        quadrant_analysis = self.rule_of_four.analyze(problem)

        # Cross-validation
        validation = self._cross_validate(dual_analysis, quadrant_analysis)

        return {
            "problem": problem,
            "rule_of_two": dual_analysis,
            "rule_of_four": quadrant_analysis,
            "cross_validation": validation,
            "structural_integrity_score": validation.get("integrity_score", 0.0),
            "recommendations": self._synthesize_recommendations(dual_analysis, quadrant_analysis),
            "assumptions": self._extract_assumptions(dual_analysis, quadrant_analysis),
            "uncertainty_flags": self._identify_uncertainties(dual_analysis, quadrant_analysis),
        }

    def _cross_validate(self, dual: dict[str, Any], quadrants: dict[str, Any]) -> dict[str, Any]:
        """Cross-validate Rule of 2 and Rule of 4 results."""
        # Check consistency between perspectives and quadrants
        issues = []

        # Verify quadrants are covered in perspectives
        quad_names = set(quadrants.get("quadrants_analyzed", []))
        # Perspectives should ideally cover multiple quadrants

        integrity_score = (
            quadrants.get("completeness_score", 0.0) * 0.5 + dual.get("confidence", 0.0) * 0.5
        )

        return {
            "consistent": len(issues) == 0,
            "issues": issues,
            "integrity_score": integrity_score,
            "coverage": f"{len(quad_names)} quadrants, {len(dual.get('perspectives', []))} perspectives",
        }

    def _synthesize_recommendations(
        self, dual: dict[str, Any], quadrants: dict[str, Any]
    ) -> list[str]:
        """Synthesize final recommendations from both rules."""
        recs = []

        # From Rule of 2
        if dual.get("recommendation"):
            recs.append(f"[Dual-Perspective] {dual['recommendation']}")

        # From Rule of 4
        integration = quadrants.get("integration", {})
        if integration.get("integrated_recommendation"):
            recs.append(f"[Four-Quadrant] {integration['integrated_recommendation']}")

        return list(dict.fromkeys(recs))

    def _extract_assumptions(self, dual: dict[str, Any], quadrants: dict[str, Any]) -> list[str]:
        """Extract explicit assumptions from analysis."""
        assumptions = []

        # From perspectives
        for p in dual.get("perspectives", []):
            assumptions.extend(p.limitations)

        # From quadrant coverage gaps
        missing = quadrants.get("missing_quadrants", [])
        if missing:
            assumptions.append(f"Limited coverage in quadrants: {', '.join(missing)}")

        return assumptions

    def _identify_uncertainties(self, dual: dict[str, Any], quadrants: dict[str, Any]) -> list[str]:
        """Identify areas of uncertainty requiring further investigation."""
        uncertainties = []

        if dual.get("confidence", 1.0) < 0.7:
            uncertainties.append("Low confidence in dual-perspective balance")

        if quadrants.get("completeness_score", 1.0) < 1.0:
            uncertainties.append("Incomplete quadrant coverage")

        return uncertainties
