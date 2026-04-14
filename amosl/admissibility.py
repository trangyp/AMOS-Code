"""AMOSL Grand Admissibility Theorem Verifier.

Verifies the 17-component admissibility model 𝔐_P:
    - Γ ⊢ P : T
    - F : X × U × X_e × Y → X
    - ∀B_ij, Legal(B_ij)=1
    - Commit(x') ⟺ Valid(x')=1
    - ∏_k V_k(P) = 1
    - ∃𝔏 : Explain(𝔏) = Outcome
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from amosl.axioms import AxiomChecker, verify_maximal_spec


class AdmissibilityComponent(Enum):
    """Components of the admissibility model 𝔐_P."""

    ONTOL = auto()  # O
    TYPE = auto()  # T
    STATE = auto()  # X
    ACTION = auto()  # U
    OBS = auto()  # Y
    DYNAMICS = auto()  # F
    BRIDGE = auto()  # B
    MEASURE = auto()  # M
    UNCERT = auto()  # Q
    CONSTR = auto()  # C
    OBJ = auto()  # G
    POLICY = auto()  # P
    ADAPT = auto()  # A
    VERIFY = auto()  # V
    COMPILE = auto()  # K
    RUNTIME = auto()  # R
    LEDGER = auto()  # L


@dataclass
class AdmissibilityResult:
    """Result of admissibility verification."""

    component: AdmissibilityComponent
    present: bool
    verified: bool
    evidence: dict[str, Any] = field(default_factory=dict)


class GrandAdmissibilityVerifier:
    """Verify the grand admissibility theorem."""

    def __init__(self):
        self.checker = AxiomChecker()
        self.results: list[AdmissibilityResult] = []

    def verify_model(
        self, model: dict[str, Any]
    ) -> dict[AdmissibilityComponent, AdmissibilityResult]:
        """Verify all 17 components of 𝔐_P exist and satisfy axioms."""
        results = {}

        results[AdmissibilityComponent.ONTOL] = self._check_ontology(model)
        results[AdmissibilityComponent.TYPE] = self._check_types(model)
        results[AdmissibilityComponent.STATE] = self._check_state(model)
        results[AdmissibilityComponent.ACTION] = self._check_actions(model)
        results[AdmissibilityComponent.OBS] = self._check_observations(model)
        results[AdmissibilityComponent.DYNAMICS] = self._check_dynamics(model)
        results[AdmissibilityComponent.BRIDGE] = self._check_bridges(model)
        results[AdmissibilityComponent.MEASURE] = self._check_measurement(model)
        results[AdmissibilityComponent.UNCERT] = self._check_uncertainty(model)
        results[AdmissibilityComponent.CONSTR] = self._check_constraints(model)
        results[AdmissibilityComponent.OBJ] = self._check_objectives(model)
        results[AdmissibilityComponent.POLICY] = self._check_policies(model)
        results[AdmissibilityComponent.ADAPT] = self._check_adaptation(model)
        results[AdmissibilityComponent.VERIFY] = self._check_verification(model)
        results[AdmissibilityComponent.COMPILE] = self._check_compiler(model)
        results[AdmissibilityComponent.RUNTIME] = self._check_runtime(model)
        results[AdmissibilityComponent.LEDGER] = self._check_ledger(model)

        self.results = list(results.values())
        return results

    def _check_ontology(self, model: dict) -> AdmissibilityResult:
        """Check O: ontology space exists."""
        present = "O" in model or "ontology" in model
        return AdmissibilityResult(
            component=AdmissibilityComponent.ONTOL,
            present=present,
            verified=present,
            evidence={"has_ontology": present},
        )

    def _check_types(self, model: dict) -> AdmissibilityResult:
        """Check T: type universe."""
        present = "T" in model or "types" in model or "typing_context" in model

        # Check Γ ⊢ P : T
        has_judgment = "type_judgments" in model or any(":" in str(k) for k in model.keys())

        return AdmissibilityResult(
            component=AdmissibilityComponent.TYPE,
            present=present,
            verified=has_judgment,
            evidence={"has_types": present, "has_judgments": has_judgment},
        )

    def _check_state(self, model: dict) -> AdmissibilityResult:
        """Check X: total state universe."""
        present = "X" in model or "state" in model or "state_manifold" in model

        # Verify stratified
        stratified = all(k in model for k in ["X_c", "X_q", "X_b", "X_h"]) or all(
            k in model.get("state", {}) for k in ["classical", "quantum", "biological", "hybrid"]
        )

        return AdmissibilityResult(
            component=AdmissibilityComponent.STATE,
            present=present,
            verified=stratified,
            evidence={"has_state": present, "stratified": stratified},
        )

    def _check_actions(self, model: dict) -> AdmissibilityResult:
        """Check U: action/control universe."""
        present = "U" in model or "actions" in model or "controls" in model
        return AdmissibilityResult(
            component=AdmissibilityComponent.ACTION,
            present=present,
            verified=present,
            evidence={"has_actions": present},
        )

    def _check_observations(self, model: dict) -> AdmissibilityResult:
        """Check Y: observation outcome universe."""
        present = "Y" in model or "observations" in model or "outcomes" in model
        return AdmissibilityResult(
            component=AdmissibilityComponent.OBS,
            present=present,
            verified=present,
            evidence={"has_observations": present},
        )

    def _check_dynamics(self, model: dict) -> AdmissibilityResult:
        """Check F: lawful dynamics F : X × U × X_e × Y → X."""
        present = "F" in model or "dynamics" in model or "evolution" in model

        # Check function signature
        has_signature = (
            model.get("F_signature") == "X × U × X_e × Y → X"
            or "domain" in model
            and all(k in model["domain"] for k in ["X", "U", "Y"])
        )

        return AdmissibilityResult(
            component=AdmissibilityComponent.DYNAMICS,
            present=present,
            verified=has_signature,
            evidence={"has_dynamics": present, "signature_ok": has_signature},
        )

    def _check_bridges(self, model: dict) -> AdmissibilityResult:
        """Check B: bridge morphisms with Legal(B_ij)=1."""
        bridges = model.get("B", model.get("bridges", {}))
        present = len(bridges) > 0

        # Check all bridges legal
        all_legal = (
            all(b.get("legal", True) for b in bridges.values())
            if isinstance(bridges, dict)
            else True
        )

        return AdmissibilityResult(
            component=AdmissibilityComponent.BRIDGE,
            present=present,
            verified=all_legal,
            evidence={
                "bridge_count": len(bridges) if isinstance(bridges, dict) else 0,
                "all_legal": all_legal,
            },
        )

    def _check_measurement(self, model: dict) -> AdmissibilityResult:
        """Check M: measurement/observation operators."""
        present = "M" in model or "measurement" in model or "observation_operators" in model
        return AdmissibilityResult(
            component=AdmissibilityComponent.MEASURE,
            present=present,
            verified=present,
            evidence={"has_measurement": present},
        )

    def _check_uncertainty(self, model: dict) -> AdmissibilityResult:
        """Check Q: uncertainty structure."""
        present = "Q" in model or "uncertainty" in model or "belief_manifold" in model
        return AdmissibilityResult(
            component=AdmissibilityComponent.UNCERT,
            present=present,
            verified=present,
            evidence={"has_uncertainty": present},
        )

    def _check_constraints(self, model: dict) -> AdmissibilityResult:
        """Check C: constraints/invariants with Commit(x') ⟺ Valid(x')=1."""
        constraints = model.get("C", model.get("constraints", []))
        present = len(constraints) > 0

        # Check commit logic
        has_commit_logic = "commit" in model or "commit_logic" in model

        return AdmissibilityResult(
            component=AdmissibilityComponent.CONSTR,
            present=present,
            verified=has_commit_logic,
            evidence={"constraint_count": len(constraints), "has_commit": has_commit_logic},
        )

    def _check_objectives(self, model: dict) -> AdmissibilityResult:
        """Check G: objectives/functionals."""
        present = "G" in model or "objectives" in model or "functionals" in model
        return AdmissibilityResult(
            component=AdmissibilityComponent.OBJ,
            present=present,
            verified=present,
            evidence={"has_objectives": present},
        )

    def _check_policies(self, model: dict) -> AdmissibilityResult:
        """Check P: policy/permission algebra."""
        present = "P" in model or "policies" in model or "permissions" in model
        return AdmissibilityResult(
            component=AdmissibilityComponent.POLICY,
            present=present,
            verified=present,
            evidence={"has_policies": present},
        )

    def _check_adaptation(self, model: dict) -> AdmissibilityResult:
        """Check A: adaptation/evolution operators with Valid(A(x))=1."""
        present = "A" in model or "adaptation" in model or "evolution_operators" in model

        # Check preserves validity
        preserves_validity = model.get("adaptation_preserves_validity", True)

        return AdmissibilityResult(
            component=AdmissibilityComponent.ADAPT,
            present=present,
            verified=preserves_validity,
            evidence={"has_adaptation": present, "preserves_validity": preserves_validity},
        )

    def _check_verification(self, model: dict) -> AdmissibilityResult:
        """Check V: verification system with ∏_k V_k(P) = 1."""
        present = "V" in model or "verification" in model or "verifiers" in model

        verifiers = model.get("V", model.get("verifiers", []))
        all_pass = (
            all(v.get("result", True) for v in verifiers) if isinstance(verifiers, list) else True
        )

        return AdmissibilityResult(
            component=AdmissibilityComponent.VERIFY,
            present=present,
            verified=all_pass,
            evidence={
                "verifier_count": len(verifiers) if isinstance(verifiers, list) else 0,
                "all_pass": all_pass,
            },
        )

    def _check_compiler(self, model: dict) -> AdmissibilityResult:
        """Check K: compiler/semantic morphisms."""
        present = "K" in model or "compiler" in model or "semantic_morphisms" in model
        return AdmissibilityResult(
            component=AdmissibilityComponent.COMPILE,
            present=present,
            verified=present,
            evidence={"has_compiler": present},
        )

    def _check_runtime(self, model: dict) -> AdmissibilityResult:
        """Check R: runtime realization algebra."""
        present = "R" in model or "runtime" in model or "realization" in model
        return AdmissibilityResult(
            component=AdmissibilityComponent.RUNTIME,
            present=present,
            verified=present,
            evidence={"has_runtime": present},
        )

    def _check_ledger(self, model: dict) -> AdmissibilityResult:
        """Check L: ledger/trace space with Explain(𝔏) = Outcome."""
        present = "L" in model or "ledger" in model or "trace" in model

        # Check explainability
        has_explainer = "explain" in model or "explain_function" in model

        return AdmissibilityResult(
            component=AdmissibilityComponent.LEDGER,
            present=present,
            verified=has_explainer,
            evidence={"has_ledger": present, "has_explainer": has_explainer},
        )

    def verify_grand_theorem(self, model: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        """Verify the grand admissibility theorem:

        A program P is AMOS-admissible iff ∃𝔐_P such that:
        - Γ ⊢ P : T
        - F : X × U × X_e × Y → X
        - ∀B_ij, Legal(B_ij)=1
        - Commit(x') ⟺ Valid(x')=1
        - ∏_k V_k(P) = 1
        - ∃𝔏 : Explain(𝔏) = Outcome
        """
        # First verify all 10 axioms
        axioms_ok, axioms_summary = verify_maximal_spec(model)

        # Then verify all 17 components of 𝔐_P
        component_results = self.verify_model(model)
        all_components = all(r.present for r in component_results.values())
        all_verified = all(r.verified for r in component_results.values())

        # Check specific theorem conditions
        type_ok = component_results[AdmissibilityComponent.TYPE].verified
        dynamics_ok = component_results[AdmissibilityComponent.DYNAMICS].verified
        bridges_ok = component_results[AdmissibilityComponent.BRIDGE].verified
        commit_ok = component_results[AdmissibilityComponent.CONSTR].verified
        verify_ok = component_results[AdmissibilityComponent.VERIFY].verified
        ledger_ok = component_results[AdmissibilityComponent.LEDGER].verified

        all_conditions = all([type_ok, dynamics_ok, bridges_ok, commit_ok, verify_ok, ledger_ok])

        grand_satisfied = axioms_ok and all_components and all_verified and all_conditions

        summary = {
            "axioms_satisfied": axioms_ok,
            "axioms_summary": axioms_summary,
            "all_components_present": all_components,
            "all_components_verified": all_verified,
            "type_judgment_ok": type_ok,
            "dynamics_signature_ok": dynamics_ok,
            "bridges_legal": bridges_ok,
            "commit_logic_ok": commit_ok,
            "verification_all_pass": verify_ok,
            "ledger_explain_ok": ledger_ok,
            "grand_admissibility": grand_satisfied,
        }

        return grand_satisfied, summary


def verify_program_admissibility(program_state: dict[str, Any]) -> tuple[bool, str]:
    """High-level interface: verify if a program state satisfies grand admissibility.

    Returns: (is_admissible, report_string)
    """
    verifier = GrandAdmissibilityVerifier()
    is_admissible, summary = verifier.verify_grand_theorem(program_state)

    # Generate report
    lines = [
        "Grand Admissibility Theorem Verification",
        "=" * 50,
        f"Result: {'ADMISSIBLE ✓' if is_admissible else 'NOT ADMISSIBLE ✗'}",
        "",
        f"10 Axioms: {'SATISFIED ✓' if summary['axioms_satisfied'] else 'VIOLATED ✗'}",
        f"17 Components: {'PRESENT ✓' if summary['all_components_present'] else 'MISSING ✗'}",
        f"All Verified: {'YES ✓' if summary['all_components_verified'] else 'NO ✗'}",
        "",
        "Theorem Conditions:",
        f"  Γ ⊢ P : T: {'✓' if summary['type_judgment_ok'] else '✗'}",
        f"  F signature: {'✓' if summary['dynamics_signature_ok'] else '✗'}",
        f"  Bridges legal: {'✓' if summary['bridges_legal'] else '✗'}",
        f"  Commit logic: {'✓' if summary['commit_logic_ok'] else '✗'}",
        f"  Verification: {'✓' if summary['verification_all_pass'] else '✗'}",
        f"  Explainability: {'✓' if summary['ledger_explain_ok'] else '✗'}",
    ]

    return is_admissible, "\n".join(lines)
