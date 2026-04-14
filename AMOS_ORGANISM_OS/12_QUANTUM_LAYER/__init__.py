"""12_QUANTUM_LAYER — Probabilistic timing and decision layer

The quantum substrate of AMOS. Manages superposition states,
probabilistic decisions, uncertainty quantification, and
timing/synchronicity flows.

Role: Timing, probability flows, synchronicities, collapse logic
Kernel refs: AMOS_Vn_Quantum_Engine, PROBABILITY_KERNEL, TIMING_KERNEL

Owner: Trang
Version: 1.0.0
"""

from .probability_engine import ProbabilityDistribution, ProbabilityEngine, get_probability_engine
from .quantum_decision_engine import (
    DecisionPath,
    QuantumDecisionEngine,
    get_quantum_decision_engine,
)
from .superposition_manager import (
    SuperpositionManager,
    SuperpositionState,
    get_superposition_manager,
)
from .timing_synchronizer import SynchronicityEvent, TimingSynchronizer, get_timing_synchronizer

__all__ = [
    # Superposition
    "SuperpositionManager",
    "SuperpositionState",
    "get_superposition_manager",
    # Probability
    "ProbabilityEngine",
    "ProbabilityDistribution",
    "get_probability_engine",
    # Timing
    "TimingSynchronizer",
    "SynchronicityEvent",
    "get_timing_synchronizer",
    # Decisions
    "QuantumDecisionEngine",
    "DecisionPath",
    "get_quantum_decision_engine",
]
