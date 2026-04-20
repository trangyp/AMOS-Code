"""SOCIAL_ENGINE negotiation_engine stub — Re-exports from 10_SOCIAL_ENGINE"""

import importlib.util
from pathlib import Path

# Load from 10_SOCIAL_ENGINE using importlib
_social_path = Path(__file__).parent.parent / "10_SOCIAL_ENGINE" / "negotiation_engine.py"
_spec = importlib.util.spec_from_file_location("_nego_eng", _social_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
NegotiationEngine = _mod.NegotiationEngine
NegotiationResult = _mod.NegotiationResult
Proposal = _mod.Proposal

__all__ = ["NegotiationEngine", "NegotiationResult", "Proposal"]
