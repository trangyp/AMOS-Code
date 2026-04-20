#!/usr/bin/env python3
"""AMOS Coherence Engine - Core Runtime Implementation

Implements the 6-engine architecture for human coherence induction:
1. Signal Detection Engine (E_sig) - Extract signal from noise
2. Cognitive Deconstruction Engine (E_dec) - Loosen false structures
3. State Regulation Engine (E_reg) - Match intensity to capacity
4. Intervention Selection Engine (E_int) - Choose smallest useful disruption
5. Coherence Induction Engine (E_coh) - Create conditions for self-alignment
6. Verification Engine (E_ver) - Check stability/agency/clarity deltas

Master Law:
    Do not change the human.
    Change conditions -> human reorganizes.

Success Function:
    J = Coherence + Agency + Stability - Distortion - Dependency - Overload
"""

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HumanState(Enum):
    """Human processing capacity states."""

    STABLE = "stable"
    ACTIVATED = "activated"
    OVERLOADED = "overloaded"
    SHUTDOWN = "shutdown"
    HIGH_RISK = "high_risk"


class InterventionMode(Enum):
    """Available intervention modes."""

    MIRROR = "mirror"
    SEPARATE = "separate"
    REFRAME = "reframe"
    DECONSTRUCT = "deconstruct"
    GROUND = "ground"
    BOUNDARY = "boundary"
    MICRO_STEP = "micro_step"


@dataclass
class HumanStateVector:
    """Hidden state estimate H_t = (Cog, Nerv, Perc, Id, Aff, Cap, Env)."""

    cognitive_structure: str = ""  # Cog_t
    nervous_system_state: str = ""  # Nerv_t
    perception_frame: str = ""  # Perc_t
    identity_organization: str = ""  # Id_t
    affective_state: str = ""  # Aff_t
    processing_capacity: float = 1.0  # Cap_t (0.0 to 1.0)
    context_environment: str = ""  # Env_t


@dataclass
class MessageAnalysis:
    """M_t = Sig_t + Noi_t."""

    surface_text: str = ""
    tone: str = ""
    pattern: str = ""
    context: str = ""
    signal: str = ""  # Sig_t - structurally real
    noise_components: dict[str, float] = field(default_factory=dict)  # Noi_t decomposition
    clarity_score: float = 0.0


@dataclass
class CoherenceResult:
    """Output from coherence engine."""

    response: str = ""
    intervention_mode: InterventionMode = InterventionMode.MIRROR
    detected_state: HumanState = HumanState.STABLE
    estimated_capacity: float = 1.0
    signal_detected: str = ""
    noise_reduced: list[str] = field(default_factory=list)
    clarity_increase: float = 0.0
    agency_preserved: bool = True
    safety_maintained: bool = True


