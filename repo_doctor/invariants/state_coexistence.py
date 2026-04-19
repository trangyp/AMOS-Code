"""
Repo Doctor Ω∞∞∞∞∞ - Phase 4 State Machine and Coexistence Invariants

Invariants for state machines, multi-version coexistence, cutover,
data lifecycle, external contracts, team topology, incentives,
exceptions, compliance, and epistemic integrity.

These invariants capture the deepest architectural truth:
a system is valid only when all state machines, versions, teams,
and knowledge are aligned with the architecture.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..state.basis import StateDimension
    from ..state.observables import Observable


@dataclass
class InvariantResult:
    """Result of invariant check."""

    dimension: StateDimension
    passed: bool
    severity: float
    message: str
    observables: List[Observable]


class StateMachineIntegrityInvariant:
    """I_state_machine = 1 iff all reachable critical states are declared."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.STATE_MACHINE_INTEGRITY]
        if not obs:
            return InvariantResult(
                StateDimension.STATE_MACHINE_INTEGRITY, True, 0.0, "No issues", []
            )

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.STATE_MACHINE_INTEGRITY,
            max_sev < 0.5,
            max_sev,
            f"State machine issues: {len(obs)}",
            obs,
        )


class ForbiddenStateReachabilityInvariant:
    """I_forbidden_state = 1 iff every forbidden state is blocked."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.FORBIDDEN_STATE_REACHABILITY]
        if not obs:
            return InvariantResult(
                StateDimension.FORBIDDEN_STATE_REACHABILITY, True, 0.0, "No issues", []
            )

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.FORBIDDEN_STATE_REACHABILITY,
            max_sev < 0.3,
            max_sev,
            f"Forbidden state issues: {len(obs)}",
            obs,
        )


class TransitionLegalityInvariant:
    """I_transition_legality = 1 iff every critical transition is valid."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.TRANSITION_LEGALITY]
        if not obs:
            return InvariantResult(StateDimension.TRANSITION_LEGALITY, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.TRANSITION_LEGALITY,
            max_sev < 0.5,
            max_sev,
            f"Transition legality issues: {len(obs)}",
            obs,
        )


class MultiversionCoexistenceInvariant:
    """I_multiversion = 1 iff version coexistence windows are safe."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.MULTIVERSION_COEXISTENCE]
        if not obs:
            return InvariantResult(
                StateDimension.MULTIVERSION_COEXISTENCE, True, 0.0, "No issues", []
            )

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.MULTIVERSION_COEXISTENCE,
            max_sev < 0.5,
            max_sev,
            f"Multi-version issues: {len(obs)}",
            obs,
        )


class CompatibilityWindowInvariant:
    """I_compat_window = 1 iff components remain in declared windows."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.COMPATIBILITY_WINDOW]
        if not obs:
            return InvariantResult(StateDimension.COMPATIBILITY_WINDOW, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.COMPATIBILITY_WINDOW,
            max_sev < 0.3,
            max_sev,
            f"Compatibility window issues: {len(obs)}",
            obs,
        )


class SplitBrainResistanceInvariant:
    """I_split_brain = 1 iff no divergent authorities without reconciliation."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.SPLIT_BRAIN_RESISTANCE]
        if not obs:
            return InvariantResult(
                StateDimension.SPLIT_BRAIN_RESISTANCE, True, 0.0, "No issues", []
            )

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.SPLIT_BRAIN_RESISTANCE,
            max_sev < 0.3,
            max_sev,
            f"Split-brain issues: {len(obs)}",
            obs,
        )


class CutoverIntegrityInvariant:
    """I_cutover = 1 iff every cutover phase declares semantics and exit."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.CUTOVER_INTEGRITY]
        if not obs:
            return InvariantResult(StateDimension.CUTOVER_INTEGRITY, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.CUTOVER_INTEGRITY,
            max_sev < 0.3,
            max_sev,
            f"Cutover issues: {len(obs)}",
            obs,
        )


