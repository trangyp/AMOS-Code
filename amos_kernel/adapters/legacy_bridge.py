"""Legacy Bridge - Adapts old amos_brain API to new kernel-first architecture"""

from typing import Any, Optional

from ..core.deterministic import DeterministicCore
from ..core.interaction import InteractionOperator
from ..core.law import UniversalLawKernel
from ..core.state import TensorState, UniversalStateModel, integrity


class KernelAdapter:
    """Adapts legacy amos_brain calls to kernel-first architecture."""

    def __init__(self):
        self.law = UniversalLawKernel()
        self.state = UniversalStateModel()
        self.interaction = InteractionOperator()
        self.deterministic = DeterministicCore()

    def process_task(self, task: str, context: Optional[dict] = None) -> dict[str, Any]:
        """Legacy task_processor.process_task adapter."""
        # Normalize input to tensor state
        raw_state = {
            "biological": {"task_complexity": len(task) / 1000},
            "cognitive": {"context_size": len(str(context)) if context else 0},
            "system": {"task": task},
            "environment": context or {},
        }

        tensor = self.state.normalize(raw_state)

        # Run law validation
        integ = integrity(tensor)
        law_result = self.law.validate_invariants(
            contradictions=0,
            has_internal=bool(tensor.biological),
            has_external=bool(tensor.environment),
            has_feedback=True,
            stability=self._make_stability(),
            bio=self._make_bio(tensor),
            quadrants=integ.to_quadrant(),
            communication_text=task,
        )

        # Execute interaction
        interaction = self.interaction.apply(tensor.biological, tensor.environment)

        return {
            "task": task,
            "law_compliant": law_result.passed,
            "collapse_risk": law_result.collapse_risk,
            "quadrants": list(tensor.get_quadrants()),
            "coupling_strength": interaction.coupling_strength,
            "healthy": law_result.healthy,
        }

    def check_laws(self, text: str) -> dict[str, Any]:
        """Legacy GlobalLaws.check adapter."""
        result = self.law.validate_action(text)
        return {
            "compliant": result.compliant,
            "violations": result.violations,
        }

    def _make_stability(self):
        from ..core.law import StabilityConstraint

        return StabilityConstraint(contradiction_rate=0.1, correction_rate=0.2)

    def _make_bio(self, tensor: TensorState):
        from ..core.law import BiologicalConstraint

        load = sum(tensor.biological.values()) if tensor.biological else 0
        capacity = 100.0
        return BiologicalConstraint(load=load, capacity=capacity)


def get_kernel_adapter() -> KernelAdapter:
    """Factory function for legacy compatibility."""
    return KernelAdapter()
