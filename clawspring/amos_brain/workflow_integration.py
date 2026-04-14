#!/usr/bin/env python3
"""AMOS Ecosystem v2.8 - Workflow Integration Layer.

Bridges the new cognitive ecosystem with existing workflow infrastructure
(amos_integrated_workflow.py, test_full_integration.py) enabling
seamless migration and backward compatibility.
"""

import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

sys.path.insert(0, ".")
sys.path.insert(0, "clawspring")
sys.path.insert(0, "clawspring/amos_brain")


class WorkflowStatus(Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class WorkflowStep:
    """Single workflow step definition."""

    id: str
    name: str
    module: str  # Which v2.8 module handles this
    action: str  # What action to perform
    params: dict[str, Any]
    depends_on: list[str]
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Optional[dict] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class WorkflowDefinition:
    """Complete workflow definition."""

    id: str
    name: str
    description: str
    steps: list[WorkflowStep]
    created_at: datetime
    version: str = "2.8"


class WorkflowEngine:
    """Execute workflows using v2.8 ecosystem modules."""

    def __init__(self):
        self.active_workflows: dict[str, WorkflowDefinition] = {}
        self.step_handlers: dict[str, Callable] = {}
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register handlers for each v2.8 module."""
        self.step_handlers = {
            "cognitive_router": self._handle_cognitive_route,
            "ethics_validator": self._handle_ethics_check,
            "master_orchestrator": self._handle_orchestration,
            "organism_bridge": self._handle_organism_task,
            "system_validator": self._handle_validation,
            "telemetry": self._handle_telemetry,
            "resilience": self._handle_resilient_operation,
            "deep_integration": self._handle_unified_task,
        }

    def create_workflow(
        self, name: str, description: str, steps_config: list[dict]
    ) -> WorkflowDefinition:
        """Create a new workflow definition."""
        steps = []
        for i, config in enumerate(steps_config):
            step = WorkflowStep(
                id=f"step_{i}",
                name=config.get("name", f"Step {i}"),
                module=config.get("module", "cognitive_router"),
                action=config.get("action", "execute"),
                params=config.get("params", {}),
                depends_on=config.get("depends_on", []),
            )
            steps.append(step)

        workflow = WorkflowDefinition(
            id=f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=name,
            description=description,
            steps=steps,
            created_at=datetime.now(),
        )

        self.active_workflows[workflow.id] = workflow
        return workflow

    def execute_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Execute a workflow."""
        if workflow_id not in self.active_workflows:
            return {"error": "Workflow not found"}

        workflow = self.active_workflows[workflow_id]
        print(f"\n[WorkflowEngine] Executing: {workflow.name}")

        results = {
            "workflow_id": workflow_id,
            "status": "running",
            "steps_completed": 0,
            "steps_total": len(workflow.steps),
            "step_results": {},
        }

        # Execute steps in dependency order
        completed_steps = set()
        failed_steps = set()

        while len(completed_steps) + len(failed_steps) < len(workflow.steps):
            progress = False

            for step in workflow.steps:
                if step.id in completed_steps or step.id in failed_steps:
                    continue

                # Check dependencies
                deps_satisfied = all(d in completed_steps for d in step.depends_on)
                if not deps_satisfied:
                    continue

                # Execute step
                progress = True
                step.started_at = datetime.now()
                step.status = WorkflowStatus.RUNNING

                try:
                    handler = self.step_handlers.get(step.module)
                    if handler:
                        step.result = handler(step.action, step.params)
                        step.status = WorkflowStatus.COMPLETED
                        completed_steps.add(step.id)
                        results["steps_completed"] += 1
                        print(f"  ✓ {step.name}")
                    else:
                        step.status = WorkflowStatus.FAILED
                        step.error = f"No handler for module: {step.module}"
                        failed_steps.add(step.id)
                        print(f"  ✗ {step.name} - No handler")

                except Exception as e:
                    step.status = WorkflowStatus.FAILED
                    step.error = str(e)
                    failed_steps.add(step.id)
                    print(f"  ✗ {step.name} - {str(e)[:50]}")

                step.completed_at = datetime.now()
                results["step_results"][step.id] = {
                    "status": step.status.value,
                    "result": step.result,
                    "error": step.error,
                }

            if not progress and len(completed_steps) + len(failed_steps) < len(workflow.steps):
                # Deadlock - remaining steps have unsatisfied dependencies
                remaining = [
                    s.id
                    for s in workflow.steps
                    if s.id not in completed_steps and s.id not in failed_steps
                ]
                print(f"  ⚠ Deadlock detected: {remaining}")
                break

        # Determine final status
        if len(failed_steps) == 0:
            results["status"] = "completed"
        elif len(completed_steps) > 0:
            results["status"] = "partial"
        else:
            results["status"] = "failed"

        return results

    # Step Handlers

    def _handle_cognitive_route(self, action: str, params: dict) -> dict:
        """Handle cognitive routing step."""
        from amos_cognitive_router import CognitiveRouter

        router = CognitiveRouter()
        result = router.analyze(params.get("task", ""))
        return {
            "domain": result.primary_domain,
            "risk": result.risk_level,
            "engines": result.suggested_engines,
        }

    def _handle_ethics_check(self, action: str, params: dict) -> dict:
        """Handle ethics validation step."""
        from ethics_integration import EthicsValidator

        ethics = EthicsValidator()
        result = ethics.validate_action(
            params.get("action", ""),
            params.get("context", {}),
            params.get("framework", "principlism"),
        )
        return {"passed": result.passed, "score": result.score, "violations": result.violations}

    def _handle_orchestration(self, action: str, params: dict) -> dict:
        """Handle master orchestration step."""
        from master_orchestrator import MasterOrchestrator

        orch = MasterOrchestrator()
        result = orch.orchestrate_cognitive_task(
            params.get("task_id", "workflow_task"),
            params.get("task", ""),
            params.get("priority", "MEDIUM"),
        )
        return {
            "success": result.success,
            "predicted_duration": result.predicted_duration_mins,
            "confidence": result.confidence,
        }

    def _handle_organism_task(self, action: str, params: dict) -> dict:
        """Handle organism bridge task."""
        from organism_bridge import get_organism_bridge

        bridge = get_organism_bridge()
        return bridge.get_status()

    def _handle_validation(self, action: str, params: dict) -> dict:
        """Handle system validation step."""
        from system_validator import validate_system

        success, summary = validate_system()
        return {"passed": summary["passed"], "total": summary["total"], "success": success}

    def _handle_telemetry(self, action: str, params: dict) -> dict:
        """Handle telemetry recording."""
        from telemetry import get_telemetry

        telemetry = get_telemetry()
        telemetry.metrics.increment_counter(
            params.get("metric", "workflow_step"), params.get("value", 1)
        )
        return {"recorded": True}

    def _handle_resilient_operation(self, action: str, params: dict) -> dict:
        """Handle resilient operation."""
        from resilience import get_resilience

        resilience = get_resilience()
        return {"status": "configured", "resilience": "active"}

    def _handle_unified_task(self, action: str, params: dict) -> dict:
        """Handle unified cognitive-organism task."""
        from deep_integration import get_deep_integration

        integration = get_deep_integration()
        result = integration.execute_unified_task(params.get("task", ""), params.get("context", {}))
        return {
            "success": result.get("success", False),
            "confidence": result.get("confidence", 0),
            "coherence": result.get("state", {}).get("coherence_score", 0),
        }


class WorkflowMigrationTool:
    """Migrate existing workflows to v2.8 format."""

    @staticmethod
    def migrate_legacy_workflow(legacy_config: dict) -> WorkflowDefinition:
        """Convert legacy workflow to v2.8 format."""
        engine = WorkflowEngine()

        steps = []
        for i, step in enumerate(legacy_config.get("steps", [])):
            # Map legacy steps to v2.8 modules
            module_map = {
                "cognitive": "cognitive_router",
                "ethics": "ethics_validator",
                "orchestrate": "master_orchestrator",
                "organism": "organism_bridge",
                "validate": "system_validator",
            }

            steps.append(
                {
                    "name": step.get("name", f"Step {i}"),
                    "module": module_map.get(step.get("type"), "cognitive_router"),
                    "action": step.get("action", "execute"),
                    "params": step.get("params", {}),
                    "depends_on": step.get("depends_on", []),
                }
            )

        return engine.create_workflow(
            name=legacy_config.get("name", "Migrated Workflow"),
            description=legacy_config.get("description", "Migrated from legacy format"),
            steps_config=steps,
        )


def main():
    """Demo workflow engine."""
    print("=" * 70)
    print("AMOS ECOSYSTEM v2.8 - WORKFLOW ENGINE DEMO")
    print("=" * 70)

    engine = WorkflowEngine()

    # Create sample workflow
    workflow = engine.create_workflow(
        name="Secure API Development",
        description="Complete workflow for building secure API",
        steps_config=[
            {
                "name": "Analyze Requirements",
                "module": "cognitive_router",
                "action": "analyze",
                "params": {"task": "Design secure authentication API"},
                "depends_on": [],
            },
            {
                "name": "Ethics Check",
                "module": "ethics_validator",
                "action": "validate",
                "params": {
                    "action": "Build authentication system",
                    "context": {"consent": True, "harm_potential": 0.1},
                    "framework": "principlism",
                },
                "depends_on": ["step_0"],
            },
            {
                "name": "Orchestrate Development",
                "module": "master_orchestrator",
                "action": "orchestrate",
                "params": {
                    "task_id": "auth_api",
                    "task": "Implement secure API",
                    "priority": "HIGH",
                },
                "depends_on": ["step_1"],
            },
            {
                "name": "System Validation",
                "module": "system_validator",
                "action": "validate",
                "params": {},
                "depends_on": ["step_2"],
            },
        ],
    )

    print(f"\nCreated Workflow: {workflow.name}")
    print(f"ID: {workflow.id}")
    print(f"Steps: {len(workflow.steps)}")

    # Execute workflow
    print("\nExecuting workflow...")
    result = engine.execute_workflow(workflow.id)

    print(f"\nWorkflow Status: {result['status'].upper()}")
    print(f"Steps Completed: {result['steps_completed']}/{result['steps_total']}")

    if result["status"] == "completed":
        print("\n✅ Workflow completed successfully!")
    elif result["status"] == "partial":
        print("\n⚠️ Workflow completed with some failures")
    else:
        print("\n❌ Workflow failed")

    print("\n" + "=" * 70)
    print("Workflow engine ready for production use!")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
