"""QUANTUM_LAYER scenario_engine stub — Re-exports from 09_QUANTUM_LAYER"""

import importlib.util
from pathlib import Path

# Load from 09_QUANTUM_LAYER using importlib
_quantum_path = Path(__file__).parent.parent / "09_QUANTUM_LAYER" / "scenario_engine.py"
_spec = importlib.util.spec_from_file_location("_quantum_scenario", _quantum_path)
_quantum_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_quantum_mod)

Scenario = _quantum_mod.Scenario
ScenarioEngine = _quantum_mod.ScenarioEngine
ScenarioResult = _quantum_mod.ScenarioResult
get_scenario_engine = _quantum_mod.get_scenario_engine

__all__ = ["ScenarioEngine", "Scenario", "ScenarioResult", "get_scenario_engine"]
