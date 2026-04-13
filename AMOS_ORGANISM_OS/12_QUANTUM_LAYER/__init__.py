"""
12_QUANTUM_LAYER — Probabilistic timing and decision layer

The quantum substrate of AMOS. Manages superposition states,
probabilistic decisions, uncertainty quantification, and
timing/synchronicity flows.

Role: Timing, probability flows, synchronicities, collapse logic
Kernel refs: AMOS_Vn_Quantum_Engine, PROBABILITY_KERNEL, TIMING_KERNEL

Owner: Trang
Version: 1.0.0
"""

from .superposition_manager import SuperpositionManager, SuperpositionState, get_superposition_manager
from .probability_engine import ProbabilityEngine, ProbabilityDistribution, get_probability_engine
from .timing_synchronizer import TimingSynchronizer, SynchronicityEvent, get_timing_synchronizer
from .quantum_decision_engine import QuantumDecisionEngine, DecisionPath, get_quantum_decision_engine

__all__ = [
    # Superposition
    "SuperpositionManager", "SuperpositionState", "get_superposition_manager",
    # Probability
    "ProbabilityEngine", "ProbabilityDistribution", "get_probability_engine",
    # Timing
    "TimingSynchronizer", "SynchronicityEvent", "get_timing_synchronizer",
    # Decisions
    "QuantumDecisionEngine", "DecisionPath", "get_quantum_decision_engine",
]
