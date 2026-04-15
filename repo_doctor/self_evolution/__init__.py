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
- Learning (remember and improve from history)
"""

from .detector import EvolutionOpportunityDetector
from .contract import EvolutionContract, EvolutionRegistry
from .planner import SelfPatchPlanner
from .guard import RegressionGuard, RollbackGuard
from .engine import SelfEvolutionEngine
from .memory import EvolutionMemoryStore, LearningEngine, EvolutionMemory
from .audit import EvolutionAuditor, GovernanceController, AuditEntry, AuditAction

__all__ = [
    "EvolutionOpportunityDetector",
    "EvolutionContract",
    "EvolutionRegistry",
    "SelfPatchPlanner",
    "RegressionGuard",
    "RollbackGuard",
    "SelfEvolutionEngine",
    "EvolutionMemoryStore",
    "LearningEngine",
    "EvolutionMemory",
    "EvolutionAuditor",
    "GovernanceController",
    "AuditEntry",
    "AuditAction",
]
