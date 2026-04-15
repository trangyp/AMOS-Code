"""
Repo Doctor Ω∞∞∞∞∞∞ - Complete Hard Invariants Module.

Core invariants implemented (60+ surfaces across Phase 1-4):

Phase 1-2 (18 invariants):
I_parse, I_import, I_api, I_entry, I_pack, I_runtime,
I_persist, I_status, I_tests, I_security, I_history,
I_migration, I_perf, I_obs, I_auth, I_env, I_artifact

Phase 3 - Control Systems (12 invariants):
I_clock, I_cache, I_consistency, I_identity_lifecycle,
I_capability, I_queue, I_fallback, I_idempotency,
I_control_stable, I_failure_domains, I_negative_capability, I_debt

Phase 4 - State Machine & Coexistence (34 invariants):
I_state_machine, I_forbidden_state, I_transition_legality,
I_multiversion, I_compat_window, I_split_brain,
I_cutover, I_canary, I_coordination,
I_data_quality, I_backfill, I_gc,
I_external_contract, I_quota, I_vendor_substitutability,
I_experiment, I_flag_lattice, I_mode_activation,
I_economic_envelope, I_resource_coupling,
I_team_topology, I_knowledge_distribution, I_incentive,
I_exception_governance, I_override_decay, I_hotfix,
I_compliance, I_epistemic,
I_constitution, I_state_ownership, I_absence,
I_dr, I_graceful, I_interop

Total: 64 invariants
RepoValid = ∧n I_n (64 invariants - Ω∞∞∞∞∞ complete)
"""

# Import base classes
# Import Phase 1-2 invariants (18 total)
from .api import APIInvariant
from .artifact import ArtifactInvariant
from .authorization import AuthorizationInvariant
from .base import Invariant, InvariantGroup, InvariantResult, InvariantSeverity

# Import Phase 3 Control System invariants (12 total)
from .control_systems import (
    ArchitecturalDebtInvariant,
    CacheInvariant,
    CapabilityInvariant,
    ClockInvariant,
    ConsistencyInvariant,
    ControlLoopInvariant,
    FailureDomainsInvariant,
    FallbackInvariant,
    IdempotencyInvariant,
    IdentityLifecycleInvariant,
    NegativeCapabilityInvariant,
    QueueInvariant,
)

# Import engine
from .engine import InvariantEngine
from .entrypoints import EntrypointInvariant
from .environment import EnvironmentInvariant
from .history import HistoryInvariant
from .imports import ImportInvariant
from .migration import MigrationInvariant
from .observability import ObservabilityInvariant
from .packaging import PackagingInvariant
from .parse import ParseInvariant
from .performance import PerformanceInvariant
from .persistence import PersistenceInvariant
from .runtime import RuntimeInvariant
from .security import SecurityInvariant

# Import Phase 4 State Coexistence invariants (34 total)
from .state_coexistence import (
    AbsenceSemanticsInvariant,
    BackfillIntegrityInvariant,
    CanarySafetyInvariant,
    ChangeCoordinationInvariant,
    ComplianceLifecycleInvariant,
    ConstitutionalIntegrityInvariant,
    CutoverIntegrityInvariant,
    DataQualityInvariant,
    DisasterRecoveryInvariant,
    EconomicEnvelopeInvariant,
    EpistemicIntegrityInvariant,
    ExceptionGovernanceInvariant,
    ExperimentSafetyInvariant,
    ExternalContractInvariant,
    FlagLatticeInvariant,
    ForbiddenStateReachabilityInvariant,
    GarbageCollectionInvariant,
    GracefulDegradationInvariant,
    HotfixTopologyInvariant,
    IncentiveAlignmentInvariant,
    InteroperabilityInvariant,
    KnowledgeDistributionInvariant,
    ModeActivationInvariant,
    MultiversionCoexistenceInvariant,
    OverrideDecayInvariant,
    QuotaArchitectureInvariant,
    ResourceCouplingInvariant,
    SplitBrainResistanceInvariant,
    StateMachineIntegrityInvariant,
    StateOwnershipInvariant,
    TeamTopologyFitInvariant,
    TransitionLegalityInvariant,
    VendorSubstitutabilityInvariant,
)
from .status import StatusInvariant
from .tests import TestsInvariant
from .types import TypeInvariant

# Import Phase 5 Distributed Systems Physics invariants (7)
from .distributed_physics import (
    AdaptiveStabilityInvariant,
    CompensationInvariant,
    EntropyInvariant,
    IrreversibilityInvariant,
    PolicyPrecedenceInvariant,
    QuiescenceInvariant,
    TruthArbitrationInvariant,
)

__all__ = [
    # Base
    "Invariant",
    "InvariantGroup",
    "InvariantResult",
    "InvariantSeverity",
    # Engine
    "InvariantEngine",
    # 12 Hard Invariants
    "ParseInvariant",
    "ImportInvariant",
    "TypeInvariant",
    "APIInvariant",
    "EntrypointInvariant",
    "PackagingInvariant",
    "RuntimeInvariant",
    "PersistenceInvariant",
    "StatusInvariant",
    "TestsInvariant",
    "SecurityInvariant",
    "HistoryInvariant",
    # Phase 1-2 additions
    "MigrationInvariant",
    "PerformanceInvariant",
    "ObservabilityInvariant",
    "AuthorizationInvariant",
    "EnvironmentInvariant",
    "ArtifactInvariant",
    # Phase 3 Control System invariants (12)
    "ClockInvariant",
    "CacheInvariant",
    "ConsistencyInvariant",
    "IdentityLifecycleInvariant",
    "CapabilityInvariant",
    "QueueInvariant",
    "FallbackInvariant",
    "IdempotencyInvariant",
    "ControlLoopInvariant",
    "FailureDomainsInvariant",
    "NegativeCapabilityInvariant",
    "ArchitecturalDebtInvariant",
    # Phase 4 State Coexistence invariants (34)
    "StateMachineIntegrityInvariant",
    "ForbiddenStateReachabilityInvariant",
    "TransitionLegalityInvariant",
    "MultiversionCoexistenceInvariant",
    "CompatibilityWindowInvariant",
    "SplitBrainResistanceInvariant",
    "CutoverIntegrityInvariant",
    "CanarySafetyInvariant",
    "ChangeCoordinationInvariant",
    "DataQualityInvariant",
    "BackfillIntegrityInvariant",
    "GarbageCollectionInvariant",
    "ExternalContractInvariant",
    "QuotaArchitectureInvariant",
    "VendorSubstitutabilityInvariant",
    "ExperimentSafetyInvariant",
    "FlagLatticeInvariant",
    "ModeActivationInvariant",
    "EconomicEnvelopeInvariant",
    "ResourceCouplingInvariant",
    "TeamTopologyFitInvariant",
    "KnowledgeDistributionInvariant",
    "IncentiveAlignmentInvariant",
    "ExceptionGovernanceInvariant",
    "OverrideDecayInvariant",
    "HotfixTopologyInvariant",
    "ComplianceLifecycleInvariant",
    "EpistemicIntegrityInvariant",
    "ConstitutionalIntegrityInvariant",
    "StateOwnershipInvariant",
    "AbsenceSemanticsInvariant",
    "DisasterRecoveryInvariant",
    "GracefulDegradationInvariant",
    "InteroperabilityInvariant",
    # Phase 5 Distributed Systems Physics invariants (7)
    "TruthArbitrationInvariant",
    "IrreversibilityInvariant",
    "CompensationInvariant",
    "QuiescenceInvariant",
    "PolicyPrecedenceInvariant",
    "AdaptiveStabilityInvariant",
    "EntropyInvariant",
]
