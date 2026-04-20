"""Tests for Repair Layer (L5)"""

from amos_kernel.core.observe import DriftItem, DriftReport
from amos_kernel.core.repair import propose_repairs, verify_repairs


class TestProposeRepairs:
    def test_empty_report_returns_safe_plan(self):
        report = DriftReport(healthy=True, items=[])
        result = propose_repairs(report)
        assert result.safe is True
        assert result.action_count == 0

    def test_with_drift_items(self):
        items = [DriftItem(code="test", message="error", severity="error")]
        report = DriftReport(healthy=False, items=items)
        result = propose_repairs(report)
        assert result.action_count == 1

    def test_fatal_makes_unsafe(self):
        items = [DriftItem(code="test", message="fatal", severity="fatal")]
        report = DriftReport(healthy=False, items=items)
        result = propose_repairs(report)
        assert result.safe is False


class TestVerifyRepairs:
    def test_empty_plan_passes(self):
        from amos_kernel.core.repair import RepairPlan

        plan = RepairPlan(safe=True, actions=[])
        result = verify_repairs(plan)
        assert result.passed is True

    def test_unsafe_plan_fails(self):
        from amos_kernel.core.repair import RepairPlan

        plan = RepairPlan(safe=False, actions=[])
        result = verify_repairs(plan)
        assert result.passed is False
