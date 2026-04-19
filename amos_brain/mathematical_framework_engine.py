"""Mathematical Framework Engine - Redirect to clawspring implementation."""

import sys
from pathlib import Path

# Add clawspring/amos_brain to path for direct import
_clawspring_brain_path = str(Path(__file__).parent.parent / "clawspring" / "amos_brain")
if _clawspring_brain_path not in sys.path:
    sys.path.insert(0, _clawspring_brain_path)

# Import directly from the clawspring implementation file
from mathematical_framework_engine import (
    Domain,
    Equation,
    Framework,
    Invariant,
    MathematicalFrameworkEngine,
    get_framework_engine,
)

__all__ = [
    "Domain",
    "Equation",
    "Framework",
    "Invariant",
    "MathematicalFrameworkEngine",
    "get_framework_engine",
]
