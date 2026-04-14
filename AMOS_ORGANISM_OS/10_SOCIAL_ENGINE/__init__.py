"""10_SOCIAL_ENGINE — Multi-Agent Coordination & Communication
==========================================================

The social interaction layer of AMOS.
Handles multi-agent coordination, external communication,
human interaction, and negotiation protocols.

Role: Multi-agent coordination, external communication, social interaction
Kernel refs: SOCIAL_KERNEL, COMMUNICATION_KERNEL, NEGOTIATION_KERNEL

Owner: Trang
Version: 1.0.0
"""

from .agent_coordinator import AgentCoordinator, AgentPool, AgentTask
from .communication_bridge import CommunicationBridge, Message, MessageType
from .human_interface import HumanInterface, InteractionMode
from .negotiation_engine import NegotiationEngine, NegotiationResult, Proposal

__all__ = [
    # Agent coordination
    "AgentCoordinator",
    "AgentPool",
    "AgentTask",
    # Communication
    "CommunicationBridge",
    "Message",
    "MessageType",
    # Human interface
    "HumanInterface",
    "InteractionMode",
    # Negotiation
    "NegotiationEngine",
    "Proposal",
    "NegotiationResult",
]
