"""AMOSL Bridge Executor - Cross-Substrate Morphisms.

Implements:
    B_{i→j}: (X_i, q_i) → Signal_{ij} → (X_j, q_j)

Legality:
    Legal(B_{ij}) = TypeCompat · UnitCompat · TimeCompat · ObsCompat · ErrorCompat

Bridges:
    - Classical → Quantum (encoding)
    - Quantum → Classical (measurement)
    - Biological → Classical (threshold)
    - Classical → Biological (control)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class BridgeType(Enum):
    """Types of cross-substrate bridges."""

    C_TO_Q = auto()  # Classical to Quantum
    Q_TO_C = auto()  # Quantum to Classical (measurement)
    C_TO_B = auto()  # Classical to Biological
    B_TO_C = auto()  # Biological to Classical
    B_TO_Q = auto()  # Biological to Quantum
    Q_TO_B = auto()  # Quantum to Biological


@dataclass
class BridgeSignal:
    """Intermediate signal representation."""

    value: Any
    uncertainty: float
    timestamp: float
    metadata: dict[str, Any]


class BridgeExecutor:
    """Executes cross-substrate bridges with legality checking."""

    def __init__(self):
        self.bridges: dict[str, dict[str, Any]] = {}
        self.active_bridges: dict[str, BridgeSignal] = {}

    def check_legality(
        self,
        bridge_type: BridgeType,
        type_compat: bool = True,
        unit_compat: bool = True,
        time_compat: bool = True,
        obs_compat: bool = True,
        error_compat: bool = True,
    ) -> tuple[bool, str]:
        """Check Legal(B_{ij})."""
        checks = {
            "TypeCompat": type_compat,
            "UnitCompat": unit_compat,
            "TimeCompat": time_compat,
            "ObsCompat": obs_compat,
            "ErrorCompat": error_compat,
        }

        failed = [k for k, v in checks.items() if not v]

        if failed:
            return False, f"Failed: {', '.join(failed)}"

        return True, "Legal(B) = 1"

    def execute_classical_to_quantum(
        self, classical_value: Any, qubit_index: int = 0
    ) -> dict[str, Any]:
        """B_{c→q}: Encode classical bit as qubit.

        |0⟩ for 0, |1⟩ for 1
        """
        if classical_value == 0:
            qubit_state = {"basis": "computational", "value": "|0⟩"}
        elif classical_value == 1:
            qubit_state = {"basis": "computational", "value": "|1⟩"}
        else:
            # Superposition for non-boolean
            qubit_state = {"basis": "superposition", "value": "α|0⟩+β|1⟩"}

        signal = BridgeSignal(
            value=classical_value,
            uncertainty=0.0,  # Classical is certain
            timestamp=0.0,
            metadata={"target_qubit": qubit_index},
        )

        return {
            "type": "c_to_q",
            "input": classical_value,
            "output": qubit_state,
            "signal": signal,
            "legality": self.check_legality(BridgeType.C_TO_Q),
        }

    def execute_quantum_to_classical(
        self, measurement_result: Any, basis: str = "computational"
    ) -> dict[str, Any]:
        """B_{q→c}: Measurement → Classical decision.

        Collapses quantum state to classical bit.
        """
        if basis == "computational":
            classical_value = measurement_result.get("outcome", 0)
        else:
            # Other bases
            classical_value = measurement_result.get("probabilities", {}).get("0", 0.5) > 0.5

        signal = BridgeSignal(
            value=classical_value,
            uncertainty=measurement_result.get("uncertainty", 0.1),
            timestamp=0.0,
            metadata={"basis": basis, "perturbation": True},
        )

        return {
            "type": "q_to_c",
            "input": measurement_result,
            "output": classical_value,
            "signal": signal,
            "legality": self.check_legality(BridgeType.Q_TO_C),
        }

    def execute_classical_to_biological(
        self, control_signal: float, threshold: float = 0.5
    ) -> dict[str, Any]:
        """B_{c→b}: Classical control → Biological actuation.

        Threshold-based gene expression trigger.
        """
        activated = control_signal > threshold

        bio_action = {
            "type": "expression_trigger",
            "activated": activated,
            "level": control_signal if activated else 0.0,
        }

        signal = BridgeSignal(
            value=control_signal,
            uncertainty=0.05,  # Biological noise
            timestamp=0.0,
            metadata={"threshold": threshold, "activated": activated},
        )

        return {
            "type": "c_to_b",
            "input": control_signal,
            "output": bio_action,
            "signal": signal,
            "legality": self.check_legality(BridgeType.C_TO_B),
        }

    def execute_biological_to_classical(
        self, expression_level: float, threshold: float = 0.5
    ) -> dict[str, Any]:
        """B_{b→c}: Expression level → Classical threshold.

        Converts continuous bio signal to discrete classical state.
        """
        classical_state = expression_level > threshold

        signal = BridgeSignal(
            value=expression_level,
            uncertainty=0.1,  # Assay noise
            timestamp=0.0,
            metadata={"threshold": threshold, "binary": classical_state},
        )

        return {
            "type": "b_to_c",
            "input": expression_level,
            "output": classical_state,
            "signal": signal,
            "legality": self.check_legality(BridgeType.B_TO_C),
        }

    def execute_biological_to_quantum(self, protein_concentration: float) -> dict[str, Any]:
        """B_{b→q}: Protein concentration → Quantum register encoding."""
        # Encode concentration as quantum phase
        normalized = min(max(protein_concentration / 100.0, 0.0), 1.0)

        qubit_state = {
            "type": "phase_encoding",
            "phase": normalized * 3.14159,
            "amplitude": normalized,
        }

        signal = BridgeSignal(
            value=protein_concentration,
            uncertainty=0.15,  # Bio + quantum noise
            timestamp=0.0,
            metadata={"encoding": "phase", "normalized": normalized},
        )

        return {
            "type": "b_to_q",
            "input": protein_concentration,
            "output": qubit_state,
            "signal": signal,
            "legality": self.check_legality(BridgeType.B_TO_Q),
        }

    def execute_quantum_to_biological(self, quantum_state: dict) -> dict[str, Any]:
        """B_{q→b}: Quantum state → Biological stimulus."""
        # Extract probability amplitude
        prob_1 = quantum_state.get("probabilities", {}).get("1", 0.5)

        # Map to biological activation level
        bio_stimulus = {
            "type": "quantum_induced",
            "activation_level": prob_1,
            "duration": 1.0,  # time units
        }

        signal = BridgeSignal(
            value=prob_1,
            uncertainty=0.2,  # High uncertainty
            timestamp=0.0,
            metadata={"quantum_influence": True},
        )

        return {
            "type": "q_to_b",
            "input": quantum_state,
            "output": bio_stimulus,
            "signal": signal,
            "legality": self.check_legality(BridgeType.Q_TO_B),
        }

    def execute(self, bridge_type: BridgeType, value: Any, **kwargs) -> dict[str, Any]:
        """Execute bridge by type."""
        dispatch = {
            BridgeType.C_TO_Q: lambda: self.execute_classical_to_quantum(
                value, kwargs.get("qubit", 0)
            ),
            BridgeType.Q_TO_C: lambda: self.execute_quantum_to_classical(
                value, kwargs.get("basis", "computational")
            ),
            BridgeType.C_TO_B: lambda: self.execute_classical_to_biological(
                value, kwargs.get("threshold", 0.5)
            ),
            BridgeType.B_TO_C: lambda: self.execute_biological_to_classical(
                value, kwargs.get("threshold", 0.5)
            ),
            BridgeType.B_TO_Q: lambda: self.execute_biological_to_quantum(value),
            BridgeType.Q_TO_B: lambda: self.execute_quantum_to_biological(value),
        }

        if bridge_type in dispatch:
            return dispatch[bridge_type]()

        return {"error": f"Unknown bridge type: {bridge_type}"}

    def get_bridge_perturbation(self, bridge_type: BridgeType) -> float:
        """Get expected perturbation for bridge type.

        Π(B) = Π(M_i) + Π(T_ij) + Π(Write_j)
        """
        perturbations = {
            BridgeType.C_TO_Q: 0.0,  # Encoding is deterministic
            BridgeType.Q_TO_C: 1.0,  # Measurement collapses state
            BridgeType.C_TO_B: 0.05,  # Biological noise
            BridgeType.B_TO_C: 0.1,  # Assay noise
            BridgeType.B_TO_Q: 0.15,  # Combined noise
            BridgeType.Q_TO_B: 0.2,  # High uncertainty
        }
        return perturbations.get(bridge_type, 0.1)