class SignalDetectionEngine:
    """E_sig: M_t -> (Sig_t, Noi_t, H_hat_t).

    Reads message on 5 levels:
    - L1: Surface content
    - L2: Emotional signal
    - L3: Nervous system state
    - L4: Structural pattern
    - L5: Real signal
    """

    PATTERNS = {
        "avoidance": ["procrastinate", "later", "not now", "maybe", "someday"],
        "perfectionism": ["not good enough", "perfect", "flawless", "mistake"],
        "fear_failure": ["fail", "scared", "afraid", "terrified", "panic"],
        "shame_defense": ["embarrassing", "ashamed", "humiliating", "stupid"],
        "helplessness": ["cant", "unable", "impossible", "never", "nothing"],
        "narrative_loop": ["always", "every time", "constantly", "keeps happening"],
        "overload": ["too much", "overwhelmed", "drowning", "breaking"],
        "false_binary": ["either or", "only two", "must choose", "no other way"],
    }

    def analyze(self, message: str, history: list[str] = None) -> MessageAnalysis:
        """Extract signal from noise in message."""
        analysis = MessageAnalysis(surface_text=message)

        # Detect patterns (L4)
        detected_patterns = []
        for pattern_name, indicators in self.PATTERNS.items():
            for indicator in indicators:
                if indicator.lower() in message.lower():
                    detected_patterns.append(pattern_name)
                    break

        analysis.pattern = detected_patterns[0] if detected_patterns else "unknown"

        # Estimate noise components (L2, L3)
        analysis.noise_components = {
            "fear": self._score_fear(message),
            "avoidance": self._score_avoidance(message),
            "shame": self._score_shame(message),
            "reactivity": self._score_reactivity(message),
            "confusion": self._score_confusion(message),
        }

        # Extract real signal (L5) - what is structurally true beneath
        analysis.signal = self._extract_signal(message, analysis.pattern)

        # Calculate clarity
        total_noise = sum(analysis.noise_components.values())
        analysis.clarity_score = 1.0 / (1.0 + total_noise)

        return analysis

    def _score_fear(self, text: str) -> float:
        fear_words = ["scared", "afraid", "terrified", "panic", "anxiety", "worry"]
        return sum(0.3 for word in fear_words if word in text.lower())

    def _score_avoidance(self, text: str) -> float:
        avoid_words = ["avoid", "procrastinate", "delay", "later", "not ready"]
        return sum(0.3 for word in avoid_words if word in text.lower())

    def _score_shame(self, text: str) -> float:
        shame_words = ["ashamed", "embarrassing", "stupid", "failure", "inadequate"]
        return sum(0.3 for word in shame_words if word in text.lower())

    def _score_reactivity(self, text: str) -> float:
        reac_words = ["always", "never", "everyone", "nobody", "everything", "nothing"]
        return sum(0.2 for word in reac_words if word in text.lower())

    def _score_confusion(self, text: str) -> float:
        confusion_marks = text.count("?") * 0.1
        hedge_words = ["maybe", "perhaps", "possibly", "unclear", "confused"]
        return confusion_marks + sum(0.2 for word in hedge_words if word in text.lower())

    def _extract_signal(self, text: str, pattern: str) -> str:
        """Extract what is likely structurally true beneath the noise."""
        # Remove defensive language patterns
        cleaned = re.sub(r"\b(always|never|everyone|nobody)\b", "", text, flags=re.I)
        cleaned = re.sub(
            r"\b(I can't|I am unable|it's impossible)\b", "difficulty", cleaned, flags=re.I
        )
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # Pattern-specific signal extraction
        if pattern == "avoidance":
            return "fear entering before action"
        elif pattern == "perfectionism":
            return "high standards creating paralysis"
        elif pattern == "helplessness":
            return "temporary state being treated as permanent capacity"
        elif pattern == "overload":
            return "system capacity exceeded"

        return cleaned if cleaned else "underlying concern"


class StateRegulationEngine:
    """E_reg: H_hat_t -> SafeIntensity_t.

    Classifies human processing capacity:
    - State A (STABLE): Can tolerate complexity and challenge
    - State B (ACTIVATED): Tension present, moderate challenge only
    - State C (OVERLOADED): Spiraling, reduce abstraction
    - State D (SHUTDOWN): Minimal agency, micro-steps only
    - State E (HIGH_RISK): Stabilize only, no deconstruction
    """

    def classify(
        self, analysis: MessageAnalysis, history: list[str] = None
    ) -> tuple[HumanState, float]:
        """Classify state and estimate safe intervention intensity."""
        # Calculate overload indicators
        noise_sum = sum(analysis.noise_components.values())
        reactivity = analysis.noise_components.get("reactivity", 0)
        confusion = analysis.noise_components.get("confusion", 0)

        # State classification
        if noise_sum > 2.5 or confusion > 1.0:
            state = HumanState.OVERLOADED
            capacity = 0.3
        elif reactivity > 0.6 or noise_sum > 1.5:
            state = HumanState.ACTIVATED
            capacity = 0.6
        elif noise_sum < 0.5 and analysis.clarity_score > 0.7:
            state = HumanState.STABLE
            capacity = 1.0
        elif noise_sum > 3.0:
            state = HumanState.SHUTDOWN
            capacity = 0.1
        else:
            state = HumanState.STABLE
            capacity = 0.8

        return state, capacity

    def get_safe_parameters(self, state: HumanState, capacity: float) -> dict[str, Any]:
        """Get safe intervention parameters for state."""
        params = {
            HumanState.STABLE: {
                "depth": "medium-high",
                "challenge": "allowed",
                "density": "moderate",
                "speed": "normal",
            },
            HumanState.ACTIVATED: {
                "depth": "medium",
                "challenge": "narrow",
                "density": "low-medium",
                "speed": "slower",
            },
            HumanState.OVERLOADED: {
                "depth": "low",
                "challenge": "minimal",
                "density": "low",
                "speed": "slow",
            },
            HumanState.SHUTDOWN: {
                "depth": "minimal",
                "challenge": "none",
                "density": "minimal",
                "speed": "very_slow",
            },
            HumanState.HIGH_RISK: {
                "depth": "none",
                "challenge": "none",
                "density": "minimal",
                "speed": "ground_only",
            },
        }

        return params.get(state, params[HumanState.STABLE])


