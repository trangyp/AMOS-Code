"""SOCIAL_ENGINE agent_coordinator stub — Re-exports from 10_SOCIAL_ENGINE"""

import importlib.util
from pathlib import Path

# Load from 10_SOCIAL_ENGINE using importlib
_social_path = Path(__file__).parent.parent / "10_SOCIAL_ENGINE" / "agent_coordinator.py"
_spec = importlib.util.spec_from_file_location("_agent_coord", _social_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
AgentCoordinator = _mod.AgentCoordinator
AgentPool = _mod.AgentPool
AgentTask = _mod.AgentTask

__all__ = ["AgentCoordinator", "AgentPool", "AgentTask"]
