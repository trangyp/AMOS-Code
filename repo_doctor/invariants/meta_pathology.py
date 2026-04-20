"""
Phase 6: Meta-System Pathology Invariants.

The upper envelope of architectural defect class validations covering:
- Reference-frame, timescale, phase-transition failures
- Adapter laundering, semantic forking, compatibility theater
- Entropy export, debt concealment, commons collapse
- Institutional capture, constitutional drift
- Proof transport, cross-model inconsistency
- Topological holes, world-model drift
"""

from typing import Any

from repo_doctor.model.invariants import Invariant, InvariantResult
from repo_doctor.state.meta_pathology_dimensions import (
    MetaPathologyDimension,
)


class ReferenceFrameInvariant(Invariant):
    """
    I_reference_frame = 1 iff every architecture-critical claim is tagged
    to an explicit reference frame and no cross-frame decision occurs
    without a declared translation.
    """

    name = "reference_frame"
    dimension = MetaPathologyDimension.REFERENCE_FRAME_INTEGRITY
    severity = "critical"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        frames = context.get("reference_frames", [])
        claims = context.get("critical_claims", [])
        translations = context.get("frame_translations", [])

        missing_tags = sum(1 for c in claims if not c.get("frame_tag"))
        untranslated = sum(
            1 for c in claims if c.get("cross_frame") and not c.get("translation_declared")
        )

        passed = missing_tags == 0 and untranslated == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=(
                f"All claims tagged, {untranslated} cross-frame decisions untranslated"
                if missing_tags == 0
                else f"{missing_tags} claims missing frame tags"
            ),
            details={
                "frames_count": len(frames),
                "claims_count": len(claims),
                "translations_count": len(translations),
                "missing_tags": missing_tags,
                "untranslated_decisions": untranslated,
            },
            affected_files=[c.get("source", "unknown") for c in claims if not c.get("frame_tag")],
        )


class FrameTranslationInvariant(Invariant):
    """
    I_frame_translation = 1 iff every required translation between architectural
    reference frames is explicit, bounded, and semantics-preserving.
    """

    name = "frame_translation"
    dimension = MetaPathologyDimension.FRAME_TRANSLATION_VALIDITY
    severity = "critical"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        translations = context.get("frame_translations", [])

        unbounded = sum(1 for t in translations if not t.get("bounds_declared"))
        non_preserving = sum(1 for t in translations if not t.get("semantics_preserving"))
        implicit = sum(1 for t in translations if not t.get("explicit"))

        passed = unbounded == 0 and non_preserving == 0 and implicit == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{implicit} implicit, {unbounded} unbounded, {non_preserving} non-preserving translations",
            details={
                "translation_count": len(translations),
                "implicit": implicit,
                "unbounded": unbounded,
                "non_preserving": non_preserving,
            },
            affected_files=[t.get("source") for t in translations if not t.get("explicit")],
        )


class TimescaleInvariant(Invariant):
    """
    I_timescale = 1 iff all critical interacting surfaces have declared
    timescales and no protected workflow depends on incompatible
    implicit timescale assumptions.
    """

    name = "timescale"
    dimension = MetaPathologyDimension.TIMESCALE_ALIGNMENT
    severity = "high"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        surfaces = context.get("interacting_surfaces", [])
        workflows = context.get("protected_workflows", [])

        undeclared = sum(1 for s in surfaces if not s.get("timescale_declared"))
        incompatible = sum(
            1 for w in workflows if w.get("timescale_mismatch") and not w.get("explicit_coupling")
        )

        passed = undeclared == 0 and incompatible == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{undeclared} surfaces undeclared, {incompatible} incompatible couplings",
            details={
                "surfaces_count": len(surfaces),
                "workflows_count": len(workflows),
                "undeclared": undeclared,
                "incompatible": incompatible,
            },
            affected_files=[s.get("source") for s in surfaces if not s.get("timescale_declared")],
        )


