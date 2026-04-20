"""KNOWLEDGE_CORE alias module for AMOS Knowledge Core subsystem."""

import sys
from pathlib import Path

# Get the organism root (parent of AMOS_ORGANISM_OS)
ORGANISM_ROOT = Path(__file__).resolve().parent.parent / "AMOS_ORGANISM_OS"

# Add the actual subsystem paths
_subsystem_paths = [
    ORGANISM_ROOT / "15_KNOWLEDGE_CORE",
]

for _path in _subsystem_paths:
    if _path.exists() and str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

# This allows: from KNOWLEDGE_CORE import feature_registry
# Which maps to: AMOS_ORGANISM_OS/15_KNOWLEDGE_CORE/feature_registry.py
