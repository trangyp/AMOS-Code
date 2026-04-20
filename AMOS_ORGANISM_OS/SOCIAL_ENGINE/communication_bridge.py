"""SOCIAL_ENGINE communication_bridge stub — Re-exports from 10_SOCIAL_ENGINE"""

import importlib.util
from pathlib import Path

# Load from 10_SOCIAL_ENGINE using importlib
_social_path = Path(__file__).parent.parent / "10_SOCIAL_ENGINE" / "communication_bridge.py"
_spec = importlib.util.spec_from_file_location("_comm_bridge", _social_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CommunicationBridge = _mod.CommunicationBridge
Message = _mod.Message
MessageType = _mod.MessageType

__all__ = ["CommunicationBridge", "Message", "MessageType"]
