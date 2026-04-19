"""Phase 6: Meta-System Pathology Dimensions (Ω∞∞∞∞∞∞).

The upper envelope of architectural defect classes covering:
- Reference-frame and timescale failures
- Phase-transition and metastability
- Adapter laundering and authority laundering
- Semantic forking and compatibility theater
- Entropy export and debt concealment
- Commons collapse and institutional capture
- Proof transport failures
- Cross-model inconsistency
- Topological holes in architecture
- World-model-reality drift
"""

from enum import Enum


class MetaPathologyDimension(Enum):
    """
    Phase 6: Meta-System Pathology dimensions (36 new dimensions).

    These capture the upper envelope of architectural defect classes
    that emerge at scale in complex socio-technical systems.
    """

    # Reference-frame failures (3)
    REFERENCE_FRAME_INTEGRITY = "reference_frame_integrity"  # |Frame⟩ frame alignment
    FRAME_TRANSLATION_VALIDITY = "frame_translation_validity"  # |Trans⟩ translation lawful
    FRAME_COLLAPSE_RESISTANCE = "frame_collapse_resistance"  # |NoCollapse⟩ frame separation

    # Timescale failures (3)
    TIMESCALE_ALIGNMENT = "timescale_alignment"  # |Scale⟩ timescale coupling
    TIMESCALE_STABILITY = "timescale_stability"  # |Stable⟩ fast/slow loop coupling
    TEMPORAL_DEBT_VISIBILITY = "temporal_debt_visibility"  # |DebtVis⟩ retirement timing

    # Phase-transition failures (3)
    PHASE_TRANSITION_SAFETY = "phase_transition_safety"  # |Phase⟩ threshold modeling
    METASTABILITY_RESISTANCE = "metastability_resistance"  # |Meta⟩ escape rules
    REGIME_AWARENESS = "regime_awareness"  # |Regime⟩ rule-regime tagging

    # Adapter and laundering failures (3)
    ADAPTER_SEMANTIC_INTEGRITY = "adapter_semantic_integrity"  # |Adapt⟩ semantics declared
    AUTHORITY_LAUNDERING_RESISTANCE = "authority_laundering_resistance"  # |NoWash⟩ no strengthening
    CONSTRAINT_LAUNDERING_RESISTANCE = (
        "constraint_laundering_resistance"  # |Constraint⟩ survive mediation
    )

    # Semantic-fork failures (3)
    SEMANTIC_FORK_RESISTANCE = "semantic_fork_resistance"  # |NoFork⟩ term disambiguation
    SEMANTIC_COMPATIBILITY_TRUTH = "semantic_compat_truth"  # |SemComp⟩ obligations preserved
    SEMANTIC_UNIVERSE_COHERENCE = "semantic_universe_coherence"  # |Univ⟩ unified semantics

    # Compatibility theater (2)
    COMPATIBILITY_TRUTHFULNESS = "compatibility_truthfulness"  # |Truth⟩ semantic not survival
    SURVIVAL_VALIDITY_SEPARATION = "survival_validity_separation"  # |Separate⟩ degraded explicit

    # Entropy and debt (3)
    ENTROPY_EXPORT_RESISTANCE = "entropy_export_resistance"  # |NoExport⟩ no hidden push
    DEBT_VISIBILITY = "debt_visibility"  # |DebtVis⟩ workarounds observable
    DEBT_AUTOMATION_RESISTANCE = "debt_automation_resistance"  # |NoAutoDebt⟩ no silent permanent

    # Commons failures (2)
    SHARED_RESOURCE_GOVERNANCE = "shared_resource_governance"  # |Commons⟩ explicit allocation
    COMMONS_INCENTIVE_ALIGNMENT = "commons_incentive_alignment"  # |Incentive⟩ no tragedy

    # Institutional capture (3)
    INSTITUTIONAL_CAPTURE_RESISTANCE = (
        "institutional_capture_resistance"  # |NoCapture⟩ authority ratified
    )
    CONSTITUTIONAL_DRIFT_RESISTANCE = "constitutional_drift_resistance"  # |NoDrift⟩ law versioned
    META_AUTHORITY_CLARITY = "meta_authority_clarity"  # |MetaAuth⟩ who changes rules

    # Proof transport (2)
    PROOF_TRANSPORT_INTEGRITY = "proof_transport_integrity"  # |Proof⟩ assumptions preserved
    SCOPE_HONESTY = "scope_honesty"  # |Scope⟩ labeled boundaries

    # Cross-model consistency (3)
    CROSS_MODEL_COHERENCE = "cross_model_coherence"  # |Model⟩ mutual satisfiability
    MODEL_PRECEDENCE_CLARITY = "model_precedence_clarity"  # |Prec⟩ arbitration explicit
    MODEL_ENFORCEMENT_PATH = "model_enforcement_path"  # |Live⟩ enforcement current

    # Topological holes (3)
    TOPOLOGICAL_AUTHORITY_CLOSURE = "topological_authority_closure"  # |AuthTopo⟩ detection to fix
    TOPOLOGICAL_TRUTH_PROPAGATION = "topological_truth_propagation"  # |TruthTopo⟩ complete paths
    TOPOLOGICAL_RETIREMENT_PATH = "topological_retirement_path"  # |RetireTopo⟩ neutralization path

    # World-model-reality drift (3)
    WORLD_MODEL_ALIGNMENT = "world_model_alignment"  # |World⟩ bounded lag
    MODEL_REALITY_LAG = "model_reality_lag"  # |Lag⟩ drift bounded
    TRIPLE_DRIFT_STABILITY = "triple_drift_stability"  # |Triple⟩ impl+model+world bounded

    # Adaptive pressure (2)
    ADAPTIVE_PRESSURE_ALIGNMENT = "adaptive_pressure_alignment"  # |Pressure⟩ adaptation healthy
    ARCHITECTURE_DEPENDENT_HALLUCINATION = "arch_hallucination"  # |NoHalluc⟩ model validity

    # Policy laundering (1)
    POLICY_LAUNDERING_RESISTANCE = "policy_laundering_resistance"  # |NoPolicyWash⟩ rules survive