class TemporalDebtInvariant(Invariant):
    """
    I_temporal_debt = 1 iff any temporary architectural artifact has a
    retirement mechanism operating on a commensurate or faster timescale
    than its activation mechanism.
    """

    name = "temporal_debt"
    dimension = MetaPathologyDimension.TEMPORAL_DEBT_VISIBILITY
    severity = "high"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        artifacts = context.get("temporary_artifacts", [])

        rollover = sum(
            1
            for a in artifacts
            if a.get("retirement_timescale", float("inf")) > a.get("activation_timescale", 1)
        )
        no_retirement = sum(1 for a in artifacts if not a.get("retirement_mechanism"))

        passed = rollover == 0 and no_retirement == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{rollover} debt rollovers, {no_retirement} without retirement",
            details={
                "artifact_count": len(artifacts),
                "rollover": rollover,
                "no_retirement": no_retirement,
            },
            affected_files=[
                a.get("source") for a in artifacts if not a.get("retirement_mechanism")
            ],
        )


class PhaseTransitionInvariant(Invariant):
    """
    I_phase_transition = 1 iff critical architectural thresholds and
    regime changes are explicitly modeled and bounded.
    """

    name = "phase_transition"
    dimension = MetaPathologyDimension.PHASE_TRANSITION_SAFETY
    severity = "high"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        thresholds = context.get("architectural_thresholds", [])

        unmodeled = sum(1 for t in thresholds if not t.get("explicitly_modeled"))
        unbounded = sum(1 for t in thresholds if not t.get("bounds_declared"))

        passed = unmodeled == 0 and unbounded == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{unmodeled} unmodeled, {unbounded} unbounded thresholds",
            details={
                "threshold_count": len(thresholds),
                "unmodeled": unmodeled,
                "unbounded": unbounded,
            },
            affected_files=[t.get("source") for t in thresholds if not t.get("explicitly_modeled")],
        )


class MetastabilityInvariant(Invariant):
    """
    I_metastable = 1 iff metastable architectural regions are identified
    and either avoided or bounded by explicit escape rules.
    """

    name = "metastability"
    dimension = MetaPathologyDimension.METASTABILITY_RESISTANCE
    severity = "critical"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        regions = context.get("architectural_regions", [])

        metastable_unbounded = sum(
            1 for r in regions if r.get("metastable") and not r.get("escape_rules")
        )

        passed = metastable_unbounded == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{metastable_unbounded} metastable regions without escape rules",
            details={
                "region_count": len(regions),
                "metastable_unbounded": metastable_unbounded,
            },
            affected_files=[
                r.get("source")
                for r in regions
                if r.get("metastable") and not r.get("escape_rules")
            ],
        )


class AdapterSemanticInvariant(Invariant):
    """
    I_adapter = 1 iff every adapter declares exactly which semantics
    it preserves, weakens, drops, or synthesizes.
    """

    name = "adapter_semantic"
    dimension = MetaPathologyDimension.ADAPTER_SEMANTIC_INTEGRITY
    severity = "critical"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        adapters = context.get("adapters", [])

        undeclared = sum(1 for a in adapters if not a.get("semantics_declared"))
        weakens_undeclared = sum(
            1 for a in adapters if a.get("weakens_semantics") and not a.get("weakening_declared")
        )

        passed = undeclared == 0 and weakens_undeclared == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{undeclared} undeclared, {weakens_undeclared} weakening undeclared",
            details={
                "adapter_count": len(adapters),
                "undeclared": undeclared,
                "weakens_undeclared": weakens_undeclared,
            },
            affected_files=[a.get("source") for a in adapters if not a.get("semantics_declared")],
        )


