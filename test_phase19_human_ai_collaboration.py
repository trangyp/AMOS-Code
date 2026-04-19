"""Test suite for Phase 19: Human-AI Collaborative Cognition."""

from typing import Any, Dict

import pytest

from amos_human_ai_collaboration import (
    CollaborationMode,
    HumanAICollaboration,
    HumanCognitiveStyle,
    create_collaborative_cognition,
)


@pytest.fixture
def collaboration() -> HumanAICollaboration:
    """Create a fresh collaboration instance."""
    return create_collaborative_cognition(CollaborationMode.CO_CREATION)


@pytest.fixture
def mock_reasoning() -> Any:
    """Mock reasoning function for testing."""

    def reasoning(prompt: str, context: Dict[str, Any]) -> str:
        return f"Analysis of: {prompt[:30]}"

    return reasoning


class TestCollaborationCreation:
    """Test collaboration system creation and initialization."""

    def test_default_creation(self) -> None:
        """Test creating collaboration with default settings."""
        collab = create_collaborative_cognition()
        assert collab.collaboration_mode == CollaborationMode.CO_CREATION
        assert collab.current_intent is None
        assert collab.shared_context is None
        assert collab.active_chain is None

    def test_creation_with_mode(self) -> None:
        """Test creating collaboration with specific mode."""
        collab = create_collaborative_cognition(CollaborationMode.HUMAN_LED)
        assert collab.collaboration_mode == CollaborationMode.HUMAN_LED

    def test_adaptation_initialization(self, collaboration: HumanAICollaboration) -> None:
        """Test that adaptation profile is initialized correctly."""
        assert collaboration.adaptation.synergy_score == 0.5
        assert collaboration.adaptation.mutual_improvement_rate == 0.0
        assert collaboration.adaptation.learned_preferences == {}


class TestHumanIntentParsing:
    """Test human intent parsing with cognitive style detection."""

    def test_parse_visual_style(self, collaboration: HumanAICollaboration) -> None:
        """Test detecting visual cognitive style."""
        intent = collaboration.parse_human_intent("I need to visualize the system architecture")
        assert intent.detected_style == HumanCognitiveStyle.VISUAL
        assert "visualize" in intent.explicit_goal.lower()

    def test_parse_analytical_style(self, collaboration: HumanAICollaboration) -> None:
        """Test detecting analytical cognitive style."""
        intent = collaboration.parse_human_intent(
            "Let's analyze step by step using systematic logic"
        )
        assert intent.detected_style == HumanCognitiveStyle.ANALYTICAL

    def test_parse_intuitive_style(self, collaboration: HumanAICollaboration) -> None:
        """Test detecting intuitive cognitive style."""
        intent = collaboration.parse_human_intent("I feel there's a pattern we should recognize")
        assert intent.detected_style == HumanCognitiveStyle.INTUITIVE

    def test_parse_experimental_style(self, collaboration: HumanAICollaboration) -> None:
        """Test detecting experimental cognitive style."""
        intent = collaboration.parse_human_intent("Let's try hands-on testing and experiments")
        assert intent.detected_style == HumanCognitiveStyle.EXPERIMENTAL

    def test_infer_implicit_needs(self, collaboration: HumanAICollaboration) -> None:
        """Test implicit need detection."""
        intent = collaboration.parse_human_intent("I need help understanding this")
        assert "assistance" in intent.implicit_needs
        assert "education" in intent.implicit_needs

    def test_estimate_urgency(self, collaboration: HumanAICollaboration) -> None:
        """Test urgency estimation."""
        urgent = collaboration.parse_human_intent("This is urgent, fix immediately!")
        assert urgent.urgency_level > 0.3

        calm = collaboration.parse_human_intent("When you have time, check this")
        assert calm.urgency_level == 0.0

    def test_estimate_expertise(self, collaboration: HumanAICollaboration) -> None:
        """Test expertise level estimation."""
        expert = collaboration.parse_human_intent(
            "The architecture implementation requires optimization of the algorithm"
        )
        assert expert.expertise_level > 0.5

        novice = collaboration.parse_human_intent("How do I start?")
        assert novice.expertise_level < 0.3

    def test_intent_history_tracking(self, collaboration: HumanAICollaboration) -> None:
        """Test that intents are tracked in history."""
        initial_count = len(collaboration.intent_history)
        collaboration.parse_human_intent("First query")
        collaboration.parse_human_intent("Second query")
        assert len(collaboration.intent_history) == initial_count + 2

    def test_style_adaptation_update(self, collaboration: HumanAICollaboration) -> None:
        """Test style profile updates with new intents."""
        collaboration.parse_human_intent("Visual diagram needed")
        profile = collaboration.adaptation.human_style_profile
        assert profile["detected_style"] == HumanCognitiveStyle.VISUAL