# Dimension weights for Hamiltonian (severity/importance)
META_PATHOLOGY_WEIGHTS: dict[MetaPathologyDimension, float] = {
    # Reference-frame (critical - system coherence)
    MetaPathologyDimension.REFERENCE_FRAME_INTEGRITY: 95.0,
    MetaPathologyDimension.FRAME_TRANSLATION_VALIDITY: 90.0,
    MetaPathologyDimension.FRAME_COLLAPSE_RESISTANCE: 85.0,
    # Timescale (critical - temporal coupling)
    MetaPathologyDimension.TIMESCALE_ALIGNMENT: 90.0,
    MetaPathologyDimension.TIMESCALE_STABILITY: 85.0,
    MetaPathologyDimension.TEMPORAL_DEBT_VISIBILITY: 80.0,
    # Phase-transition (high - regime changes)
    MetaPathologyDimension.PHASE_TRANSITION_SAFETY: 85.0,
    MetaPathologyDimension.METASTABILITY_RESISTANCE: 80.0,
    MetaPathologyDimension.REGIME_AWARENESS: 75.0,
    # Adapter/laundering (critical - hidden corruption)
    MetaPathologyDimension.ADAPTER_SEMANTIC_INTEGRITY: 90.0,
    MetaPathologyDimension.AUTHORITY_LAUNDERING_RESISTANCE: 95.0,
    MetaPathologyDimension.CONSTRAINT_LAUNDERING_RESISTANCE: 90.0,
    # Semantic (high - meaning coherence)
    MetaPathologyDimension.SEMANTIC_FORK_RESISTANCE: 85.0,
    MetaPathologyDimension.SEMANTIC_COMPATIBILITY_TRUTH: 80.0,
    MetaPathologyDimension.SEMANTIC_UNIVERSE_COHERENCE: 75.0,
    # Compatibility (medium - operational theater)
    MetaPathologyDimension.COMPATIBILITY_TRUTHFULNESS: 80.0,
    MetaPathologyDimension.SURVIVAL_VALIDITY_SEPARATION: 75.0,
    # Debt/entropy (high - structural rot)
    MetaPathologyDimension.ENTROPY_EXPORT_RESISTANCE: 85.0,
    MetaPathologyDimension.DEBT_VISIBILITY: 80.0,
    MetaPathologyDimension.DEBT_AUTOMATION_RESISTANCE: 75.0,
    # Commons (high - shared resources)
    MetaPathologyDimension.SHARED_RESOURCE_GOVERNANCE: 85.0,
    MetaPathologyDimension.COMMONS_INCENTIVE_ALIGNMENT: 80.0,
    # Institutional (critical - power/authority)
    MetaPathologyDimension.INSTITUTIONAL_CAPTURE_RESISTANCE: 90.0,
    MetaPathologyDimension.CONSTITUTIONAL_DRIFT_RESISTANCE: 85.0,
    MetaPathologyDimension.META_AUTHORITY_CLARITY: 80.0,
    # Proof transport (high - guarantee validity)
    MetaPathologyDimension.PROOF_TRANSPORT_INTEGRITY: 85.0,
    MetaPathologyDimension.SCOPE_HONESTY: 80.0,
    # Cross-model (high - model coherence)
    MetaPathologyDimension.CROSS_MODEL_COHERENCE: 85.0,
    MetaPathologyDimension.MODEL_PRECEDENCE_CLARITY: 80.0,
    MetaPathologyDimension.MODEL_ENFORCEMENT_PATH: 75.0,
    # Topological (high - path completeness)
    MetaPathologyDimension.TOPOLOGICAL_AUTHORITY_CLOSURE: 85.0,
    MetaPathologyDimension.TOPOLOGICAL_TRUTH_PROPAGATION: 80.0,
    MetaPathologyDimension.TOPOLOGICAL_RETIREMENT_PATH: 75.0,
    # World drift (critical - reality alignment)
    MetaPathologyDimension.WORLD_MODEL_ALIGNMENT: 90.0,
    MetaPathologyDimension.MODEL_REALITY_LAG: 85.0,
    MetaPathologyDimension.TRIPLE_DRIFT_STABILITY: 80.0,
    # Adaptive (medium - healthy pressure)
    MetaPathologyDimension.ADAPTIVE_PRESSURE_ALIGNMENT: 75.0,
    MetaPathologyDimension.ARCHITECTURE_DEPENDENT_HALLUCINATION: 70.0,
    # Policy laundering (high)
    MetaPathologyDimension.POLICY_LAUNDERING_RESISTANCE: 85.0,
}

