"""
BRAIN module — Alias for 01_BRAIN
"""

# Re-export from 01_BRAIN
import sys
from pathlib import Path

# Add 01_BRAIN to path
brain_path = Path(__file__).parent.parent / "01_BRAIN"
if str(brain_path) not in sys.path:
    sys.path.insert(0, str(brain_path))

# Import and re-export
from brain_os import BrainOS, BrainState, Thought, Plan, ThoughtType
from router import SystemRouter, RoutingDecision
from memory_layer import MemoryLayer, Memory

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
