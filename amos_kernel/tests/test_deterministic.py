"""Tests for Deterministic Layer (L3)"""

from amos_kernel.core.deterministic import (
    DeterministicCore,
    compare,
)


class TestDeterministicCore:
    def test_predict_returns_dict(self):
        core = DeterministicCore()
        state = {"prediction": {"a": 0.5, "b": 0.8}}
        result = core.predict(state, ["a", "b"])
        assert isinstance(result, dict)
        assert "a" in result

    def test_compare_calculates_error(self):
        core = DeterministicCore()
        predicted = {"x": 0.5}
        observed = {"x": 0.7}
        result = core.compare(predicted, observed)
        assert result.error["x"] == 0.2

    def test_correct_updates_values(self):
        core = DeterministicCore()
        current = {"x": 0.5}
        error = {"x": 0.1}
        result = core.correct(current, error, alpha=0.5)
        assert result.corrected["x"] == 0.55

    def test_transition_with_valid_constraints(self):
        core = DeterministicCore()
        state = {"counter": 0}
        interaction = {"input": "test"}
        result = core.transition(state, interaction, constraints_ok=True)
        assert result.changed is True

    def test_transition_with_invalid_constraints(self):
        core = DeterministicCore()
        state = {"counter": 0}
        interaction = {"input": "test"}
        result = core.transition(state, interaction, constraints_ok=False)
        assert result.changed is False


class TestCompare:
    def test_compare_with_matching_values(self):
        predicted = {"x": 0.5}
        observed = {"x": 0.5}
        result = compare(predicted, observed)
        assert result.error["x"] == 0.0

    def test_compare_with_different_values(self):
        predicted = {"x": 0.5}
        observed = {"x": 0.7}
        result = compare(predicted, observed)
        assert result.error["x"] == 0.2