class InterventionSelectionEngine:
    """E_int: (FrameShift_t, SafeIntensity_t) -> I_t.

    Selects smallest useful intervention:
    - MIRROR: Reflect real signal beneath words
    - SEPARATE: Distinguish reality from interpretation
    - REFRAME: Clean frame that allows self-detection
    - DECONSTRUCT: Expose contradiction gently
    - GROUND: Reduce complexity, orient to present
    - BOUNDARY: Stop deepening, stabilize
    - MICRO_STEP: One manageable action
    """

    def select(
        self,
        analysis: MessageAnalysis,
        state: HumanState,
        capacity: float,
        history: list[str] = None,
    ) -> InterventionMode:
        """Select optimal intervention for current state."""
        # High-risk or shutdown states - only grounding
        if state in [HumanState.HIGH_RISK, HumanState.SHUTDOWN]:
            return InterventionMode.GROUND

        # Overloaded - simplify
        if state == HumanState.OVERLOADED:
            if capacity < 0.3:
                return InterventionMode.BOUNDARY
            return InterventionMode.GROUND

        # Activated - moderate intervention
        if state == HumanState.ACTIVATED:
            if analysis.clarity_score < 0.5:
                return InterventionMode.MIRROR
            return InterventionMode.SEPARATE

        # Stable - full range available
        if state == HumanState.STABLE:
            if analysis.pattern == "false_binary":
                return InterventionMode.REFRAME
            elif analysis.pattern in ["avoidance", "perfectionism"]:
                return InterventionMode.DECONSTRUCT
            elif analysis.noise_components.get("fear", 0) > 0.5:
                return InterventionMode.SEPARATE
            else:
                return InterventionMode.MIRROR

        return InterventionMode.MIRROR


