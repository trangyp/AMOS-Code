# Stub to re-export from 01_BRAIN
import sys
from pathlib import Path

brain_path = Path(__file__).parent.parent / "01_BRAIN"
if str(brain_path) not in sys.path:
    sys.path.insert(0, str(brain_path))

from memory_layer import MemoryLayer, Memory

__all__ = ["MemoryLayer", "Memory"]
