"""Mathematical Framework Engine - Redirect to clawspring implementation."""

# Import from proper package (no sys.path hack needed)
from clawspring.amos_brain.mathematical_framework_engine import (
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