class AuthorityLaunderingInvariant(Invariant):
    """
    I_authority_launder = 1 iff no wrapper or adapter can silently
    strengthen the authority of the surface it mediates.
    """

    name = "authority_laundering"
    dimension = MetaPathologyDimension.AUTHORITY_LAUNDERING_RESISTANCE
    severity = "critical"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        wrappers = context.get("wrappers", [])
        adapters = context.get("adapters", [])

        laundering = sum(
            1
            for w in list(wrappers) + list(adapters)
            if w.get("output_authority", 0) > w.get("input_authority", 0)
            and not w.get("authority_strengthening_declared")
        )

        passed = laundering == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{laundering} authority laundering instances detected",
            details={
                "wrapper_count": len(wrappers),
                "adapter_count": len(adapters),
                "laundering_instances": laundering,
            },
            affected_files=[
                w.get("source")
                for w in list(wrappers) + list(adapters)
                if w.get("output_authority", 0) > w.get("input_authority", 0)
                and not w.get("authority_strengthening_declared")
            ],
        )


class SemanticForkInvariant(Invariant):
    """
    I_semantic_fork = 1 iff architecture-critical terms cannot diverge
    across repos, teams, or planes without explicit versioned disambiguation.
    """

    name = "semantic_fork"
    dimension = MetaPathologyDimension.SEMANTIC_FORK_RESISTANCE
    severity = "high"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        terms = context.get("critical_terms", [])

        forked = sum(
            1 for t in terms if len(t.get("definitions", [])) > 1 and not t.get("disambiguation")
        )

        passed = forked == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{forked} terms forked without disambiguation",
            details={
                "term_count": len(terms),
                "forked": forked,
            },
            affected_files=[
                t.get("sources", [])[0] if t.get("sources") else "unknown"
                for t in terms
                if len(t.get("definitions", [])) > 1 and not t.get("disambiguation")
            ],
        )


class CompatibilityTheaterInvariant(Invariant):
    """
    I_compatibility_truth = 1 iff compatibility claims are tied to
    preserved semantic obligations, not only superficial operational survival.
    """

    name = "compatibility_theater"
    dimension = MetaPathologyDimension.COMPATIBILITY_TRUTHFULNESS
    severity = "high"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        claims = context.get("compatibility_claims", [])

        theater = sum(
            1 for c in claims if c.get("survives") and not c.get("semantic_obligations_preserved")
        )

        passed = theater == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{theater} compatibility theater instances",
            details={
                "claim_count": len(claims),
                "theater": theater,
            },
            affected_files=[
                c.get("source")
                for c in claims
                if c.get("survives") and not c.get("semantic_obligations_preserved")
            ],
        )


class EntropyExportInvariant(Invariant):
    """
    I_entropy_export = 1 iff architecture cannot improve one surface
    merely by exporting hidden complexity, ambiguity, or risk into
    another protected surface.
    """

    name = "entropy_export"
    dimension = MetaPathologyDimension.ENTROPY_EXPORT_RESISTANCE
    severity = "high"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        surfaces = context.get("surfaces", [])

        exports = sum(
            1 for s in surfaces if s.get("local_entropy_reduced") and s.get("exported_to_protected")
        )

        passed = exports == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{exports} entropy export instances",
            details={
                "surface_count": len(surfaces),
                "exports": exports,
            },
            affected_files=[
                s.get("source")
                for s in surfaces
                if s.get("local_entropy_reduced") and s.get("exported_to_protected")
            ],
        )


class DebtVisibilityInvariant(Invariant):
    """
    I_debt_visibility = 1 iff every persistent architectural workaround
    is observable, attributable, and measured as debt.
    """

    name = "debt_visibility"
    dimension = MetaPathologyDimension.DEBT_VISIBILITY
    severity = "high"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        workarounds = context.get("architectural_workarounds", [])

        hidden = sum(
            1
            for w in workarounds
            if not w.get("observable") or not w.get("attributable") or not w.get("measured")
        )

        passed = hidden == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{hidden} hidden debt instances",
            details={
                "workaround_count": len(workarounds),
                "hidden": hidden,
            },
            affected_files=[
                w.get("source")
                for w in workarounds
                if not w.get("observable") or not w.get("attributable") or not w.get("measured")
            ],
        )


