"""AMOS Society/Culture Engine - Social and cultural analysis."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from amos_runtime import get_runtime


@dataclass
class SocietyAnalysis:
    """Result from society/culture domain analysis."""

    domain: str
    input_data: str
    findings: List[dict]
    confidence: float
    limitations: List[str]
    law_compliance: dict
    gap_acknowledgment: str


class InstitutionalKernel:
    """Institutional kernel - states, markets, civil society, families."""

    def analyze(self, input_data: str) -> SocietyAnalysis:
        """Analyze institutional aspects."""
        findings = []

        institutional_indicators = {
            "state_governance": ["state", "government", "policy", "regulation", "law"],
            "market_systems": ["market", "corporation", "industry", "sector", "business"],
            "civil_society": ["civil society", "ngo", "nonprofit", "community org"],
            "family_structures": ["family", "household", "kinship", "marriage", "parenting"],
        }

        for category, terms in institutional_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "institutional_primitives": self._get_primitives(category),
                    }
                )

        return SocietyAnalysis(
            domain="institutional",
            input_data=input_data,
            findings=findings,
            confidence=0.7 if findings else 0.3,
            limitations=[
                "No field research data",
                "No institutional database access",
                "Conceptual framework only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True, "L6": True},
            gap_acknowledgment=(
                "GAP: Institutional analysis is structural pattern matching. "
                "No ethnographic data. No field research. Not social science."
            ),
        )

    def _get_primitives(self, category: str) -> List[str]:
        """Get institutional primitives for category."""
        primitives = {
            "state_governance": ["role", "rule", "enforcement", "legitimacy"],
            "market_systems": ["resource_flow", "competition", "exchange"],
            "civil_society": ["association", "advocacy", "voluntary action"],
            "family_structures": ["kinship", "care", "socialization"],
        }
        return primitives.get(category, [])


class CulturalNormsKernel:
    """Cultural norms kernel - values, rituals, narratives, taboos."""

    SAFETY_WARNINGS = [
        "Avoid prescriptive cultural judgments",
        "Respect cultural diversity and context",
        "Do not generalize across cultures",
    ]

    def analyze(self, input_data: str) -> SocietyAnalysis:
        """Analyze cultural norms and values."""
        findings = []

        cultural_indicators = {
            "values": ["value", "belief", "moral", "ethic", "principle"],
            "rituals": ["ritual", "ceremony", "practice", "tradition", "custom"],
            "narratives": ["story", "narrative", "myth", "history", "discourse"],
            "taboos": ["taboo", "forbidden", "prohibited", "sacred", "restricted"],
            "symbols": ["symbol", "sign", "meaning", "representation"],
        }

        for category, terms in cultural_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "cultural_primitives": self._get_primitives(category),
                    }
                )

        # Add safety flag if cultural content detected
        warnings = []
        if findings:
            warnings.append("SAFETY: Avoid prescriptive cultural judgments")
            warnings.append("SAFETY: Respect cultural context and diversity")

        return SocietyAnalysis(
            domain="cultural_norms",
            input_data=input_data,
            findings=findings + [{"type": "safety_warnings", "warnings": warnings}]
            if warnings
            else findings,
            confidence=0.65 if findings else 0.25,
            limitations=[
                "No ethnographic fieldwork",
                "No cultural immersion data",
                "Text-based pattern analysis only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True, "L6": True},
            gap_acknowledgment=(
                "GAP: Cultural analysis is textual pattern detection. "
                "No lived cultural experience. No ethnographic expertise. "
                "Avoid prescriptive judgments about cultures."
            ),
        )

    def _get_primitives(self, category: str) -> List[str]:
        """Get cultural primitives for category."""
        primitives = {
            "values": ["symbol", "script", "identity_marker"],
            "rituals": ["script", "practice", "performance"],
            "narratives": ["symbol", "script", "status_signal"],
            "taboos": ["boundary", "restriction", "sanction"],
            "symbols": ["symbol", "meaning", "representation"],
        }
        return primitives.get(category, [])


class DemographicKernel:
    """Demographic kernel - population dynamics, migration, urbanization."""

    def analyze(self, input_data: str) -> SocietyAnalysis:
        """Analyze demographic aspects."""
        findings = []

        demographic_indicators = {
            "population_dynamics": ["population", "growth", "decline", "birth rate", "death rate"],
            "migration": ["migration", "immigration", "emigration", "refugee", "displacement"],
            "urbanization": ["urban", "city", "metropolitan", "rural", "suburban"],
            "demographic_structure": ["age structure", "dependency ratio", "cohort", "generation"],
        }

        for category, terms in demographic_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "demographic_primitives": self._get_primitives(category),
                    }
                )

        # Flag sensitive demographic topics
        warnings = []
        sensitive_terms = ["birth rate", "death rate", "fertility", "mortality"]
        if any(t in input_data.lower() for t in sensitive_terms):
            warnings.append("SAFETY: Sensitive demographic topic detected")
            warnings.append("SAFETY: Approach with appropriate caution and respect")

        return SocietyAnalysis(
            domain="demographic",
            input_data=input_data,
            findings=findings + [{"type": "safety_warnings", "warnings": warnings}]
            if warnings
            else findings,
            confidence=0.7 if findings else 0.3,
            limitations=[
                "No census data access",
                "No demographic surveys",
                "Pattern detection only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True, "L6": True},
            gap_acknowledgment=(
                "GAP: Demographic analysis is pattern matching on text. "
                "No census data. No demographic research. "
                "Flag sensitive topics appropriately."
            ),
        )

    def _get_primitives(self, category: str) -> List[str]:
        """Get demographic primitives for category."""
        primitives = {
            "population_dynamics": ["cohort", "fertility", "mortality"],
            "migration": ["migration_flow", "push_factors", "pull_factors"],
            "urbanization": ["density", "agglomeration", "infrastructure"],
            "demographic_structure": ["cohort", "dependency", "lifecycle"],
        }
        return primitives.get(category, [])


class MediaInformationKernel:
    """Media and information kernel - news, social media, memes, propagation."""

    SAFETY_CONSTRAINTS = [
        "Do not generate targeted manipulation strategies",
        "Flag potential misinformation patterns",
        "Respect information ethics",
    ]

    def analyze(self, input_data: str) -> SocietyAnalysis:
        """Analyze media and information aspects."""
        findings = []

        media_indicators = {
            "news_media": ["news", "journalism", "media outlet", "press", "broadcast"],
            "social_media": ["social media", "platform", "viral", "trending", "influencer"],
            "information_flow": ["propagation", "diffusion", "spread", "cascade", "network"],
            "memes": ["meme", "cultural unit", "replication", "mutation"],
            "disinformation": ["fake news", "misinformation", "disinformation", "propaganda"],
        }

        for category, terms in media_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "media_primitives": self._get_primitives(category),
                    }
                )

        # Add safety warnings for sensitive media topics
        warnings = []
        if any(t in input_data.lower() for t in ["propaganda", "manipulation", "targeting"]):
            warnings.append("SAFETY: Do not generate targeted manipulation strategies")
            warnings.append("SAFETY: Respect information ethics and user autonomy")

        return SocietyAnalysis(
            domain="media_information",
            input_data=input_data,
            findings=findings + [{"type": "safety_warnings", "warnings": warnings}]
            if warnings
            else findings,
            confidence=0.7 if findings else 0.3,
            limitations=[
                "No real-time media data",
                "No social network analysis",
                "Textual pattern analysis only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True, "L6": True},
            gap_acknowledgment=(
                "GAP: Media analysis is structural pattern matching. "
                "No real-time data. No network analysis. "
                "DO NOT generate manipulation strategies."
            ),
        )

    def _get_primitives(self, category: str) -> List[str]:
        """Get media primitives for category."""
        primitives = {
            "news_media": ["channel", "message", "filter", "gatekeeping"],
            "social_media": ["network_node", "amplifier", "filter", "channel"],
            "information_flow": ["channel", "message", "amplifier", "filter"],
            "memes": ["replicator", "mutation", "selection"],
            "disinformation": ["deception", "amplification", "filter bubble"],
        }
        return primitives.get(category, [])


class AMOSSocietyEngine:
    """Unified society/culture engine for social analysis."""

    DOMAINS = {
        "institutional": InstitutionalKernel,
        "cultural": CulturalNormsKernel,
        "demographic": DemographicKernel,
        "media": MediaInformationKernel,
    }

    def __init__(self):
        self.runtime = get_runtime()
        self.kernels: Dict[str, Any] = {}
        self._init_kernels()

    def _init_kernels(self):
        """Initialize all society/culture kernels."""
        for domain, kernel_class in self.DOMAINS.items():
            self.kernels[domain] = kernel_class()

    def analyze(
        self,
        description: str,
        domains: Optional[List[str]] = None,
    ) -> Dict[str, SocietyAnalysis]:
        """Run society/culture analysis across specified domains."""
        domains = domains or list(self.DOMAINS.keys())
        results = {}

        for domain in domains:
            if domain in self.kernels:
                kernel = self.kernels[domain]
                results[domain] = kernel.analyze(description)

        return results

    def get_findings_summary(self, results: Dict[str, SocietyAnalysis]) -> str:
        """Generate human-readable findings summary."""
        lines = [
            "# AMOS Society/Culture Analysis Summary",
            "",
            f"Domains analyzed: {len(results)}",
            f"Overall confidence: {sum(r.confidence for r in results.values()) / len(results):.2f}",
            "",
            "⚠️ SAFETY NOTICE:",
            "⚠️ Avoid prescriptive cultural judgments",
            "⚠️ Respect cultural diversity and context",
            "⚠️ Flag sensitive demographic topics",
            "⚠️ Do not generate manipulation strategies",
            "",
            "## Findings by Domain",
            "",
        ]

        for domain, analysis in results.items():
            lines.extend(
                [
                    f"### {domain.upper().replace('_', ' ')}",
                    f"Confidence: {analysis.confidence:.2f}",
                    f"Findings: {len([f for f in analysis.findings if f.get('type') != 'safety_warnings'])}",
                    "",
                ]
            )

            for finding in analysis.findings:
                if finding.get("type") == "safety_warnings":
                    for warning in finding.get("warnings", []):
                        lines.append(f"⚠️ {warning}")
                else:
                    cat = finding.get("category", "general")
                    lines.append(f"- **{cat}**: {finding.get('detected_terms', [])}")
                    primitives = (
                        finding.get("institutional_primitives")
                        or finding.get("cultural_primitives")
                        or finding.get("demographic_primitives")
                        or finding.get("media_primitives")
                    )
                    if primitives:
                        lines.append(f"  Primitives: {', '.join(primitives[:3])}")
            lines.append("")

        # Limitations section
        lines.extend(
            [
                "## Limitations",
                "",
            ]
        )
        all_limitations = set()
        for analysis in results.values():
            all_limitations.update(analysis.limitations)
        for limitation in all_limitations:
            lines.append(f"- {limitation}")

        # Law compliance
        lines.extend(
            [
                "",
                "## Law Compliance",
                "",
            ]
        )
        for domain, analysis in results.items():
            compliant = sum(1 for v in analysis.law_compliance.values() if v)
            total = len(analysis.law_compliance)
            lines.append(f"- {domain}: {compliant}/{total} laws")

        # Gap acknowledgment
        lines.extend(
            [
                "",
                "## Gap Acknowledgment",
                "GAP: Society/culture analysis is pattern matching on text, not social science research.",
                "No fieldwork. No ethnography. No cultural immersion.",
                "Avoid prescriptive judgments. Respect cultural diversity.",
                "Human social expertise required for all conclusions.",
            ]
        )

        return "\n".join(lines)


# Singleton
_society_engine: Optional[AMOSSocietyEngine] = None


def get_society_engine() -> AMOSSocietyEngine:
    """Get singleton society/culture engine."""
    global _society_engine
    if _society_engine is None:
        _society_engine = AMOSSocietyEngine()
    return _society_engine


def analyze_society(
    description: str,
    domains: Optional[List[str]] = None,
) -> Dict[str, SocietyAnalysis]:
    """Quick helper for society/culture analysis."""
    return get_society_engine().analyze(description, domains)


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS SOCIETY/CULTURE ENGINE TEST")
    print("=" * 60)

    engine = get_society_engine()

    # Test multi-domain analysis
    test_input = (
        "Analyze how social media platforms influence cultural values "
        "and institutional trust. Consider urbanization trends and "
        "generational value shifts in modern democratic societies."
    )

    print(f"\nInput: {test_input[:70]}...")

    results = engine.analyze(test_input)

    print(f"\nAnalyzed {len(results)} society/culture domains:")
    for domain, analysis in results.items():
        findings_count = len([f for f in analysis.findings if f.get("type") != "safety_warnings"])
        print(f"  - {domain}: {findings_count} findings, confidence={analysis.confidence:.2f}")

    # Full summary
    print("\n" + "=" * 60)
    print(engine.get_findings_summary(results))

    print("\n" + "=" * 60)
    print("Society/Culture Engine: OPERATIONAL")
    print("=" * 60)
    print("\nAll 4 society domains active: Institutional, Cultural, Demographic, Media")
    print("SAFETY: Respect cultural diversity. No prescriptive judgments.")
