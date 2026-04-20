"""SKELETON module — Alias for 05_SKELETON"""

import importlib.util
from pathlib import Path

# Load from 05_SKELETON using importlib
_skeleton_dir = Path(__file__).parent.parent / "05_SKELETON"

_spec_ce = importlib.util.spec_from_file_location(
    "_skeleton_ce", _skeleton_dir / "constraint_engine.py"
)
_mod_ce = importlib.util.module_from_spec(_spec_ce)
_spec_ce.loader.exec_module(_mod_ce)
ConstraintEngine = _mod_ce.ConstraintEngine

_spec_rv = importlib.util.spec_from_file_location(
    "_skeleton_rv", _skeleton_dir / "rule_validator.py"
)
_mod_rv = importlib.util.module_from_spec(_spec_rv)
_spec_rv.loader.exec_module(_mod_rv)
RuleValidator = _mod_rv.RuleValidator

_spec_si = importlib.util.spec_from_file_location(
    "_skeleton_si", _skeleton_dir / "structural_integrity.py"
)
_mod_si = importlib.util.module_from_spec(_spec_si)
_spec_si.loader.exec_module(_mod_si)
StructuralIntegrity = _mod_si.StructuralIntegrity

__all__ = [
    "ConstraintEngine",
    "RuleValidator",
    "StructuralIntegrity",
]
