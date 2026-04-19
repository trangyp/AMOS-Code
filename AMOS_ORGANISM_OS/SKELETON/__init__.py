"""SKELETON module — Alias for 05_SKELETON"""

import sys
from pathlib import Path

skeleton_path = Path(__file__).parent.parent / "05_SKELETON"
if str(skeleton_path) not in sys.path:
    sys.path.insert(0, str(skeleton_path))

from constraint_engine import ConstraintEngine
from rule_validator import RuleValidator
from structural_integrity import StructuralIntegrity

__all__ = [
    "ConstraintEngine",
    "RuleValidator",
    "StructuralIntegrity",
]
