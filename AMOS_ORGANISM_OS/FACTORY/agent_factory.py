"""FACTORY agent_factory stub — Re-exports from 13_FACTORY"""

import importlib.util
from pathlib import Path

# Load from 13_FACTORY using importlib
_factory_path = Path(__file__).parent.parent / "13_FACTORY" / "agent_factory.py"
_spec = importlib.util.spec_from_file_location("_agent_fact", _factory_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
AgentFactory = _mod.AgentFactory
AgentInstance = _mod.AgentInstance
AgentSpec = _mod.AgentSpec

__all__ = ["AgentFactory", "AgentSpec", "AgentInstance"]
