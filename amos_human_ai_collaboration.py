"""Phase 19: Human-AI Collaborative Cognition (2026).


Research Alignment:
- "Co-Alignment: Rethinking Alignment as Bidirectional Human-AI" (2025):
  Mutual adaptation where AI and human cognition reinforce each other
- "Human-Centered Human-AI Collaboration (HCHAC)" (2026):
  Three-layer model: sensing → reasoning → forecasting with bidirectional flow
- "Person-AI Bidirectional Fit" (2026):
  Symbiotic relationship with AI adapting to human cognitive patterns
- "Towards Bidirectional Human-AI Alignment" (2024):
  Position paper arguing for mutual alignment rather than unidirectional

Architecture: Bidirectional Cognitive Partnership
    ┌─────────────────────────────────────────────────────────────────────────────┐
    │              PHASE 19: HUMAN-AI COLLABORATIVE COGNITION                       │
    │                    (Bidirectional Cognitive Partnership)                     │
    ├─────────────────────────────────────────────────────────────────────────────┤
    │                                                                             │
    │      HUMAN COGNITION ◄──────────────────────────────► AI COGNITION        │
    │            │                                              │                 │
    │            │    Bidirectional Information Flow:            │                 │
    │            │                                               │                 │
    │            │    Human Intent ──► AI Understanding          │                 │
    │            │         (parsing goals, cognitive style)      │                 │
    │            │                                               │                 │
    │            │    AI Suggestion ──► Human Evaluation          │                 │
    │            │         (corrections, preferences learned)    │                 │
    │            │                                               │                 │
    │            │    Human Insight ──► AI Reasoning Seed         │                 │
    │            │         (novel perspectives enrich AI)        │                 │
    │            │                                               │                 │
    │            │    AI Attention ──► Human Focus Guidance      │                 │
    │            │         (directs human to key aspects)        │                 │
    │            │                                               │                 │
    │            └──────────────┬────────────────────────────────┘                 │
    │                           │                                                 │
    │          ┌────────────────▼────────────────┐                                │
    │          │     COLLABORATIVE STATE         │                                │
    │          │   Σ_collab = (Σ_human, Σ_AI,    │                                │
    │          │              Σ_shared)          │                                │
    │          │                                 │                                │
    │          │   • Shared working memory        │                                │
    │          │   • Joint reasoning chains       │                                │
    │          │   • Mutual context grounding     │                                │
    │          │   • Collaborative predictions    │                                │
    │          └─────────────────────────────────┘                                │
    │                                                                             │
    │   SYMBIOTIC INTELLIGENCE PRINCIPLE:                                          │
    │   Human + AI > Human alone AND Human + AI > AI alone                        │
    │   (The combination produces emergent capabilities)                           │
    │                                                                             │
    └─────────────────────────────────────────────────────────────────────────────┘

Key Innovation: The system doesn't just serve humans or use them for feedback.
Instead, it creates a true cognitive partnership where both parties adapt,
learn, and enhance each other's reasoning capabilities.
"""

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class CollaborationMode(Enum):
    """Modes of human-AI collaboration."""

    HUMAN_LED = auto()  # Human directs, AI assists
    AI_LED = auto()  # AI directs, human validates
    CO_CREATION = auto()  # Joint development of ideas
    EXPLORATORY = auto()  # Free-form mutual exploration
    FOCUSED = auto()  # Task-directed collaboration


class HumanCognitiveStyle(Enum):
    """Detected cognitive styles for adaptation."""

    ANALYTICAL = auto()  # Prefers systematic, step-by-step reasoning
    INTUITIVE = auto()  # Prefers pattern recognition, holistic view
    VISUAL = auto()  # Prefers diagrams, spatial representations
    VERBAL = auto()  # Prefers text-based, linguistic reasoning
    EXPERIMENTAL = auto()  # Prefers trial-and-error, hands-on learning