class TestAISuggestionGeneration:
    """Test AI suggestion generation with style adaptation."""

    def test_suggestion_requires_intent(
        self, collaboration: HumanAICollaboration, mock_reasoning: Any
    ) -> None:
        """Test that suggestion generation requires parsed intent."""
        with pytest.raises(ValueError, match="No human intent parsed"):
            collaboration.generate_ai_suggestion(mock_reasoning)

    def test_suggestion_adapted_to_style(
        self, collaboration: HumanAICollaboration, mock_reasoning: Any
    ) -> None:
        """Test that suggestions are adapted to cognitive style."""
        collaboration.parse_human_intent("I need a systematic analysis")
        suggestion = collaboration.generate_ai_suggestion(mock_reasoning)
        assert suggestion.confidence > 0
        assert len(suggestion.reasoning) > 0

    def test_suggestion_tracking(
        self, collaboration: HumanAICollaboration, mock_reasoning: Any
    ) -> None:
        """Test that suggestions are tracked in history."""
        initial_count = len(collaboration.suggestion_history)
        collaboration.parse_human_intent("Test query")
        collaboration.generate_ai_suggestion(mock_reasoning)
        assert len(collaboration.suggestion_history) == initial_count + 1


class TestHumanFeedback:
    """Test human feedback processing and learning."""

    def test_feedback_recording(
        self, collaboration: HumanAICollaboration, mock_reasoning: Any
    ) -> None:
        """Test that feedback is recorded on suggestions."""
        collaboration.parse_human_intent("Test query")
        suggestion = collaboration.generate_ai_suggestion(mock_reasoning)

        result = collaboration.receive_human_feedback(
            suggestion, rating=0.9, feedback_text="Great suggestion", was_accepted=True
        )

        assert result["feedback_recorded"] is True
        assert suggestion.human_rating == 0.9
        assert suggestion.was_accepted is True

    def test_satisfaction_trend_update(
        self, collaboration: HumanAICollaboration, mock_reasoning: Any
    ) -> None:
        """Test satisfaction trend updates with feedback."""
        collaboration.parse_human_intent("Test query")
        suggestion = collaboration.generate_ai_suggestion(mock_reasoning)

        initial_trend_len = len(collaboration.adaptation.collaboration_satisfaction_trend)
        collaboration.receive_human_feedback(suggestion, 0.8, "Good", True)

        assert (
            len(collaboration.adaptation.collaboration_satisfaction_trend) == initial_trend_len + 1
        )

    def test_synergy_score_update(
        self, collaboration: HumanAICollaboration, mock_reasoning: Any
    ) -> None:
        """Test synergy score updates with feedback."""
        initial_synergy = collaboration.adaptation.synergy_score

        collaboration.parse_human_intent("Test query")
        suggestion = collaboration.generate_ai_suggestion(mock_reasoning)
        collaboration.receive_human_feedback(suggestion, 0.9, "Excellent", True)

        # Multiple feedbacks to trigger synergy update
        for i in range(5):
            collaboration.parse_human_intent(f"Query {i}")
            s = collaboration.generate_ai_suggestion(mock_reasoning)
            collaboration.receive_human_feedback(s, 0.9, "Good", True)

        assert collaboration.adaptation.synergy_score != initial_synergy

    def test_preference_learning(
        self, collaboration: HumanAICollaboration, mock_reasoning: Any
    ) -> None:
        """Test that preferences are learned from feedback."""
        collaboration.parse_human_intent("Test query")
        suggestion = collaboration.generate_ai_suggestion(mock_reasoning)

        collaboration.receive_human_feedback(suggestion, 0.9, "Great!", True)

        assert len(collaboration.adaptation.learned_preferences) > 0


