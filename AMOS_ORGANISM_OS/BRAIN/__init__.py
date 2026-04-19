"""BRAIN module — Alias for 01_BRAIN

NOTE: This uses sys.path to access 01_BRAIN modules.
This is a transitional pattern until package structure is fully refactored.
"""

import sys
from pathlib import Path

# Add 01_BRAIN to path for module access (transitional pattern)
_01_BRAIN_PATH = Path(__file__).parent.parent / "01_BRAIN"
if str(_01_BRAIN_PATH) not in sys.path:
    sys.path.insert(0, str(_01_BRAIN_PATH))

from brain_os import BrainOS, BrainState, Plan, Thought, ThoughtType
from memory_layer import Memory, MemoryLayer
from router import RoutingDecision, SystemRouter

__all__ = [
    "BrainOS",
    "BrainState",
    "Thought",
    "Plan",
    "ThoughtType",
    "SystemRouter",
    "RoutingDecision",
    "MemoryLayer",
    "Memory",
]