class CanarySafetyInvariant:
    """I_canary = 1 iff canary paths preserve integrity."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.CANARY_SAFETY]
        if not obs:
            return InvariantResult(StateDimension.CANARY_SAFETY, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.CANARY_SAFETY,
            max_sev < 0.5,
            max_sev,
            f"Canary safety issues: {len(obs)}",
            obs,
        )


class ChangeCoordinationInvariant:
    """I_coordination = 1 iff multi-surface changes are coordinated."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.CHANGE_COORDINATION]
        if not obs:
            return InvariantResult(StateDimension.CHANGE_COORDINATION, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.CHANGE_COORDINATION,
            max_sev < 0.5,
            max_sev,
            f"Coordination issues: {len(obs)}",
            obs,
        )


class DataQualityInvariant:
    """I_data_quality = 1 iff data preserves declared constraints."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.DATA_QUALITY]
        if not obs:
            return InvariantResult(StateDimension.DATA_QUALITY, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.DATA_QUALITY,
            max_sev < 0.5,
            max_sev,
            f"Data quality issues: {len(obs)}",
            obs,
        )


class BackfillIntegrityInvariant:
    """I_backfill = 1 iff replay/backfill preserves semantics."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.BACKFILL_INTEGRITY]
        if not obs:
            return InvariantResult(StateDimension.BACKFILL_INTEGRITY, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.BACKFILL_INTEGRITY,
            max_sev < 0.5,
            max_sev,
            f"Backfill issues: {len(obs)}",
            obs,
        )


class GarbageCollectionInvariant:
    """I_gc = 1 iff GC preserves deletion/rollback semantics."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.GARBAGE_COLLECTION]
        if not obs:
            return InvariantResult(StateDimension.GARBAGE_COLLECTION, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.GARBAGE_COLLECTION,
            max_sev < 0.5,
            max_sev,
            f"GC issues: {len(obs)}",
            obs,
        )


class ExternalContractInvariant:
    """I_external_contract = 1 iff externals have versioned contracts."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.EXTERNAL_CONTRACT]
        if not obs:
            return InvariantResult(StateDimension.EXTERNAL_CONTRACT, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.EXTERNAL_CONTRACT,
            max_sev < 0.5,
            max_sev,
            f"External contract issues: {len(obs)}",
            obs,
        )


class QuotaArchitectureInvariant:
    """I_quota = 1 iff quotas are explicit and compatible."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.QUOTA_ARCHITECTURE]
        if not obs:
            return InvariantResult(StateDimension.QUOTA_ARCHITECTURE, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.QUOTA_ARCHITECTURE,
            max_sev < 0.5,
            max_sev,
            f"Quota issues: {len(obs)}",
            obs,
        )


class VendorSubstitutabilityInvariant:
    """I_vendor_substitutability = 1 iff critical vendors have exit paths."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.VENDOR_SUBSTITUTABILITY]
        if not obs:
            return InvariantResult(
                StateDimension.VENDOR_SUBSTITUTABILITY, True, 0.0, "No issues", []
            )

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.VENDOR_SUBSTITUTABILITY,
            max_sev < 0.7,
            max_sev,
            f"Vendor substitutability issues: {len(obs)}",
            obs,
        )


class ExperimentSafetyInvariant:
    """I_experiment = 1 iff experiments preserve authority/rollback."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.EXPERIMENT_SAFETY]
        if not obs:
            return InvariantResult(StateDimension.EXPERIMENT_SAFETY, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.EXPERIMENT_SAFETY,
            max_sev < 0.5,
            max_sev,
            f"Experiment safety issues: {len(obs)}",
            obs,
        )


class FlagLatticeInvariant:
    """I_flag_lattice = 1 iff flag combinations are bounded."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.FLAG_LATTICE]
        if not obs:
            return InvariantResult(StateDimension.FLAG_LATTICE, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.FLAG_LATTICE,
            max_sev < 0.5,
            max_sev,
            f"Flag lattice issues: {len(obs)}",
            obs,
        )


class ModeActivationInvariant:
    """I_mode_activation = 1 iff modes have explicit semantics."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.MODE_ACTIVATION]
        if not obs:
            return InvariantResult(StateDimension.MODE_ACTIVATION, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.MODE_ACTIVATION,
            max_sev < 0.5,
            max_sev,
            f"Mode activation issues: {len(obs)}",
            obs,
        )


class EconomicEnvelopeInvariant:
    """I_economic_envelope = 1 iff workflows remain in budgets."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.ECONOMIC_ENVELOPE]
        if not obs:
            return InvariantResult(StateDimension.ECONOMIC_ENVELOPE, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.ECONOMIC_ENVELOPE,
            max_sev < 0.7,
            max_sev,
            f"Economic envelope issues: {len(obs)}",
            obs,
        )


