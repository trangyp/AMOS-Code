"""Tests for State Layer (L1)"""

from amos_kernel.core.state import (
    IntegrityTensor,
    TensorState,
    UniversalStateModel,
    bounded_score,
    integrity,
)


class TestUniversalStateModel:
    def test_normalize_creates_tensor(self):
        model = UniversalStateModel()
        raw = {"biological": {"load": 0.5}, "environment": {"temp": 25}}
        result = model.normalize(raw)
        assert isinstance(result, TensorState)
        assert result.biological == {"load": 0.5}

    def test_validate_quadrants_with_data(self):
        model = UniversalStateModel()
        tensor = TensorState(biological={"x": 1})
        assert model.validate_quadrants(tensor) is True

    def test_validate_quadrants_empty(self):
        model = UniversalStateModel()
        tensor = TensorState()
        assert model.validate_quadrants(tensor) is False


class TestIntegrity:
    def test_integrity_calculates_scores(self):
        state = TensorState(
            biological={"a": 0.5, "b": 0.8},
            cognitive={"c": 0.9},
        )
        result = integrity(state)
        assert isinstance(result, IntegrityTensor)
        assert 0.0 <= result.biological <= 1.0

    def test_bounded_score_with_values(self):
        values = {"a": 0.5, "b": 0.8}
        result = bounded_score(values)
        assert 0.0 <= result <= 1.0

    def test_bounded_score_empty(self):
        result = bounded_score({})
        assert result == 0.0


class TestTensorState:
    def test_get_quadrants_returns_set(self):
        state = TensorState(
            biological={"x": 1},
            system={"y": 2},
        )
        quadrants = state.get_quadrants()
        assert "biological" in quadrants
        assert "technical" in quadrants
