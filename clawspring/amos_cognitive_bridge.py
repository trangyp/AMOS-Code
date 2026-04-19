#!/usr/bin/env python3
"""AMOS Cognitive Bridge - UBI-LLM Integration Layer

Architectural Pattern: Perception (UBI) → Cognition (LLM) → Action (Response)
Connects biological intelligence analysis to LLM interactions for human-aware AI.

Owner: Trang
Version: 1.0.0
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from clawspring.amos_ubi_engine import AMOSUBIEngine, UBIResult


@dataclass
class CognitiveContext:
    """Contextual awareness for LLM interactions."""

    cognitive_load: str  # low, medium, high
    emotional_state: str  # calm, stressed, excited
    body_comfort: str  # comfortable, strained, fatigued
    environmental_fit: str  # optimal, acceptable, poor
    timestamp: datetime

    def to_prompt_injection(self) -> str:
        """Convert to LLM prompt context injection."""
        return f"""
[AMOS Biological Context - {self.timestamp.strftime('%H:%M')}]
- User cognitive load: {self.cognitive_load}
- Emotional state: {self.emotional_state}
- Physical comfort: {self.body_comfort}
- Environment: {self.environmental_fit}

Adapt response accordingly:
- High cognitive load → Simplify, bullet points, shorter sentences
- Stressed → Calm tone, reassurance, clear structure
- Physical strain → Minimize interaction steps, offer breaks
- Poor environment → Larger text, high contrast suggestions
"""


class CognitiveBridge:
    """Bridge between UBI Engine and LLM providers."""

    def __init__(self):
        self.ubi = AMOSUBIEngine()
        self._last_analysis: Optional[CognitiveContext] = None

    def analyze_user_state(self, description: str) -> CognitiveContext:
        """Analyze user biological state via UBI Engine."""
        results = self.ubi.analyze(description)

        # Extract from NBI (Neurobiological Intelligence)
        nbi = results.get("NBI", {})
        cognitive_load = self._assess_cognitive_load(nbi)

        # Extract from NEI (Neuroemotional Intelligence)
        nei = results.get("NEI", {})
        emotional_state = self._assess_emotional_state(nei)

        # Extract from SI (Somatic Intelligence)
        si = results.get("SI", {})
        body_comfort = self._assess_body_comfort(si)

        # Extract from BEI (Bioelectromagnetic Intelligence)
        bei = results.get("BEI", {})
        environmental_fit = self._assess_environment(bei)

        context = CognitiveContext(
            cognitive_load=cognitive_load,
            emotional_state=emotional_state,
            body_comfort=body_comfort,
            environmental_fit=environmental_fit,
            timestamp=datetime.now(UTC),
        )

        self._last_analysis = context
        return context

    def _assess_cognitive_load(self, nbi_result: UBIResult) -> str:
        """Assess cognitive load from NBI analysis."""
        risk_flags = nbi_result.risk_flags if nbi_result else []

        if "high_cognitive_load" in risk_flags:
            return "high"
        elif "moderate_cognitive_load" in risk_flags:
            return "medium"
        return "low"

    def _assess_emotional_state(self, nei_result: UBIResult) -> str:
        """Assess emotional state from NEI analysis."""
        risk_flags = nei_result.risk_flags if nei_result else []

        if any(r in risk_flags for r in ["high_arousal", "negative_valence"]):
            return "stressed"
        elif "moderate_arousal" in risk_flags:
            return "focused"
        return "calm"

    def _assess_body_comfort(self, si_result: UBIResult) -> str:
        """Assess physical comfort from SI analysis."""
        risk_flags = si_result.risk_flags if si_result else []

        if "posture_strain" in risk_flags or "repetitive_strain" in risk_flags:
            return "strained"
        elif "fatigue_risk" in risk_flags:
            return "fatigued"
        return "comfortable"

    def _assess_environment(self, bei_result: UBIResult) -> str:
        """Assess environmental fit from BEI analysis."""
        risk_flags = bei_result.risk_flags if bei_result else []

        if any(r in risk_flags for r in ["sleep_disruption", "attention_disruption"]):
            return "poor"
        elif "suboptimal_conditions" in risk_flags:
            return "acceptable"
        return "optimal"

    def enhance_prompt(self, user_prompt: str, context: Optional[CognitiveContext] = None) -> str:
        """Enhance user prompt with biological context for LLM."""
        if context is None:
            context = self._last_analysis

        if context is None:
            return user_prompt

        return f"""{context.to_prompt_injection()}

[User Request]
{user_prompt}
"""

    def get_response_guidelines(self) -> Dict[str, Any]:
        """Get UI/UX guidelines based on current biological state."""
        if self._last_analysis is None:
            return {
                "font_size": "16px",
                "line_height": "1.5",
                "max_width": "800px",
                "chunking": False,
                "tone": "neutral",
            }

        guidelines = {
            "font_size": "16px",
            "line_height": "1.5",
            "max_width": "800px",
            "chunking": False,
            "tone": "neutral",
        }

        # Adjust based on cognitive load
        if self._last_analysis.cognitive_load == "high":
            guidelines.update(
                {"font_size": "18px", "line_height": "1.8", "chunking": True, "max_width": "600px"}
            )

        # Adjust based on emotional state
        if self._last_analysis.emotional_state == "stressed":
            guidelines.update({"tone": "calm", "add_reassurance": True})

        # Adjust based on body comfort
        if self._last_analysis.body_comfort == "strained":
            guidelines.update({"minimize_interaction": True, "suggest_break": True})

        return guidelines


# Singleton instance
_cognitive_bridge: Optional[CognitiveBridge] = None


def get_cognitive_bridge() -> CognitiveBridge:
    """Get singleton cognitive bridge instance."""
    global _cognitive_bridge
    if _cognitive_bridge is None:
        _cognitive_bridge = CognitiveBridge()
    return _cognitive_bridge


def analyze_and_enhance(user_prompt: str, context_description: str = "") -> Tuple[str, dict]:
    """Convenience function: analyze state and enhance prompt."""
    bridge = get_cognitive_bridge()

    # Analyze biological state
    if context_description:
        context = bridge.analyze_user_state(context_description)
    else:
        context = bridge._last_analysis

    # Enhance prompt
    enhanced = bridge.enhance_prompt(user_prompt, context)
    guidelines = bridge.get_response_guidelines()

    return enhanced, guidelines
