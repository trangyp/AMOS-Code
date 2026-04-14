"""SOCIAL_ENGINE module — Alias for 10_SOCIAL_ENGINE"""

import sys
from pathlib import Path

social_path = Path(__file__).parent.parent / "10_SOCIAL_ENGINE"
if str(social_path) not in sys.path:
    sys.path.insert(0, str(social_path))

from agent_coordinator import AgentCoordinator, AgentPool, AgentTask
from communication_bridge import CommunicationBridge, Message, MessageType
from human_interface import HumanInterface, InteractionMode
from negotiation_engine import NegotiationEngine, NegotiationResult, Proposal

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
