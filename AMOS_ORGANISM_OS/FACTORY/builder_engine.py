"""FACTORY builder_engine stub — Re-exports from 13_FACTORY"""

import importlib.util
from pathlib import Path

# Load from 13_FACTORY using importlib
_factory_path = Path(__file__).parent.parent / "13_FACTORY" / "builder_engine.py"
_spec = importlib.util.spec_from_file_location("_build_eng", _factory_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
BuilderEngine = _mod.BuilderEngine
BuildTask = _mod.BuildTask
BuildResult = _mod.BuildResult

__all__ = ["BuilderEngine", "BuildTask", "BuildResult"]
