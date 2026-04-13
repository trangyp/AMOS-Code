"""
02_SENSES — Environment, context, signal detection subsystem.

The sensory system of AMOS. Scans filesystem, detects changes,
monitors environment, and gathers context for the brain.
"""

from .environment_scanner import EnvironmentScanner, FileChange
from .context_gatherer import ContextGatherer, ContextSnapshot
from .signal_detector import SignalDetector, Signal

__all__ = [
    "EnvironmentScanner",
    "FileChange",
    "ContextGatherer",
    "ContextSnapshot",
    "SignalDetector",
    "Signal",
]
