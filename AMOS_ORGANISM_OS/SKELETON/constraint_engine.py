# Stub to re-export from 05_SKELETON
import sys
from pathlib import Path

skeleton_path = Path(__file__).parent.parent / "05_SKELETON"
if str(skeleton_path) not in sys.path:
    sys.path.insert(0, str(skeleton_path))

from constraint_engine import (
    Constraint,
    ConstraintEngine,
    ConstraintOp,
    ConstraintResult,
    ConstraintType,
)

__all__ = [
    "ConstraintEngine",
    "Constraint",
    "ConstraintResult",
    "ConstraintType",
    "ConstraintOp",
]
