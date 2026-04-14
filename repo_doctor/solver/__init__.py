"""
Repo Doctor Omega - Z3 SMT Solver Integration

Formal verification using Z3:
- Encode repository truths as logical formulas
- Check satisfiability of invariants
- Extract unsat cores for minimal failing sets
- Repair optimization
"""

from .repair_optimizer import RepairOptimizer
from .unsat_core import UnsatCoreExtractor
from .z3_model import InvariantFormula, Z3Model

__all__ = [
    "Z3Model",
    "InvariantFormula",
    "UnsatCoreExtractor",
    "RepairOptimizer",
]