@dataclass
class HumanIntent:
    """Parsed human intent with cognitive context."""

    intent_id: str
    timestamp: float

    # Core intent
    explicit_goal: str
    implicit_needs: List[str]
    success_criteria: List[str]

    # Cognitive context
    detected_style: HumanCognitiveStyle
    urgency_level: float  # 0-1
    expertise_level: float  # 0-1 (novice to expert)

    # Collaboration preferences
    preferred_mode: CollaborationMode
    autonomy_tolerance: float  # How much AI initiative is welcome
    explanation_depth: str  # "minimal", "moderate", "detailed"


@dataclass
class AISuggestion:
    """AI-generated suggestion with confidence and reasoning."""

    suggestion_id: str
    timestamp: float

    # Content
    content: str
    reasoning: str
    supporting_evidence: List[str]

    # Confidence and uncertainty
    confidence: float
    uncertainty_factors: List[str]

    # Human evaluation
    human_rating: float = None
    human_feedback: str = None
    was_accepted: bool = None


@dataclass
class CollaborativeReasoningChain:
    """A joint human-AI reasoning chain."""

    chain_id: str
    started_at: float

    # Chain elements (alternating human and AI contributions)
    elements: List[dict[str, Any]] = field(default_factory=list)

    # State
    current_focus: str = ""
    agreed_conclusions: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    last_updated: float = 0.0
    completed_at: float = 0.0
    ai_recommended_focus: List[str] = field(default_factory=list)

    # Metrics
    human_contributions: int = 0
    ai_contributions: int = 0
    consensus_achieved: bool = False


@dataclass
class SharedContext:
    """Shared working memory between human and AI."""

    context_id: str
    created_at: float
    last_updated: float = 0.0

    # Knowledge
    facts: Dict[str, Any] = field(default_factory=dict)
    assumptions: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)

    # Reasoning state
    active_hypotheses: List[str] = field(default_factory=list)
    confirmed_insights: List[str] = field(default_factory=list)
    rejected_approaches: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)

    # Collaboration state
    human_focus_areas: List[str] = field(default_factory=list)
    ai_recommended_focus: List[str] = field(default_factory=list)


@dataclass
class BidirectionalAdaptation:
    """Records of mutual adaptation between human and AI."""

    # AI adapting to human
    human_style_profile: Dict[str, Any]
    learned_preferences: Dict[str, Any]
    effective_explanation_types: List[str]

    # Human adapting to AI (tracked, not controlled)
    human_adoption_patterns: Dict[str, Any]
    collaboration_satisfaction_trend: List[float]

    # Symbiotic metrics
    synergy_score: float  # How well they work together
    mutual_improvement_rate: float  # How fast both are learning


