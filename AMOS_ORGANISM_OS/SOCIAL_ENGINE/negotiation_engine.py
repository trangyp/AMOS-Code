"""SOCIAL_ENGINE negotiation_engine stub — Re-exports from 10_SOCIAL_ENGINE"""

import sys
from pathlib import Path

social_path = Path(__file__).parent.parent / "10_SOCIAL_ENGINE"
if str(social_path) not in sys.path:
    sys.path.insert(0, str(social_path))

from negotiation_engine import NegotiationEngine, NegotiationResult, Proposal

__all__ = ["NegotiationEngine", "Proposal", "NegotiationResult"]
