"""QUANTUM_LAYER alias module for AMOS_ORGANISM_OS.12_QUANTUM_LAYER

This module provides alias imports for the QUANTUM_LAYER subsystem.
"""

import sys
from pathlib import Path

# Add the actual subsystem to path
subsystem_path = Path(__file__).parent.parent / "AMOS_ORGANISM_OS" / "12_QUANTUM_LAYER"
if str(subsystem_path) not in sys.path:
    sys.path.insert(0, str(subsystem_path))

# Export all from the actual module
try:
    from predictive_engine import *
except ImportError:
    pass
