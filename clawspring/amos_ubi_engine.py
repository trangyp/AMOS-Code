"""AMOS UBI Engine - Unified Biological Intelligence domains."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from amos_runtime import get_runtime


@dataclass
class UBIInput:
    """Input for UBI domain analysis."""

    description: str
    context: dict = field(default_factory=dict)
    time_horizon: str = "immediate"
    constraints: list[str] = field(default_factory=list)


@dataclass
class UBIResult:
    """Result from UBI domain analysis."""

    domain: str
    analysis: dict
    risk_flags: list[str]
    design_levers: list[str]
    safety_notices: list[str]
    gap_acknowledgment: str


class NBIEngine:
    """Neurobiological Intelligence - cognitive load, attention, bandwidth."""

    SAFETY_CONSTRAINTS = [
        "no_medical_diagnosis",
        "no_brain_state_diagnosis",
        "no_treatment_protocols",
        "no_harmful_instructions",
    ]

    def analyze(self, input_data: UBIInput) -> dict:
        """Analyze cognitive load and bandwidth."""
        # Estimate cognitive load from description complexity
        word_count = len(input_data.description.split())
        complexity = "high" if word_count > 50 else "medium" if word_count > 20 else "low"

        return {
            "cognitive_load_profile": complexity,
            "bandwidth_estimate": "limited" if complexity == "high" else "adequate",
            "complexity_fit": "requires_chunking" if complexity == "high" else "appropriate",
            "stability_estimate": "stable_under_normal_conditions",
            "design_levers": [
                "chunk_information",
                "reduce_steps",
                "provide_clear_progress_indicators",
            ],
        }


class NEIEngine:
    """Neuroemotional Intelligence - stress, arousal, valence patterns."""

    SAFETY_CONSTRAINTS = [
        "no_emotional_manipulation",
        "no_coercion",
        "respect_autonomy",
    ]

    def analyze(self, input_data: UBIInput) -> dict:
        """Analyze emotional dimensions (structural, not diagnostic)."""
        # Detect potential stress indicators
        stress_terms = ["urgent", "critical", "emergency", "deadline", "pressure"]
        stress_count = sum(1 for term in stress_terms if term in input_data.description.lower())
        arousal_level = "elevated" if stress_count > 1 else "normal"

        return {
            "arousal_pattern": arousal_level,
            "valence_estimate": "neutral_to_negative" if stress_count > 0 else "neutral",
            "stress_indicators_detected": stress_count,
            "design_levers": [
                "provide_reassurance_if_stress_detected",
                "avoid_additional_pressure",
                "offer_control_and_choice",
            ],
        }


class SIEngine:
    """Somatic Intelligence - body state, physical interaction, ergonomics."""

    SAFETY_CONSTRAINTS = [
        "no_physical_harm",
        "respect_ergonomic_limits",
        "consider_accessibility",
    ]

    def analyze(self, input_data: UBIInput) -> dict:
        """Analyze somatic/physical dimensions."""
        return {
            "posture_considerations": [
                "minimize_repetitive_strain",
                "support_varied_positions",
            ],
            "interaction_load": "consider_mouse_keyboard_fatigue",
            "ergonomic_recommendations": [
                "44px_minimum_touch_target",
                "readable_font_sizes_16px_plus",
                "contrast_for_visual_comfort",
            ],
            "design_levers": [
                "reduce_physical_effort",
                "support_alternate_input_methods",
            ],
        }


class BEIEngine:
    """Bioelectromagnetic Intelligence - rhythms, environmental coupling."""

    SAFETY_CONSTRAINTS = [
        "no_mystical_claims",
        "use_concrete_terms",
        "avoid_pseudoscience",
    ]

    def analyze(self, input_data: UBIInput) -> dict:
        """Analyze bioelectromagnetic/environmental dimensions."""
        return {
            "circadian_considerations": "respect_natural_energy_cycles",
            "environmental_coupling": [
                "lighting_conditions",
                "ambient_noise_levels",
                "temperature_comfort",
            ],
            "design_levers": [
                "avoid_sleep_disrupting_patterns",
                "respect_attention_cycles",
            ],
            "structural_note": "Environmental factors affect human performance",
        }


class AMOSUBIEngine:
    """Unified Biological Intelligence super-engine."""

    DOMAINS: dict[str, Any] = {
        "NBI": NBIEngine,
        "NEI": NEIEngine,
        "SI": SIEngine,
        "BEI": BEIEngine,
    }

    def __init__(self):
        self.runtime = get_runtime()
        self._engines: dict[str, Any] = {}

    def _get_engine(self, domain: str) -> Any:
        """Get or create domain engine."""
        if domain not in self._engines:
            engine_class = self.DOMAINS.get(domain)
            if engine_class:
                self._engines[domain] = engine_class()
        return self._engines.get(domain)

    def analyze(
        self,
        description: str,
        domains: list[str] | None = None,
        context: dict | None = None,
    ) -> dict[str, UBIResult]:
        """Run UBI analysis across specified domains."""
        target_domains = domains or list(self.DOMAINS.keys())
        input_data = UBIInput(
            description=description,
            context=context or {},
        )

        results = {}
        for domain in target_domains:
            engine = self._get_engine(domain)
            if engine:
                analysis = engine.analyze(input_data)
                results[domain] = UBIResult(
                    domain=domain,
                    analysis=analysis,
                    risk_flags=self._extract_risks(analysis),
                    design_levers=analysis.get("design_levers", []),
                    safety_notices=getattr(engine, "SAFETY_CONSTRAINTS", []),
                    gap_acknowledgment=(
                        f"GAP: {domain} analysis is structural modeling only. "
                        "No medical diagnosis, no physiological measurement, "
                        "no lived experience. Human biological reality is complex "
                        "and requires human judgment."
                    ),
                )

        return results

    def _extract_risks(self, analysis: dict) -> list[str]:
        """Extract risk flags from analysis."""
        risks = []
        if analysis.get("cognitive_load_profile") == "high":
            risks.append("high_cognitive_load")
        if analysis.get("stress_indicators_detected", 0) > 1:
            risks.append("elevated_stress_detected")
        return risks

    def get_human_factors_report(self, description: str) -> str:
        """Generate human factors report with UBI alignment."""
        results = self.analyze(description)

        lines = [
            "# AMOS UBI Human Factors Report",
            f"Input: {description[:60]}...",
            "",
            "## Biological Intelligence Analysis",
            "",
        ]

        for domain, result in results.items():
            lines.extend([
                f"### {domain}",
                f"Key findings: {list(result.analysis.keys())[:3]}",
                f"Design levers: {', '.join(result.design_levers[:2])}",
                "",
            ])

        lines.extend([
            "## Unified Recommendations",
            "1. Respect human cognitive limits (Miller's Law: 7±2 items)",
            "2. Minimize physical and mental strain",
            "3. Provide clear progress and control",
            "4. Avoid manipulative patterns",
            "",
            "## Safety Constraints",
            "- No medical diagnosis",
            "- No therapy or treatment protocols",
            "- No personal predictions",
            "- Respect human autonomy",
            "",
            "## Gap Acknowledgment",
            "This analysis models biological factors structurally.",
            "Human biology is complex and variable.",
            "Human testing and judgment required.",
        ])

        return "\n".join(lines)

    def get_engine_status(self) -> dict:
        """Get UBI engine status."""
        return {
            "domains": list(self.DOMAINS.keys()),
            "amos_version": "vInfinity",
            "ubi_aligned": True,
            "safety_first": True,
            "creator": "Trang Phan",
        }


# Singleton
_ubi_engine: AMOSUBIEngine | None = None


def get_ubi_engine() -> AMOSUBIEngine:
    """Get singleton UBI engine."""
    global _ubi_engine
    if _ubi_engine is None:
        _ubi_engine = AMOSUBIEngine()
    return _ubi_engine


def analyze_human_factors(description: str, domains: list[str] | None = None) -> dict[str, UBIResult]:
    """Quick human factors analysis with UBI alignment."""
    return get_ubi_engine().analyze(description, domains)


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS UBI ENGINE TEST")
    print("=" * 60)

    engine = get_ubi_engine()

    # Test scenarios
    test_cases = [
        "Design a stressful financial trading dashboard with real-time alerts",
        "Create a calm meditation app interface",
        "Build a complex multi-step form for tax filing",
    ]

    for test in test_cases:
        print(f"\n{'='*50}")
        print(f"Scenario: {test[:50]}...")
        print("=" * 50)

        results = engine.analyze(test)

        for domain, result in results.items():
            print(f"\n{domain}:")
            print(f"  Analysis keys: {list(result.analysis.keys())[:2]}")
            print(f"  Risk flags: {result.risk_flags or 'None'}")
            print(f"  Design levers: {result.design_levers[:2]}")

    print("\n" + "=" * 60)
    print("UBI Engine: OPERATIONAL")
    print("=" * 60)
    print("\nSafety: All UBI domains enforce structural modeling only.")
    print("No medical claims. No diagnosis. Human judgment required.")
