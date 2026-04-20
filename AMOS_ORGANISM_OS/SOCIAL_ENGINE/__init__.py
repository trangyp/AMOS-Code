"""SOCIAL_ENGINE module — Alias for 10_SOCIAL_ENGINE"""

import importlib.util
from pathlib import Path

# Load modules from 10_SOCIAL_ENGINE using importlib
_10_SOCIAL_PATH = Path(__file__).parent.parent / "10_SOCIAL_ENGINE"

# agent_coordinator
_spec_ac = importlib.util.spec_from_file_location(
    "_agent_coord", _10_SOCIAL_PATH / "agent_coordinator.py"
)
_mod_ac = importlib.util.module_from_spec(_spec_ac)
_spec_ac.loader.exec_module(_mod_ac)
AgentCoordinator = _mod_ac.AgentCoordinator
AgentPool = _mod_ac.AgentPool
AgentTask = _mod_ac.AgentTask

# communication_bridge
_spec_cb = importlib.util.spec_from_file_location(
    "_comm_bridge", _10_SOCIAL_PATH / "communication_bridge.py"
)
_mod_cb = importlib.util.module_from_spec(_spec_cb)
_spec_cb.loader.exec_module(_mod_cb)
CommunicationBridge = _mod_cb.CommunicationBridge
Message = _mod_cb.Message
MessageType = _mod_cb.MessageType

# human_interface
_spec_hi = importlib.util.spec_from_file_location(
    "_human_intf", _10_SOCIAL_PATH / "human_interface.py"
)
_mod_hi = importlib.util.module_from_spec(_spec_hi)
_spec_hi.loader.exec_module(_mod_hi)
HumanInterface = _mod_hi.HumanInterface
InteractionMode = _mod_hi.InteractionMode

# negotiation_engine
_spec_ne = importlib.util.spec_from_file_location(
    "_nego_eng", _10_SOCIAL_PATH / "negotiation_engine.py"
)
_mod_ne = importlib.util.module_from_spec(_spec_ne)
_spec_ne.loader.exec_module(_mod_ne)
NegotiationEngine = _mod_ne.NegotiationEngine
NegotiationResult = _mod_ne.NegotiationResult
Proposal = _mod_ne.Proposal

__all__ = [
    "AgentCoordinator",
    "AgentPool",
    "AgentTask",
    "CommunicationBridge",
    "Message",
    "MessageType",
    "HumanInterface",
    "InteractionMode",
    "NegotiationEngine",
    "Proposal",
    "NegotiationResult",
]