class TestCollaborativeReasoning:
    """Test collaborative reasoning chains."""

    def test_chain_creation(self, collaboration: HumanAICollaboration) -> None:
        """Test creating a collaborative reasoning chain."""
        chain = collaboration.initiate_collaborative_reasoning("How to optimize?")
        assert chain.current_focus == "How to optimize?"
        assert len(chain.elements) == 1
        assert chain.human_contributions == 0
        assert chain.ai_contributions == 0

    def test_human_contribution(self, collaboration: HumanAICollaboration) -> None:
        """Test adding human contribution to chain."""
        chain = collaboration.initiate_collaborative_reasoning("Problem statement")
        result = collaboration.add_human_contribution(
            chain, "Database is the bottleneck", "insight"
        )

        assert result["contribution_recorded"] is True
        assert chain.human_contributions == 1
        assert len(chain.elements) == 2

    def test_ai_contribution(self, collaboration: HumanAICollaboration) -> None:
        """Test adding AI contribution to chain."""
        chain = collaboration.initiate_collaborative_reasoning("Problem statement")
        collaboration.add_human_contribution(chain, "Initial insight", "insight")

        result = collaboration.add_ai_contribution(chain, "Analysis shows 60% latency", "analysis")

        assert result["contribution_recorded"] is True
        assert chain.ai_contributions == 1

    def test_shared_context_update(self, collaboration: HumanAICollaboration) -> None:
        """Test shared context updates with contributions."""
        chain = collaboration.initiate_collaborative_reasoning("Problem")
        collaboration.add_human_contribution(chain, "Key insight", "insight")

        assert collaboration.shared_context is not None
        assert len(collaboration.shared_context.confirmed_insights) > 0

    def test_chain_finalization(self, collaboration: HumanAICollaboration) -> None:
        """Test finalizing a collaborative reasoning chain."""
        chain = collaboration.initiate_collaborative_reasoning("How to optimize?")
        collaboration.add_human_contribution(chain, "Database bottleneck", "insight")
        collaboration.add_ai_contribution(chain, "Query analysis", "analysis")

        result = collaboration.finalize_collaborative_reasoning(chain)

        assert "conclusions" in result
        assert result["human_contributions"] == 1
        assert result["ai_contributions"] == 1
        assert chain.consensus_achieved is True
        assert chain.completed_at > 0

    def test_chain_history_tracking(self, collaboration: HumanAICollaboration) -> None:
        """Test that completed chains are tracked."""
        initial_count = len(collaboration.reasoning_chains)

        chain = collaboration.initiate_collaborative_reasoning("Problem")
        collaboration.add_human_contribution(chain, "Insight", "insight")
        collaboration.finalize_collaborative_reasoning(chain)

        assert len(collaboration.reasoning_chains) == initial_count + 1


class TestCollaborationModes:
    """Test different collaboration mode detection."""

    def test_exploratory_mode_detection(self, collaboration: HumanAICollaboration) -> None:
        """Test detection of exploratory mode."""
        intent = collaboration.parse_human_intent("Let's explore what if scenarios")
        assert intent.preferred_mode == CollaborationMode.EXPLORATORY

    def test_ai_led_mode_detection(self, collaboration: HumanAICollaboration) -> None:
        """Test detection of AI-led mode."""
        intent = collaboration.parse_human_intent("I need you to handle this task")
        assert intent.preferred_mode == CollaborationMode.AI_LED

    def test_human_led_mode_detection(self, collaboration: HumanAICollaboration) -> None:
        """Test detection of human-led mode."""
        intent = collaboration.parse_human_intent("Let me work on this problem")
        assert intent.preferred_mode == CollaborationMode.HUMAN_LED

    def test_co_creation_mode_detection(self, collaboration: HumanAICollaboration) -> None:
        """Test detection of co-creation mode."""
        intent = collaboration.parse_human_intent("Let's collaborate together")
        assert intent.preferred_mode == CollaborationMode.CO_CREATION


