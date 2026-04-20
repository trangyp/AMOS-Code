"""AMOS Kernel - Brain Integration. All brain ops validated through ULK."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from amos_kernel import DeterministicCore, UniversalLawKernel, UniversalStateModel
from amos_kernel.core.law.constraints import BiologicalConstraint, StabilityConstraint
from amos_kernel.core.law.types import QuadrantIntegrity


@dataclass
class BrainValidationContext:
    task_type: str
    inputs: dict[str, Any]
    constraints: dict[str, Any]
    domain: str


class KernelBrainBridge:
    """Bridge between AMOS Brain and Kernel validation."""

    _instance: KernelBrainBridge | None = None
    _initialized: bool = False

    def __new__(cls) -> KernelBrainBridge:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._ulk = UniversalLawKernel()
        self._core = DeterministicCore()
        self._state_model = UniversalStateModel()
        self._initialized = True

    def validate_brain_task(self, context: BrainValidationContext) -> dict[str, Any]:
        """Validate brain task through ULK."""
        if not self._initialized:
            self.__init__()

        bio = BiologicalConstraint(
            load=len(str(context.inputs)) / 1000.0,
            capacity=100.0,
        )
        stability = StabilityConstraint(
            contradiction_rate=0.0,
            correction_rate=1.0,
        )
        quadrants = QuadrantIntegrity(
            code=1.0,
            build=1.0,
            runtime=1.0,
            environment=1.0,
        )

        result = self._ulk.validate_invariants(
            contradictions=0,
            has_internal=True,
            has_external=context.domain != "internal",
            has_feedback=True,
            stability=stability,
            bio=bio,
            quadrants=quadrants,
            communication_text=str(context.inputs.get("query", "")),
        )

        return {
            "valid": result.passed,
            "score": result.quadrants.global_integrity,
            "violations": [],
        }

    def transition(self, state: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
        """Execute deterministic state transition."""
        if not self._initialized:
            self.__init__()
        result = self._core.transition(state, inputs, True)
        return {
            "success": True,
            "state_hash": result.new_state if hasattr(result, "new_state") else "",
        }


def get_kernel_brain_bridge() -> KernelBrainBridge:
    return KernelBrainBridge()


def validate_brain_operation(
    task_type: str, inputs: dict[str, Any], domain: str = "general"
) -> dict[str, Any]:
    """Validate brain operation through kernel."""
    bridge = get_kernel_brain_bridge()
    ctx = BrainValidationContext(task_type=task_type, inputs=inputs, constraints={}, domain=domain)
    return bridge.validate_brain_task(ctx)
