"""QUANTUM_LAYER module — Alias for 09_QUANTUM_LAYER"""

import sys
from pathlib import Path

quantum_path = Path(__file__).parent.parent / "09_QUANTUM_LAYER"
if str(quantum_path) not in sys.path:
    sys.path.insert(0, str(quantum_path))

from decision_optimizer import Decision, DecisionOptimizer, DecisionOutcome, get_decision_optimizer
from monte_carlo import MonteCarloSimulator, SimulationResult, get_monte_carlo_simulator
from quantum_router import QuantumRouter, RouteDecision, get_quantum_router
from scenario_engine import Scenario, ScenarioEngine, ScenarioResult, get_scenario_engine

__all__ = [
    "ScenarioEngine",
    "Scenario",
    "ScenarioResult",
    "get_scenario_engine",
    "MonteCarloSimulator",
    "SimulationResult",
    "get_monte_carlo_simulator",
    "DecisionOptimizer",
    "Decision",
    "DecisionOutcome",
    "get_decision_optimizer",
    "QuantumRouter",
    "RouteDecision",
    "get_quantum_router",
]