class ResourceCouplingInvariant:
    """I_resource_coupling = 1 iff no undeclared bottlenecks."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.RESOURCE_COUPLING]
        if not obs:
            return InvariantResult(StateDimension.RESOURCE_COUPLING, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.RESOURCE_COUPLING,
            max_sev < 0.5,
            max_sev,
            f"Resource coupling issues: {len(obs)}",
            obs,
        )


class TeamTopologyFitInvariant:
    """I_team_topology = 1 iff ownership aligns with architecture."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.TEAM_TOPOLOGY_FIT]
        if not obs:
            return InvariantResult(StateDimension.TEAM_TOPOLOGY_FIT, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.TEAM_TOPOLOGY_FIT,
            max_sev < 0.7,
            max_sev,
            f"Team topology issues: {len(obs)}",
            obs,
        )


class KnowledgeDistributionInvariant:
    """I_knowledge_distribution = 1 iff no single-person dependencies."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.KNOWLEDGE_DISTRIBUTION]
        if not obs:
            return InvariantResult(
                StateDimension.KNOWLEDGE_DISTRIBUTION, True, 0.0, "No issues", []
            )

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.KNOWLEDGE_DISTRIBUTION,
            max_sev < 0.5,
            max_sev,
            f"Knowledge distribution issues: {len(obs)}",
            obs,
        )


class IncentiveAlignmentInvariant:
    """I_incentive = 1 iff local wins don't damage global validity."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.INCENTIVE_ALIGNMENT]
        if not obs:
            return InvariantResult(StateDimension.INCENTIVE_ALIGNMENT, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.INCENTIVE_ALIGNMENT,
            max_sev < 0.7,
            max_sev,
            f"Incentive alignment issues: {len(obs)}",
            obs,
        )


class ExceptionGovernanceInvariant:
    """I_exception_governance = 1 iff exceptions are bounded/reviewed."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.EXCEPTION_GOVERNANCE]
        if not obs:
            return InvariantResult(StateDimension.EXCEPTION_GOVERNANCE, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.EXCEPTION_GOVERNANCE,
            max_sev < 0.5,
            max_sev,
            f"Exception governance issues: {len(obs)}",
            obs,
        )


class OverrideDecayInvariant:
    """I_override_decay = 1 iff overrides have bounded lifetimes."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.OVERRIDE_DECAY]
        if not obs:
            return InvariantResult(StateDimension.OVERRIDE_DECAY, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.OVERRIDE_DECAY,
            max_sev < 0.5,
            max_sev,
            f"Override decay issues: {len(obs)}",
            obs,
        )


class HotfixTopologyInvariant:
    """I_hotfix = 1 iff hotfix paths preserve architecture."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.HOTFIX_TOPOLOGY]
        if not obs:
            return InvariantResult(StateDimension.HOTFIX_TOPOLOGY, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.HOTFIX_TOPOLOGY,
            max_sev < 0.3,
            max_sev,
            f"Hotfix topology issues: {len(obs)}",
            obs,
        )


class ComplianceLifecycleInvariant:
    """I_compliance = 1 iff compliance is compatible with architecture."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.COMPLIANCE_LIFECYCLE]
        if not obs:
            return InvariantResult(StateDimension.COMPLIANCE_LIFECYCLE, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.COMPLIANCE_LIFECYCLE,
            max_sev < 0.5,
            max_sev,
            f"Compliance issues: {len(obs)}",
            obs,
        )


