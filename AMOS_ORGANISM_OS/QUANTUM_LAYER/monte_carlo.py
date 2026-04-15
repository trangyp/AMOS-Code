"""QUANTUM_LAYER monte_carlo stub — Re-exports from 09_QUANTUM_LAYER"""

import sys
from pathlib import Path

quantum_path = Path(__file__).parent.parent / "09_QUANTUM_LAYER"
if str(quantum_path) not in sys.path:
    sys.path.insert(0, str(quantum_path))

from monte_carlo import MonteCarloSimulator, SimulationResult, get_monte_carlo_simulator

__all__ = ["MonteCarloSimulator", "SimulationResult", "get_monte_carlo_simulator"]
