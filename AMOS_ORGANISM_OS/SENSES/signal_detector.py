"""SENSES signal_detector stub — Re-exports from 02_SENSES"""

import importlib.util
from pathlib import Path

# Load from 02_SENSES using importlib
_senses_path = Path(__file__).parent.parent / "02_SENSES" / "signal_detector.py"
_spec = importlib.util.spec_from_file_location("_sig_det", _senses_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
SignalDetector = _mod.SignalDetector
Signal = _mod.Signal

__all__ = ["SignalDetector", "Signal"]
