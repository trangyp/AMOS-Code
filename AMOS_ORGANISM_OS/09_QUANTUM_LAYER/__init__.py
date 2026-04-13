"""
09_QUANTUM_LAYER — Decision Optimization Engine
=================================================

The quantum decision layer of AMOS.
Handles parallel scenario evaluation, Monte Carlo simulation,
and decision optimization before action execution.

Role: Decision optimization - scenarios, simulation, risk analysis
Kernel refs: QUANTUM_KERNEL, DECISION_KERNEL

Owner: Trang
Version: 1.0.0
"""

from .scenario_engine import ScenarioEngine, Scenario, ScenarioResult
from .monte_carlo import MonteCarloSimulator, SimulationResult
from .decision_optimizer import DecisionOptimizer, Decision, DecisionOutcome
from .quantum_router import QuantumRouter, RouteDecision

__all__ = [
    # Scenario engine
    "ScenarioEngine",
    "Scenario",
    "ScenarioResult",
    # Monte Carlo simulation
    "MonteCarloSimulator",
    "SimulationResult",
    # Decision optimization
    "DecisionOptimizer",
    "Decision",
    "DecisionOutcome",
    # Quantum routing
    "QuantumRouter",
    "RouteDecision",
]