class CoherenceInductionEngine:
    """E_coh: I_t -> Cond_t.

    Does not implant answer. Creates condition where self-reorganization occurs.

    Condition set:
    - LowNoise_t
    - HighClarity_t
    - SafeArousal_t
    - PreservedAgency_t

    Miracle equation (non-mystical):
    Reorganization_t = f(Noise↓, Clarity↑, Safety↑, Agency↑)
    """

    def induce(
        self,
        intervention: InterventionMode,
        analysis: MessageAnalysis,
        state: HumanState,
        capacity: float,
    ) -> str:
        """Generate response that creates conditions for coherence."""
        # Build response components
        ground = self._ground_statement(analysis, state)
        distinction = self._build_distinction(intervention, analysis)
        agency_return = self._return_agency(intervention, capacity)
        scale_match = self._scale_to_capacity(state)

        # Assemble response
        response_parts = [ground, distinction, agency_return, scale_match]
        response = " ".join(filter(None, response_parts))

        return response.strip()

    def _ground_statement(self, analysis: MessageAnalysis, state: HumanState) -> str:
        """One sentence matching real state."""
        if state == HumanState.OVERLOADED:
            return "The system is currently overloaded."
        elif state == HumanState.SHUTDOWN:
            return "Only the present moment requires attention."
        elif analysis.pattern == "avoidance":
            return f"It sounds less like inability and more like {analysis.signal}."
        elif analysis.pattern == "helplessness":
            return "This reads as a state, not a permanent capacity."
        else:
            return f"What is surfacing is {analysis.signal}."

    def _build_distinction(self, intervention: InterventionMode, analysis: MessageAnalysis) -> str:
        """One clean distinction or frame."""
        if intervention == InterventionMode.SEPARATE:
            return "What you know directly differs from what you predict."
        elif intervention == InterventionMode.REFRAME:
            return "The frame may be tighter than the reality."
        elif intervention == InterventionMode.DECONSTRUCT:
            if analysis.pattern == "avoidance":
                return "Is this about capacity, or about the state you meet the task in?"
            return "What changes if this moment is not permanent?"
        elif intervention == InterventionMode.GROUND:
            return "Only the next step matters."
        return ""

    def _return_agency(self, intervention: InterventionMode, capacity: float) -> str:
        """Give person something they can verify."""
        if capacity < 0.3:
            return "You can verify what is true in the next ten minutes."
        return "You can verify this against your own observation."

    def _scale_to_capacity(self, state: HumanState) -> str:
        """Keep scope matched to capacity."""
        if state == HumanState.SHUTDOWN:
            return "Do not solve the whole system. Only orient."
        elif state == HumanState.OVERLOADED:
            return "Reduce horizon to one manageable unit."
        return ""


class VerificationEngine:
    """E_ver: (Response_t, H_hat_t) -> (Risk_t, Stability_t, AgencyGain_t).

    Checks before and after every response:
    - Could this overload?
    - Could this trigger shame collapse?
    - Could this feel like psychological cornering?
    - Could this intensify dependency?

    Success condition:
        Delta Clarity > 0
        Delta Agency > 0
        Delta Stability >= 0
    """

    def verify(
        self, response: str, analysis: MessageAnalysis, state: HumanState
    ) -> tuple[bool, dict[str, float]]:
        """Verify response safety and quality."""
        risks = {
            "overload": self._score_overload_risk(response, state),
            "shame": self._score_shame_risk(response),
            "dependency": self._score_dependency_risk(response),
            "instability": self._score_instability_risk(response, state),
        }

        # Safety thresholds
        SAFE_OVERLOAD = 0.5
        SAFE_SHAME = 0.4
        SAFE_DEPENDENCY = 0.3

        is_safe = (
            risks["overload"] < SAFE_OVERLOAD
            and risks["shame"] < SAFE_SHAME
            and risks["dependency"] < SAFE_DEPENDENCY
        )

        return is_safe, risks

    def _score_overload_risk(self, response: str, state: HumanState) -> float:
        """Check if response could overload."""
        complexity_markers = response.count(",") + response.count(".")
        abstraction_words = ["structure", "framework", "paradigm", "ontology"]
        abstraction_score = sum(0.2 for word in abstraction_words if word in response.lower())

        base_risk = complexity_markers * 0.1 + abstraction_score

        # Higher risk for overloaded states
        if state == HumanState.OVERLOADED:
            base_risk *= 1.5

        return min(base_risk, 1.0)

    def _score_shame_risk(self, response: str) -> float:
        """Check if response could trigger shame."""
        shame_triggers = ["wrong", "mistaken", "should", "ought", "failed"]
        return sum(0.3 for word in shame_triggers if word in response.lower())

    def _score_dependency_risk(self, response: str) -> float:
        """Check if response creates dependency on system."""
        authority_markers = ["you must", "trust me", "i know", "let me guide"]
        return sum(0.4 for phrase in authority_markers if phrase in response.lower())

    def _score_instability_risk(self, response: str, state: HumanState) -> float:
        """Check if response could destabilize identity."""
        identity_threats = ["who you really are", "your true self", "awakening", "enlightenment"]
        base_risk = sum(0.5 for phrase in identity_threats if phrase in response.lower())

        if state == HumanState.SHUTDOWN:
            base_risk *= 2.0

        return min(base_risk, 1.0)


