"""BRAIN brain_os stub — Re-exports from 01_BRAIN"""

import importlib.util
from pathlib import Path

# Load from 01_BRAIN using importlib
_brain_path = Path(__file__).parent.parent / "01_BRAIN" / "brain_os.py"
_spec = importlib.util.spec_from_file_location("_brain_os", _brain_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BrainOS = _mod.BrainOS
BrainState = _mod.BrainState
Plan = _mod.Plan
Thought = _mod.Thought
ThoughtType = _mod.ThoughtType

__all__ = ["BrainOS", "BrainState", "Thought", "Plan", "ThoughtType"]
