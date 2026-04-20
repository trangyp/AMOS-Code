"""FACTORY quality_checker stub — Re-exports from 13_FACTORY"""

import importlib.util
from pathlib import Path

# Load from 13_FACTORY using importlib
_factory_path = Path(__file__).parent.parent / "13_FACTORY" / "quality_checker.py"
_spec = importlib.util.spec_from_file_location("_qual_check", _factory_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
QualityChecker = _mod.QualityChecker
QualityReport = _mod.QualityReport

__all__ = ["QualityChecker", "QualityReport"]
