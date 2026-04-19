"""AMOS Self-Evolution Infrastructure Package.

This package provides the complete self-evolution subsystem for AMOS:
- E001: Evolution Contract Registry
- E002: Evolution Opportunity Detector
- E003: Regression Guard
- E004: Rollback Guard
- E012: Evolution Execution Engine
- Governance-Evolution Bridge
- Omega-Evolution Bridge

Per AMOS Self-Evolution Directive:
- Patch-only evolution (no broad rewrites)
- Evidence-triggered (detected opportunities)
- Contract-bound (every evolution formalized)
- Regression-verified (E003 checks before mutation)
- Reversible (E004 snapshots for rollback)
"""

# Evolution Infrastructure
from .evolution_contract_registry import (
    EvolutionContract,
    EvolutionContractRegistry,
    EvolutionStatus,
)
from .evolution_execution_engine import (
    EvolutionExecutionEngine,
    ExecutionPhase,
    ExecutionResult,
    ExecutionStep,
    PatchOperation,
)
from .evolution_opportunity_detector import (
    DetectedOpportunity,
    EvolutionOpportunityDetector,
    OpportunityType,
)

# Bridges
from .governance_evolution_bridge import (
    BridgeDecision,
    BridgeMetrics,
    BridgeMode,
    GovernanceEvolutionBridge,
    get_governance_evolution_bridge,
)
from .regression_guard import (
    CheckStatus,
    RegressionCheck,
    RegressionGuard,
    RegressionReport,
)
from .rollback_guard import (
    RollbackGuard,
    RollbackResult,
    RollbackSnapshot,
)

__all__ = [
    # E001 - Contract Registry
    "EvolutionContract",
    "EvolutionContractRegistry",
    "EvolutionStatus",
    # E002 - Opportunity Detector
    "DetectedOpportunity",
    "EvolutionOpportunityDetector",
    "OpportunityType",
    # E003 - Regression Guard
    "CheckStatus",
    "RegressionCheck",
    "RegressionGuard",
    "RegressionReport",
    # E004 - Rollback Guard
    "RollbackGuard",
    "RollbackResult",
    "RollbackSnapshot",
    # E012 - Execution Engine
    "EvolutionExecutionEngine",
    "ExecutionPhase",
    "ExecutionResult",
    "ExecutionStep",
    "PatchOperation",
    # Bridges
    "BridgeDecision",
    "BridgeMetrics",
    "BridgeMode",
    "GovernanceEvolutionBridge",
    "get_governance_evolution_bridge",
]

__version__ = "1.0.0"
__evolution_id__ = "E001-E012"
