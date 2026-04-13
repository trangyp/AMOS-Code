"""
05_SKELETON — Constraint, rule, and structural validation subsystem.

The skeletal system of AMOS. Enforces structural constraints,
validates rules, and maintains structural integrity.
"""

from .constraint_engine import ConstraintEngine, Constraint, ConstraintResult
from .rule_validator import RuleValidator, Rule, ValidationOutcome
from .structural_integrity import StructuralIntegrity, IntegrityCheck

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
