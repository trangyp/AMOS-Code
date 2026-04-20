"""METABOLISM alias module for AMOS_ORGANISM_OS.07_METABOLISM

This module provides alias imports for the METABOLISM subsystem.
"""

import sys
from pathlib import Path

# Add the actual subsystem to path
subsystem_path = Path(__file__).parent.parent / "AMOS_ORGANISM_OS" / "07_METABOLISM"
if str(subsystem_path) not in sys.path:
    sys.path.insert(0, str(subsystem_path))

# Export all from the actual module
try:
    from pipeline_engine import *
except ImportError:
    pass
