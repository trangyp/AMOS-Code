"""Integration tests for coherence bridge + local runtime.

Tests the integration between:
- AMOS coherence engine (signal detection, state assessment)
- Local LLM runtime (Ollama, LM Studio backends)
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add project to path  # noqa: E402
_here = os.path.dirname(os.path.abspath(__file__))  # noqa: E402
sys.path.insert(0, os.path.join(_here, ".."))  # noqa: E402

from amos_coherence_bridge import (  # noqa: E402
    CoherenceLocalBridge,
)
from amos_coherence_engine import (  # noqa: E402
    HumanState,
    InterventionMode,
)


class TestCoherenceLocalBridge(unittest.TestCase):
    """Test coherence + local runtime integration."""

    @patch("amos_coherence_bridge.create_local_runtime")
    def test_initialization(self, mock_create_runtime):
        """Test bridge initializes both systems."""
        # Mock runtime
        mock_runtime = Mock()
        mock_runtime.initialize.return_value = {
            "ready": True,
            "backend": {"backend": "ollama", "model": "test"},
        }
        mock_create_runtime.return_value = mock_runtime

        # Create bridge
        bridge = CoherenceLocalBridge()
        status = bridge.initialize()

        self.assertTrue(status["runtime_ready"])
        self.assertTrue(status["coherence_ready"])
        mock_runtime.initialize.assert_called_once()

    @patch("amos_coherence_bridge.create_local_runtime")
    def test_signal_detection(self, mock_create_runtime):
        """Test signal detection works with local analysis."""
        mock_runtime = Mock()
        mock_create_runtime.return_value = mock_runtime

        bridge = CoherenceLocalBridge(runtime=mock_runtime)

        # Analyze a message
        analysis = bridge.signal_detector.analyze("I'm feeling overwhelmed with everything")

        # Should detect noise components
        self.assertIn("noise_components", dir(analysis))
        self.assertIsInstance(analysis.noise_components, dict)

    def test_state_assessment_overloaded(self):
        """Test state assessment for high-noise message."""
        bridge = CoherenceLocalBridge(runtime=Mock())

        # Create analysis with high noise
        mock_analysis = Mock()
        mock_analysis.noise_components = {
            "overwhelm": 0.8,
            "confusion": 0.7,
            "anxiety": 0.6,
        }

        state = bridge._assess_state(mock_analysis)

        # High noise should result in OVERLOADED
        self.assertEqual(state, HumanState.OVERLOADED)

    def test_state_assessment_stable(self):
        """Test state assessment for calm message."""
        bridge = CoherenceLocalBridge(runtime=Mock())

        # Create analysis with low noise
        mock_analysis = Mock()
        mock_analysis.noise_components = {
            "confusion": 0.1,
        }

        state = bridge._assess_state(mock_analysis)

        # Low noise should result in STABLE
        self.assertEqual(state, HumanState.STABLE)

    @patch("amos_coherence_bridge.create_local_runtime")
    def test_process_with_coherence_fallback(self, mock_create_runtime):
        """Test fallback when LLM fails."""
        # Mock runtime that fails
        mock_runtime = Mock()
        mock_runtime.reply.return_value = {"ok": False, "error": "Failed"}
        mock_create_runtime.return_value = mock_runtime

        bridge = CoherenceLocalBridge(runtime=mock_runtime)

        result = bridge.process_with_coherence("Test message")

        # Should return fallback response
        self.assertIsNotNone(result.response)
        self.assertGreater(len(result.response), 0)

    def test_intervention_selection_overloaded(self):
        """Test intervention selection for overloaded state."""
        bridge = CoherenceLocalBridge(runtime=Mock())

        # Create mock analysis for overloaded state
        mock_analysis = Mock()
        mock_analysis.pattern = "overwhelm"
        mock_analysis.clarity_score = 0.3
        mock_analysis.noise_components = {"overwhelm": 0.9}

        # Get state
        state = bridge._assess_state(mock_analysis)
        self.assertEqual(state, HumanState.OVERLOADED)

        # Select intervention
        intervention = bridge.intervention_selector.select(mock_analysis, state, 0.3)

        # Should select grounding or boundary for overloaded
        valid = [InterventionMode.GROUND, InterventionMode.BOUNDARY]
        self.assertIn(intervention, valid)

    def test_verify_coherence_improvement(self):
        """Test coherence verification detects improvement."""
        bridge = CoherenceLocalBridge(runtime=Mock())

        # Original analysis with high noise
        original = Mock()
        original.noise_components = {"anxiety": 0.8, "confusion": 0.6}

        # Mock that new analysis has lower noise
        with patch.object(bridge.signal_detector, "analyze") as mock_analyze:
            new_analysis = Mock()
            new_analysis.noise_components = {"anxiety": 0.2}  # Reduced
            mock_analyze.return_value = new_analysis

            score = bridge._verify_coherence("Better response", original)

            # Should show improvement
            self.assertGreater(score, 0)

    def test_build_coherence_prompt(self):
        """Test prompt building includes coherence context."""
        bridge = CoherenceLocalBridge(runtime=Mock())

        analysis = Mock()
        analysis.signal = "overwhelm"
        analysis.pattern = "overload"
        analysis.clarity_score = 0.3
        analysis.noise_components = {"overwhelm": 0.8}

        prompt = bridge._build_coherence_prompt(
            "I'm overwhelmed",
            analysis,
            HumanState.OVERLOADED,
            InterventionMode.GROUND,
        )

        # Prompt should include key elements
        self.assertIn("overwhelm", prompt)
        self.assertIn("OVERLOADED", prompt)
        self.assertIn("I'm overwhelmed", prompt)
        self.assertIn("GROUND", prompt)


class TestCoherenceBridgeIntegration(unittest.TestCase):
    """Integration tests requiring actual backends (optional)."""

    @unittest.skipUnless(os.getenv("RUN_INTEGRATION_TESTS"), "Set RUN_INTEGRATION_TESTS=1 to run")
    def test_full_pipeline_with_mock(self):
        """Full pipeline test - skipped unless explicitly enabled."""
        # This test would run the full pipeline
        # Only runs if RUN_INTEGRATION_TESTS=1 is set
        pass


if __name__ == "__main__":
    unittest.main()
