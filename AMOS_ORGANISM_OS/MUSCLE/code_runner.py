"""MUSCLE code_runner stub — Re-exports from 06_MUSCLE"""

import importlib.util
from pathlib import Path

# Load from 06_MUSCLE using importlib
_muscle_path = Path(__file__).parent.parent / "06_MUSCLE" / "code_runner.py"
_spec = importlib.util.spec_from_file_location("_code_run", _muscle_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CodeRunner = _mod.CodeRunner
CodeRunResult = _mod.CodeRunResult
Language = _mod.Language

__all__ = ["CodeRunner", "CodeRunResult", "Language"]