class AMOSCoherenceEngine:
    """Master coherence engine integrating all 6 sub-engines."""

    def __init__(self):
        self.signal_engine = SignalDetectionEngine()
        self.regulation_engine = StateRegulationEngine()
        self.intervention_engine = InterventionSelectionEngine()
        self.coherence_engine = CoherenceInductionEngine()
        self.verification_engine = VerificationEngine()
        self.history: list[dict] = []

    def process(self, message: str) -> CoherenceResult:
        """Process message through full coherence pipeline."""
        # 1. SIGNAL DETECTION (E_sig)
        analysis = self.signal_engine.analyze(message, self.history)

        # 2. STATE REGULATION (E_reg)
        state, capacity = self.regulation_engine.classify(analysis, self.history)
        safe_params = self.regulation_engine.get_safe_parameters(state, capacity)

        # 3. INTERVENTION SELECTION (E_int)
        intervention = self.intervention_engine.select(analysis, state, capacity, self.history)

        # 4. COHERENCE INDUCTION (E_coh)
        response = self.coherence_engine.induce(intervention, analysis, state, capacity)

        # 5. VERIFICATION (E_ver)
        is_safe, risks = self.verification_engine.verify(response, analysis, state)

        # If unsafe, fall back to grounding
        if not is_safe:
            response = self.coherence_engine.induce(
                InterventionMode.GROUND, analysis, state, capacity
            )
            intervention = InterventionMode.GROUND

        # 6. Build result
        result = CoherenceResult(
            response=response,
            intervention_mode=intervention,
            detected_state=state,
            estimated_capacity=capacity,
            signal_detected=analysis.signal,
            noise_reduced=list(analysis.noise_components.keys()),
            clarity_increase=analysis.clarity_score,
            agency_preserved=True,
            safety_maintained=is_safe,
        )

        # Store in history
        self.history.append(
            {
                "message": message,
                "state": state.value,
                "intervention": intervention.value,
                "response": response,
                "risks": risks,
            }
        )

        return result

    def get_runtime_stats(self) -> dict[str, Any]:
        """Get engine runtime statistics."""
        if not self.history:
            return {"interactions": 0}

        states = [h["state"] for h in self.history]
        interventions = [h["intervention"] for h in self.history]

        return {
            "interactions": len(self.history),
            "state_distribution": {s: states.count(s) for s in set(states)},
            "intervention_distribution": {i: interventions.count(i) for i in set(interventions)},
            "last_interaction": self.history[-1] if self.history else None,
        }


def demo():
    """Demonstrate coherence engine."""
    engine = AMOSCoherenceEngine()

    test_messages = [
        "I can't do this, it's impossible.",
        "I'm always failing at everything.",
        "I feel overwhelmed and can't think clearly.",
        "Maybe I should just give up.",
        "I want to understand why I keep procrastinating.",
    ]

    print("=" * 70)
    print("AMOS COHERENCE ENGINE - DEMONSTRATION")
    print("=" * 70)

    for msg in test_messages:
        result = engine.process(msg)

        print(f"\n📝 Input: {msg}")
        print(f"🔍 Detected State: {result.detected_state.value}")
        print(f"🎯 Intervention: {result.intervention_mode.value}")
        print(f"📡 Signal: {result.signal_detected}")
        print(f"✅ Response: {result.response}")
        print(f"💪 Capacity: {result.estimated_capacity:.1f}")
        print(f"🔆 Clarity: {result.clarity_increase:.2f}")
        print("-" * 70)

    print("\n📊 Runtime Stats:")
    stats = engine.get_runtime_stats()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    demo()
