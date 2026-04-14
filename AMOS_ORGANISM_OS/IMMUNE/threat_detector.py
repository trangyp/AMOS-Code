# Stub to re-export from 03_IMMUNE
import sys
from pathlib import Path

immune_path = Path(__file__).parent.parent / "03_IMMUNE"
if str(immune_path) not in sys.path:
    sys.path.insert(0, str(immune_path))

from threat_detector import Threat, ThreatDetector

__all__ = ["ThreatDetector", "Threat"]
