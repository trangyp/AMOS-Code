"""Law Layer (L0) - Invariant validation and constraint enforcement"""

from .collapse import collapse_risk, should_collapse
from .constraints import (
    ActionRequest,
    ActionResult,
    BiologicalConstraint,
    StabilityConstraint,
)
from .invariants import (
    communication_clear,
    dual_interaction_present,
    feedback_exists,
    no_contradiction,
    quadrants_present,
    structural_integrity,
    ubi_alignment,
)
from .types import (
    InvariantResult,
    Law,
    LawCheckResult,
    QuadrantIntegrity,
    Severity,
    ValidationResult,
)
from .validators import UniversalLawKernel

__all__ = [
    # Types
    "InvariantResult",
    "Law",
    "LawCheckResult",
    "QuadrantIntegrity",
    "Severity",
    "ValidationResult",
    # Constraints
    "ActionRequest",
    "ActionResult",
    "BiologicalConstraint",
    "StabilityConstraint",
    # Invariants
    "communication_clear",
    "dual_interaction_present",
    "feedback_exists",
    "no_contradiction",
    "quadrants_present",
    "structural_integrity",
    "ubi_alignment",
    # Collapse
    "collapse_risk",
    "should_collapse",
    # Kernel
    "UniversalLawKernel",
]
