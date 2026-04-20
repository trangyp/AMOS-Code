#!/usr/bin/env python3

from typing import Any

"""AMOS Brain Status - Unified status reporting for all brain components.

Real-time operational status across:
- MasterOrchestrator
- OrganismBridge
- Task Queue
- Workflow Engine
- Detection Engine
- Auto-Remediation Engine

Owner: Trang Phan
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone

UTC = timezone.utc


@dataclass
class ComponentStatus:
    """Status of a single brain component."""

    name: str
    status: str  # operational, degraded, failed, unavailable
    version: str = "1.0.0"
    last_check: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class BrainSystemStatus:
    """Complete brain system status."""

    overall: str
    components: list[ComponentStatus]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_components: int = 0
    operational_count: int = 0
    degraded_count: int = 0
    failed_count: int = 0


class BrainStatusReporter:
    """Unified status reporter for AMOS brain ecosystem."""

    def __init__(self):
        self._components: dict[str, ComponentStatus] = {}

    async def check_master_orchestrator(self) -> ComponentStatus:
        """Check MasterOrchestrator status."""
        try:
            from amos_brain.master_orchestrator import get_master_orchestrator

            orch = get_master_orchestrator()
            status = "operational" if orch._initialized else "degraded"

            return ComponentStatus(
                name="MasterOrchestrator",
                status=status,
                details={
                    "initialized": orch._initialized,
                    "organism_bridge_ready": orch._organism_bridge is not None,
                    "task_executor_ready": orch._task_executor is not None,
                    "predictive_ready": orch._predictive is not None,
                },
            )
        except Exception as e:
            return ComponentStatus(
                name="MasterOrchestrator",
                status="failed",
                details={"error": str(e)},
            )

    async def check_organism_bridge(self) -> ComponentStatus:
        """Check OrganismBridge status."""
        try:
            from amos_brain.organism_bridge import get_organism_bridge

            bridge = get_organism_bridge()
            status_data = bridge.get_status()

            connected = status_data.get("total_connected", 0)
            available = status_data.get("total_available", 3)

            if connected == available:
                status = "operational"
            elif connected > 0:
                status = "degraded"
            else:
                status = "failed"

            return ComponentStatus(
                name="OrganismBridge",
                status=status,
                details=status_data,
            )
        except Exception as e:
            return ComponentStatus(
                name="OrganismBridge",
                status="failed",
                details={"error": str(e)},
            )

    async def check_task_queue(self) -> ComponentStatus:
        """Check Task Queue status."""
        try:
            from amos_brain.task_queue import get_task_queue

            queue = await get_task_queue()
            tasks = queue.list_tasks()

            pending = sum(1 for t in tasks if t.status.value == "pending")
            running = sum(1 for t in tasks if t.status.value == "running")
            completed = sum(1 for t in tasks if t.status.value == "completed")
            failed = sum(1 for t in tasks if t.status.value == "failed")

            return ComponentStatus(
                name="TaskQueue",
                status="operational",
                details={
                    "workers": queue._max_workers,
                    "total_tasks": len(tasks),
                    "pending": pending,
                    "running": running,
                    "completed": completed,
                    "failed": failed,
                },
            )
        except Exception as e:
            return ComponentStatus(
                name="TaskQueue",
                status="failed",
                details={"error": str(e)},
            )

    async def check_workflow_engine(self) -> ComponentStatus:
        """Check Workflow Engine status."""
        try:
            from amos_brain.brain_workflow_engine import get_workflow_engine

            engine = get_workflow_engine()
            workflows = engine.list_workflows()

            active = sum(1 for w in workflows if w.status == "running")
            pending = sum(1 for w in workflows if w.status == "pending")
            completed = sum(1 for w in workflows if w.status == "completed")

            return ComponentStatus(
                name="WorkflowEngine",
                status="operational",
                details={
                    "total_workflows": len(workflows),
                    "active": active,
                    "pending": pending,
                    "completed": completed,
                },
            )
        except Exception as e:
            return ComponentStatus(
                name="WorkflowEngine",
                status="failed",
                details={"error": str(e)},
            )

    async def check_detection_engine(self) -> ComponentStatus:
        """Check UnifiedDetectionEngine status."""
        try:
            from amos_brain.unified_detection_engine import (
                SCIPY_AVAILABLE,
                SKLEARN_AVAILABLE,
                UnifiedDetectionEngine,
            )

            # Test basic instantiation
            UnifiedDetectionEngine()

            return ComponentStatus(
                name="DetectionEngine",
                status="operational",
                details={
                    "scipy_available": SCIPY_AVAILABLE,
                    "sklearn_available": SKLEARN_AVAILABLE,
                },
            )
        except Exception as e:
            return ComponentStatus(
                name="DetectionEngine",
                status="failed",
                details={"error": str(e)},
            )

    async def check_remediation_engine(self) -> ComponentStatus:
        """Check AutoRemediationEngine status."""
        try:
            from amos_brain.auto_remediation_engine import AutoRemediationEngine

            engine = AutoRemediationEngine()

            return ComponentStatus(
                name="RemediationEngine",
                status="operational",
                details={
                    "history_entries": len(engine._history),
                    "active_plans": len(engine._active_plans),
                    "completed_plans": len(engine._completed_plans),
                },
            )
        except Exception as e:
            return ComponentStatus(
                name="RemediationEngine",
                status="failed",
                details={"error": str(e)},
            )

    async def get_full_status(self) -> BrainSystemStatus:
        """Get complete brain system status."""
        checks = [
            self.check_master_orchestrator(),
            self.check_organism_bridge(),
            self.check_task_queue(),
            self.check_workflow_engine(),
            self.check_detection_engine(),
            self.check_remediation_engine(),
        ]

        components = await asyncio.gather(*checks, return_exceptions=True)

        # Handle exceptions
        processed_components = []
        for comp in components:
            if isinstance(comp, Exception):
                processed_components.append(
                    ComponentStatus(
                        name="Unknown",
                        status="failed",
                        details={"error": str(comp)},
                    ),
                )
            else:
                processed_components.append(comp)

        operational = sum(1 for c in processed_components if c.status == "operational")
        degraded = sum(1 for c in processed_components if c.status == "degraded")
        failed = sum(1 for c in processed_components if c.status == "failed")

        # Determine overall status
        if failed == len(processed_components):
            overall = "critical"
        elif failed > 0:
            overall = "degraded"
        elif degraded > 0:
            overall = "warning"
        else:
            overall = "healthy"

        return BrainSystemStatus(
            overall=overall,
            components=processed_components,
            total_components=len(processed_components),
            operational_count=operational,
            degraded_count=degraded,
            failed_count=failed,
        )

    def print_status_report(self, status: BrainSystemStatus) -> None:
        """Print formatted status report."""
        print("=" * 70)
        print(f"AMOS BRAIN SYSTEM STATUS - {status.timestamp}")
        print("=" * 70)

        # Overall status
        overall_icon = {
            "healthy": "✓",
            "warning": "⚠️",
            "degraded": "⚠️",
            "critical": "✗",
        }.get(status.overall, "?")
        print(f"\nOverall: {overall_icon} {status.overall.upper()}")
        print(
            f"  Components: {status.operational_count} operational, "
            f"{status.degraded_count} degraded, {status.failed_count} failed"
        )

        # Component details
        print("\nComponent Status:")
        for comp in status.components:
            icon = {
                "operational": "✓",
                "degraded": "~",
                "failed": "✗",
                "unavailable": "-",
            }.get(comp.status, "?")

            print(f"\n  {icon} {comp.name}: {comp.status}")
            for key, value in comp.details.items():
                if isinstance(value, dict):
                    print(f"    {key}:")
                    for k, v in value.items():
                        print(f"      {k}: {v}")
                else:
                    print(f"    {key}: {value}")

        print("\n" + "=" * 70)


async def main():
    """Run status report."""
    reporter = BrainStatusReporter()
    status = await reporter.get_full_status()
    reporter.print_status_report(status)

    # Export JSON for dashboard
    import json

    status_dict = {
        "overall": status.overall,
        "timestamp": status.timestamp,
        "summary": {
            "total": status.total_components,
            "operational": status.operational_count,
            "degraded": status.degraded_count,
            "failed": status.failed_count,
        },
        "components": [
            {
                "name": c.name,
                "status": c.status,
                "version": c.version,
                "details": c.details,
            }
            for c in status.components
        ],
    }
    print("\nJSON Export:")
    print(json.dumps(status_dict, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
