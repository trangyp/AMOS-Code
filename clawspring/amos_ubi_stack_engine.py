"""AMOS UBI Stack Engine - Universal Biological Intelligence."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class BrainRegion(Enum):
    """Key brain regions for neurobiological analysis."""

    PREFRONTAL_CORTEX = "prefrontal_cortex"
    AMYGDALA = "amygdala"
    HIPPOCAMPUS = "hippocampus"
    INSULA = "insula"
    ANTERIOR_CINGULATE = "anterior_cingulate"
    BASAL_GANGLIA = "basal_ganglia"


class Neurotransmitter(Enum):
    """Major neurotransmitters."""

    DOPAMINE = "dopamine"
    SEROTONIN = "serotonin"
    NOREPINEPHRINE = "norepinephrine"
    GABA = "gaba"
    GLUTAMATE = "glutamate"
    ACETYLCHOLINE = "acetylcholine"
    OXYTOCIN = "oxytocin"
    CORTISOL = "cortisol"


class ANSState(Enum):
    """Autonomic Nervous System states."""

    SYMPATHETIC_AROUSAL = "sympathetic_arousal"
    PARASYMPATHETIC_REST = "parasympathetic_rest"
    VENTRAL_VAGAL_SAFE = "ventral_vagal_safe"
    DORSAL_VAGAL_SHUTDOWN = "dorsal_vagal_shutdown"


@dataclass
class BiologicalState:
    """Represents a biological state snapshot."""

    timestamp: float
    ans_state: ANSState
    threat_index: float  # 0-1
    safety_index: float  # 0-1
    neurotransmitter_levels: dict[str, float] = field(default_factory=dict)


class NeurobiologyKernel:
    """Core neurobiological understanding."""

    def __init__(self):
        self.brain_regions = {region: {"activation": 0.5} for region in BrainRegion}
        self.neurotransmitter_baseline = {
            Neurotransmitter.DOPAMINE: 0.5,
            Neurotransmitter.SEROTONIN: 0.6,
            Neurotransmitter.NOREPINEPHRINE: 0.3,
            Neurotransmitter.GABA: 0.7,
            Neurotransmitter.GLUTAMATE: 0.5,
            Neurotransmitter.ACETYLCHOLINE: 0.4,
            Neurotransmitter.OXYTOCIN: 0.3,
            Neurotransmitter.CORTISOL: 0.2,
        }

    def simulate_stress_response(self, stressor_intensity: float) -> dict[str, Any]:
        """Simulate neurobiological stress response."""
        # Amygdala detects threat
        amygdala_activation = min(1.0, 0.3 + stressor_intensity * 0.7)
        self.brain_regions[BrainRegion.AMYGDALA]["activation"] = amygdala_activation
        # HPA axis activation
        cortisol_level = min(1.0, 0.2 + stressor_intensity * 0.8)
        # Norepinephrine release ( sympathetic arousal)
        ne_level = min(1.0, 0.3 + stressor_intensity * 0.6)
        # Prefrontal cortex suppression ( stress reduces executive function)
        pfc_suppression = max(0.2, 0.7 - stressor_intensity * 0.4)
        self.brain_regions[BrainRegion.PREFRONTAL_CORTEX]["activation"] = pfc_suppression
        return {
            "amygdala_activation": round(amygdala_activation, 2),
            "cortisol_level": round(cortisol_level, 2),
            "norepinephrine": round(ne_level, 2),
            "pfc_activation": round(pfc_suppression, 2),
            "ans_state": ANSState.SYMPATHETIC_AROUSAL.value,
        }

    def simulate_calm_response(self, safety_signals: float) -> dict[str, Any]:
        """Simulate neurobiological calm/safety response."""
        # Oxytocin release ( social bonding/safety)
        oxytocin = min(1.0, 0.3 + safety_signals * 0.5)
        # GABA increase ( inhibition/reduced anxiety)
        gaba = min(1.0, 0.7 + safety_signals * 0.2)
        # Serotonin stabilization
        serotonin = min(1.0, 0.6 + safety_signals * 0.3)
        # Prefrontal cortex optimal activation
        self.brain_regions[BrainRegion.PREFRONTAL_CORTEX]["activation"] = 0.8
        return {
            "oxytocin": round(oxytocin, 2),
            "gaba": round(gaba, 2),
            "serotonin": round(serotonin, 2),
            "pfc_activation": 0.8,
            "ans_state": ANSState.VENTRAL_VAGAL_SAFE.value,
        }

    def get_window_of_tolerance(self, arousal: float) -> str:
        """Determine window of tolerance based on arousal."""
        if arousal < 0.3:
            return "hypoarousal (dorsal vagal)"
        elif arousal < 0.7:
            return "window_of_tolerance (ventral vagal)"
        else:
            return "hyperarousal (sympathetic)"


class AutonomicNervousSystemKernel:
    """ANS regulation and polyvagal theory implementation."""

    def __init__(self):
        self.current_state = ANSState.VENTRAL_VAGAL_SAFE
        self.arousal_level = 0.5
        self.heart_rate_variability = 0.6  # Higher is better

    def assess_vagal_tone(self, hrv: float, respiratory_rate: float) -> dict[str, Any]:
        """Assess vagal tone (parasympathetic capacity)."""
        # Higher HRV indicates better vagal tone
        vagal_tone = min(1.0, hrv * 1.2)
        # Slower respiratory rate indicates better regulation
        respiratory_health = max(0.0, 1.0 - (respiratory_rate - 12) / 20)
        return {
            "vagal_tone": round(vagal_tone, 2),
            "respiratory_regulation": round(respiratory_health, 2),
            "overall_capacity": round((vagal_tone + respiratory_health) / 2, 2),
        }

    def detect_state_shift(self, new_arousal: float, context: str) -> ANSState:
        """Detect ANS state shift."""
        if new_arousal > 0.8:
            return ANSState.SYMPATHETIC_AROUSAL
        elif new_arousal < 0.2:
            return ANSState.DORSAL_VAGAL_SHUTDOWN
        elif "social" in context.lower() or "safe" in context.lower():
            return ANSState.VENTRAL_VAGAL_SAFE
        else:
            return ANSState.PARASYMPATHETIC_REST

    def get_regulation_strategy(self, current_state: ANSState) -> str:
        """Get appropriate regulation strategy."""
        strategies = {
            ANSState.SYMPATHETIC_AROUSAL: "Grounding, slow breathing, bilateral stimulation",
            ANSState.DORSAL_VAGAL_SHUTDOWN: "Gentle movement, warmth, social engagement",
            ANSState.VENTRAL_VAGAL_SAFE: "Maintain connection, collaborative problem-solving",
            ANSState.PARASYMPATHETIC_REST: "Gradual engagement, energy conservation",
        }
        return strategies.get(current_state, "General regulation techniques")


class StressPhysiologyKernel:
    """HPA axis and stress response physiology."""

    def __init__(self):
        self.hpa_axis_active = False
        self.cortisol_cycle = {"morning": 0.9, "afternoon": 0.5, "evening": 0.3}
        self.allostatic_load = 0.0  # Cumulative wear and tear

    def calculate_allostatic_load(self, stressors: list[float]) -> float:
        """Calculate cumulative allostatic load."""
        # Sum of stressor magnitudes with time decay
        load = sum(s * (0.9**i) for i, s in enumerate(stressors[-10:]))
        self.allostatic_load = min(1.0, load / 5)
        return self.allostatic_load

    def hpa_axis_response(
        self, threat_perception: float, time_of_day: str = "morning"
    ) -> dict[str, Any]:
        """Simulate HPA axis cortisol response."""
        baseline = self.cortisol_cycle.get(time_of_day, 0.5)
        # Cortisol rises with threat, peaks at 20-30 minutes
        cortisol_response = min(1.0, baseline + threat_perception * 0.4)
        # Negative feedback loop (delayed)
        recovery_time = 30 + int(threat_perception * 60)  # minutes
        return {
            "baseline_cortisol": baseline,
            "peak_cortisol": round(cortisol_response, 2),
            "recovery_time_minutes": recovery_time,
            "hpa_active": threat_perception > 0.3,
        }

    def assess_recovery_capacity(self, sleep_quality: float, social_support: float) -> float:
        """Assess capacity for physiological recovery."""
        return min(1.0, (sleep_quality * 0.5 + social_support * 0.5))


class SocialEngagementSystem:
    """Ventrolateral vagal complex - social engagement circuitry."""

    def __init__(self):
        self.engagement_capacity = 0.7
        self.recent_social_signals: list[dict] = []

    def detect_safety_cues(self, input_text: str) -> dict[str, Any]:
        """Detect prosodic and linguistic safety cues."""
        safety_markers = ["welcome", "safe", "together", "connection", "trust", "gentle"]
        threat_markers = ["danger", "attack", "alone", "abandon", "reject"]
        safety_count = sum(1 for m in safety_markers if m in input_text.lower())
        threat_count = sum(1 for m in threat_markers if m in input_text.lower())
        return {
            "safety_cues": safety_count,
            "threat_cues": threat_count,
            "net_safety": safety_count - threat_count,
            "can_socially_engage": safety_count > threat_count,
        }

    def assess_facial_vocal_cues(self, prosody: str = "neutral") -> dict[str, Any]:
        """Assess facial and vocal prosody (simulated)."""
        cues = {
            "warm": {"engagement": 0.8, "safety": 0.9},
            "neutral": {"engagement": 0.5, "safety": 0.6},
            "cold": {"engagement": 0.2, "safety": 0.3},
            "animated": {"engagement": 0.9, "safety": 0.7},
        }
        return cues.get(prosody, cues["neutral"])


class UBIStackEngine:
    """AMOS UBI Stack Engine - Universal Biological Intelligence."""

    VERSION = "vInfinity_UBI_1.0.0"
    NAME = "AMOS_UBI_Stack_OMEGA"

    def __init__(self):
        self.neurobiology = NeurobiologyKernel()
        self.ans = AutonomicNervousSystemKernel()
        self.stress = StressPhysiologyKernel()
        self.social = SocialEngagementSystem()

    def analyze(self, scenario: str, context: dict[str, Any] = None) -> dict[str, Any]:
        """Run UBI neurobiological analysis."""
        context = context or {}
        scenario_lower = scenario.lower()
        results: dict[str, Any] = {
            "scenario": scenario[:100],
            "neurobiology": {},
            "ans_analysis": {},
            "stress_physiology": {},
            "social_engagement": {},
            "recommendations": [],
        }
        # Detect stress vs calm in scenario
        stress_keywords = ["stress", "anxiety", "fear", "panic", "overwhelm", "threat", "danger"]
        calm_keywords = ["calm", "safe", "relaxed", "peaceful", "rest", "breathe", "gentle"]
        stress_level = sum(1 for kw in stress_keywords if kw in scenario_lower) / len(
            stress_keywords
        )
        calm_level = sum(1 for kw in calm_keywords if kw in scenario_lower) / len(calm_keywords)
        # Neurobiology analysis
        if stress_level > calm_level:
            neuro_result = self.neurobiology.simulate_stress_response(stress_level)
            results["neurobiology"] = {**neuro_result, "state": "stress_response"}
        else:
            neuro_result = self.neurobiology.simulate_calm_response(calm_level)
            results["neurobiology"] = {**neuro_result, "state": "calm_response"}
        # ANS analysis
        arousal = neuro_result.get("amygdala_activation", 0.5) if stress_level > calm_level else 0.3
        window = self.neurobiology.get_window_of_tolerance(arousal)
        current_ans = self.ans.detect_state_shift(arousal, scenario)
        regulation_strategy = self.ans.get_regulation_strategy(current_ans)
        results["ans_analysis"] = {
            "arousal_level": round(arousal, 2),
            "window_of_tolerance": window,
            "current_state": current_ans.value,
            "regulation_strategy": regulation_strategy,
        }
        # Stress physiology
        allostatic = self.stress.calculate_allostatic_load([stress_level, calm_level])
        hpa = self.stress.hpa_axis_response(stress_level)
        results["stress_physiology"] = {
            "allostatic_load": round(allostatic, 2),
            "hpa_axis": hpa,
        }
        # Social engagement
        safety_cues = self.social.detect_safety_cues(scenario)
        prosody = self.social.assess_facial_vocal_cues()
        results["social_engagement"] = {
            "safety_cues": safety_cues,
            "prosodic_assessment": prosody,
            "can_socially_engage": safety_cues["can_socially_engage"]
            and prosody["engagement"] > 0.5,
        }
        # Generate recommendations
        recommendations = []
        if current_ans == ANSState.SYMPATHETIC_AROUSAL:
            recommendations.append("Immediate: Grounding techniques (5-4-3-2-1 senses)")
            recommendations.append("Breathing: Extended exhale (4-7-8 pattern)")
            recommendations.append("Movement: Bilateral stimulation (walking, tapping)")
        elif current_ans == ANSState.DORSAL_VAGAL_SHUTDOWN:
            recommendations.append("Gentle: Small movements, warmth, orienting")
            recommendations.append("Social: Minimal demand, presence without pressure")
        elif current_ans == ANSState.VENTRAL_VAGAL_SAFE:
            recommendations.append("Optimal: Collaborative problem-solving possible")
            recommendations.append("Maintain: Social connection and engagement")
        if not safety_cues["can_socially_engage"]:
            recommendations.append("Safety: Establish safety cues before complex tasks")
        results["recommendations"] = recommendations
        return results

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "Role: Universal Biological Intelligence - Neurobiological Analysis",
            "",
            "## UBI Stack Overview",
            "The UBI Stack provides neurobiological intelligence for understanding",
            "stress responses, autonomic nervous system states, and biological",
            "foundations of cognition and behavior.",
            "",
            "## Neurobiological Analysis",
        ]
        neuro = results.get("neurobiology", {})
        lines.extend(
            [
                f"- **State**: {neuro.get('state', 'N/A')}",
                f"- **Amygdala Activation**: {neuro.get('amygdala_activation', 'N/A')}",
                f"- **Prefrontal Cortex**: {neuro.get('pfc_activation', 'N/A')}",
                f"- **Cortisol Level**: {neuro.get('cortisol_level', 'N/A')}",
            ]
        )
        if "oxytocin" in neuro:
            lines.append(f"- **Oxytocin**: {neuro.get('oxytocin')}")
        if "gaba" in neuro:
            lines.append(f"- **GABA**: {neuro.get('gaba')}")
        ans = results.get("ans_analysis", {})
        lines.extend(
            [
                "",
                "## Autonomic Nervous System",
                f"- **Current State**: {ans.get('current_state', 'N/A')}",
                f"- **Arousal Level**: {ans.get('arousal_level', 0):.2f}",
                f"- **Window of Tolerance**: {ans.get('window_of_tolerance', 'N/A')}",
            ]
        )
        lines.extend(
            [
                "",
                "### Polyvagal Theory States",
                "- **Ventral Vagal (Safe/Social)**: Social engagement, connectedness",
                "- **Sympathetic (Arousal)**: Fight/flight, mobilization",
                "- **Dorsal Vagal (Shutdown)**: Freeze, immobilization, conservation",
            ]
        )
        stress = results.get("stress_physiology", {})
        lines.extend(
            [
                "",
                "## Stress Physiology",
                f"- **Allostatic Load**: {stress.get('allostatic_load', 0):.2f} (cumulative wear)",
            ]
        )
        hpa = stress.get("hpa_axis", {})
        if hpa:
            lines.extend(
                [
                    "",
                    "### HPA Axis Response",
                    f"- **Baseline Cortisol**: {hpa.get('baseline_cortisol', 0):.2f}",
                    f"- **Peak Cortisol**: {hpa.get('peak_cortisol', 0):.2f}",
                    f"- **Recovery Time**: {hpa.get('recovery_time_minutes', 0)} min",
                    f"- **HPA Active**: {hpa.get('hpa_active', False)}",
                ]
            )
        social = results.get("social_engagement", {})
        safety = social.get("safety_cues", {})
        prosody = social.get("prosodic_assessment", {})
        lines.extend(
            [
                "",
                "## Social Engagement System",
                f"- **Safety Cues Detected**: {safety.get('safety_cues', 0)}",
                f"- **Threat Cues Detected**: {safety.get('threat_cues', 0)}",
                f"- **Net Safety Score**: {safety.get('net_safety', 0)}",
                f"- **Can Socially Engage**: {social.get('can_socially_engage', False)}",
                f"- **Engagement Capacity**: {prosody.get('engagement', 0):.2f}",
            ]
        )
        recommendations = results.get("recommendations", [])
        if recommendations:
            lines.extend(
                [
                    "",
                    "## Neurobiological Recommendations",
                ]
            )
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
        lines.extend(
            [
                "",
                "## Key Neurotransmitters",
                "- **Dopamine**: Reward, motivation, prediction error",
                "- **Serotonin**: Mood stabilization, well-being",
                "- **Norepinephrine**: Arousal, alertness, attention",
                "- **GABA**: Inhibition, anxiety reduction",
                "- **Oxytocin**: Social bonding, trust, safety",
                "- **Cortisol**: Stress response, energy mobilization",
                "",
                "## Brain Regions",
                "- **Prefrontal Cortex**: Executive function, decision-making",
                "- **Amygdala**: Threat detection, emotional salience",
                "- **Hippocampus**: Memory, context, time perception",
                "- **Insula**: Interoception, emotional awareness",
                "",
                "## Safety and Constraints",
                "- Does not replace medical or therapeutic advice",
                "- Simplified neurobiological modeling",
                "- Not for diagnosing medical conditions",
                "- Focus on educational and self-regulation support",
                "",
                "## Integration with Species Interaction Core",
                "The UBI Stack provides biological foundation for the Species",
                "Interaction Core's nervous system monitoring and safety",
                "assessment capabilities.",
            ]
        )
        return "\n".join(lines)


# Singleton instance
_ubi_engine: UBIStackEngine | None = None


def get_ubi_stack_engine() -> UBIStackEngine:
    """Get or create the UBI Stack Engine singleton."""
    global _ubi_engine
    if _ubi_engine is None:
        _ubi_engine = UBIStackEngine()
    return _ubi_engine
