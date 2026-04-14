"""02_SENSES — Environment, context, signal detection subsystem.

The sensory system of AMOS. Scans filesystem, detects changes,
monitors environment, and gathers context for the brain.
"""

from .context_gatherer import ContextGatherer, ContextSnapshot
from .environment_scanner import EnvironmentScanner, FileChange
from .signal_detector import Signal, SignalDetector

__all__ = [
    "EnvironmentScanner",
    "FileChange",
    "ContextGatherer",
    "ContextSnapshot",
    "SignalDetector",
    "Signal",
]
