"""FACTORY code_generator stub — Re-exports from 13_FACTORY"""

import importlib.util
from pathlib import Path

# Load from 13_FACTORY using importlib
_factory_path = Path(__file__).parent.parent / "13_FACTORY" / "code_generator.py"
_spec = importlib.util.spec_from_file_location("_code_gen", _factory_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
CodeGenerator = _mod.CodeGenerator
CodeTemplate = _mod.CodeTemplate
GeneratedCode = _mod.GeneratedCode

__all__ = ["CodeGenerator", "CodeTemplate", "GeneratedCode"]
