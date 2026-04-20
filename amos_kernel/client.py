"""AMOS Kernel Client - Unified interface to kernel layers"""

from dataclasses import dataclass
from typing import Any, Optional

from .core.deterministic import DeterministicCore
from .core.interaction import InteractionOperator
from .core.law import UniversalLawKernel, ValidationResult
from .core.state import TensorState
from .workflows import KernelWorkflowEngine, WorkflowResult


@dataclass
class KernelContext:
    """Context for kernel operations"""

    biological: dict
    cognitive: dict
    system: dict
    environment: dict


class AMOSKernelClient:
    """Unified client for AMOS kernel operations

    Provides simplified access to all six kernel layers:
    - law (L0)
    - state (L1)
    - interaction (L2)
    - deterministic (L3)
    - observe (L4)
    - repair (L5)
    """

    def __init__(self):
        self.law = UniversalLawKernel()
        self.state = TensorState()
        self.interaction = InteractionOperator()
        self.deterministic = DeterministicCore()
        self._workflow_engine = KernelWorkflowEngine()

    def validate(self, context: KernelContext) -> ValidationResult:
        """Validate context through universal law kernel"""
        return self.law.validate(context)

    def execute_workflow(
        self,
        workflow_id: str,
        context: KernelContext,
        validate_laws: bool = True,
    ) -> WorkflowResult:
        """Execute workflow with kernel validation"""
        raw_input = {
            "biological": context.biological,
            "cognitive": context.cognitive,
            "system": context.system,
            "environment": context.environment,
        }
        return self._workflow_engine.execute(
            workflow_id=workflow_id,
            raw_input=raw_input,
            validate_laws=validate_laws,
        )

    def process_task(
        self,
        task_type: str,
        payload: dict,
        context: KernelContext,
    ) -> dict[str, Any]:
        """Process task through kernel layers"""
        # Validate through law
        law_result = self.validate(context)
        if not law_result.passed:
            return {
                "success": False,
                "error": "Law validation failed",
                "violations": law_result.violations,
            }

        # Normalize state
        raw_state = {
            "biological": context.biological,
            "cognitive": context.cognitive,
            "system": context.system,
            "environment": context.environment,
        }
        tensor = self.state.normalize(raw_state)

        # Process through deterministic core
        det_result = self.deterministic.apply(tensor, payload)

        return {
            "success": True,
            "tensor": tensor,
            "deterministic_output": det_result.output if det_result else None,
            "law_valid": True,
        }

    def health(self) -> dict[str, Any]:
        """Get kernel health status"""
        return {
            "kernel_version": "7.0.0",
            "layers": {
                "law": self.law is not None,
                "state": self.state is not None,
                "interaction": self.interaction is not None,
                "deterministic": self.deterministic is not None,
            },
            "status": "healthy",
        }


# Singleton instance
_kernel_client: Optional[AMOSKernelClient] = None


def get_kernel() -> AMOSKernelClient:
    """Get or create kernel client singleton"""
    global _kernel_client
    if _kernel_client is None:
        _kernel_client = AMOSKernelClient()
    return _kernel_client


def create_kernel() -> AMOSKernelClient:
    """Create new kernel client instance"""
    return AMOSKernelClient()
