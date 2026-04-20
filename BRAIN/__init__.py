"""BRAIN alias module for AMOS_ORGANISM_OS.01_BRAIN

This module provides alias imports for the BRAIN subsystem.
"""

import sys
from pathlib import Path

# Add the actual subsystem to path
subsystem_path = Path(__file__).parent.parent / "AMOS_ORGANISM_OS" / "01_BRAIN"
if str(subsystem_path) not in sys.path:
    sys.path.insert(0, str(subsystem_path))

# Export all from the actual module
try:
    from brain_os import *
    from cognitive_engine_activator import *
    from router import *
except ImportError:
    pass
