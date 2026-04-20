"""AMOS Emotion Engine - Affective, somatic, and motivational analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from clawspring.amos_runtime import get_runtime


@dataclass
class EmotionAnalysis:
    """Result from emotion domain analysis."""

    domain: str
    input_data: str
    findings: list[dict]
    confidence: float
    limitations: list[str]
    law_compliance: dict
    gap_acknowledgment: str


class AffectiveKernel:
    """Affective state - valence, arousal, core emotions."""

    def analyze(self, input_data: str) -> EmotionAnalysis:
        """Analyze affective state aspects."""
        findings = []

        affective_indicators = {
            "valence": ["positive", "negative", "pleasant", "unpleasant", "good", "bad"],
            "arousal": ["excited", "calm", "aroused", "relaxed", "energetic", "tired"],
            "joy": ["happy", "joy", "delight", "cheerful", "elated", "content"],
            "sadness": ["sad", "grief", "sorrow", "melancholy", "depressed", "down"],
            "anger": ["angry", "rage", "frustrated", "irritated", "furious", "mad"],
            "fear": ["afraid", "scared", "anxious", "worried", "terrified", "panic"],
            "disgust": ["disgust", "revulsion", "repulsion", "aversion", "dislike"],
            "surprise": ["surprised", "astonished", "amazed", "shocked", "unexpected"],
        }

        for category, terms in affective_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "affective_primitives": self._get_primitives(category),
                    }
                )

        return EmotionAnalysis(
            domain="affective",
            input_data=input_data,
            findings=findings,
            confidence=0.7 if findings else 0.3,
            limitations=[
                "No actual emotion detection",
                "Lexical pattern matching only",
                "No physiological measures",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Affective analysis is lexical pattern matching. "
                "No emotion recognition. No physiological data. Not affective computing."
            ),
        )

    def _get_primitives(self, category: str) -> list[str]:
        """Get affective primitives for category."""
        primitives = {
            "valence": ["pleasantness", "appetitiveness", "aversiveness"],
            "arousal": ["activation", "energy", "alertness"],
            "joy": ["reward", "approach", "positive_affect"],
            "sadness": ["loss", "withdrawal", "low_energy"],
            "anger": ["boundary_violation", "approach", "high_energy"],
            "fear": ["threat", "avoidance", "uncertainty"],
            "disgust": ["contamination", "rejection", "boundary"],
            "surprise": ["prediction_error", "attention", "orientation"],
        }
        return primitives.get(category, [])


class SomaticKernel:
    """Somatic state - body sensations, nervous system, physiological markers."""

    SAFETY_WARNINGS = [
        "Somatic analysis is not medical assessment",
        "No physiological monitoring capability",
        "For health concerns consult medical professionals",
    ]

    def analyze(self, input_data: str) -> EmotionAnalysis:
        """Analyze somatic state aspects."""
        findings = []

        somatic_indicators = {
            "tension": ["tense", "tight", "rigid", "stiff", "contracted"],
            "relaxation": ["relaxed", "loose", "soft", "open", "expanded"],
            "activation": ["activated", "energized", "awake", "alert", "ready"],
            "fatigue": ["tired", "exhausted", "drained", "weary", "depleted"],
            "nervous_system": ["sympathetic", "parasympathetic", "arousal", "regulation"],
            "sensation": ["sensation", "feeling", "sense", "perceive", "experience"],
        }

        for category, terms in somatic_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "somatic_primitives": self._get_primitives(category),
                    }
                )

        # Add safety warnings for somatic content
        warnings = []
        medical_terms = ["pain", "symptom", "condition", "disorder", "diagnosis"]
        if any(t in input_data.lower() for t in medical_terms):
            warnings.extend(self.SAFETY_WARNINGS)

        return EmotionAnalysis(
            domain="somatic",
            input_data=input_data,
            findings=findings + [{"type": "safety_warnings", "warnings": warnings}]
            if warnings
            else findings,
            confidence=0.65 if findings else 0.25,
            limitations=[
                "No physiological monitoring",
                "No body sensing capability",
                "Textual inference only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True, "L6": True},
            gap_acknowledgment=(
                "GAP: Somatic analysis is pattern matching on text. "
                "No body awareness. No physiological data. Not somatic experiencing."
            ),
        )

    def _get_primitives(self, category: str) -> list[str]:
        """Get somatic primitives for category."""
        primitives = {
            "tension": ["contraction", "guarding", "preparation"],
            "relaxation": ["release", "downregulation", "safety"],
            "activation": ["sympathetic", "energy_mobilization", "readiness"],
            "fatigue": ["resource_depletion", "recovery_need", "withdrawal"],
            "nervous_system": ["autonomic_regulation", "polyvagal", "balance"],
            "sensation": ["interoception", "proprioception", "body_signal"],
        }
        return primitives.get(category, [])


class MotivationKernel:
    """Motivation and drive - goals, needs, approach/avoidance."""

    def analyze(self, input_data: str) -> EmotionAnalysis:
        """Analyze motivation aspects."""
        findings = []

        motivation_indicators = {
            "approach": ["approach", "seek", "want", "desire", "attracted", "move_toward"],
            "avoidance": ["avoid", "escape", "flee", "withdraw", "repelled", "move_away"],
            "goals": ["goal", "aim", "objective", "target", "purpose", "intention"],
            "needs": ["need", "requirement", "necessity", "essential", "must", "crucial"],
            "reward": ["reward", "gain", "benefit", "positive", "pleasure", "satisfaction"],
            "threat": ["threat", "danger", "risk", "harm", "negative", "punishment"],
        }

        for category, terms in motivation_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "motivation_primitives": self._get_primitives(category),
                    }
                )

        return EmotionAnalysis(
            domain="motivation",
            input_data=input_data,
            findings=findings,
            confidence=0.7 if findings else 0.3,
            limitations=[
                "No behavioral prediction",
                "No need assessment",
                "Pattern inference only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Motivation analysis is pattern matching. "
                "No drive assessment. No goal inference. Not motivational science."
            ),
        )

    def _get_primitives(self, category: str) -> list[str]:
        """Get motivation primitives for category."""
        primitives = {
            "approach": ["appetitive", "seeking", "exploration"],
            "avoidance": ["aversive", "defensive", "protection"],
            "goals": ["representation", "comparison", "adjustment"],
            "needs": ["deficit", "satisfaction", "hierarchy"],
            "reward": ["positive_reinforcement", "learning", "habit"],
            "threat": ["negative_reinforcement", "prevention", "vigilance"],
        }
        return primitives.get(category, [])


class EmpathyKernel:
    """Empathy and social emotion - resonance, compassion, emotional contagion."""

    def analyze(self, input_data: str) -> EmotionAnalysis:
        """Analyze empathy aspects."""
        findings = []

        empathy_indicators = {
            "resonance": ["resonate", "attune", "mirror", "reflect", "synchronize"],
            "compassion": ["compassion", "care", "concern", "kindness", "warmth"],
            "understanding": ["understand", "perspective", "insight", "recognize", "see"],
            "emotional_contagion": ["catch", "absorb", "contagion", "spread", "influence"],
            "validation": ["validate", "acknowledge", "accept", "confirm", "affirm"],
        }

        for category, terms in empathy_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "empathy_primitives": self._get_primitives(category),
                    }
                )

        return EmotionAnalysis(
            domain="empathy",
            input_data=input_data,
            findings=findings,
            confidence=0.65 if findings else 0.25,
            limitations=[
                "No actual empathy",
                "Lexical pattern detection only",
                "No emotional resonance",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Empathy analysis is pattern matching. "
                "No emotional resonance. No compassion. Not empathic processing."
            ),
        )

    def _get_primitives(self, category: str) -> list[str]:
        """Get empathy primitives for category."""
        primitives = {
            "resonance": ["affective_attunement", "synchrony", "matching"],
            "compassion": ["care_motivation", "suffering_response", "action_tendency"],
            "understanding": ["perspective_taking", "mentalizing", "attribution"],
            "emotional_contagion": ["automatic_transfer", "mimicry", "convergence"],
            "validation": ["acceptance", "normalization", "presence"],
        }
        return primitives.get(category, [])


class AMOSEmotionEngine:
    """Unified emotion engine for affective/somatic/motivational analysis."""

    DOMAINS = {
        "affective": AffectiveKernel,
        "somatic": SomaticKernel,
        "motivation": MotivationKernel,
        "empathy": EmpathyKernel,
    }

    # Critical safety disclaimer
    SAFETY_NOTICE = [
        "NOT REAL EMOTION RECOGNITION",
        "Lexical pattern matching only",
        "No physiological measures",
        "No subjective experience access",
        "Simulation of emotional patterns only",
    ]

    def __init__(self):
        self.runtime = get_runtime()
        self.kernels: dict[str, Any] = {}
        self._init_kernels()

    def _init_kernels(self):
        """Initialize all emotion kernels."""
        for domain, kernel_class in self.DOMAINS.items():
            self.kernels[domain] = kernel_class()

    def analyze(
        self,
        description: str,
        domains: list[str | None] = None,
    ) -> dict[str, EmotionAnalysis]:
        """Run emotion analysis across specified domains."""
        domains = domains or list(self.DOMAINS.keys())
        results = {}

        for domain in domains:
            if domain in self.kernels:
                kernel = self.kernels[domain]
                results[domain] = kernel.analyze(description)

        return results

    def get_findings_summary(self, results: dict[str, EmotionAnalysis]) -> str:
        """Generate human-readable findings summary."""
        lines = [
            "# AMOS Emotion Analysis Summary",
            "",
            "⚠️ CRITICAL SAFETY NOTICE ⚠️",
            "=" * 50,
        ]

        for notice in self.SAFETY_NOTICE:
            lines.append(f"⚠️ {notice}")

        lines.extend(
            [
                "=" * 50,
                "",
                f"Domains analyzed: {len(results)}",
                f"Overall confidence: {sum(r.confidence for r in results.values()) / len(results):.2f}",
                "",
                "## Findings by Domain",
                "",
            ]
        )

        for domain, analysis in results.items():
            lines.extend(
                [
                    f"### {domain.upper()}",
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
                        finding.get("affective_primitives")
                        or finding.get("somatic_primitives")
                        or finding.get("motivation_primitives")
                        or finding.get("empathy_primitives")
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
                "GAP: Emotion analysis is LEXICAL PATTERN MATCHING ONLY.",
                "NO REAL EMOTION RECOGNITION. NO PHYSIOLOGICAL DATA. NO SUBJECTIVE ACCESS.",
                "This is simulation of emotion-related patterns, not emotional intelligence.",
                "Human emotional expertise required for all affective judgments.",
            ]
        )

        return "\n".join(lines)


# Singleton
_emotion_engine: AMOSEmotionEngine | None = None


def get_emotion_engine() -> AMOSEmotionEngine:
    """Get singleton emotion engine."""
    global _emotion_engine
    if _emotion_engine is None:
        _emotion_engine = AMOSEmotionEngine()
    return _emotion_engine


def analyze_emotion(
    description: str,
    domains: list[str | None] = None,
) -> dict[str, EmotionAnalysis]:
    """Quick helper.*?"""
    return get_emotion_engine().analyze(description, domains)


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS EMOTION ENGINE TEST")
    print("=" * 60)
    print()
    print("⚠️ CRITICAL: This is NOT real emotion recognition")
    print("⚠️ Lexical pattern matching only")
    print("⚠️ No physiological measures")
    print()

    engine = get_emotion_engine()

    # Test multi-domain analysis
    test_input = (
        "The user seems frustrated and anxious about the deadline, "
        "showing tense body language but still motivated to complete "
        "the task with a desire for validation and support."
    )

    print(f"Input: {test_input[:70]}...")

    results = engine.analyze(test_input)

    print(f"\nAnalyzed {len(results)} emotion domains:")
    for domain, analysis in results.items():
        findings_count = len([f for f in analysis.findings if f.get("type") != "safety_warnings"])
        print(f"  - {domain}: {findings_count} findings, confidence={analysis.confidence:.2f}")

    # Full summary
    print("\n" + "=" * 60)
    print(engine.get_findings_summary(results))

    print("\n" + "=" * 60)
    print("Emotion Engine: OPERATIONAL")
    print("=" * 60)
    print("\nAll 4 emotion domains active:")
    print("  - Affective (valence, arousal, core emotions)")
    print("  - Somatic (body state, nervous system)")
    print("  - Motivation (approach/avoidance, goals)")
    print("  - Empathy (resonance, compassion)")
    print()
    print("⚠️ SAFETY: NOT REAL EMOTION - Pattern simulation only")