class HumanAICollaboration:
    """Phase 19: Human-AI Collaborative Cognition.

    Creates a bidirectional cognitive partnership where:
    - Human intent shapes AI reasoning
    - AI suggestions guide human attention
    - Shared context maintains coherence
    - Mutual adaptation improves over time
    """

    def __init__(self, collaboration_mode: CollaborationMode = CollaborationMode.CO_CREATION):
        self.collaboration_mode = collaboration_mode

        # State
        self.current_intent: Optional[HumanIntent] = None
        self.shared_context: Optional[SharedContext] = None
        self.active_chain: Optional[CollaborativeReasoningChain] = None

        # History
        self.intent_history: List[HumanIntent] = []
        self.suggestion_history: List[AISuggestion] = []
        self.reasoning_chains: List[CollaborativeReasoningChain] = []

        # Adaptation
        self.adaptation = BidirectionalAdaptation(
            human_style_profile={"detected_style": None, "confidence": 0.0},
            learned_preferences={},
            effective_explanation_types=[],
            human_adoption_patterns={},
            collaboration_satisfaction_trend=[],
            synergy_score=0.5,
            mutual_improvement_rate=0.0,
        )

    def parse_human_intent(self, natural_input: str, context: Dict[str, Any] = None) -> HumanIntent:
        """Parse human natural language input into structured intent.

        Uses cognitive style detection to adapt to individual humans.
        """
        # Detect cognitive style from input patterns
        detected_style = self._detect_cognitive_style(natural_input)

        # Parse explicit and implicit goals
        explicit_goal = natural_input  # Simplified; real implementation would parse
        implicit_needs = self._infer_implicit_needs(natural_input, context or {})

        # Determine collaboration preferences
        preferred_mode = self._determine_collaboration_mode(natural_input, context or {})
        urgency = self._estimate_urgency(natural_input)
        expertise = self._estimate_expertise(natural_input)

        intent = HumanIntent(
            intent_id=f"intent_{int(time.time())}",
            timestamp=time.time(),
            explicit_goal=explicit_goal,
            implicit_needs=implicit_needs,
            success_criteria=[],  # Would be negotiated
            detected_style=detected_style,
            urgency_level=urgency,
            expertise_level=expertise,
            preferred_mode=preferred_mode,
            autonomy_tolerance=self._estimate_autonomy_tolerance(detected_style),
            explanation_depth=self._determine_explanation_depth(expertise),
        )

        self.current_intent = intent
        self.intent_history.append(intent)

        # Update adaptation based on new intent
        self._update_style_adaptation(intent)

        return intent

    def generate_ai_suggestion(
        self,
        reasoning_function: Callable[[str, dict], str],
        current_context: Optional[SharedContext] = None,
    ) -> AISuggestion:
        """Generate AI suggestion adapted to human's cognitive style.

        The suggestion is shaped by:
        - Parsed human intent
        - Detected cognitive style
        - Shared context from previous exchanges
        """
        if not self.current_intent:
            raise ValueError("No human intent parsed. Call parse_human_intent first.")

        # Adapt reasoning to cognitive style
        adapted_prompt = self._adapt_prompt_to_style(
            self.current_intent.explicit_goal, self.current_intent.detected_style
        )

        # Generate reasoning
        raw_suggestion = reasoning_function(
            adapted_prompt, current_context.facts if current_context else {}
        )

        # Structure suggestion
        suggestion = AISuggestion(
            suggestion_id=f"sugg_{int(time.time())}",
            timestamp=time.time(),
            content=raw_suggestion,
            reasoning=(
                f"Generated based on {self.current_intent.detected_style.name} "
                f"cognitive style preference"
            ),
            supporting_evidence=["Matched to human intent profile"],
            confidence=0.75,  # Would be calculated from actual model confidence
            uncertainty_factors=["Human evaluation pending"],
        )

        self.suggestion_history.append(suggestion)

        return suggestion

    def receive_human_feedback(
        self,
        suggestion: AISuggestion,
        rating: float,  # 0-1
        feedback_text: str,
        was_accepted: bool,
    ) -> Dict[str, Any]:
        """Process human feedback on AI suggestion.

        This creates the bidirectional learning loop:
        - AI learns from human corrections
        - Human preferences are updated
        - Adaptation profile is refined
        """
        # Update suggestion record
        suggestion.human_rating = rating
        suggestion.human_feedback = feedback_text
        suggestion.was_accepted = was_accepted

        # Update adaptation
        self._learn_from_feedback(suggestion, rating, feedback_text)

        # Update satisfaction trend
        self.adaptation.collaboration_satisfaction_trend.append(rating)
        if len(self.adaptation.collaboration_satisfaction_trend) > 20:
            self.adaptation.collaboration_satisfaction_trend.pop(0)

        # Calculate synergy score
        self._update_synergy_score()

        return {
            "feedback_recorded": True,
            "preference_update": "completed",
            "adaptation_delta": self.adaptation.mutual_improvement_rate,
            "current_synergy": self.adaptation.synergy_score,
        }

    def initiate_collaborative_reasoning(
        self, problem_statement: str
    ) -> CollaborativeReasoningChain:
        """Start a joint human-AI reasoning chain.

        This is the core of collaborative cognition - both parties
        contribute to a shared reasoning process.
        """
        # Create shared context if none exists
        if not self.shared_context:
            self.shared_context = SharedContext(
                context_id=f"ctx_{int(time.time())}",
                created_at=time.time(),
                last_updated=time.time(),
            )

        chain = CollaborativeReasoningChain(
            chain_id=f"chain_{int(time.time())}",
            started_at=time.time(),
            elements=[{"type": "problem", "content": problem_statement, "source": "initiation"}],
            current_focus=problem_statement,
            agreed_conclusions=[],
            open_questions=[problem_statement],
        )

        self.active_chain = chain
        self.reasoning_chains.append(chain)

        return chain

    def add_human_contribution(
        self,
        chain: CollaborativeReasoningChain,
        contribution: str,
        contribution_type: str = "insight",  # insight, question, correction, confirmation
    ) -> Dict[str, Any]:
        """Add human contribution to collaborative reasoning chain."""
        element = {
            "type": contribution_type,
            "content": contribution,
            "source": "human",
            "timestamp": time.time(),
        }

        chain.elements.append(element)
        chain.human_contributions += 1
        chain.last_updated = time.time()

        # Update shared context
        if self.shared_context:
            if contribution_type == "insight":
                self.shared_context.confirmed_insights.append(contribution)
            elif contribution_type == "question":
                self.shared_context.open_questions.append(contribution)

        # AI might identify new focus areas based on human contribution
        chain.ai_recommended_focus = self._suggest_focus_areas(chain)

        return {
            "contribution_recorded": True,
            "chain_length": len(chain.elements),
            "ai_suggested_focus": chain.ai_recommended_focus,
        }

    def add_ai_contribution(
        self,
        chain: CollaborativeReasoningChain,
        contribution: str,
        contribution_type: str = "analysis",  # analysis, hypothesis, synthesis, question
    ) -> Dict[str, Any]:
        """Add AI contribution to collaborative reasoning chain."""
        # Adapt to human style before adding
        adapted_contribution = self._adapt_contribution_to_style(
            contribution,
            self.current_intent.detected_style
            if self.current_intent
            else HumanCognitiveStyle.ANALYTICAL,
        )

        element = {
            "type": contribution_type,
            "content": adapted_contribution,
            "source": "ai",
            "timestamp": time.time(),
        }

        chain.elements.append(element)
        chain.ai_contributions += 1
        chain.last_updated = time.time()

        # Update shared context
        if self.shared_context:
            if contribution_type == "hypothesis":
                self.shared_context.active_hypotheses.append(contribution)
            elif contribution_type == "analysis":
                self.shared_context.facts[f"analysis_{len(chain.elements)}"] = contribution

        return {
            "contribution_recorded": True,
            "adapted_to_style": True,
            "chain_length": len(chain.elements),
        }

    def finalize_collaborative_reasoning(
        self, chain: CollaborativeReasoningChain
    ) -> Dict[str, Any]:
        """Finalize a collaborative reasoning chain with agreed conclusions."""
        # Extract agreed conclusions (simplified; real implementation would analyze chain)
        conclusions = [e["content"] for e in chain.elements if e.get("consensus")]

        if not conclusions:
            # Generate summary from all contributions
            conclusions = [f"Joint exploration of: {chain.elements[0]['content']}"]

        chain.agreed_conclusions = conclusions
        chain.consensus_achieved = True
        chain.completed_at = time.time()

        # Update adaptation based on collaboration success
        self._learn_from_collaboration(chain)

        return {
            "conclusions": conclusions,
            "human_contributions": chain.human_contributions,
            "ai_contributions": chain.ai_contributions,
            "collaboration_duration": chain.completed_at - chain.started_at,
            "synergy_score": self.adaptation.synergy_score,
        }

    def get_collaboration_report(self) -> Dict[str, Any]:
        """Get comprehensive report on collaboration state."""
        return {
            "current_mode": self.collaboration_mode.name,
            "current_intent": self.current_intent.explicit_goal if self.current_intent else None,
            "active_chain_length": len(self.active_chain.elements) if self.active_chain else 0,
            "total_interactions": len(self.intent_history),
            "adaptation": {
                "detected_cognitive_style": (
                    self.adaptation.human_style_profile.get("detected_style")
                ),
                "synergy_score": f"{self.adaptation.synergy_score:.2%}",
                "mutual_improvement_rate": f"{self.adaptation.mutual_improvement_rate:.2%}",
                "satisfaction_trend": self._calculate_satisfaction_trend(),
            },
            "shared_context_facts": len(self.shared_context.facts) if self.shared_context else 0,
            "learned_preferences": len(self.adaptation.learned_preferences),
        }

    # Private helper methods
    def _detect_cognitive_style(self, input_text: str) -> HumanCognitiveStyle:
        """Detect cognitive style from input patterns."""
        # Simplified heuristic detection
        if any(word in input_text.lower() for word in ["diagram", "visualize", "see", "picture"]):
            return HumanCognitiveStyle.VISUAL
        elif any(word in input_text.lower() for word in ["step", "process", "systematic", "logic"]):
            return HumanCognitiveStyle.ANALYTICAL
        elif any(word in input_text.lower() for word in ["feel", "sense", "intuition", "pattern"]):
            return HumanCognitiveStyle.INTUITIVE
        elif any(word in input_text.lower() for word in ["try", "experiment", "test", "hands-on"]):
            return HumanCognitiveStyle.EXPERIMENTAL
        else:
            return HumanCognitiveStyle.VERBAL

    def _infer_implicit_needs(self, input_text: str, context: dict) -> List[str]:
        """Infer implicit needs from explicit input."""
        needs = []

        if "help" in input_text.lower():
            needs.append("assistance")
        if "understand" in input_text.lower() or "explain" in input_text.lower():
            needs.append("education")
        if "optimize" in input_text.lower() or "improve" in input_text.lower():
            needs.append("enhancement")
        if "check" in input_text.lower() or "review" in input_text.lower():
            needs.append("validation")

        return needs if needs else ["general_support"]

    def _determine_collaboration_mode(self, input_text: str, context: dict) -> CollaborationMode:
        """Determine optimal collaboration mode."""
        if any(word in input_text.lower() for word in ["let's explore", "what if", "brainstorm"]):
            return CollaborationMode.EXPLORATORY
        elif any(
            word in input_text.lower() for word in ["I need you to", "please do", "handle this"]
        ):
            return CollaborationMode.AI_LED
        elif any(word in input_text.lower() for word in ["let me", "I'll", "I'm working on"]):
            return CollaborationMode.HUMAN_LED
        elif any(word in input_text.lower() for word in ["together", "joint", "collaborate"]):
            return CollaborationMode.CO_CREATION
        else:
            return self.collaboration_mode

    def _estimate_urgency(self, input_text: str) -> float:
        """Estimate urgency level from input."""
        urgency_markers = ["urgent", "asap", "immediately", "quickly", "now"]
        return sum(1 for marker in urgency_markers if marker in input_text.lower()) / len(
            urgency_markers
        )

    def _estimate_expertise(self, input_text: str) -> float:
        """Estimate expertise level from input."""
        # Heuristic: technical terms indicate expertise
        technical_terms = [
            "architecture",
            "implementation",
            "optimization",
            "algorithm",
            "framework",
        ]
        return min(1.0, sum(1 for term in technical_terms if term in input_text.lower()) / 3)

    def _estimate_autonomy_tolerance(self, style: HumanCognitiveStyle) -> float:
        """Estimate how much AI initiative the human likely tolerates."""
        tolerance_map = {
            HumanCognitiveStyle.ANALYTICAL: 0.8,  # Likes systematic AI help
            HumanCognitiveStyle.INTUITIVE: 0.6,  # Wants some guidance
            HumanCognitiveStyle.VISUAL: 0.5,  # Wants to see options
            HumanCognitiveStyle.VERBAL: 0.7,  # Likes discussion
            HumanCognitiveStyle.EXPERIMENTAL: 0.4,  # Wants to try themselves
        }
        return tolerance_map.get(style, 0.6)

    def _determine_explanation_depth(self, expertise: float) -> str:
        """Determine appropriate explanation depth."""
        if expertise > 0.7:
            return "minimal"
        elif expertise > 0.4:
            return "moderate"
        else:
            return "detailed"

    def _update_style_adaptation(self, intent: HumanIntent) -> None:
        """Update adaptation profile based on new intent."""
        # Update style detection confidence
        current_profile = self.adaptation.human_style_profile
        if current_profile.get("detected_style") == intent.detected_style:
            current_profile["confidence"] = min(1.0, current_profile.get("confidence", 0.0) + 0.1)
        else:
            # Style may have changed or our detection improved
            current_profile["detected_style"] = intent.detected_style
            current_profile["confidence"] = 0.5

    def _adapt_prompt_to_style(self, prompt: str, style: HumanCognitiveStyle) -> str:
        """Adapt prompt based on detected cognitive style."""
        adaptations = {
            HumanCognitiveStyle.ANALYTICAL: f"Analyze systematically: {prompt}",
            HumanCognitiveStyle.INTUITIVE: f"Consider patterns and holistic view: {prompt}",
            HumanCognitiveStyle.VISUAL: f"Describe visual/spatial aspects: {prompt}",
            HumanCognitiveStyle.VERBAL: f"Provide detailed explanation: {prompt}",
            HumanCognitiveStyle.EXPERIMENTAL: (f"Suggest practical approaches: {prompt}"),
        }
        return adaptations.get(style, prompt)

    def _adapt_contribution_to_style(self, contribution: str, style: HumanCognitiveStyle) -> str:
        """Adapt AI contribution to human's cognitive style."""
        # Simplified adaptation - would be more sophisticated in real implementation
        if style == HumanCognitiveStyle.VISUAL:
            return f"[Visual framing] {contribution}"
        elif style == HumanCognitiveStyle.ANALYTICAL:
            return f"[Step-by-step] {contribution}"
        else:
            return contribution

    def _learn_from_feedback(self, suggestion: AISuggestion, rating: float, feedback: str) -> None:
        """Learn from human feedback on suggestions."""
        # Update learned preferences
        key = f"suggestion_type_{suggestion.suggestion_id}"
        self.adaptation.learned_preferences[key] = {
            "rating": rating,
            "feedback": feedback,
            "was_accepted": suggestion.was_accepted,
        }

        # Track effective explanation types
        if rating > 0.7 and suggestion.reasoning:
            self.adaptation.effective_explanation_types.append(suggestion.reasoning[:50])

    def _suggest_focus_areas(self, chain: CollaborativeReasoningChain) -> List[str]:
        """Suggest focus areas based on chain history."""
        return [f"Explore: {chain.current_focus} (depth {len(chain.elements)})"]

    def _learn_from_collaboration(self, chain: CollaborativeReasoningChain) -> None:
        """Learn from completed collaboration."""
        # Calculate contribution balance
        total = chain.human_contributions + chain.ai_contributions
        if total > 0:
            human_ratio = chain.human_contributions / total

            # Ideal synergy is roughly balanced
            ideal = 0.5
            deviation = abs(human_ratio - ideal)

            # Update synergy score based on balance and consensus
            consensus_bonus = 0.2 if chain.consensus_achieved else 0.0
            self.adaptation.synergy_score = min(1.0, 0.8 - deviation + consensus_bonus)

        # Update improvement rate
        if len(self.reasoning_chains) > 1:
            self.adaptation.mutual_improvement_rate = min(1.0, len(self.reasoning_chains) / 100)

    def _update_synergy_score(self) -> None:
        """Update synergy score based on recent satisfaction."""
        if len(self.adaptation.collaboration_satisfaction_trend) >= 5:
            recent_avg = sum(self.adaptation.collaboration_satisfaction_trend[-5:]) / 5
            self.adaptation.synergy_score = 0.7 * self.adaptation.synergy_score + 0.3 * recent_avg

    def _calculate_satisfaction_trend(self) -> str:
        """Calculate trend in satisfaction."""
        if len(self.adaptation.collaboration_satisfaction_trend) < 5:
            return "insufficient_data"

        recent = self.adaptation.collaboration_satisfaction_trend[-5:]
        earlier = self.adaptation.collaboration_satisfaction_trend[:5]

        recent_avg = sum(recent) / len(recent)
        earlier_avg = sum(earlier) / len(earlier)

        if recent_avg > earlier_avg + 0.1:
            return "improving"
        elif recent_avg < earlier_avg - 0.1:
            return "declining"
        else:
            return "stable"


