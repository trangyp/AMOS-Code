"""
Phase 6: Meta-System Pathology Engine (Layer 19).

The upper-envelope architectural defect detection engine covering:
- Reference-frame, timescale, phase-transition failures
- Adapter laundering, semantic forking, compatibility theater
- Entropy export, debt concealment, commons collapse
- Institutional capture, constitutional drift
- Proof transport, cross-model inconsistency
- Topological holes, world-model drift
"""

from dataclasses import dataclass, field

from repo_doctor.state.meta_pathology_dimensions import (
    MetaPathologyDimension,
)


@dataclass
class MetaPathologyResult:
    """Result of meta-pathology invariant check."""

    invariant_id: str
    dimension: MetaPathologyDimension
    satisfied: bool
    severity: str
    evidence: list[str] = field(default_factory=list)
    affected_surfaces: list[str] = field(default_factory=list)


class MetaPathologyEngine:
    """
    Phase 6: Meta-System Pathology Engine.

    Detects upper-envelope architectural defects:
    - Reference-frame mismatch
    - Timescale mismatch
    - Phase-transition blindness
    - Adapter laundering
    - Semantic forking
    - Compatibility theater
    - Entropy export
    - Debt concealment
    - Commons collapse
    - Institutional capture
    - Constitutional drift
    - Proof transport failure
    - Cross-model inconsistency
    - Topological holes
    - World-model drift
    """

    VERSION = "6.0.0"

    def __init__(self):
        self.engine_id = f"meta_pathology_{id(self):x}"

    def assess_reference_frames(self, frames: list[dict]) -> MetaPathologyResult:
        """I_reference: Critical claims tagged to explicit reference frames."""
        issues = []
        for claim in frames:
            if not claim.get("frame_tag"):
                issues.append(f"Claim {claim.get('id', '?')} missing frame tag")
            if claim.get("cross_frame") and not claim.get("translation_declared"):
                issues.append(f"Cross-frame decision without translation: {claim.get('id', '?')}")

        return MetaPathologyResult(
            invariant_id="I_reference",
            dimension=MetaPathologyDimension.REFERENCE_FRAME_INTEGRITY,
            satisfied=len(issues) == 0,
            severity="critical" if issues else "info",
            evidence=issues if issues else ["All claims properly tagged to frames"],
            affected_surfaces=[c.get("source") for c in frames if not c.get("frame_tag")],
        )

    def assess_frame_translations(self, translations: list[dict]) -> MetaPathologyResult:
        """I_translation: Frame translations explicit, bounded, semantics-preserving."""
        issues = []
        for t in translations:
            if not t.get("explicit"):
                issues.append(f"Implicit translation: {t.get('from', '?')} -> {t.get('to', '?')}")
            if not t.get("bounds_declared"):
                issues.append(f"Translation unbounded: {t.get('id', '?')}")
            if not t.get("semantics_preserving"):
                issues.append(f"Non-semantics-preserving: {t.get('id', '?')}")

        return MetaPathologyResult(
            invariant_id="I_translation",
            dimension=MetaPathologyDimension.FRAME_TRANSLATION_VALIDITY,
            satisfied=len(issues) == 0,
            severity="critical" if issues else "info",
            evidence=issues if issues else ["All translations lawful"],
            affected_surfaces=[t.get("source") for t in translations if not t.get("explicit")],
        )

    def assess_timescales(self, surfaces: list[dict]) -> MetaPathologyResult:
        """I_timescale: Critical surfaces have declared, compatible timescales."""
        issues = []
        for s in surfaces:
            if not s.get("timescale_declared"):
                issues.append(f"Surface {s.get('name', '?')} lacks timescale declaration")
            if s.get("incompatible_with_dependent"):
                issues.append(f"Timescale mismatch: {s.get('name', '?')}")

        return MetaPathologyResult(
            invariant_id="I_timescale",
            dimension=MetaPathologyDimension.TIMESCALE_ALIGNMENT,
            satisfied=len(issues) == 0,
            severity="high" if issues else "info",
            evidence=issues if issues else ["Timescales aligned"],
            affected_surfaces=[
                s.get("source") for s in surfaces if not s.get("timescale_declared")
            ],
        )

    def assess_temporal_debt(self, artifacts: list[dict]) -> MetaPathologyResult:
        """I_temporal_debt: Temporary artifacts have retirement >= activation timescale."""
        issues = []
        for a in artifacts:
            if not a.get("retirement_mechanism"):
                issues.append(f"No retirement: {a.get('name', '?')}")
            elif a.get("retirement_timescale", float("inf")) > a.get("activation_timescale", 1):
                issues.append(f"Debt rollover: {a.get('name', '?')}")

        return MetaPathologyResult(
            invariant_id="I_temporal_debt",
            dimension=MetaPathologyDimension.TEMPORAL_DEBT_VISIBILITY,
            satisfied=len(issues) == 0,
            severity="high" if issues else "info",
            evidence=issues if issues else ["No temporal debt accumulation"],
            affected_surfaces=[
                a.get("source") for a in artifacts if not a.get("retirement_mechanism")
            ],
        )

    def assess_phase_transitions(self, thresholds: list[dict]) -> MetaPathologyResult:
        """I_phase: Architectural thresholds explicitly modeled and bounded."""
        issues = []
        for t in thresholds:
            if not t.get("explicitly_modeled"):
                issues.append(f"Unmodeled threshold: {t.get('name', '?')}")
            if not t.get("bounds_declared"):
                issues.append(f"Unbounded threshold: {t.get('name', '?')}")

        return MetaPathologyResult(
            invariant_id="I_phase",
            dimension=MetaPathologyDimension.PHASE_TRANSITION_SAFETY,
            satisfied=len(issues) == 0,
            severity="high" if issues else "info",
            evidence=issues if issues else ["Phase transitions safe"],
            affected_surfaces=[
                t.get("source") for t in thresholds if not t.get("explicitly_modeled")
            ],
        )

    def assess_metastability(self, regions: list[dict]) -> MetaPathologyResult:
        """I_metastable: Metastable regions identified and bounded."""
        issues = []
        for r in regions:
            if r.get("metastable") and not r.get("escape_rules"):
                issues.append(f"Metastable without escape: {r.get('name', '?')}")

        return MetaPathologyResult(
            invariant_id="I_metastable",
            dimension=MetaPathologyDimension.METASTABILITY_RESISTANCE,
            satisfied=len(issues) == 0,
            severity="critical" if issues else "info",
            evidence=issues if issues else ["No unbounded metastability"],
            affected_surfaces=[
                r.get("source")
                for r in regions
                if r.get("metastable") and not r.get("escape_rules")
            ],
        )

    def assess_adapter_semantics(self, adapters: list[dict]) -> MetaPathologyResult:
        """I_adapter: Adapters declare semantics preservation."""
        issues = []
        for a in adapters:
            if not a.get("semantics_declared"):
                issues.append(f"Adapter {a.get('name', '?')} undeclared semantics")
            if a.get("weakens_semantics") and not a.get("weakening_declared"):
                issues.append(f"Hidden weakening: {a.get('name', '?')}")

        return MetaPathologyResult(
            invariant_id="I_adapter",
            dimension=MetaPathologyDimension.ADAPTER_SEMANTIC_INTEGRITY,
            satisfied=len(issues) == 0,
            severity="critical" if issues else "info",
            evidence=issues if issues else ["Adapter semantics transparent"],
            affected_surfaces=[
                a.get("source") for a in adapters if not a.get("semantics_declared")
            ],
        )

    def assess_authority_laundering(self, wrappers: list[dict]) -> MetaPathologyResult:
        """I_authority: No silent authority strengthening through adapters."""
        issues = []
        for w in wrappers:
            in_auth = w.get("input_authority", 0)
            out_auth = w.get("output_authority", 0)
            if out_auth > in_auth and not w.get("authority_strengthening_declared"):
                issues.append(
                    f"Authority laundering: {w.get('name', '?')} ({in_auth} -> {out_auth})"
                )

        return MetaPathologyResult(
            invariant_id="I_authority_launder",
            dimension=MetaPathologyDimension.AUTHORITY_LAUNDERING_RESISTANCE,
            satisfied=len(issues) == 0,
            severity="critical" if issues else "info",
            evidence=issues if issues else ["No authority laundering detected"],
            affected_surfaces=[
                w.get("source")
                for w in wrappers
                if w.get("output_authority", 0) > w.get("input_authority", 0)
                and not w.get("authority_strengthening_declared")
            ],
        )

    def assess_semantic_forks(self, terms: list[dict]) -> MetaPathologyResult:
        """I_semantic_fork: Critical terms not diverging across domains."""
        issues = []
        for t in terms:
            defs = t.get("definitions", [])
            if len(defs) > 1 and not t.get("disambiguation"):
                issues.append(f"Forked term '{t.get('name', '?')}': {len(defs)} definitions")

        return MetaPathologyResult(
            invariant_id="I_semantic_fork",
            dimension=MetaPathologyDimension.SEMANTIC_FORK_RESISTANCE,
            satisfied=len(issues) == 0,
            severity="high" if issues else "info",
            evidence=issues if issues else ["Semantics unified"],
            affected_surfaces=[
                t.get("sources", ["unknown"])[0]
                for t in terms
                if len(t.get("definitions", [])) > 1 and not t.get("disambiguation")
            ],
        )

    def assess_compatibility_theater(self, claims: list[dict]) -> MetaPathologyResult:
        """I_compatibility: Compatibility claims tied to semantic obligations."""
        issues = []
        for c in claims:
            if c.get("survives") and not c.get("semantic_obligations_preserved"):
                issues.append(f"Theater: {c.get('name', '?')} survives but semantics changed")

        return MetaPathologyResult(
            invariant_id="I_compatibility",
            dimension=MetaPathologyDimension.COMPATIBILITY_TRUTHFULNESS,
            satisfied=len(issues) == 0,
            severity="high" if issues else "info",
            evidence=issues if issues else ["Compatibility claims valid"],
            affected_surfaces=[
                c.get("source")
                for c in claims
                if c.get("survives") and not c.get("semantic_obligations_preserved")
            ],
        )

    def assess_entropy_export(self, surfaces: list[dict]) -> MetaPathologyResult:
        """I_entropy_export: No hidden complexity pushed to protected surfaces."""
        issues = []
        for s in surfaces:
            if s.get("local_entropy_reduced") and s.get("exported_to_protected"):
                issues.append(f"Entropy export: {s.get('name', '?')} -> protected surface")

        return MetaPathologyResult(
            invariant_id="I_entropy_export",
            dimension=MetaPathologyDimension.ENTROPY_EXPORT_RESISTANCE,
            satisfied=len(issues) == 0,
            severity="high" if issues else "info",
            evidence=issues if issues else ["No entropy export detected"],
            affected_surfaces=[
                s.get("source")
                for s in surfaces
                if s.get("local_entropy_reduced") and s.get("exported_to_protected")
            ],
        )

    def assess_debt_visibility(self, workarounds: list[dict]) -> MetaPathologyResult:
        """I_debt: All workarounds observable, attributable, measured."""
        issues = []
        for w in workarounds:
            if not w.get("observable"):
                issues.append(f"Hidden debt: {w.get('name', '?')}")
            if not w.get("attributable"):
                issues.append(f"Unattributed: {w.get('name', '?')}")
            if not w.get("measured"):
                issues.append(f"Unmeasured: {w.get('name', '?')}")

        return MetaPathologyResult(
            invariant_id="I_debt",
            dimension=MetaPathologyDimension.DEBT_VISIBILITY,
            satisfied=len(issues) == 0,
            severity="high" if issues else "info",
            evidence=issues if issues else ["All debt visible"],
            affected_surfaces=[w.get("source") for w in workarounds if not w.get("observable")],
        )

    def assess_commons_governance(self, resources: list[dict]) -> MetaPathologyResult:
        """I_commons: Shared resources have explicit governance."""
        issues = []
        for r in resources:
            missing = []
            if not r.get("governance_explicit"):
                missing.append("governance")
            if not r.get("allocation_semantics"):
                missing.append("allocation")
            if not r.get("replenishment_path"):
                missing.append("replenishment")
            if not r.get("exhaustion_semantics"):
                missing.append("exhaustion")
            if missing:
                issues.append(f"{r.get('name', '?')}: missing {', '.join(missing)}")

        return MetaPathologyResult(
            invariant_id="I_commons",
            dimension=MetaPathologyDimension.SHARED_RESOURCE_GOVERNANCE,
            satisfied=len(issues) == 0,
            severity="high" if issues else "info",
            evidence=issues if issues else ["All commons governed"],
            affected_surfaces=[
                r.get("source") for r in resources if not r.get("governance_explicit")
            ],
        )

    def assess_institutional_capture(self, authorities: list[dict]) -> MetaPathologyResult:
        """I_capture: Authority not drifting from constitutional allocation."""
        issues = []
        for a in authorities:
            actual = a.get("actual_owner")
            declared = a.get("declared_owner")
            if actual != declared and not a.get("ratification_record"):
                issues.append(f"Capture: {a.get('name', '?')} ({declared} -> {actual})")

        return MetaPathologyResult(
            invariant_id="I_capture",
            dimension=MetaPathologyDimension.INSTITUTIONAL_CAPTURE_RESISTANCE,
            satisfied=len(issues) == 0,
            severity="critical" if issues else "info",
            evidence=issues if issues else ["Authority aligned with constitution"],
            affected_surfaces=[
                a.get("source")
                for a in authorities
                if a.get("actual_owner") != a.get("declared_owner")
                and not a.get("ratification_record")
            ],
        )

    def assess_constitutional_drift(self, changes: list[dict]) -> MetaPathologyResult:
        """I_constitutional: Architectural law changes versioned and enforced."""
        issues = []
        for c in changes:
            if not c.get("versioned"):
                issues.append(f"Unversioned: {c.get('description', '?')[:50]}")
            if not c.get("reviewed"):
                issues.append(f"Unreviewed: {c.get('description', '?')[:50]}")
            if not c.get("enforced"):
                issues.append(f"Unenforced: {c.get('description', '?')[:50]}")

        return MetaPathologyResult(
            invariant_id="I_constitutional",
            dimension=MetaPathologyDimension.CONSTITUTIONAL_DRIFT_RESISTANCE,
            satisfied=len(issues) == 0,
            severity="high" if issues else "info",
            evidence=issues if issues else ["Constitutional integrity maintained"],
            affected_surfaces=[c.get("source") for c in changes if not c.get("versioned")],
        )

    def assess_proof_transport(self, proofs: list[dict]) -> MetaPathologyResult:
        """I_proof_transport: Guarantees preserve assumptions across boundaries."""
        issues = []
        for p in proofs:
            if p.get("boundary_crossed") and not p.get("assumptions_preserved"):
                issues.append(f"Proof broken: {p.get('name', '?')} boundary crossed")

        return MetaPathologyResult(
            invariant_id="I_proof_transport",
            dimension=MetaPathologyDimension.PROOF_TRANSPORT_INTEGRITY,
            satisfied=len(issues) == 0,
            severity="high" if issues else "info",
            evidence=issues if issues else ["Proof transport valid"],
            affected_surfaces=[
                p.get("source")
                for p in proofs
                if p.get("boundary_crossed") and not p.get("assumptions_preserved")
            ],
        )

    def assess_cross_model_coherence(self, contradictions: list[dict]) -> MetaPathologyResult:
        """I_cross_model: Models mutually satisfiable."""
        issues = []
        for c in contradictions:
            if c.get("unsatisfiable"):
                issues.append(f"Contradiction: {c.get('models', [])}")

        return MetaPathologyResult(
            invariant_id="I_cross_model",
            dimension=MetaPathologyDimension.CROSS_MODEL_COHERENCE,
            satisfied=len(issues) == 0,
            severity="critical" if issues else "info",
            evidence=issues if issues else ["Model coherence maintained"],
            affected_surfaces=[
                c.get("sources", ["unknown"])[0] for c in contradictions if c.get("unsatisfiable")
            ],
        )

    def assess_topological_holes(self, defects: list[dict]) -> MetaPathologyResult:
        """I_topology: Complete paths from detection to remediation."""
        issues = []
        for d in defects:
            if not d.get("detection_to_remediation_path_complete"):
                issues.append(f"Hole: {d.get('class', '?')} no complete path")

        return MetaPathologyResult(
            invariant_id="I_topology",
            dimension=MetaPathologyDimension.TOPOLOGICAL_AUTHORITY_CLOSURE,
            satisfied=len(issues) == 0,
            severity="high" if issues else "info",
            evidence=issues if issues else ["Topology closed"],
            affected_surfaces=[
                d.get("source")
                for d in defects
                if not d.get("detection_to_remediation_path_complete")
            ],
        )

    def assess_world_model_alignment(
        self, assumptions: list[dict], lag_bound: float
    ) -> MetaPathologyResult:
        """I_world_model: World assumptions within bounded lag."""
        issues = []
        for a in assumptions:
            if not a.get("observed"):
                issues.append(f"Unobserved: {a.get('description', '?')[:50]}")
            elif a.get("lag", float("inf")) > lag_bound:
                issues.append(f"Lag exceeded: {a.get('description', '?')[:50]}")

        return MetaPathologyResult(
            invariant_id="I_world_model",
            dimension=MetaPathologyDimension.WORLD_MODEL_ALIGNMENT,
            satisfied=len(issues) == 0,
            severity="critical" if issues else "info",
            evidence=issues if issues else ["World-model aligned"],
            affected_surfaces=[a.get("source") for a in assumptions if not a.get("observed")],
        )

    def assess_triple_drift(self, workflows: list[dict]) -> MetaPathologyResult:
        """I_triple_drift: Implementation, model, world drift all bounded."""
        issues = []
        for w in workflows:
            drifts = []
            if w.get("impl_drift_unbounded"):
                drifts.append("implementation")
            if w.get("model_drift_unbounded"):
                drifts.append("model")
            if w.get("world_drift_unbounded"):
                drifts.append("world")
            if drifts:
                issues.append(f"{w.get('name', '?')}: unbounded {', '.join(drifts)} drift")

        return MetaPathologyResult(
            invariant_id="I_triple_drift",
            dimension=MetaPathologyDimension.TRIPLE_DRIFT_STABILITY,
            satisfied=len(issues) == 0,
            severity="high" if issues else "info",
            evidence=issues if issues else ["Triple drift stable"],
            affected_surfaces=[
                w.get("source")
                for w in workflows
                if w.get("impl_drift_unbounded")
                or w.get("model_drift_unbounded")
                or w.get("world_drift_unbounded")
            ],
        )

    def assess_all(self, context: dict) -> dict:
        """Run all meta-pathology assessments."""
        results = []

        if "reference_frames" in context:
            results.append(self.assess_reference_frames(context["reference_frames"]))
        if "translations" in context:
            results.append(self.assess_frame_translations(context["translations"]))
        if "surfaces" in context:
            results.append(self.assess_timescales(context["surfaces"]))
            results.append(self.assess_entropy_export(context["surfaces"]))
        if "artifacts" in context:
            results.append(self.assess_temporal_debt(context["artifacts"]))
        if "thresholds" in context:
            results.append(self.assess_phase_transitions(context["thresholds"]))
        if "regions" in context:
            results.append(self.assess_metastability(context["regions"]))
        if "adapters" in context:
            results.append(self.assess_adapter_semantics(context["adapters"]))
        if "wrappers" in context:
            results.append(self.assess_authority_laundering(context["wrappers"]))
        if "terms" in context:
            results.append(self.assess_semantic_forks(context["terms"]))
        if "claims" in context:
            results.append(self.assess_compatibility_theater(context["claims"]))
        if "workarounds" in context:
            results.append(self.assess_debt_visibility(context["workarounds"]))
        if "resources" in context:
            results.append(self.assess_commons_governance(context["resources"]))
        if "authorities" in context:
            results.append(self.assess_institutional_capture(context["authorities"]))
        if "changes" in context:
            results.append(self.assess_constitutional_drift(context["changes"]))
        if "proofs" in context:
            results.append(self.assess_proof_transport(context["proofs"]))
        if "contradictions" in context:
            results.append(self.assess_cross_model_coherence(context["contradictions"]))
        if "defects" in context:
            results.append(self.assess_topological_holes(context["defects"]))
        if "assumptions" in context:
            lag = context.get("max_lag", float("inf"))
            results.append(self.assess_world_model_alignment(context["assumptions"], lag))
        if "workflows" in context:
            results.append(self.assess_triple_drift(context["workflows"]))

        failed = sum(1 for r in results if not r.satisfied)
        critical = sum(1 for r in results if not r.satisfied and r.severity == "critical")
        high = sum(1 for r in results if not r.severity == "high")

        return {
            "engine_id": self.engine_id,
            "version": self.VERSION,
            "invariants": len(results),
            "failed": failed,
            "critical": critical,
            "high": high,
            "health": (len(results) - failed) / len(results) if results else 1.0,
            "results": results,
        }

    def compute_state_vector_amplitudes(
        self, results: list[MetaPathologyResult]
    ) -> dict[str, float]:
        """Map meta-pathology results to state vector amplitudes."""
        amplitudes = {}

        for result in results:
            dim = result.dimension
            if result.satisfied:
                amplitudes[dim.value] = 1.0
            else:
                # Severity-based amplitude decay
                decay = {
                    "critical": 0.2,
                    "high": 0.4,
                    "medium": 0.6,
                    "low": 0.8,
                    "info": 1.0,
                }.get(result.severity, 0.5)
                amplitudes[dim.value] = decay

        return amplitudes

    def get_critical_surfaces(
        self, results: list[MetaPathologyResult], threshold: float = 0.5
    ) -> list[str]:
        """Get surfaces with critical pathology."""
        critical = []
        for r in results:
            if not r.satisfied and r.severity in ("critical", "high"):
                critical.extend(r.affected_surfaces)
        return list(set(critical))
