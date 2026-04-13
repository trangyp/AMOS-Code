"""LEGAL_BRAIN risk_governor stub — Re-exports from 12_LEGAL_BRAIN"""
import sys
from pathlib import Path

legal_path = Path(__file__).parent.parent / "12_LEGAL_BRAIN"
if str(legal_path) not in sys.path:
    sys.path.insert(0, str(legal_path))

from risk_governor import RiskGovernor, RiskAssessment, RiskLevel

__all__ = ["RiskGovernor", "RiskAssessment", "RiskLevel"]
