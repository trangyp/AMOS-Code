"""IMMUNE immune_system stub — Re-exports from 03_IMMUNE"""

import importlib.util
from pathlib import Path

# Load from 03_IMMUNE using importlib
_immune_path = Path(__file__).parent.parent / "03_IMMUNE" / "immune_system.py"
_spec = importlib.util.spec_from_file_location("_immune_sys", _immune_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ImmuneSystem = _mod.ImmuneSystem
SafetyPolicy = _mod.SafetyPolicy
AuditLog = _mod.AuditLog
ValidationResult = _mod.ValidationResult
RiskLevel = _mod.RiskLevel
ActionType = _mod.ActionType

__all__ = [
    "ImmuneSystem",
    "SafetyPolicy",
    "AuditLog",
    "ValidationResult",
    "RiskLevel",
    "ActionType",
]
