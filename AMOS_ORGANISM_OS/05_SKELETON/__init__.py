"""05_SKELETON — Constraint, rule, and structural validation subsystem.

The skeletal system of AMOS. Enforces structural constraints,
validates rules, and maintains structural integrity.
"""

from .constraint_engine import Constraint, ConstraintEngine, ConstraintResult
from .rule_validator import Rule, RuleValidator, ValidationOutcome
from .structural_integrity import IntegrityCheck, StructuralIntegrity

__all__ = [
    "ConstraintEngine",
    "Constraint",
    "ConstraintResult",
    "RuleValidator",
    "Rule",
    "ValidationOutcome",
    "StructuralIntegrity",
    "IntegrityCheck",
]
