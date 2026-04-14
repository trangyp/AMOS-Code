# Stub to re-export from 02_SENSES
import sys
from pathlib import Path

senses_path = Path(__file__).parent.parent / "02_SENSES"
if str(senses_path) not in sys.path:
    sys.path.insert(0, str(senses_path))

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
