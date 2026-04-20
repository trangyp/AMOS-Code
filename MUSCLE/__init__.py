"""MUSCLE alias module for AMOS_ORGANISM_OS.06_MUSCLE

This module provides alias imports for the MUSCLE subsystem.
"""

import importlib.util
import sys
from pathlib import Path

# Get the organism OS path
_amos_root = Path(__file__).parent.parent
_organism_path = _amos_root / "AMOS_ORGANISM_OS"


# Use importlib to load from numeric-prefixed directories
def _load_from_organism(module_name: str, attr_names: Optional[list] = None):
    """Dynamically load a module from AMOS_ORGANISM_OS."""
    try:
        # Try to find the module in organism OS
        spec = importlib.util.spec_from_file_location(
            module_name, _organism_path / "06_MUSCLE" / f"{module_name}.py"
        )
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            if attr_names:
                return [getattr(module, name) for name in attr_names if hasattr(module, name)]
            return module
    except Exception:
        pass
    return None


# Export symbols from the subsystem
_workflow_engine = _load_from_organism("workflow_engine")
_automated_remediation = _load_from_organism("automated_remediation_engine")
_brain_backed_worker = _load_from_organism("brain_backed_worker")

# Re-export all public names if modules loaded successfully
__all__ = []
for _mod in [_workflow_engine, _automated_remediation, _brain_backed_worker]:
    if _mod and hasattr(_mod, "__all__"):
        __all__.extend(_mod.__all__)
