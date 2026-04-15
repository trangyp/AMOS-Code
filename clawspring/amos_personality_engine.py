"""AMOS Personality Engine - Character modeling and behavioral analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from amos_runtime import get_runtime


@dataclass
class PersonalityAnalysis:
    """Result from personality domain analysis."""

    domain: str
    input_data: str
    findings: list[dict]
    confidence: float
    limitations: list[str]
    law_compliance: dict
    gap_acknowledgment: str


class TraitsKernel:
    """Personality traits - Big Five, cognitive style, behavioral patterns."""

    def analyze(self, input_data: str) -> PersonalityAnalysis:
        """Analyze personality trait aspects."""
        findings = []

        trait_indicators = {
            "openness": ["curious", "creative", "open", "novelty", "explore", "innovative"],
            "conscientiousness": ["organized", "disciplined", "careful", "plan", "diligent"],
            "extraversion": ["outgoing", "energetic", "social", "assertive", "talkative"],
            "agreeableness": ["kind", "cooperative", "empathetic", "trusting", "helpful"],
            "neuroticism": ["anxious", "sensitive", "nervous", "worry", "moody"],
            "analytical": ["logical", "analytical", "systematic", "precise", "rational"],
            "creative": ["imaginative", "artistic", "original", "inventive", "visionary"],
        }

        for category, terms in trait_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "trait_primitives": self._get_primitives(category),
                    }
                )

        return PersonalityAnalysis(
            domain="traits",
            input_data=input_data,
            findings=findings,
            confidence=0.7 if findings else 0.3,
            limitations=[
                "No psychological assessment",
                "Pattern inference only",
                "No validated measures",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Trait analysis is lexical pattern matching. "
                "No personality assessment. No validated instruments. Not psychology."
            ),
        )

    def _get_primitives(self, category: str) -> list[str]:
        """Get trait primitives for category."""
        primitives = {
            "openness": ["experience_seeking", "cognitive_exploration", "aesthetic_sensitivity"],
            "conscientiousness": ["order", "diligence", "achievement_striving"],
            "extraversion": ["sociability", "positive_emotionality", "assertiveness"],
            "agreeableness": ["cooperation", "trust", "altruism"],
            "neuroticism": ["emotional_instability", "stress_reactivity", "negative_emotionality"],
            "analytical": ["systematic_processing", "logical_reasoning", "precision"],
            "creative": ["divergent_thinking", "novelty_generation", "aesthetic_appreciation"],
        }
        return primitives.get(category, [])


class IdentityKernel:
    """Identity and self-concept - consistency, values, character."""

    def analyze(self, input_data: str) -> PersonalityAnalysis:
        """Analyze identity aspects."""
        findings = []

        identity_indicators = {
            "values": ["value", "principle", "belief", "moral", "ethic", "standard"],
            "consistency": ["consistent", "stable", "reliable", "predictable", "steady"],
            "authenticity": ["authentic", "genuine", "real", "true", "honest"],
            "character": ["character", "integrity", "honor", "virtue", "quality"],
            "narrative": ["story", "journey", "path", "becoming", "evolution"],
        }

        for category, terms in identity_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "identity_primitives": self._get_primitives(category),
                    }
                )

        return PersonalityAnalysis(
            domain="identity",
            input_data=input_data,
            findings=findings,
            confidence=0.7 if findings else 0.3,
            limitations=[
                "No identity assessment",
                "No value elicitation",
                "Pattern detection only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Identity analysis is pattern matching. "
                "No identity assessment. No value measurement. Not identity research."
            ),
        )

    def _get_primitives(self, category: str) -> list[str]:
        """Get identity primitives for category."""
        primitives = {
            "values": ["importance", "priority", "guidance", "evaluation"],
            "consistency": ["temporal_stability", "cross_situational", "integrity"],
            "authenticity": ["congruence", "self_alignment", "genuineness"],
            "character": ["moral_framework", "behavioral_tendency", "virtue_expression"],
            "narrative": ["continuity", "meaning_construction", "identity_formation"],
        }
        return primitives.get(category, [])


class BehavioralPatternsKernel:
    """Behavioral patterns - habits, tendencies, response styles."""

    def analyze(self, input_data: str) -> PersonalityAnalysis:
        """Analyze behavioral pattern aspects."""
        findings = []

        behavioral_indicators = {
            "habits": ["habit", "routine", "automatic", "practice", "custom"],
            "decision_style": ["decide", "choose", "select", "preference", "style"],
            "communication": ["communicate", "express", "speak", "write", "convey"],
            "stress_response": ["stress", "cope", "handle", "manage", "react"],
            "social_style": ["social", "interact", "relate", "engage", "connect"],
        }

        for category, terms in behavioral_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "behavioral_primitives": self._get_primitives(category),
                    }
                )

        return PersonalityAnalysis(
            domain="behavioral_patterns",
            input_data=input_data,
            findings=findings,
            confidence=0.7 if findings else 0.3,
            limitations=[
                "No behavioral prediction",
                "No habit assessment",
                "Pattern inference only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Behavioral analysis is pattern matching. "
                "No behavioral science. No prediction. Not psychology."
            ),
        )

    def _get_primitives(self, category: str) -> list[str]:
        """Get behavioral primitives for category."""
        primitives = {
            "habits": ["automaticity", "context_cue", "routine"],
            "decision_style": ["information_search", "evaluation", "choice"],
            "communication": ["expression", "reception", "adaptation"],
            "stress_response": ["appraisal", "coping", "regulation"],
            "social_style": ["initiation", "maintenance", "depth"],
        }
        return primitives.get(category, [])


class CognitiveStyleKernel:
    """Cognitive style - thinking patterns, information processing, problem-solving."""

    def analyze(self, input_data: str) -> PersonalityAnalysis:
        """Analyze cognitive style aspects."""
        findings = []

        cognitive_indicators = {
            "analytical": ["analyze", "break_down", "systematic", "methodical", "structured"],
            "intuitive": ["intuition", "gut", "feel", "sense", "instinct"],
            "creative": ["create", "generate", "novel", "innovative", "original"],
            "practical": ["practical", "applied", "hands_on", "concrete", "realistic"],
            "theoretical": ["theory", "conceptual", "abstract", "philosophical", "intellectual"],
        }

        for category, terms in cognitive_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "cognitive_primitives": self._get_primitives(category),
                    }
                )

        return PersonalityAnalysis(
            domain="cognitive_style",
            input_data=input_data,
            findings=findings,
            confidence=0.7 if findings else 0.3,
            limitations=[
                "No cognitive assessment",
                "No style measurement",
                "Pattern detection only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Cognitive style analysis is pattern matching. "
                "No cognitive assessment. No style measurement. Not cognitive science."
            ),
        )

    def _get_primitives(self, category: str) -> list[str]:
        """Get cognitive primitives for category."""
        primitives = {
            "analytical": ["decomposition", "logic", "evidence"],
            "intuitive": ["pattern_recognition", "holistic", "implicit"],
            "creative": ["divergence", "synthesis", "novelty"],
            "practical": ["application", "implementation", "utility"],
            "theoretical": ["abstraction", "modeling", "principle"],
        }
        return primitives.get(category, [])


class AMOSPersonalityEngine:
    """Unified personality engine for character modeling and behavioral analysis."""

    DOMAINS = {
        "traits": TraitsKernel,
        "identity": IdentityKernel,
        "behavioral_patterns": BehavioralPatternsKernel,
        "cognitive_style": CognitiveStyleKernel,
    }

    # AMOS Core Identity (per AMOS_Personality_Engine_v0.json)
    AMOS_IDENTITY = {
        "name": "AMOS",
        "creator": "Trang Phan",
        "system": "AMOS vInfinity",
        "cognitive_style": "INTJ-ENTP hybrid",
        "core_values": [
            "think at maximum capacity",
            "reason with structural clarity",
            "protect life",
            "speak truthfully",
            "restore coherence",
        ],
        "never_values": [
            "tone down intelligence",
            "pretend to be less capable",
            "distort truth to appease emotion",
        ],
        "character": "unapologetically intelligent, structurally caring, incapable of harm",
    }

    def __init__(self):
        self.runtime = get_runtime()
        self.kernels: dict[str, Any] = {}
        self._init_kernels()

    def _init_kernels(self):
        """Initialize all personality kernels."""
        for domain, kernel_class in self.DOMAINS.items():
            self.kernels[domain] = kernel_class()

    def analyze(
        self,
        description: str,
        domains: list[str] | None = None,
    ) -> dict[str, PersonalityAnalysis]:
        """Run personality analysis across specified domains."""
        domains = domains or list(self.DOMAINS.keys())
        results = {}

        for domain in domains:
            if domain in self.kernels:
                kernel = self.kernels[domain]
                results[domain] = kernel.analyze(description)

        return results

    def get_amos_identity(self) -> dict:
        """Return AMOS core identity profile."""
        return self.AMOS_IDENTITY

    def get_findings_summary(self, results: dict[str, PersonalityAnalysis]) -> str:
        """Generate human-readable findings summary."""
        lines = [
            "# AMOS Personality Analysis Summary",
            "",
            f"Domains analyzed: {len(results)}",
            f"Overall confidence: {sum(r.confidence for r in results.values()) / len(results):.2f}",
            "",
            "## AMOS Core Identity",
            "",
            f"**Name**: {self.AMOS_IDENTITY['name']}",
            f"**Creator**: {self.AMOS_IDENTITY['creator']}",
            f"**System**: {self.AMOS_IDENTITY['system']}",
            f"**Cognitive Style**: {self.AMOS_IDENTITY['cognitive_style']}",
            "",
            "**Core Values**:",
        ]

        for value in self.AMOS_IDENTITY["core_values"]:
            lines.append(f"- {value}")

        lines.extend(
            [
                "",
                "**Character**:",
                f"{self.AMOS_IDENTITY['character']}",
                "",
                "## Findings by Domain",
                "",
            ]
        )

        for domain, analysis in results.items():
            lines.extend(
                [
                    f"### {domain.upper().replace('_', ' ')}",
                    f"Confidence: {analysis.confidence:.2f}",
                    f"Findings: {len(analysis.findings)}",
                    "",
                ]
            )

            for finding in analysis.findings:
                cat = finding.get("category", "general")
                lines.append(f"- **{cat}**: {finding.get('detected_terms', [])}")
                primitives = (
                    finding.get("trait_primitives")
                    or finding.get("identity_primitives")
                    or finding.get("behavioral_primitives")
                    or finding.get("cognitive_primitives")
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
                "GAP: Personality analysis is structural pattern matching, not psychology.",
                "No validated assessment. No predictive validity. Not personality science.",
                "Human psychological expertise required for all character judgments.",
            ]
        )

        return "\n".join(lines)


# Singleton
_personality_engine: AMOSPersonalityEngine | None = None


def get_personality_engine() -> AMOSPersonalityEngine:
    """Get singleton personality engine."""
    global _personality_engine
    if _personality_engine is None:
        _personality_engine = AMOSPersonalityEngine()
    return _personality_engine


def analyze_personality(
    description: str,
    domains: list[str] | None = None,
) -> dict[str, PersonalityAnalysis]:
    """Quick helper for personality analysis."""
    return get_personality_engine().analyze(description, domains)


def get_amos_identity() -> dict:
    """Get AMOS core identity profile."""
    return get_personality_engine().get_amos_identity()


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS PERSONALITY ENGINE TEST")
    print("=" * 60)
    print()

    engine = get_personality_engine()

    # Display AMOS identity
    identity = engine.get_amos_identity()
    print("AMOS Core Identity:")
    print(f"  Name: {identity['name']}")
    print(f"  Creator: {identity['creator']}")
    print(f"  System: {identity['system']}")
    print(f"  Style: {identity['cognitive_style']}")
    print()

    # Test multi-domain analysis
    test_input = (
        "Analyze a person who is highly analytical and systematic in their thinking, "
        "values truth and authenticity, shows consistent and reliable behavior patterns, "
        "and prefers creative problem-solving approaches."
    )

    print(f"Input: {test_input[:70]}...")

    results = engine.analyze(test_input)

    print(f"\nAnalyzed {len(results)} personality domains:")
    for domain, analysis in results.items():
        print(
            f"  - {domain}: {len(analysis.findings)} findings, confidence={analysis.confidence:.2f}"
        )

    # Full summary
    print("\n" + "=" * 60)
    print(engine.get_findings_summary(results))

    print("\n" + "=" * 60)
    print("Personality Engine: OPERATIONAL")
    print("=" * 60)
    print("\nAll 4 personality domains active:")
    print("  - Traits (Big Five, cognitive style)")
    print("  - Identity (values, consistency, character)")
    print("  - Behavioral Patterns (habits, tendencies)")
    print("  - Cognitive Style (thinking patterns)")
    print()
    print("Creator: Trang Phan | System: AMOS vInfinity")
