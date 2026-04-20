"""SENSES module — Alias for 02_SENSES"""

import importlib.util
from pathlib import Path

# Load modules from 02_SENSES using importlib
_02_SENSES_PATH = Path(__file__).parent.parent / "02_SENSES"

# context_gatherer
_spec_cg = importlib.util.spec_from_file_location(
    "_ctx_gather", _02_SENSES_PATH / "context_gatherer.py"
)
_mod_cg = importlib.util.module_from_spec(_spec_cg)
_spec_cg.loader.exec_module(_mod_cg)
ContextGatherer = _mod_cg.ContextGatherer
ContextSnapshot = _mod_cg.ContextSnapshot

# environment_scanner
_spec_es = importlib.util.spec_from_file_location(
    "_env_scan", _02_SENSES_PATH / "environment_scanner.py"
)
_mod_es = importlib.util.module_from_spec(_spec_es)
_spec_es.loader.exec_module(_mod_es)
EnvironmentScanner = _mod_es.EnvironmentScanner
FileChange = _mod_es.FileChange
ScanResult = _mod_es.ScanResult

# signal_detector
_spec_sd = importlib.util.spec_from_file_location(
    "_sig_det", _02_SENSES_PATH / "signal_detector.py"
)
_mod_sd = importlib.util.module_from_spec(_spec_sd)
_spec_sd.loader.exec_module(_mod_sd)
Signal = _mod_sd.Signal
SignalDetector = _mod_sd.SignalDetector

__all__ = [
    "EnvironmentScanner",
    "FileChange",
    "ScanResult",
    "ContextGatherer",
    "ContextSnapshot",
    "SignalDetector",
    "Signal",
]