class CommonsGovernanceInvariant(Invariant):
    """
    I_commons = 1 iff every shared architecture-critical resource has
    explicit governance, allocation, replenishment, and exhaustion semantics.
    """

    name = "commons_governance"
    dimension = MetaPathologyDimension.SHARED_RESOURCE_GOVERNANCE
    severity = "high"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        resources = context.get("shared_resources", [])

        ungoverned = sum(
            1
            for r in resources
            if not r.get("governance_explicit")
            or not r.get("allocation_semantics")
            or not r.get("replenishment_path")
            or not r.get("exhaustion_semantics")
        )

        passed = ungoverned == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{ungoverned} ungoverned commons resources",
            details={
                "resource_count": len(resources),
                "ungoverned": ungoverned,
            },
            affected_files=[r.get("source") for r in resources if not r.get("governance_explicit")],
        )


class InstitutionalCaptureInvariant(Invariant):
    """
    I_capture = 1 iff actual authority concentration cannot drift away
    from declared constitutional authority without explicit ratification.
    """

    name = "institutional_capture"
    dimension = MetaPathologyDimension.INSTITUTIONAL_CAPTURE_RESISTANCE
    severity = "critical"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        authorities = context.get("authority_surfaces", [])

        captured = sum(
            1
            for a in authorities
            if a.get("actual_owner") != a.get("declared_owner") and not a.get("ratification_record")
        )

        passed = captured == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{captured} captured authority surfaces",
            details={
                "authority_count": len(authorities),
                "captured": captured,
            },
            affected_files=[
                a.get("source")
                for a in authorities
                if a.get("actual_owner") != a.get("declared_owner")
                and not a.get("ratification_record")
            ],
        )


class ConstitutionalDriftInvariant(Invariant):
    """
    I_constitutional_drift = 1 iff changes to architectural law,
    not only system behavior, are explicitly versioned, reviewed, and enforced.
    """

    name = "constitutional_drift"
    dimension = MetaPathologyDimension.CONSTITUTIONAL_DRIFT_RESISTANCE
    severity = "high"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        changes = context.get("architectural_law_changes", [])

        drifted = sum(
            1
            for c in changes
            if not c.get("versioned") or not c.get("reviewed") or not c.get("enforced")
        )

        passed = drifted == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{drifted} constitutional drift instances",
            details={
                "change_count": len(changes),
                "drifted": drifted,
            },
            affected_files=[c.get("source") for c in changes if not c.get("versioned")],
        )


class ProofTransportInvariant(Invariant):
    """
    I_proof_transport = 1 iff any guarantee moved across mode, artifact,
    load, version, or scope boundaries preserves the assumptions required
    for that guarantee.
    """

    name = "proof_transport"
    dimension = MetaPathologyDimension.PROOF_TRANSPORT_INTEGRITY
    severity = "high"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        transports = context.get("proof_transports", [])

        invalid = sum(
            1
            for t in transports
            if t.get("boundary_crossed") and not t.get("assumptions_preserved")
        )

        passed = invalid == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{invalid} invalid proof transports",
            details={
                "transport_count": len(transports),
                "invalid": invalid,
            },
            affected_files=[
                t.get("source")
                for t in transports
                if t.get("boundary_crossed") and not t.get("assumptions_preserved")
            ],
        )


class CrossModelCoherenceInvariant(Invariant):
    """
    I_cross_model = 1 iff all models used for protected decisions
    are mutually satisfiable over shared protected entities and transitions.
    """

    name = "cross_model_coherence"
    dimension = MetaPathologyDimension.CROSS_MODEL_COHERENCE
    severity = "critical"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        models = context.get("architectural_models", [])
        contradictions = context.get("model_contradictions", [])

        unsatisfiable = len([c for c in contradictions if c.get("unsatisfiable")])

        passed = unsatisfiable == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{unsatisfiable} unsatisfiable model contradictions",
            details={
                "model_count": len(models),
                "contradiction_count": len(contradictions),
                "unsatisfiable": unsatisfiable,
            },
            affected_files=[
                c.get("sources", [])[0] if c.get("sources") else "unknown"
                for c in contradictions
                if c.get("unsatisfiable")
            ],
        )


