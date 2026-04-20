"""Tests for Observe Layer (L4)"""

from amos_kernel.core.observe import detect_drift, detect_state_drift


class TestDetectDrift:
    def test_all_passed_returns_healthy(self):
        checks = {"a": True, "b": True}
        result = detect_drift(checks)
        assert result.healthy is True
        assert result.issue_count == 0

    def test_failed_check_returns_unhealthy(self):
        checks = {"a": True, "b": False}
        result = detect_drift(checks)
        assert result.healthy is False
        assert result.issue_count == 1

    def test_has_fatal_with_fatal_error(self):
        checks = {"fatal_check": False}
        result = detect_drift(checks)
        # Note: detect_drift uses "error" severity, not "fatal"
        assert result.has_fatal is False


class TestDetectStateDrift:
    def test_no_drift_when_similar(self):
        previous = {"x": 0.5}
        current = {"x": 0.51}
        result = detect_state_drift(previous, current, threshold=0.1)
        assert result.healthy is True

    def test_drift_when_values_change(self):
        previous = {"x": 0.5}
        current = {"x": 0.9}
        result = detect_state_drift(previous, current, threshold=0.1)
        assert result.healthy is False
