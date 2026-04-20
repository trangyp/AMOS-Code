"""IMMUNE module — Alias for 03_IMMUNE"""

import importlib.util
from pathlib import Path

# Load modules from 03_IMMUNE using importlib
_03_IMMUNE_PATH = Path(__file__).parent.parent / "03_IMMUNE"

# compliance_engine
_spec_ce = importlib.util.spec_from_file_location(
    "_comp_eng", _03_IMMUNE_PATH / "compliance_engine.py"
)
_mod_ce = importlib.util.module_from_spec(_spec_ce)
_spec_ce.loader.exec_module(_mod_ce)
ComplianceEngine = _mod_ce.ComplianceEngine
ComplianceRule = _mod_ce.ComplianceRule

# immune_system
_spec_is = importlib.util.spec_from_file_location(
    "_immune_sys", _03_IMMUNE_PATH / "immune_system.py"
)
_mod_is = importlib.util.module_from_spec(_spec_is)
_spec_is.loader.exec_module(_mod_is)
ImmuneSystem = _mod_is.ImmuneSystem
SafetyPolicy = _mod_is.SafetyPolicy
AuditLog = _mod_is.AuditLog
RiskLevel = _mod_is.RiskLevel
ActionType = _mod_is.ActionType

# threat_detector
_spec_td = importlib.util.spec_from_file_location(
    "_threat_det", _03_IMMUNE_PATH / "threat_detector.py"
)
_mod_td = importlib.util.module_from_spec(_spec_td)
_spec_td.loader.exec_module(_mod_td)
ThreatDetector = _mod_td.ThreatDetector
Threat = _mod_td.Threat

__all__ = [
    "ImmuneSystem",
    "SafetyPolicy",
    "AuditLog",
    "RiskLevel",
    "ActionType",
    "ThreatDetector",
    "Threat",
    "ComplianceEngine",
    "ComplianceRule",
]
