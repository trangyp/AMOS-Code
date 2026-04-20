"""Bootstrap - initializes all kernel layers in dependency order"""

from ..core.deterministic.engine import DeterministicCore
from ..core.interaction.operator import InteractionOperator
from ..core.law.constraints import BiologicalConstraint, StabilityConstraint
from ..core.law.types import QuadrantIntegrity
from ..core.law.validators import UniversalLawKernel
from ..core.observe.drift import detect_drift
from ..core.repair.planner import propose_repairs
from ..core.state.integrity import integrity
from ..core.state.normalize import UniversalStateModel


class Bootstrap:
    """Bootstraps the AMOS kernel with all 6 layers."""

    def __init__(self):
        self.law = UniversalLawKernel()
        self.state = UniversalStateModel()
        self.core = DeterministicCore()
        self.interaction = InteractionOperator()

    def execute_cycle(self, raw_input: dict) -> dict:
        """Execute full kernel cycle through all 6 layers."""
        # L1: Normalize state
        tensor_state = self.state.normalize(raw_input)

        # L2: Apply interaction
        interaction = self.interaction.apply(tensor_state.biological, tensor_state.environment)

        # Calculate integrity for law validation
        integrity_tensor = integrity(tensor_state)

        # L0: Validate laws
        load = tensor_state.biological.get("load", 0.0)
        capacity = tensor_state.biological.get("capacity", 100.0)

        law_result = self.law.validate_invariants(
            contradictions=0,
            has_internal=bool(tensor_state.biological),
            has_external=bool(tensor_state.environment),
            has_feedback=interaction.coupling_strength > 0,
            stability=StabilityConstraint(contradiction_rate=0.1, correction_rate=0.2),
            bio=BiologicalConstraint(load=load, capacity=capacity),
            quadrants=QuadrantIntegrity(
                code=integrity_tensor.cognitive,
                build=integrity_tensor.system,
                runtime=integrity_tensor.system,
                environment=integrity_tensor.environment,
            ),
        )

        # L3: State transition
        state_dict = {
            "biological": tensor_state.biological,
            "cognitive": tensor_state.cognitive,
            "system": tensor_state.system,
            "environment": tensor_state.environment,
        }
        transition = self.core.transition(state_dict, interaction.data, law_result.passed)

        # L4: Observe/detect drift
        drift = detect_drift(
            {
                "transition_valid": transition.changed,
                "law_passed": law_result.passed,
                "healthy": law_result.healthy,
            }
        )

        # L5: Propose repairs
        repairs = propose_repairs(drift)

        return {
            "state": transition.next_state,
            "law": law_result,
            "drift": drift,
            "repairs": repairs,
            "healthy": law_result.healthy and drift.healthy,
        }

    def is_healthy(self) -> bool:
        """Check if bootstrap initialized correctly."""
        return all(
            [
                self.law is not None,
                self.state is not None,
                self.core is not None,
                self.interaction is not None,
            ]
        )
