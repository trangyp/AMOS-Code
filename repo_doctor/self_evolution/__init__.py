"""
AMOS Self-Evolution Engine - Safe Self-Improving Codebase System.

This module enables AMOS to analyze, detect weaknesses in, and safely improve
its own codebase following bounded, reversible, verified evolution contracts.

Core Principles:
- Patch-only evolution (edit, don't recreate)
- Evidence-triggered (no speculative changes)
- Bounded scope (minimal effective change)
- Verified improvement (measure before/after)
- Reversible (rollback on regression)
"""

from .contract import EvolutionContract, EvolutionRegistry
from .detector import EvolutionOpportunityDetector
from .engine import SelfEvolutionEngine
from .guard import RegressionGuard, RollbackGuard
from .planner import SelfPatchPlanner

__all__ = [
    "EvolutionOpportunityDetector",
    "EvolutionContract",
    "EvolutionRegistry",
    "SelfPatchPlanner",
    "RegressionGuard",
    "RollbackGuard",
    "SelfEvolutionEngine",
]