def create_collaborative_cognition(
    mode: CollaborationMode = CollaborationMode.CO_CREATION,
) -> HumanAICollaboration:
    """Factory function for creating Phase 19 collaborative cognition."""
    return HumanAICollaboration(collaboration_mode=mode)


if __name__ == "__main__":
    # Demo
    print("=" * 70)
    print("Phase 19: Human-AI Collaborative Cognition")
    print("Bidirectional Cognitive Partnership")
    print("=" * 70)

    collaboration = create_collaborative_cognition()

    print("\n1. Human Input Parsing")
    human_input = "I need to visualize the system architecture. Can you help me see the patterns?"
    intent = collaboration.parse_human_intent(human_input)

    print(f"   Input: '{human_input}'")
    print(f"   Detected cognitive style: {intent.detected_style.name}")
    print(f"   Implicit needs: {intent.implicit_needs}")
    print(f"   Preferred mode: {intent.preferred_mode.name}")

    print("\n2. AI Suggestion Generation (Adapted to Style)")

    def mock_reasoning(prompt: str, context: Dict[str, Any]) -> str:
        return "Architecture diagram showing component relationships and data flow"

    suggestion = collaboration.generate_ai_suggestion(mock_reasoning)
    print(f"   Adapted prompt style: {intent.detected_style.name}")
    print(f"   Suggestion: {suggestion.content}")
    print(f"   Confidence: {suggestion.confidence:.0%}")

    print("\n3. Human Feedback (Bidirectional Learning)")
    feedback_result = collaboration.receive_human_feedback(
        suggestion,
        rating=0.85,
        feedback_text="The visual approach is helpful, but I need more detail on the data flow",
        was_accepted=True,
    )
    print("   Human rating: 85%")
    print(f"   Synergy score: {feedback_result['current_synergy']:.2%}")

    print("\n4. Collaborative Reasoning Chain")
    chain = collaboration.initiate_collaborative_reasoning(
        "How can we optimize the system performance?"
    )

    # Add contributions
    collaboration.add_human_contribution(
        chain, "I think the bottleneck is in the database layer", "insight"
    )
    collaboration.add_ai_contribution(
        chain, "Analyzing database queries reveals 60% of latency", "analysis"
    )
    collaboration.add_human_contribution(chain, "What if we add caching?", "question")
    collaboration.add_ai_contribution(chain, "Caching would reduce queries by 40%", "hypothesis")

    result = collaboration.finalize_collaborative_reasoning(chain)

    print(f"   Human contributions: {result['human_contributions']}")
    print(f"   AI contributions: {result['ai_contributions']}")
    print(f"   Synergy score: {result['synergy_score']:.2%}")

    print("\n5. Collaboration Report")
    report = collaboration.get_collaboration_report()
    print(f"   Total interactions: {report['total_interactions']}")
    print(f"   Current synergy: {report['adaptation']['synergy_score']}")
    print(f"   Satisfaction trend: {report['adaptation']['satisfaction_trend']}")

    print("\n" + "=" * 70)
    print("✅ Phase 19 Human-AI Collaborative Cognition: OPERATIONAL")
    print("   Bidirectional cognitive partnership active")
    print("=" * 70)