# Collapse thresholds (θk) - minimum amplitude before hard-fail
META_PATHOLOGY_THRESHOLDS: dict[MetaPathologyDimension, float] = {
    # Critical dimensions (0.90-0.95)
    MetaPathologyDimension.REFERENCE_FRAME_INTEGRITY: 0.95,
    MetaPathologyDimension.AUTHORITY_LAUNDERING_RESISTANCE: 0.95,
    MetaPathologyDimension.WORLD_MODEL_ALIGNMENT: 0.90,
    # High dimensions (0.80-0.85)
    MetaPathologyDimension.FRAME_TRANSLATION_VALIDITY: 0.90,
    MetaPathologyDimension.CONSTRAINT_LAUNDERING_RESISTANCE: 0.90,
    MetaPathologyDimension.INSTITUTIONAL_CAPTURE_RESISTANCE: 0.90,
    MetaPathologyDimension.TIMESCALE_ALIGNMENT: 0.85,
    MetaPathologyDimension.ADAPTER_SEMANTIC_INTEGRITY: 0.85,
    MetaPathologyDimension.ENTROPY_EXPORT_RESISTANCE: 0.85,
    MetaPathologyDimension.CROSS_MODEL_COHERENCE: 0.85,
    MetaPathologyDimension.MODEL_REALITY_LAG: 0.85,
    MetaPathologyDimension.TOPOLOGICAL_AUTHORITY_CLOSURE: 0.85,
    # Medium dimensions (0.70-0.80)
    MetaPathologyDimension.FRAME_COLLAPSE_RESISTANCE: 0.85,
    MetaPathologyDimension.PHASE_TRANSITION_SAFETY: 0.80,
    MetaPathologyDimension.SEMANTIC_FORK_RESISTANCE: 0.80,
    MetaPathologyDimension.SHARED_RESOURCE_GOVERNANCE: 0.80,
    MetaPathologyDimension.CONSTITUTIONAL_DRIFT_RESISTANCE: 0.80,
    MetaPathologyDimension.PROOF_TRANSPORT_INTEGRITY: 0.80,
    # Lower dimensions (0.65-0.75)
    MetaPathologyDimension.REGIME_AWARENESS: 0.75,
    MetaPathologyDimension.SURVIVAL_VALIDITY_SEPARATION: 0.75,
    MetaPathologyDimension.DEBT_AUTOMATION_RESISTANCE: 0.75,
    MetaPathologyDimension.MODEL_ENFORCEMENT_PATH: 0.75,
    MetaPathologyDimension.TOPOLOGICAL_RETIREMENT_PATH: 0.75,
    MetaPathologyDimension.ARCHITECTURE_DEPENDENT_HALLUCINATION: 0.70,
}

# Hard-fail dimensions (critical to system validity)
HARD_FAIL_META_PATHOLOGY: List[MetaPathologyDimension] = [
    MetaPathologyDimension.REFERENCE_FRAME_INTEGRITY,
    MetaPathologyDimension.AUTHORITY_LAUNDERING_RESISTANCE,
    MetaPathologyDimension.CONSTRAINT_LAUNDERING_RESISTANCE,
    MetaPathologyDimension.WORLD_MODEL_ALIGNMENT,
    MetaPathologyDimension.INSTITUTIONAL_CAPTURE_RESISTANCE,
    MetaPathologyDimension.TIMESCALE_STABILITY,
    MetaPathologyDimension.METASTABILITY_RESISTANCE,
    MetaPathologyDimension.CROSS_MODEL_COHERENCE,
]


def get_critical_meta_dimensions(threshold: float = 0.80) -> List[MetaPathologyDimension]:
    """Get meta-pathology dimensions above threshold importance."""
    return [dim for dim, weight in META_PATHOLOGY_WEIGHTS.items() if weight >= threshold * 100]


def check_hard_fail_meta(dimension: MetaPathologyDimension, amplitude: float) -> bool:
    """Check if meta-pathology dimension is in hard-fail state."""
    if dimension not in HARD_FAIL_META_PATHOLOGY:
        return False
    threshold = META_PATHOLOGY_THRESHOLDS.get(dimension, 0.80)
    return amplitude < threshold
