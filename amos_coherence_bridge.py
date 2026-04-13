"""Bridge between AMOS Coherence Engine and Local Model Runtime.

Integrates the signal detection/coherence induction system with
the local LLM runtime for privacy-preserving cognitive support.
"""
from __future__ import annotations

from typing import Any

from amos_brain.local_runtime import create_local_runtime, AMOSLocalRuntime
from amos_coherence_engine import (
    AMOSCoherenceEngine,
    SignalDetectionEngine,
    StateRegulationEngine,
    InterventionSelectionEngine,
    CoherenceResult,
    HumanState,
)


class CoherenceLocalBridge:
    """Bridge connecting coherence engine to local LLM runtime.

    Enables privacy-preserving cognitive support by running:
    1. Coherence analysis locally (signal detection, state assessment)
    2. LLM inference locally via Ollama/LM Studio (interventions, responses)
    """

    def __init__(
        self,
        runtime: AMOSLocalRuntime | None = None,
        coherence_engine: CoherenceEngine | None = None,
    ):
        self.runtime = runtime or create_local_runtime()
        self.coherence = coherence_engine or CoherenceEngine()
        self.signal_detector = SignalDetectionEngine()
        self.state_regulator = StateRegulationEngine()
        self.intervention_selector = InterventionSelector()

    def initialize(self) -> dict[str, Any]:
        """Initialize both systems."""
        # Initialize local runtime
        runtime_status = self.runtime.initialize()

        # Initialize coherence engine
        return {
            "runtime_ready": runtime_status.get("ready", False),
            "coherence_ready": True,
            "runtime_backend": runtime_status.get("backend", {}),
        }

    def process_with_coherence(self, message: str) -> CoherenceResult:
        """Process message through coherence engine + local LLM.

        Flow:
        1. Detect signals in message (local)
        2. Assess human state (local)
        3. Select intervention (local)
        4. Generate response via local LLM
        5. Verify coherence maintained (local)
        """
        # Step 1: Signal detection (local, privacy-safe)
        analysis = self.signal_detector.analyze(message)

        # Step 2: State assessment (local)
        state = self._assess_state(analysis)

        # Step 3: Intervention selection (local)
        intervention = self.intervention_selector.select(
            state, analysis.pattern, analysis.clarity_score
        )

        # Step 4: Generate response via local LLM
        prompt = self._build_coherence_prompt(
            message, analysis, state, intervention
        )

        response = self.runtime.reply(prompt)

        if not response.get("ok"):
            # Fallback to basic coherence response
            return CoherenceResult(
                response=self._basic_intervention(intervention, message),
                intervention_mode=intervention,
                detected_state=state,
                clarity_increase=0.1,
            )

        # Step 5: Verify coherence
        coherence_text = response["text"]
        coherence_score = self._verify_coherence(coherence_text, analysis)

        return CoherenceResult(
            response=coherence_text,
            intervention_mode=intervention,
            detected_state=state,
            signal_detected=analysis.signal,
            noise_reduced=list(analysis.noise_components.keys()),
            clarity_increase=coherence_score,
        )

    def _assess_state(self, analysis) -> HumanState:
        """Assess human state from signal analysis."""
        noise_sum = sum(analysis.noise_components.values())

        if noise_sum > 1.5:
            return HumanState.OVERLOADED
        elif noise_sum > 1.0:
            return HumanState.DYSREGULATED
        elif noise_sum > 0.5:
            return HumanState.FRAGILE
        else:
            return HumanState.STABLE

    def _build_coherence_prompt(
        self,
        message: str,
        analysis,
        state: HumanState,
        intervention: Any,
    ) -> str:
        """Build prompt for coherence-aware response."""
        context = f"""
You are providing cognitive support to a human in distress.

DETECTED STATE: {state.name}
SIGNALS DETECTED: {analysis.signal}
PATTERN: {analysis.pattern}
CLARITY SCORE: {analysis.clarity_score:.2f}
NOISE COMPONENTS: {analysis.noise_components}

INTERVENTION MODE: {intervention.name}

Your task: Provide a response that:
1. Acknowledges the underlying signal (not surface noise)
2. Helps reduce the detected noise components
3. Increases clarity and coherence
4. Preserves the person's agency and autonomy
5. Maintains safety above all else

HUMAN MESSAGE: {message}

Respond with clarity, compassion, and structural precision.
"""
        return context

    def _basic_intervention(self, intervention, message: str) -> str:
        """Fallback basic response if LLM fails."""
        interventions = {
            "MIRROR": f"I hear you saying: {message}",
            "GROUND": "Let's take a moment to breathe and ground ourselves.",
            "CLARIFY": "Can you help me understand what is most important now?",
            "SIMPLIFY": "It sounds complex. What is one small step to focus on?",
        }
        return interventions.get(intervention.name, "Tell me more.")

    def _verify_coherence(self, response: str, original_analysis) -> float:
        """Verify that response maintains/improves coherence."""
        # Simple heuristic: response should not add noise
        new_analysis = self.signal_detector.analyze(response)

        original_noise = sum(original_analysis.noise_components.values())
        new_noise = sum(new_analysis.noise_components.values())

        if new_noise < original_noise:
            return 0.3  # Improved
        elif new_noise == original_noise:
            return 0.1  # Maintained
        else:
            return 0.0  # No improvement


def demo_coherence_bridge():
    """Demonstrate coherence + local LLM integration."""
    print("=" * 60)
    print("Coherence Engine + Local LLM Bridge Demo")
    print("=" * 60)
    print()

    # Create bridge
    bridge = CoherenceLocalBridge()

    print("Initializing...")
    status = bridge.initialize()

    if not status["runtime_ready"]:
        print("Local runtime not ready. Make sure Ollama is running.")
        return 1

    print(f"✓ Backend: {status['runtime_backend'].get('backend')}")
    print(f"✓ Model: {status['runtime_backend'].get('model')}")
    print()

    # Test messages showing different states
    test_messages = [
        "I'm feeling overwhelmed with everything I have to do",
        "I keep procrastinating on this important project",
        "What is machine learning?",  # Neutral
    ]

    for msg in test_messages:
        print(f"Message: {msg}")
        print("-" * 40)

        result = bridge.process_with_coherence(msg)

        print(f"Detected state: {result.detected_state.name}")
        print(f"Intervention: {result.intervention_mode.name}")
        print(f"Clarity improvement: {result.clarity_increase:.2f}")
        print(f"Response: {result.response[:150]}...")
        print()

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(demo_coherence_bridge())
