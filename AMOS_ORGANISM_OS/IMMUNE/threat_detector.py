"""IMMUNE threat_detector stub — Re-exports from 03_IMMUNE"""

import importlib.util
from pathlib import Path

# Load from 03_IMMUNE using importlib
_immune_path = Path(__file__).parent.parent / "03_IMMUNE" / "threat_detector.py"
_spec = importlib.util.spec_from_file_location("_threat_det", _immune_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ThreatDetector = _mod.ThreatDetector
Threat = _mod.Threat

__all__ = ["ThreatDetector", "Threat"]
