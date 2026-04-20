"""SENSES context_gatherer stub — Re-exports from 02_SENSES"""

import importlib.util
from pathlib import Path

# Load from 02_SENSES using importlib
_senses_path = Path(__file__).parent.parent / "02_SENSES" / "context_gatherer.py"
_spec = importlib.util.spec_from_file_location("_ctx_gather", _senses_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
ContextGatherer = _mod.ContextGatherer
ContextSnapshot = _mod.ContextSnapshot

__all__ = ["ContextGatherer", "ContextSnapshot"]
