"""IMMUNE alias module for AMOS_ORGANISM_OS.03_IMMUNE

This module provides alias imports for the IMMUNE subsystem.
"""

import sys
from pathlib import Path

# Add the actual subsystem to path
subsystem_path = Path(__file__).parent.parent / "AMOS_ORGANISM_OS" / "03_IMMUNE"
if str(subsystem_path) not in sys.path:
    sys.path.insert(0, str(subsystem_path))

# Export all from the actual module
try:
    from immune_system import *

    from alert_manager import *
except ImportError:
    pass
