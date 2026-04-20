"""Repair planning - extracted from amos_brain/repair_bridge.py"""

from ..observe.types import DriftReport
from .types import RepairAction, RepairPlan


def propose_repairs(report: DriftReport) -> RepairPlan:
    """Generate repair plan from drift report."""
    actions = []
    for item in report.items:
        actions.append(
            RepairAction(
                kind="codemod",
                target=item.code,
                description=f"Repair for {item.code}: {item.message}",
            )
        )

    # Safe if no fatal issues
    safe = not report.has_fatal

    return RepairPlan(safe=safe, actions=actions)


def prioritize_repairs(plan: RepairPlan) -> list[RepairAction]:
    """Sort repairs by priority (fatal first)."""
    # Simple priority: keep current order
    return plan.actions
