"""
09_SOCIAL_ENGINE — Social Interaction & Knowledge Sharing

The social nervous system of AMOS.
Handles messaging, collaboration, and knowledge exchange.

Role: Social interaction, knowledge sharing, external communication
Kernel refs: SOCIAL_KERNEL, MESSAGING_KERNEL

Owner: Trang
Version: 1.0.0
"""

from .social_engine import (
    SocialEngine, Message, SocialConnection, KnowledgeShare,
    get_social_engine,
)

__all__ = [
    "SocialEngine",
    "Message",
    "SocialConnection",
    "KnowledgeShare",
    "get_social_engine",
]