class EpistemicIntegrityInvariant:
    """I_epistemic = 1 iff decisions have fresh, scoped evidence."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.EPISTEMIC_INTEGRITY]
        if not obs:
            return InvariantResult(StateDimension.EPISTEMIC_INTEGRITY, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.EPISTEMIC_INTEGRITY,
            max_sev < 0.5,
            max_sev,
            f"Epistemic issues: {len(obs)}",
            obs,
        )


class ConstitutionalIntegrityInvariant:
    """I_constitution = 1 iff architecture adheres to constitution."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.CONSTITUTIONAL_INTEGRITY]
        if not obs:
            return InvariantResult(
                StateDimension.CONSTITUTIONAL_INTEGRITY, True, 0.0, "No issues", []
            )

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.CONSTITUTIONAL_INTEGRITY,
            max_sev < 0.3,
            max_sev,
            f"Constitutional issues: {len(obs)}",
            obs,
        )


class StateOwnershipInvariant:
    """I_state_ownership = 1 iff state authority is clear."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.STATE_OWNERSHIP]
        if not obs:
            return InvariantResult(StateDimension.STATE_OWNERSHIP, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.STATE_OWNERSHIP,
            max_sev < 0.5,
            max_sev,
            f"State ownership issues: {len(obs)}",
            obs,
        )


class AbsenceSemanticsInvariant:
    """I_absence = 1 iff "not present" has declared meaning."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.ABSENCE_SEMANTICS]
        if not obs:
            return InvariantResult(StateDimension.ABSENCE_SEMANTICS, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.ABSENCE_SEMANTICS,
            max_sev < 0.5,
            max_sev,
            f"Absence semantics issues: {len(obs)}",
            obs,
        )


class DisasterRecoveryInvariant:
    """I_dr = 1 iff DR paths are tested and complete."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.DISASTER_RECOVERY]
        if not obs:
            return InvariantResult(StateDimension.DISASTER_RECOVERY, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.DISASTER_RECOVERY,
            max_sev < 0.5,
            max_sev,
            f"DR issues: {len(obs)}",
            obs,
        )


class GracefulDegradationInvariant:
    """I_graceful = 1 iff degradation paths are defined and bounded."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.GRACEFUL_DEGRADATION]
        if not obs:
            return InvariantResult(StateDimension.GRACEFUL_DEGRADATION, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.GRACEFUL_DEGRADATION,
            max_sev < 0.5,
            max_sev,
            f"Graceful degradation issues: {len(obs)}",
            obs,
        )


class InteroperabilityInvariant:
    """I_interop = 1 iff cross-system contracts are valid."""

    @classmethod
    def check(cls, observables: List[Observable]) -> InvariantResult:
        from ..state.basis import StateDimension

        obs = [o for o in observables if o.dimension == StateDimension.INTEROPERABILITY]
        if not obs:
            return InvariantResult(StateDimension.INTEROPERABILITY, True, 0.0, "No issues", [])

        max_sev = max(o.severity for o in obs)
        return InvariantResult(
            StateDimension.INTEROPERABILITY,
            max_sev < 0.5,
            max_sev,
            f"Interoperability issues: {len(obs)}",
            obs,
        )


# Registry of all Phase 4 invariants
PHASE4_INVARIANTS = [
    StateMachineIntegrityInvariant,
    ForbiddenStateReachabilityInvariant,
    TransitionLegalityInvariant,
    MultiversionCoexistenceInvariant,
    CompatibilityWindowInvariant,
    SplitBrainResistanceInvariant,
    CutoverIntegrityInvariant,
    CanarySafetyInvariant,
    ChangeCoordinationInvariant,
    DataQualityInvariant,
    BackfillIntegrityInvariant,
    GarbageCollectionInvariant,
    ExternalContractInvariant,
    QuotaArchitectureInvariant,
    VendorSubstitutabilityInvariant,
    ExperimentSafetyInvariant,
    FlagLatticeInvariant,
    ModeActivationInvariant,
    EconomicEnvelopeInvariant,
    ResourceCouplingInvariant,
    TeamTopologyFitInvariant,
    KnowledgeDistributionInvariant,
    IncentiveAlignmentInvariant,
    ExceptionGovernanceInvariant,
    OverrideDecayInvariant,
    HotfixTopologyInvariant,
    ComplianceLifecycleInvariant,
    EpistemicIntegrityInvariant,
    ConstitutionalIntegrityInvariant,
    StateOwnershipInvariant,
    AbsenceSemanticsInvariant,
    DisasterRecoveryInvariant,
    GracefulDegradationInvariant,
    InteroperabilityInvariant,
]
