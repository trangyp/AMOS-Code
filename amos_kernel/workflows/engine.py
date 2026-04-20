from __future__ import annotations

"""Workflow Engine - Orchestrates kernel layers for task execution"""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Optional

from ..core.deterministic import DeterministicCore
from ..core.interaction import InteractionOperator
from ..core.law import UniversalLawKernel, ValidationResult
from ..core.observe import detect_drift
from ..core.repair import propose_repairs, verify_repairs
from ..core.state import UniversalStateModel, integrity


@dataclass
class WorkflowStep:
    name: str
    status: str = "pending"  # pending, running, completed, failed
    result: dict | None = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class WorkflowResult:
    workflow_id: str
    success: bool
    steps: list[WorkflowStep]
    law_validation: Optional[ValidationResult] = None
    final_state: dict | None = None
    drift_detected: bool = False
    repairs_proposed: int = 0


class KernelWorkflowEngine:
    """Executes workflows through all 6 kernel layers."""

    def __init__(self):
        self.law = UniversalLawKernel()
        self.state = UniversalStateModel()
        self.interaction = InteractionOperator()
        self.deterministic = DeterministicCore()

    def execute(
        self,
        workflow_id: str,
        raw_input: dict[str, Any],
        validate_laws: bool = True,
    ) -> WorkflowResult:
        """Execute workflow through kernel stack."""
        steps = []

        # Step 1: L1 - Normalize state
        step1 = WorkflowStep(name="state_normalization")
        step1.started_at = datetime.now(UTC).isoformat()
        tensor = self.state.normalize(raw_input)
        step1.status = "completed"
        step1.result = {"quadrants": list(tensor.get_quadrants())}
        step1.completed_at = datetime.now(UTC).isoformat()
        steps.append(step1)

        # Step 2: L2 - Apply interaction
        step2 = WorkflowStep(name="interaction")
        step2.started_at = datetime.now(UTC).isoformat()
        interaction = self.interaction.apply(tensor.biological, tensor.environment)
        step2.status = "completed"
        step2.result = {"coupling": interaction.coupling_strength}
        step2.completed_at = datetime.now(UTC).isoformat()
        steps.append(step2)

        # Step 3: L0 - Validate laws
        law_result = None
        if validate_laws:
            step3 = WorkflowStep(name="law_validation")
            step3.started_at = datetime.now(UTC).isoformat()

            integ = integrity(tensor)
            from ..core.law import BiologicalConstraint, QuadrantIntegrity, StabilityConstraint

            law_result = self.law.validate_invariants(
                contradictions=0,
                has_internal=bool(tensor.biological),
                has_external=bool(tensor.environment),
                has_feedback=interaction.coupling_strength > 0,
                stability=StabilityConstraint(0.1, 0.2),
                bio=BiologicalConstraint(
                    sum(tensor.biological.values()) if tensor.biological else 0, 100.0
                ),
                quadrants=QuadrantIntegrity(
                    code=integ.cognitive,
                    build=integ.system,
                    runtime=integ.system,
                    environment=integ.environment,
                ),
            )
            step3.status = "completed" if law_result.passed else "failed"
            step3.result = {
                "passed": law_result.passed,
                "collapse_risk": law_result.collapse_risk,
            }
            step3.completed_at = datetime.now(UTC).isoformat()
            steps.append(step3)

        # Step 4: L3 - State transition
        step4 = WorkflowStep(name="deterministic_transition")
        step4.started_at = datetime.now(UTC).isoformat()
        state_dict = {
            "biological": tensor.biological,
            "cognitive": tensor.cognitive,
            "system": tensor.system,
            "environment": tensor.environment,
        }
        transition = self.deterministic.transition(
            state_dict, interaction.data, law_result.passed if law_result else True
        )
        step4.status = "completed" if transition.changed else "failed"
        step4.result = {"changed": transition.changed, "reason": transition.reason}
        step4.completed_at = datetime.now(UTC).isoformat()
        steps.append(step4)

        # Step 5: L4 - Observe/Drift detection
        step5 = WorkflowStep(name="drift_detection")
        step5.started_at = datetime.now(UTC).isoformat()
        drift = detect_drift(
            {
                "transition_valid": transition.changed,
                "law_passed": law_result.passed if law_result else True,
            }
        )
        step5.status = "completed"
        step5.result = {"healthy": drift.healthy, "issues": drift.issue_count}
        step5.completed_at = datetime.now(UTC).isoformat()
        steps.append(step5)

        # Step 6: L5 - Repair planning
        step6 = WorkflowStep(name="repair_planning")
        step6.started_at = datetime.now(UTC).isoformat()
        repairs = propose_repairs(drift)
        verify = verify_repairs(repairs)
        step6.status = "completed"
        step6.result = {
            "safe": repairs.safe,
            "actions": repairs.action_count,
            "verified": verify.passed,
        }
        step6.completed_at = datetime.now(UTC).isoformat()
        steps.append(step6)

        # Overall success
        success = all(s.status == "completed" for s in steps)

        return WorkflowResult(
            workflow_id=workflow_id,
            success=success,
            steps=steps,
            law_validation=law_result,
            final_state=transition.next_state,
            drift_detected=not drift.healthy,
            repairs_proposed=repairs.action_count,
        )


def get_workflow_engine() -> KernelWorkflowEngine:
    """Factory for workflow engine."""
    return KernelWorkflowEngine()