class TestAdaptationAndMetrics:
    """Test adaptation mechanisms and metrics."""

    def test_explanation_depth_determination(self, collaboration: HumanAICollaboration) -> None:
        """Test explanation depth based on expertise."""
        expert = collaboration.parse_human_intent("Architecture optimization algorithm framework")
        assert expert.explanation_depth == "minimal"

        novice = collaboration.parse_human_intent("Help me understand")
        assert novice.explanation_depth == "detailed"

    def test_autonomy_tolerance_estimation(self, collaboration: HumanAICollaboration) -> None:
        """Test autonomy tolerance based on cognitive style."""
        analytical = collaboration.parse_human_intent("Systematic step analysis")
        assert analytical.autonomy_tolerance == 0.8

        experimental = collaboration.parse_human_intent("Try experiment test")
        assert experimental.autonomy_tolerance == 0.4

    def test_satisfaction_trend_calculation(
        self, collaboration: HumanAICollaboration, mock_reasoning: Any
    ) -> None:
        """Test satisfaction trend calculation."""
        # Not enough data initially
        assert collaboration._calculate_satisfaction_trend() == "insufficient_data"

        # Add feedback to build trend
        for i in range(10):
            collaboration.parse_human_intent(f"Query {i}")
            s = collaboration.generate_ai_suggestion(mock_reasoning)
            collaboration.receive_human_feedback(s, 0.9, "Good", True)

        trend = collaboration._calculate_satisfaction_trend()
        assert trend in ["improving", "stable", "declining"]

    def test_synergy_from_collaboration(self, collaboration: HumanAICollaboration) -> None:
        """Test synergy score from completed collaborations."""
        chain = collaboration.initiate_collaborative_reasoning("Problem")
        # Balanced contributions
        for _ in range(3):
            collaboration.add_human_contribution(chain, "Human insight", "insight")
            collaboration.add_ai_contribution(chain, "AI analysis", "analysis")

        collaboration.finalize_collaborative_reasoning(chain)
        assert collaboration.adaptation.synergy_score > 0


class TestCollaborationReporting:
    """Test collaboration reporting functionality."""

    def test_report_structure(self, collaboration: HumanAICollaboration) -> None:
        """Test report contains expected fields."""
        report = collaboration.get_collaboration_report()

        assert "current_mode" in report
        assert "total_interactions" in report
        assert "adaptation" in report
        assert "synergy_score" in report["adaptation"]

    def test_report_with_active_collaboration(
        self, collaboration: HumanAICollaboration, mock_reasoning: Any
    ) -> None:
        """Test report with active collaboration data."""
        collaboration.parse_human_intent("Test query")
        collaboration.generate_ai_suggestion(mock_reasoning)

        report = collaboration.get_collaboration_report()
        assert report["total_interactions"] > 0
        assert report["current_intent"] is not None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_input(self, collaboration: HumanAICollaboration) -> None:
        """Test handling of empty input."""
        intent = collaboration.parse_human_intent("")
        assert intent.detected_style == HumanCognitiveStyle.VERBAL  # Default

    def test_very_long_input(self, collaboration: HumanAICollaboration) -> None:
        """Test handling of very long input."""
        long_input = "optimization " * 1000
        intent = collaboration.parse_human_intent(long_input)
        assert intent.expertise_level > 0.5

    def test_finalize_empty_chain(self, collaboration: HumanAICollaboration) -> None:
        """Test finalizing chain with no contributions."""
        chain = collaboration.initiate_collaborative_reasoning("Problem")
        result = collaboration.finalize_collaborative_reasoning(chain)
        assert "conclusions" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
