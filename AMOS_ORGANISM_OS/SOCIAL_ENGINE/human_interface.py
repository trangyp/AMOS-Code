"""SOCIAL_ENGINE human_interface stub — Re-exports from 10_SOCIAL_ENGINE"""

import importlib.util
from pathlib import Path

# Load from 10_SOCIAL_ENGINE using importlib
_social_path = Path(__file__).parent.parent / "10_SOCIAL_ENGINE" / "human_interface.py"
_spec = importlib.util.spec_from_file_location("_human_intf", _social_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
HumanInterface = _mod.HumanInterface
InteractionMode = _mod.InteractionMode

__all__ = ["HumanInterface", "InteractionMode"]
