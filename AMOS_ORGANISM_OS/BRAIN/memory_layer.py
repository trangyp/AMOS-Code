"""BRAIN memory_layer stub — Re-exports from 01_BRAIN"""

import importlib.util
from pathlib import Path

# Load from 01_BRAIN using importlib
_brain_path = Path(__file__).parent.parent / "01_BRAIN" / "memory_layer.py"
_spec = importlib.util.spec_from_file_location("_mem_layer", _brain_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
MemoryLayer = _mod.MemoryLayer
Memory = _mod.Memory

__all__ = ["MemoryLayer", "Memory"]
