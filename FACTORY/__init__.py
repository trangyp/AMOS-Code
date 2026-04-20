"""FACTORY alias module for AMOS_ORGANISM_OS.13_FACTORY

This module provides alias imports for the FACTORY subsystem.
"""

import importlib.util
import sys
from pathlib import Path

_amos_root = Path(__file__).parent.parent
_organism_path = _amos_root / "AMOS_ORGANISM_OS"


def _load_from_organism(module_name: str, attr_names: Optional[list] = None):
    """Dynamically load a module from AMOS_ORGANISM_OS."""
    try:
        spec = importlib.util.spec_from_file_location(
            module_name, _organism_path / "13_FACTORY" / f"{module_name}.py"
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


_agent_factory = _load_from_organism("agent_factory")

__all__ = []
if _agent_factory and hasattr(_agent_factory, "__all__"):
    __all__.extend(_agent_factory.__all__)
