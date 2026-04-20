"""IMMUNE compliance_engine stub — Re-exports from 03_IMMUNE"""

import importlib.util
from pathlib import Path

# Load from 03_IMMUNE using importlib
_immune_path = Path(__file__).parent.parent / "03_IMMUNE" / "compliance_engine.py"
_spec = importlib.util.spec_from_file_location("_comp_eng", _immune_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ComplianceEngine = _mod.ComplianceEngine
ComplianceRule = _mod.ComplianceRule

__all__ = ["ComplianceEngine", "ComplianceRule"]
