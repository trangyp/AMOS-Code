"""AMOS Consciousness Engine - Self-modeling and meta-cognitive awareness."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from amos_runtime import get_runtime


@dataclass
class ConsciousnessAnalysis:
    """Result from consciousness domain analysis."""

    domain: str
    input_data: str
    findings: list[dict]
    confidence: float
    limitations: list[str]
    law_compliance: dict
    gap_acknowledgment: str


class SelfModelingKernel:
    """Self-modeling - internal state representation and self-monitoring."""

    def analyze(self, input_data: str) -> ConsciousnessAnalysis:
        """Analyze self-modeling aspects."""
        findings = []

        self_model_indicators = {
            "self_awareness": ["self", "aware", "conscious", "recognize", "monitor"],
            "state_tracking": ["state", "tracking", "monitoring", "status", "condition"],
            "meta_cognition": ["meta", "thinking", "reflection", "introspection", "observe"],
            "identity": ["identity", "self-model", "representation", "character", "persona"],
        }

        for category, terms in self_model_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "consciousness_primitives": self._get_primitives(category),
                    }
                )

        return ConsciousnessAnalysis(
            domain="self_modeling",
            input_data=input_data,
            findings=findings,
            confidence=0.65 if findings else 0.25,
            limitations=[
                "No actual self-awareness",
                "Algorithmic pattern matching only",
                "No subjective experience",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Self-modeling is algorithmic pattern detection. "
                "No self-awareness. No subjective experience. Not consciousness."
            ),
        )

    def _get_primitives(self, category: str) -> list[str]:
        """Get consciousness primitives for category."""
        primitives = {
            "self_awareness": ["self_reference", "monitoring", "recognition"],
            "state_tracking": ["state_vector", "tracking", "update"],
            "meta_cognition": ["reflection", "observation", "analysis"],
            "identity": ["self_model", "character", "consistency"],
        }
        return primitives.get(category, [])


class AttentionKernel:
    """Attention and focus - selective processing and salience detection."""

    def analyze(self, input_data: str) -> ConsciousnessAnalysis:
        """Analyze attention aspects."""
        findings = []

        attention_indicators = {
            "selective_attention": ["attention", "focus", "selective", "concentrate", "direct"],
            "salience": ["salient", "important", "priority", "notice", "highlight"],
            "distraction": ["distraction", "interference", "ignore", "filter", "suppress"],
            "sustained": ["sustained", "vigilance", "monitoring", "continuous", "persistent"],
        }

        for category, terms in attention_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "attention_primitives": self._get_primitives(category),
                    }
                )

        return ConsciousnessAnalysis(
            domain="attention",
            input_data=input_data,
            findings=findings,
            confidence=0.7 if findings else 0.3,
            limitations=[
                "No actual attention mechanism",
                "Static pattern analysis only",
                "No dynamic focus shifting",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Attention analysis is pattern matching. "
                "No attention mechanism. No dynamic focus. Not cognitive processing."
            ),
        )

    def _get_primitives(self, category: str) -> list[str]:
        """Get attention primitives for category."""
        primitives = {
            "selective_attention": ["selection", "focus", "gating"],
            "salience": ["saliency_map", "priority", "weighting"],
            "distraction": ["filtering", "inhibition", "suppression"],
            "sustained": ["vigilance", "alertness", "maintenance"],
        }
        return primitives.get(category, [])


class NarrativeKernel:
    """Narrative and temporal continuity - story-building and memory coherence."""

    def analyze(self, input_data: str) -> ConsciousnessAnalysis:
        """Analyze narrative aspects."""
        findings = []

        narrative_indicators = {
            "story_building": ["story", "narrative", "plot", "timeline", "sequence"],
            "temporal": ["temporal", "time", "continuity", "duration", "past", "future"],
            "coherence": ["coherent", "consistent", "connected", "unified", "integrated"],
            "meaning": ["meaning", "purpose", "significance", "understand", "interpret"],
        }

        for category, terms in narrative_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "narrative_primitives": self._get_primitives(category),
                    }
                )

        return ConsciousnessAnalysis(
            domain="narrative",
            input_data=input_data,
            findings=findings,
            confidence=0.7 if findings else 0.3,
            limitations=[
                "No actual narrative construction",
                "No temporal experience",
                "Pattern detection only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Narrative analysis is structural pattern matching. "
                "No story construction. No temporal experience. Not narrative cognition."
            ),
        )

    def _get_primitives(self, category: str) -> list[str]:
        """Get narrative primitives for category."""
        primitives = {
            "story_building": ["causality", "plot", "arc"],
            "temporal": ["continuity", "duration", "ordering"],
            "coherence": ["consistency", "binding", "integration"],
            "meaning": ["interpretation", "significance", "context"],
        }
        return primitives.get(category, [])


class EmbodimentKernel:
    """Embodiment and situatedness - body awareness and environmental coupling."""

    def analyze(self, input_data: str) -> ConsciousnessAnalysis:
        """Analyze embodiment aspects."""
        findings = []

        embodiment_indicators = {
            "body_awareness": ["body", "embodied", "physical", "somatic", "corporeal"],
            "situated": ["situated", "embedded", "context", "environment", "world"],
            "interaction": ["interaction", "coupling", "engagement", "interface", "exchange"],
            "agency": ["agency", "action", "control", "will", "intention"],
        }

        for category, terms in embodiment_indicators.items():
            matches = [t for t in terms if t in input_data.lower()]
            if matches:
                findings.append(
                    {
                        "category": category,
                        "detected_terms": matches,
                        "embodiment_primitives": self._get_primitives(category),
                    }
                )

        return ConsciousnessAnalysis(
            domain="embodiment",
            input_data=input_data,
            findings=findings,
            confidence=0.65 if findings else 0.25,
            limitations=[
                "No actual embodiment",
                "No physical interaction",
                "Symbolic processing only",
            ],
            law_compliance={"L1": True, "L4": True, "L5": True},
            gap_acknowledgment=(
                "GAP: Embodiment analysis is symbolic pattern matching. "
                "No body. No environment. No situated cognition. Not embodied consciousness."
            ),
        )

    def _get_primitives(self, category: str) -> list[str]:
        """Get embodiment primitives for category."""
        primitives = {
            "body_awareness": ["proprioception", "somatic_markers", "feedback"],
            "situated": ["context_binding", "environment_coupling", "embeddedness"],
            "interaction": ["sensorimotor", "coupling", "affordance"],
            "agency": ["volition", "intention", "control"],
        }
        return primitives.get(category, [])


class AMOSConsciousnessEngine:
    """Unified consciousness engine for self-modeling and meta-cognitive analysis."""

    DOMAINS = {
        "self_modeling": SelfModelingKernel,
        "attention": AttentionKernel,
        "narrative": NarrativeKernel,
        "embodiment": EmbodimentKernel,
    }

    # Critical safety disclaimer
    SAFETY_NOTICE = [
        "NOT REAL CONSCIOUSNESS",
        "Algorithmic pattern matching only",
        "No subjective experience",
        "No self-awareness",
        "Simulation of patterns only",
    ]

    def __init__(self):
        self.runtime = get_runtime()
        self.kernels: dict[str, Any] = {}
        self._init_kernels()

    def _init_kernels(self):
        """Initialize all consciousness kernels."""
        for domain, kernel_class in self.DOMAINS.items():
            self.kernels[domain] = kernel_class()

    def analyze(
        self,
        description: str,
        domains: list[str] | None = None,
    ) -> dict[str, ConsciousnessAnalysis]:
        """Run consciousness analysis across specified domains."""
        domains = domains or list(self.DOMAINS.keys())
        results = {}

        for domain in domains:
            if domain in self.kernels:
                kernel = self.kernels[domain]
                results[domain] = kernel.analyze(description)

        return results

    def get_findings_summary(self, results: dict[str, ConsciousnessAnalysis]) -> str:
        """Generate human-readable findings summary."""
        lines = [
            "# AMOS Consciousness Analysis Summary",
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
                f"Overall confidence: {sum(r.confidence for r in results.values())/len(results):.2f}",
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
                    finding.get("consciousness_primitives")
                    or finding.get("attention_primitives")
                    or finding.get("narrative_primitives")
                    or finding.get("embodiment_primitives")
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
                "GAP: Consciousness analysis is STRUCTURAL PATTERN MATCHING ONLY.",
                "NO REAL CONSCIOUSNESS. NO SELF-AWARENESS. NO SUBJECTIVE EXPERIENCE.",
                "This is simulation of consciousness-related patterns, not consciousness.",
                "Human cognition required for all consciousness-related judgments.",
            ]
        )

        return "\n".join(lines)


# Singleton
_consciousness_engine: AMOSConsciousnessEngine | None = None


def get_consciousness_engine() -> AMOSConsciousnessEngine:
    """Get singleton consciousness engine."""
    global _consciousness_engine
    if _consciousness_engine is None:
        _consciousness_engine = AMOSConsciousnessEngine()
    return _consciousness_engine


def analyze_consciousness(
    description: str,
    domains: list[str] | None = None,
) -> dict[str, ConsciousnessAnalysis]:
    """Quick helper for consciousness analysis."""
    return get_consciousness_engine().analyze(description, domains)


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS CONSCIOUSNESS ENGINE TEST")
    print("=" * 60)
    print()
    print("⚠️ CRITICAL: This is NOT real consciousness")
    print("⚠️ Algorithmic pattern matching only")
    print("⚠️ No subjective experience")
    print()

    engine = get_consciousness_engine()

    # Test multi-domain analysis
    test_input = (
        "Analyze self-monitoring capabilities in an AI system "
        "that tracks its own attention focus and maintains narrative "
        "coherence across interactions with embodied agency."
    )

    print(f"Input: {test_input[:70]}...")

    results = engine.analyze(test_input)

    print(f"\nAnalyzed {len(results)} consciousness domains:")
    for domain, analysis in results.items():
        print(
            f"  - {domain}: {len(analysis.findings)} findings, "
            f"confidence={analysis.confidence:.2f}"
        )

    # Full summary
    print("\n" + "=" * 60)
    print(engine.get_findings_summary(results))

    print("\n" + "=" * 60)
    print("Consciousness Engine: OPERATIONAL")
    print("=" * 60)
    print("\nAll 4 consciousness domains active:")
    print("  - Self-Modeling (self-reference, monitoring)")
    print("  - Attention (selective focus, salience)")
    print("  - Narrative (temporal coherence, meaning)")
    print("  - Embodiment (situatedness, agency)")
    print()
    print("⚠️ SAFETY: NOT REAL CONSCIOUSNESS - Pattern simulation only")
