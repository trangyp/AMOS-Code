"""Meta-Architecture Bridge.

Integrates meta-pathology detection with the AMOS Brain.

The true state is:
R** = (
  implementation_state,
  architecture_state,
  temporal_order_state,
  trust_state,
  containment_state,
  recovery_state,
  semantic_state,
  governance_state,
  operator_state,
  diagnostic_self_state
)

New state vector amplitudes:
- αSem|SemanticIntegrity⟩
- αOrd|TemporalOrder⟩
- αProv|Provenance⟩
- αRec|Recovery⟩
- αBlast|BlastContainment⟩
- αIso|Isolation⟩
- αGov|Governance⟩
- αHum|OperatorPath⟩
- αSelf|DoctorSelfIntegrity⟩
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# Import meta-pathology detection
try:
    from repo_doctor.meta_pathologies import (
        MetaPathology,
        MetaPathologyEngine,
        MetaPathologyType,
        get_meta_pathology_engine,
    )

    META_PATHOLOGY_AVAILABLE = True
except ImportError:
    META_PATHOLOGY_AVAILABLE = False


@dataclass
class MetaArchitectureContext:
    """Complete meta-architecture context."""

    # Semantic integrity
    semantic_score: float = 1.0  # 0-1, higher is better
    ontology_issues: list[str] = field(default_factory=list)
    alias_explosions: list[str] = field(default_factory=list)
    false_equivalences: list[str] = field(default_factory=list)

    # Temporal order
    temporal_score: float = 1.0
    partial_order_failures: list[str] = field(default_factory=list)
    plane_skews: list[str] = field(default_factory=list)
    eventuality_traps: list[str] = field(default_factory=list)

    # Provenance and trust
    provenance_score: float = 1.0
    provenance_gaps: list[str] = field(default_factory=list)
    supply_chain_issues: list[str] = field(default_factory=list)
    reproducibility_issues: list[str] = field(default_factory=list)

    # Recovery and containment
    recovery_score: float = 1.0
    recovery_gaps: list[str] = field(default_factory=list)
    non_idempotent_recovers: list[str] = field(default_factory=list)
    blast_containment_failures: list[str] = field(default_factory=list)

    # Isolation
    isolation_score: float = 1.0
    isolation_failures: list[str] = field(default_factory=list)
    namespace_collisions: list[str] = field(default_factory=list)

    # Diagnostic self-integrity
    diagnostic_score: float = 1.0
    blind_spots: list[str] = field(default_factory=list)
    false_proofs: list[str] = field(default_factory=list)
    oracle_issues: list[str] = field(default_factory=list)
    repair_unsoundness: list[str] = field(default_factory=list)

    # Overall
    total_issues: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0


class MetaArchitectureBridge:
    """Bridge between meta-pathology detection and AMOS Brain cognition.

    Provides:
    - Meta-architecture context with all failure classes
    - Semantic integrity analysis
    - Temporal-order validation
    - Provenance and trust assessment
    - Recovery and containment verification
    - Diagnostic self-integrity checking
    """

    def __init__(self, repo_path: Union[str, Path]):
        self.repo_path = Path(repo_path)
        self._engine: Optional[MetaPathologyEngine] = None

    @property
    def engine(self) -> Optional[MetaPathologyEngine]:
        """Lazy initialization of meta-pathology engine."""
        if self._engine is None and META_PATHOLOGY_AVAILABLE:
            self._engine = get_meta_pathology_engine(self.repo_path)
        return self._engine

    def get_meta_context(self) -> Optional[MetaArchitectureContext]:
        """Get complete meta-architecture context."""
        if not META_PATHOLOGY_AVAILABLE or self.engine is None:
            return None

        results = self.engine.detect_all()
        ctx = MetaArchitectureContext()

        # Process all detected pathologies
        for detector_name, pathologies in results.items():
            for p in pathologies:
                self._categorize_pathology(ctx, p)

        # Calculate scores
        ctx.total_issues = sum(len(pathologies) for pathologies in results.values())
        ctx.semantic_score = self._calculate_score(
            ctx.ontology_issues, ctx.alias_explosions, ctx.false_equivalences
        )
        ctx.temporal_score = self._calculate_score(
            ctx.partial_order_failures, ctx.plane_skews, ctx.eventuality_traps
        )
        ctx.provenance_score = self._calculate_score(
            ctx.provenance_gaps, ctx.supply_chain_issues, ctx.reproducibility_issues
        )
        ctx.recovery_score = self._calculate_score(
            ctx.recovery_gaps, ctx.non_idempotent_recovers, ctx.blast_containment_failures
        )
        ctx.isolation_score = self._calculate_score(
            ctx.isolation_failures, ctx.namespace_collisions, []
        )
        ctx.diagnostic_score = self._calculate_score(
            ctx.blind_spots, ctx.false_proofs, ctx.oracle_issues, ctx.repair_unsoundness
        )

        return ctx

    def check_meta_invariants(self) -> dict[str, bool]:
        """Check all meta-architecture invariants."""
        if not META_PATHOLOGY_AVAILABLE or self.engine is None:
            return {}

        results = self.engine.detect_all()
        all_pathologies = []
        for pathologies in results.values():
            all_pathologies.extend(pathologies)

        return {
            "I_ontology": not any(
                p.pathology_type == MetaPathologyType.ONTOLOGY_DRIFT for p in all_pathologies
            ),
            "I_semantic_alias": not any(
                p.pathology_type == MetaPathologyType.SEMANTIC_ALIAS_EXPLOSION
                for p in all_pathologies
            ),
            "I_false_equivalence": not any(
                p.pathology_type == MetaPathologyType.FALSE_SEMANTIC_EQUIVALENCE
                for p in all_pathologies
            ),
            "I_partial_order": not any(
                p.pathology_type == MetaPathologyType.PARTIAL_ORDER_FAILURE for p in all_pathologies
            ),
            "I_plane_skew": not any(
                p.pathology_type == MetaPathologyType.TEMPORAL_PLANE_SKEW for p in all_pathologies
            ),
            "I_eventuality": not any(
                p.pathology_type == MetaPathologyType.EVENTUAL_VALIDITY_TRAP
                for p in all_pathologies
            ),
            "I_provenance": not any(
                p.pathology_type == MetaPathologyType.PROVENANCE_GAP for p in all_pathologies
            ),
            "I_supply_semantic": not any(
                p.pathology_type == MetaPathologyType.SUPPLY_CHAIN_SEMANTIC_TRUST_FAILURE
                for p in all_pathologies
            ),
            "I_reproducible": not any(
                p.pathology_type == MetaPathologyType.REPRODUCIBILITY_FAILURE
                for p in all_pathologies
            ),
            "I_recovery": not any(
                p.pathology_type == MetaPathologyType.RECOVERY_PATH_INCOMPLETENESS
                for p in all_pathologies
            ),
            "I_recovery_idempotent": not any(
                p.pathology_type == MetaPathologyType.NON_IDEMPOTENT_RECOVERY
                for p in all_pathologies
            ),
            "I_blast": not any(
                p.pathology_type == MetaPathologyType.BLAST_CONTAINMENT_FAILURE
                for p in all_pathologies
            ),
            "I_isolation": not any(
                p.pathology_type == MetaPathologyType.ISOLATION_FAILURE for p in all_pathologies
            ),
            "I_namespace": not any(
                p.pathology_type == MetaPathologyType.NAMESPACE_COLLISION for p in all_pathologies
            ),
            "I_measurement_complete": not any(
                p.pathology_type == MetaPathologyType.MEASUREMENT_BLIND_SPOT
                for p in all_pathologies
            ),
            "I_proof_strength": not any(
                p.pathology_type == MetaPathologyType.FALSE_PROOF_SURFACE for p in all_pathologies
            ),
            "I_oracle_sound": not any(
                p.pathology_type == MetaPathologyType.ORACLE_UNSOUNDNESS for p in all_pathologies
            ),
            "I_repair_sound": not any(
                p.pathology_type == MetaPathologyType.REPAIR_RECOMMENDATION_UNSOUNDNESS
                for p in all_pathologies
            ),
        }

    def get_critical_meta_issues(self) -> list[MetaPathology]:
        """Get critical meta-architecture issues."""
        if not META_PATHOLOGY_AVAILABLE or self.engine is None:
            return []

        results = self.engine.detect_all()
        critical = []
        for pathologies in results.values():
            for p in pathologies:
                if p.severity == "critical":
                    critical.append(p)
        return critical

    def _categorize_pathology(self, ctx: MetaArchitectureContext, p: MetaPathology):
        """Categorize a pathology into the context."""
        # Count by severity
        if p.severity == "critical":
            ctx.critical_count += 1
        elif p.severity == "high":
            ctx.high_count += 1
        elif p.severity == "medium":
            ctx.medium_count += 1
        else:
            ctx.low_count += 1

        # Categorize by type
        ptype = p.pathology_type

        if ptype == MetaPathologyType.ONTOLOGY_DRIFT:
            ctx.ontology_issues.append(p.message)
        elif ptype == MetaPathologyType.SEMANTIC_ALIAS_EXPLOSION:
            ctx.alias_explosions.append(p.message)
        elif ptype == MetaPathologyType.FALSE_SEMANTIC_EQUIVALENCE:
            ctx.false_equivalences.append(p.message)
        elif ptype == MetaPathologyType.PARTIAL_ORDER_FAILURE:
            ctx.partial_order_failures.append(p.message)
        elif ptype == MetaPathologyType.TEMPORAL_PLANE_SKEW:
            ctx.plane_skews.append(p.message)
        elif ptype == MetaPathologyType.EVENTUAL_VALIDITY_TRAP:
            ctx.eventuality_traps.append(p.message)
        elif ptype == MetaPathologyType.PROVENANCE_GAP:
            ctx.provenance_gaps.append(p.message)
        elif ptype == MetaPathologyType.SUPPLY_CHAIN_SEMANTIC_TRUST_FAILURE:
            ctx.supply_chain_issues.append(p.message)
        elif ptype == MetaPathologyType.REPRODUCIBILITY_FAILURE:
            ctx.reproducibility_issues.append(p.message)
        elif ptype == MetaPathologyType.RECOVERY_PATH_INCOMPLETENESS:
            ctx.recovery_gaps.append(p.message)
        elif ptype == MetaPathologyType.NON_IDEMPOTENT_RECOVERY:
            ctx.non_idempotent_recovers.append(p.message)
        elif ptype == MetaPathologyType.BLAST_CONTAINMENT_FAILURE:
            ctx.blast_containment_failures.append(p.message)
        elif ptype == MetaPathologyType.ISOLATION_FAILURE:
            ctx.isolation_failures.append(p.message)
        elif ptype == MetaPathologyType.NAMESPACE_COLLISION:
            ctx.namespace_collisions.append(p.message)
        elif ptype == MetaPathologyType.MEASUREMENT_BLIND_SPOT:
            ctx.blind_spots.append(p.message)
        elif ptype == MetaPathologyType.FALSE_PROOF_SURFACE:
            ctx.false_proofs.append(p.message)
        elif ptype == MetaPathologyType.ORACLE_UNSOUNDNESS:
            ctx.oracle_issues.append(p.message)
        elif ptype == MetaPathologyType.REPAIR_RECOMMENDATION_UNSOUNDNESS:
            ctx.repair_unsoundness.append(p.message)

    def _calculate_score(self, *issue_lists: list[str]) -> float:
        """Calculate a score based on issue counts."""
        total_issues = sum(len(lst) for lst in issue_lists)
        if total_issues == 0:
            return 1.0
        # Score decreases as issues increase
        return max(0.0, 1.0 - (total_issues * 0.1))


def get_meta_architecture_bridge(repo_path: Union[str, Path] = None) -> MetaArchitectureBridge:
    """Factory function to get meta-architecture bridge instance."""
    return MetaArchitectureBridge(repo_path or ".")