class TopologicalHoleInvariant(Invariant):
    """
    I_topology_authority = 1 iff every critical defect class has a
    complete graph path from detection to authorized remediation.
    """

    name = "topological_hole"
    dimension = MetaPathologyDimension.TOPOLOGICAL_AUTHORITY_CLOSURE
    severity = "high"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        defect_classes = context.get("defect_classes", [])

        holes = sum(
            1 for d in defect_classes if not d.get("detection_to_remediation_path_complete")
        )

        passed = holes == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{holes} topological holes in authority paths",
            details={
                "defect_class_count": len(defect_classes),
                "holes": holes,
            },
            affected_files=[
                d.get("source")
                for d in defect_classes
                if not d.get("detection_to_remediation_path_complete")
            ],
        )


class WorldModelAlignmentInvariant(Invariant):
    """
    I_world_model = 1 iff world-facing assumptions that affect protected
    workflows are observed and incorporated into the model within bounded lag.
    """

    name = "world_model_alignment"
    dimension = MetaPathologyDimension.WORLD_MODEL_ALIGNMENT
    severity = "critical"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        assumptions = context.get("world_assumptions", [])
        lag_bound = context.get("max_acceptable_lag", float("inf"))

        unbounded = sum(
            1
            for a in assumptions
            if not a.get("observed") or a.get("lag", float("inf")) > lag_bound
        )

        passed = unbounded == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{unbounded} unbounded world-model assumptions",
            details={
                "assumption_count": len(assumptions),
                "unbounded": unbounded,
                "lag_bound": lag_bound,
            },
            affected_files=[a.get("source") for a in assumptions if not a.get("observed")],
        )


class TripleDriftInvariant(Invariant):
    """
    I_triple_drift = 1 iff simultaneous boundedness is maintained over
    implementation drift, model drift, and world drift for protected workflows.
    """

    name = "triple_drift"
    dimension = MetaPathologyDimension.TRIPLE_DRIFT_STABILITY
    severity = "high"

    def check(self, context: dict[str, Any]) -> InvariantResult:
        workflows = context.get("protected_workflows", [])

        unstable = sum(
            1
            for w in workflows
            if w.get("impl_drift_unbounded")
            or w.get("model_drift_unbounded")
            or w.get("world_drift_unbounded")
        )

        passed = unstable == 0

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=f"{unstable} workflows with unbounded triple drift",
            details={
                "workflow_count": len(workflows),
                "unstable": unstable,
            },
            affected_files=[
                w.get("source")
                for w in workflows
                if w.get("impl_drift_unbounded")
                or w.get("model_drift_unbounded")
                or w.get("world_drift_unbounded")
            ],
        )


# Export all Phase 6 invariants
__all__ = [
    "ReferenceFrameInvariant",
    "FrameTranslationInvariant",
    "TimescaleInvariant",
    "TemporalDebtInvariant",
    "PhaseTransitionInvariant",
    "MetastabilityInvariant",
    "AdapterSemanticInvariant",
    "AuthorityLaunderingInvariant",
    "SemanticForkInvariant",
    "CompatibilityTheaterInvariant",
    "EntropyExportInvariant",
    "DebtVisibilityInvariant",
    "CommonsGovernanceInvariant",
    "InstitutionalCaptureInvariant",
    "ConstitutionalDriftInvariant",
    "ProofTransportInvariant",
    "CrossModelCoherenceInvariant",
    "TopologicalHoleInvariant",
    "WorldModelAlignmentInvariant",
    "TripleDriftInvariant",
]
