"""QUANTUM_LAYER quantum_router stub — Re-exports from 09_QUANTUM_LAYER"""
import sys
from pathlib import Path

quantum_path = Path(__file__).parent.parent / "09_QUANTUM_LAYER"
if str(quantum_path) not in sys.path:
    sys.path.insert(0, str(quantum_path))

from quantum_router import QuantumRouter, RouteDecision, get_quantum_router

__all__ = ["QuantumRouter", "RouteDecision", "get_quantum_router"]
