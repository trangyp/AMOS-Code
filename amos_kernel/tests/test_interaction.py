"""Tests for Interaction Layer (L2)"""

from amos_kernel.core.interaction import InteractionOperator, InteractionResult


class TestInteractionOperator:
    def test_apply_with_both_inputs(self):
        op = InteractionOperator()
        internal = {"state": "active"}
        external = {"observation": "data"}
        result = op.apply(internal, external)
        assert isinstance(result, InteractionResult)
        assert result.coupling_strength == 1.0

    def test_apply_with_missing_external(self):
        op = InteractionOperator()
        internal = {"state": "active"}
        external = {}
        result = op.apply(internal, external)
        assert result.coupling_strength == 0.0

    def test_extract_feedback(self):
        op = InteractionOperator()
        result = op.apply({"x": 1}, {"y": 2})
        feedback = op.extract_feedback(result)
        assert "coupling_strength" in feedback
