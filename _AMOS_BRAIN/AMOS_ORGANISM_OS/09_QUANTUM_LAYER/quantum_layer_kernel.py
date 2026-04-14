#!/usr/bin/env python3
"""AMOS Quantum Layer Kernel - 09_QUANTUM_LAYER Subsystem

Responsible for:
- Probabilistic computing and quantum-inspired algorithms
- Superposition state management (multiple possibilities)
- Uncertainty quantification and measurement
- Multi-path exploration and decision branching
- Quantum probability engine for decision making
"""

from __future__ import annotations

import json
import logging
import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos.quantum")


class QuantumState(Enum):
    """States of a quantum possibility."""

    SUPERPOSITION = auto()  # Multiple states simultaneously
    ENTANGLED = auto()  # Correlated with other qubits
    COLLAPSED = auto()  # Measured, definite state
    DECOHERED = auto()  # Lost quantum properties


@dataclass
class Qubit:
    """A quantum bit - represents a probabilistic state.
    Can be in superposition of 0 and 1 (or multiple values).
    """

    qubit_id: str
    amplitudes: dict[str, complex] = field(default_factory=dict)
    state: QuantumState = QuantumState.SUPERPOSITION
    entangled_with: list[str] = field(default_factory=list)
    created_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()

        # Normalize amplitudes
        if self.amplitudes:
            self._normalize()

    def _normalize(self):
        """Normalize probability amplitudes."""
        total_prob = sum(abs(a) ** 2 for a in self.amplitudes.values())
        if total_prob > 0:
            factor = 1.0 / math.sqrt(total_prob)
            for key in self.amplitudes:
                self.amplitudes[key] *= factor

    def get_probabilities(self) -> dict[str, float]:
        """Get measurement probabilities."""
        return {k: abs(v) ** 2 for k, v in self.amplitudes.items()}

    def measure(self) -> str:
        """Collapse superposition to definite state.
        Returns the measured value based on probabilities.
        """
        probs = self.get_probabilities()
        if not probs:
            return "unknown"

        # Weighted random selection
        total = sum(probs.values())
        r = random.random() * total
        cumulative = 0

        for value, prob in probs.items():
            cumulative += prob
            if r <= cumulative:
                self.state = QuantumState.COLLAPSED
                return value

        return list(probs.keys())[-1]


@dataclass
class Superposition:
    """A superposition of multiple possibilities."""

    superposition_id: str
    possibilities: dict[str, dict[str, Any]] = field(default_factory=dict)
    weights: dict[str, float] = field(default_factory=dict)
    coherence_time: float = 60.0  # Seconds before decoherence
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        self._normalize_weights()

    def _normalize_weights(self):
        """Normalize weights to sum to 1."""
        total = sum(self.weights.values())
        if total > 0:
            for key in self.weights:
                self.weights[key] /= total

    def add_possibility(self, id: str, data: dict[str, Any], weight: float = 1.0):
        """Add a possibility to the superposition."""
        self.possibilities[id] = data
        self.weights[id] = weight
        self._normalize_weights()

    def collapse(self) -> tuple[str, dict[str, Any]]:
        """Collapse to single possibility based on weights."""
        if not self.possibilities:
            return ("none", {})

        # Weighted random selection
        items = list(self.possibilities.items())
        weights = [self.weights.get(k, 1.0) for k, _ in items]
        total = sum(weights)

        if total == 0:
            return items[0]

        r = random.random() * total
        cumulative = 0

        for (key, value), weight in zip(items, weights):
            cumulative += weight
            if r <= cumulative:
                return (key, value)

        return items[-1]

    def get_most_probable(self) -> Optional[tuple[str, dict[str, Any]]]:
        """Get the highest probability possibility."""
        if not self.weights:
            return None

        max_key = max(self.weights.keys(), key=lambda k: self.weights[k])
        return (max_key, self.possibilities.get(max_key, {}))


