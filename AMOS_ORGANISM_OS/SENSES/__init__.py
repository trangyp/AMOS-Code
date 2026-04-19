"""SENSES module — Alias for 02_SENSES

NOTE: This uses sys.path to access 02_SENSES modules.
This is a transitional pattern until package structure is fully refactored.
"""

import sys
from pathlib import Path

# Add 02_SENSES to path for module access (transitional pattern)
_02_SENSES_PATH = Path(__file__).parent.parent / "02_SENSES"
if str(_02_SENSES_PATH) not in sys.path:
    sys.path.insert(0, str(_02_SENSES_PATH))

from context_gatherer import ContextGatherer, ContextSnapshot
from environment_scanner import EnvironmentScanner, FileChange, ScanResult
from signal_detector import Signal, SignalDetector

__all__ = [
    "EnvironmentScanner",
    "FileChange",
    "ScanResult",
    "ContextGatherer",
    "ContextSnapshot",
    "SignalDetector",
    "Signal",
]