@dataclass
class Uncertainty:
    """Uncertainty quantification for a variable."""

    mean: float
    variance: float
    confidence_interval: tuple[float, float]
    sample_size: int = 0
    distribution_type: str = "normal"  # normal, uniform, beta, etc.

    def get_confidence(self, level: float = 0.95) -> tuple[float, float]:
        """Get confidence interval at specified level."""
        # Simplified - assumes normal distribution
        z_score = 1.96 if level == 0.95 else 1.64 if level == 0.90 else 2.58
        margin = z_score * math.sqrt(self.variance)
        return (self.mean - margin, self.mean + margin)

    def is_significant(self, threshold: float = 0.05) -> bool:
        """Check if uncertainty is below threshold."""
        cv = math.sqrt(self.variance) / self.mean if self.mean != 0 else float("inf")
        return cv < threshold


class QuantumLayerKernel:
    """The Quantum Layer Kernel provides probabilistic computing capabilities
    inspired by quantum mechanics - superposition, uncertainty, and multi-path
    exploration.
    """

    def __init__(self, organism_root: Path):
        self.root = organism_root
        self.quantum_path = organism_root / "09_QUANTUM_LAYER"
        self.memory_path = self.quantum_path / "memory"
        self.logs_path = self.quantum_path / "logs"

        # Ensure directories
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Qubit registry
        self.qubits: dict[str, Qubit] = {}

        # Active superpositions
        self.superpositions: dict[str, Superposition] = {}

        # Uncertainty tracking
        self.uncertainties: dict[str, Uncertainty] = {}

        # Entanglement graph
        self.entanglements: dict[str, set[str]] = defaultdict(set)

        # Statistics
        self.stats = {
            "qubits_created": 0,
            "measurements_performed": 0,
            "superpositions_resolved": 0,
            "uncertainties_quantified": 0,
        }

        logger.info(f"QuantumLayerKernel initialized at {self.quantum_path}")

    def create_qubit(
        self,
        qubit_id: Optional[str] = None,
        initial_state: Optional[dict[str, complex]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> Qubit:
        """Create a new qubit in superposition."""
        if qubit_id is None:
            qubit_id = f"qubit_{len(self.qubits)}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        amplitudes = initial_state or {"0": 1.0, "1": 1.0}

        qubit = Qubit(
            qubit_id=qubit_id,
            amplitudes=amplitudes,
            state=QuantumState.SUPERPOSITION,
            metadata=metadata or {},
        )

        self.qubits[qubit_id] = qubit
        self.stats["qubits_created"] += 1

        logger.debug(f"Created qubit: {qubit_id}")
        return qubit

    def entangle(self, qubit_id1: str, qubit_id2: str) -> bool:
        """Create quantum entanglement between two qubits."""
        if qubit_id1 not in self.qubits or qubit_id2 not in self.qubits:
            return False

        self.entanglements[qubit_id1].add(qubit_id2)
        self.entanglements[qubit_id2].add(qubit_id1)

        self.qubits[qubit_id1].entangled_with.append(qubit_id2)
        self.qubits[qubit_id1].state = QuantumState.ENTANGLED
        self.qubits[qubit_id2].entangled_with.append(qubit_id1)
        self.qubits[qubit_id2].state = QuantumState.ENTANGLED

        logger.debug(f"Entangled: {qubit_id1} <-> {qubit_id2}")
        return True

    def measure(self, qubit_id: str) -> str:
        """Measure a qubit, collapsing its superposition."""
        if qubit_id not in self.qubits:
            return "unknown"

        qubit = self.qubits[qubit_id]
        result = qubit.measure()

        # If entangled, collapse entangled qubits too
        if qubit.state == QuantumState.COLLAPSED:
            for entangled_id in qubit.entangled_with:
                if entangled_id in self.qubits:
                    self.qubits[entangled_id].state = QuantumState.COLLAPSED

        self.stats["measurements_performed"] += 1
        logger.debug(f"Measured {qubit_id}: {result}")
        return result

    def create_superposition(
        self, superposition_id: Optional[str] = None, coherence_time: float = 60.0
    ) -> Superposition:
        """Create a new superposition container."""
        if superposition_id is None:
            superposition_id = (
                f"super_{len(self.superpositions)}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            )

        superposition = Superposition(
            superposition_id=superposition_id, coherence_time=coherence_time
        )

        self.superpositions[superposition_id] = superposition
        return superposition

    def add_to_superposition(
        self, superposition_id: str, possibility_id: str, data: dict[str, Any], weight: float = 1.0
    ) -> bool:
        """Add a possibility to a superposition."""
        if superposition_id not in self.superpositions:
            return False

        self.superpositions[superposition_id].add_possibility(possibility_id, data, weight)
        return True

    def collapse_superposition(self, superposition_id: str) -> tuple[str, dict[str, Any]]:
        """Collapse superposition to single outcome."""
        if superposition_id not in self.superpositions:
            return ("none", {})

        result = self.superpositions[superposition_id].collapse()
        self.stats["superpositions_resolved"] += 1

        logger.info(f"Collapsed superposition {superposition_id}: {result[0]}")
        return result

    def quantify_uncertainty(
        self, variable_id: str, samples: list[float], distribution_type: str = "normal"
    ) -> Uncertainty:
        """Quantify uncertainty from sample data."""
        if not samples:
            uncertainty = Uncertainty(
                mean=0.0,
                variance=1.0,
                confidence_interval=(-1.96, 1.96),
                sample_size=0,
                distribution_type=distribution_type,
            )
        else:
            n = len(samples)
            mean = sum(samples) / n
            variance = sum((x - mean) ** 2 for x in samples) / n
            std_dev = math.sqrt(variance)

            uncertainty = Uncertainty(
                mean=mean,
                variance=variance,
                confidence_interval=(mean - 1.96 * std_dev, mean + 1.96 * std_dev),
                sample_size=n,
                distribution_type=distribution_type,
            )

        self.uncertainties[variable_id] = uncertainty
        self.stats["uncertainties_quantified"] += 1

        return uncertainty

    def get_uncertainty(self, variable_id: str) -> Optional[Uncertainty]:
        """Get uncertainty for a variable."""
        return self.uncertainties.get(variable_id)

    def explore_paths(
        self, initial_state: dict[str, Any], decision_points: list[dict[str, Any]], depth: int = 3
    ) -> list[dict[str, Any]]:
        """Multi-path exploration - explore multiple decision branches simultaneously.
        Returns list of possible paths with probabilities.
        """
        paths = []

        def explore_recursive(current_state, decisions_remaining, current_path, probability):
            if not decisions_remaining or len(current_path) >= depth:
                paths.append(
                    {
                        "path": current_path.copy(),
                        "final_state": current_state,
                        "probability": probability,
                    }
                )
                return

            decision = decisions_remaining[0]
            options = decision.get("options", [])

            for option in options:
                option_prob = option.get("probability", 1.0 / len(options))
                new_state = {**current_state, **option.get("effects", {})}
                new_path = current_path + [option.get("id", "unknown")]

                explore_recursive(
                    new_state, decisions_remaining[1:], new_path, probability * option_prob
                )

        explore_recursive(initial_state, decision_points, [], 1.0)

        # Normalize probabilities
        total_prob = sum(p["probability"] for p in paths)
        if total_prob > 0:
            for p in paths:
                p["probability"] /= total_prob

        logger.info(f"Explored {len(paths)} possible paths")
        return paths

    def quantum_decision(
        self, options: list[dict[str, Any]], context: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make a decision using quantum probability.
        Creates superposition of options, then collapses based on context.
        """
        if not options:
            return {"error": "No options provided"}

        # Create superposition of options
        superposition_id = f"decision_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        superposition = self.create_superposition(superposition_id)

        # Add each option as a possibility
        for option in options:
            option_id = option.get("id", f"opt_{len(superposition.possibilities)}")
            weight = option.get("score", 0.5) * option.get("confidence", 0.5)

            self.add_to_superposition(superposition_id, option_id, option, weight)

        # Collapse to decision
        selected_id, selected_data = self.collapse_superposition(superposition_id)

        return {
            "selected_id": selected_id,
            "selected_option": selected_data,
            "superposition_id": superposition_id,
            "total_options": len(options),
            "probability": superposition.weights.get(selected_id, 0),
        }

    def get_state(self) -> dict[str, Any]:
        """Get current quantum layer state."""
        superposition_states = {}
        for sid, sup in self.superpositions.items():
            superposition_states[sid] = {
                "possibilities": len(sup.possibilities),
                "most_probable": sup.get_most_probable()[0] if sup.get_most_probable() else None,
            }

        return {
            "qubits_active": len(
                [q for q in self.qubits.values() if q.state == QuantumState.SUPERPOSITION]
            ),
            "qubits_measured": len(
                [q for q in self.qubits.values() if q.state == QuantumState.COLLAPSED]
            ),
            "qubits_entangled": len(
                [q for q in self.qubits.values() if q.state == QuantumState.ENTANGLED]
            ),
            "superpositions_active": len(self.superpositions),
            "uncertainties_tracked": len(self.uncertainties),
            "total_qubits": len(self.qubits),
            "qubits_created": self.stats["qubits_created"],
            "measurements": self.stats["measurements_performed"],
            "superpositions_resolved": self.stats["superpositions_resolved"],
            "timestamp": datetime.utcnow().isoformat(),
        }


if __name__ == "__main__":
    # Test the quantum layer kernel
    root = Path(__file__).parent.parent
    quantum = QuantumLayerKernel(root)

    print("Quantum Layer State (initial):")
    print(json.dumps(quantum.get_state(), indent=2))

    print("\n=== Test 1: Create qubits ===")
    q1 = quantum.create_qubit("test_qubit_1", {"0": 0.7, "1": 0.7})
    q2 = quantum.create_qubit("test_qubit_2", {"A": 0.5, "B": 0.5, "C": 0.5})
    print(f"Created qubits: {q1.qubit_id}, {q2.qubit_id}")
    print(f"Q1 probabilities: {q1.get_probabilities()}")

    print("\n=== Test 2: Entangle qubits ===")
    quantum.entangle(q1.qubit_id, q2.qubit_id)
    print(f"Q1 entangled with: {q1.entangled_with}")

    print("\n=== Test 3: Measure qubit ===")
    result = quantum.measure(q1.qubit_id)
    print(f"Measured q1: {result}")
    print(f"Q1 state: {q1.state.name}")
    print(f"Q2 state (entangled): {q2.state.name}")

    print("\n=== Test 4: Create superposition ===")
    superposition = quantum.create_superposition("test_super")
    superposition.add_possibility("option_A", {"value": 10, "risk": "low"}, 0.6)
    superposition.add_possibility("option_B", {"value": 20, "risk": "high"}, 0.4)
    print(f"Superposition created with {len(superposition.possibilities)} options")
    print(f"Weights: {superposition.weights}")

    print("\n=== Test 5: Collapse superposition ===")
    selected_id, selected_data = quantum.collapse_superposition("test_super")
    print(f"Selected: {selected_id}")
    print(f"Data: {selected_data}")

    print("\n=== Test 6: Quantify uncertainty ===")
    samples = [0.5, 0.6, 0.55, 0.7, 0.45, 0.6, 0.65, 0.5]
    uncertainty = quantum.quantify_uncertainty("test_variable", samples)
    print(f"Mean: {uncertainty.mean:.3f}")
    print(f"Variance: {uncertainty.variance:.6f}")
    print(f"95% CI: {uncertainty.confidence_interval}")

    print("\n=== Test 7: Multi-path exploration ===")
    initial = {"position": "start", "resources": 100}
    decisions = [
        {
            "options": [
                {"id": "path_A", "probability": 0.6, "effects": {"position": "A"}},
                {"id": "path_B", "probability": 0.4, "effects": {"position": "B"}},
            ]
        },
        {
            "options": [
                {"id": "continue", "probability": 0.7, "effects": {"resources": 80}},
                {"id": "retreat", "probability": 0.3, "effects": {"resources": 90}},
            ]
        },
    ]
    paths = quantum.explore_paths(initial, decisions, depth=2)
    print(f"Explored {len(paths)} paths")
    for p in paths[:3]:  # Show first 3
        print(f"  Path: {p['path']}, Prob: {p['probability']:.3f}")

    print("\n=== Test 8: Quantum decision ===")
    options = [
        {"id": "action_1", "score": 0.8, "confidence": 0.9, "description": "Safe option"},
        {"id": "action_2", "score": 0.9, "confidence": 0.6, "description": "Risky option"},
        {"id": "action_3", "score": 0.7, "confidence": 0.8, "description": "Balanced option"},
    ]
    decision = quantum.quantum_decision(options)
    print(f"Decision: {decision['selected_id']}")
    print(f"Selected option: {decision['selected_option'].get('description')}")

    print("\nFinal State:")
    print(json.dumps(quantum.get_state(), indent=2))
