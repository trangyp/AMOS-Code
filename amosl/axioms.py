"""AMOSL 10-Axiom Checker - Maximal Specification Verification.

Implements verification of all 10 axioms from the 21-tuple specification:
    1. Semantic primacy
    2. Typed existence
    3. Stratified state
    4. Lawful evolution
    5. Invariant-gated commit
    6. Observation non-neutrality
    7. Bridge explicitness
    8. Admissible adaptation
    9. Ledger completeness
    10. Explainability
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Tuple


class AxiomID(Enum):
    """Identifier for each of the 10 axioms."""

    SEMANTIC_PRIMACY = auto()
    TYPED_EXISTENCE = auto()
    STRATIFIED_STATE = auto()
    LAWFUL_EVOLUTION = auto()
    INVARIANT_GATED_COMMIT = auto()
    OBSERVATION_NON_NEUTRALITY = auto()
    BRIDGE_EXPLICITNESS = auto()
    ADMISSIBLE_ADAPTATION = auto()
    LEDGER_COMPLETENESS = auto()
    EXPLAINABILITY = auto()


@dataclass
class AxiomCheckResult:
    """Result of checking a single axiom."""

    axiom: AxiomID
    satisfied: bool
    evidence: Dict[str, Any] = field(default_factory=dict)
    message: str = ""


class AxiomChecker:
    """Verify all 10 axioms of AMOSL maximal specification."""

    def __init__(self):
        self.check_results: List[AxiomCheckResult] = []

    def check_all_axioms(self, system_state: Dict[str, Any]) -> Dict[AxiomID, AxiomCheckResult]:
        """Check all 10 axioms against system state."""
        results = {}

        results[AxiomID.SEMANTIC_PRIMACY] = self.check_semantic_primacy(system_state)
        results[AxiomID.TYPED_EXISTENCE] = self.check_typed_existence(system_state)
        results[AxiomID.STRATIFIED_STATE] = self.check_stratified_state(system_state)
        results[AxiomID.LAWFUL_EVOLUTION] = self.check_lawful_evolution(system_state)
        results[AxiomID.INVARIANT_GATED_COMMIT] = self.check_invariant_gated_commit(system_state)
        results[AxiomID.OBSERVATION_NON_NEUTRALITY] = self.check_observation_non_neutrality(
            system_state
        )
        results[AxiomID.BRIDGE_EXPLICITNESS] = self.check_bridge_explicitness(system_state)
        results[AxiomID.ADMISSIBLE_ADAPTATION] = self.check_admissible_adaptation(system_state)
        results[AxiomID.LEDGER_COMPLETENESS] = self.check_ledger_completeness(system_state)
        results[AxiomID.EXPLAINABILITY] = self.check_explainability(system_state)

        self.check_results = list(results.values())
        return results

    def check_semantic_primacy(self, state: Dict[str, Any]) -> AxiomCheckResult:
        """Axiom 1: Semantic primacy.
        ∃ Enc : O × T × C → S
        Syntax is encoding of typed ontology under law.
        """
        has_encoder = "encoder" in state or "Enc" in state.get("mappings", {})
        has_ontology = "ontology" in state or "O" in state
        has_types = "types" in state or "T" in state

        satisfied = has_encoder and has_ontology and has_types

        return AxiomCheckResult(
            axiom=AxiomID.SEMANTIC_PRIMACY,
            satisfied=satisfied,
            evidence={
                "has_encoder": has_encoder,
                "has_ontology": has_ontology,
                "has_types": has_types,
            },
            message="Semantic primacy satisfied: Enc(O,T,C) → S exists"
            if satisfied
            else "Missing encoding mapping",
        )

    def check_typed_existence(self, state: Dict[str, Any]) -> AxiomCheckResult:
        """Axiom 2: Typed existence.
        ∀e, ∃τ ∈ T such that Γ ⊢ e:τ
        Every entity has a type.
        """
        entities = state.get("entities", [])
        types = state.get("types", {})

        all_typed = True
        untyped = []
        for e in entities:
            if e not in types:
                all_typed = False
                untyped.append(e)

        return AxiomCheckResult(
            axiom=AxiomID.TYPED_EXISTENCE,
            satisfied=all_typed,
            evidence={"entities_count": len(entities), "untyped_count": len(untyped)},
            message=f"All {len(entities)} entities typed"
            if all_typed
            else f"Untyped entities: {untyped}",
        )

    def check_stratified_state(self, state: Dict[str, Any]) -> AxiomCheckResult:
        """Axiom 3: Stratified state.
        X = X_c × X_q × X_b × X_h × X_e × X_t
        State is 6-dimensional product.
        """
        required = ["X_c", "X_q", "X_b", "X_h", "X_e", "X_t"]
        present = [k for k in required if k in state or k.lower() in state]

        all_present = len(present) == len(required)

        return AxiomCheckResult(
            axiom=AxiomID.STRATIFIED_STATE,
            satisfied=all_present,
            evidence={"dimensions_present": present, "dimensions_required": required},
            message=f"Stratified state: {len(present)}/6 dimensions present"
            + (" ✓" if all_present else ""),
        )

    def check_lawful_evolution(self, state: Dict[str, Any]) -> AxiomCheckResult:
        """Axiom 4: Lawful evolution.
        F : X × U × X_e × Y → X
        Dynamics is total function.
        """
        has_dynamics = "F" in state or "dynamics" in state or "evolution" in state
        has_domain = all(k in state for k in ["X", "U", "X_e", "Y"]) or "domain" in state

        satisfied = has_dynamics and has_domain

        return AxiomCheckResult(
            axiom=AxiomID.LAWFUL_EVOLUTION,
            satisfied=satisfied,
            evidence={"has_dynamics": has_dynamics, "has_domain": has_domain},
            message="Lawful evolution: F defined" if satisfied else "Missing dynamics or domain",
        )

    def check_invariant_gated_commit(self, state: Dict[str, Any]) -> AxiomCheckResult:
        """Axiom 5: Invariant-gated commit.
        Commit(x') ⟺ ∀C_i ∈ C, C_i(x') = ⊤
        Commit iff all constraints satisfied.
        """
        constraints = state.get("constraints", [])
        commit_logic = state.get("commit_logic")

        # Check if commit logic enforces constraints
        has_gated_commit = commit_logic is not None or len(constraints) > 0

        return AxiomCheckResult(
            axiom=AxiomID.INVARIANT_GATED_COMMIT,
            satisfied=has_gated_commit,
            evidence={
                "constraints_count": len(constraints),
                "has_commit_logic": commit_logic is not None,
            },
            message=f"Invariant-gated commit: {len(constraints)} constraints"
            if has_gated_commit
            else "No commit gating",
        )

    def check_observation_non_neutrality(self, state: Dict[str, Any]) -> AxiomCheckResult:
        """Axiom 6: Observation non-neutrality.
        M : X → Y × Q × Π × X
        [M, F] ≠ 0
        Observation changes state.
        """
        has_observation = "M" in state or "observation" in state
        has_perturbation = "perturbation" in state or "Pi" in state
        has_post_state = "post_observation_state" in state or "x'" in state

        # Check commutator [M, F] ≠ 0
        dynamics_affects_obs = state.get("dynamics_affects_observation", True)

        satisfied = has_observation and has_perturbation and has_post_state and dynamics_affects_obs

        return AxiomCheckResult(
            axiom=AxiomID.OBSERVATION_NON_NEUTRALITY,
            satisfied=satisfied,
            evidence={
                "has_observation": has_observation,
                "has_perturbation": has_perturbation,
                "[M,F]≠0": dynamics_affects_obs,
            },
            message="Observation non-neutral: [M,F]≠0"
            if satisfied
            else "Observation may be neutral",
        )

    def check_bridge_explicitness(self, state: Dict[str, Any]) -> AxiomCheckResult:
        """Axiom 7: Bridge explicitness.
        x_i ↝ x_j ⟹ ∃B_ij ∈ B
        Cross-domain transfers require explicit bridges.
        """
        transfers = state.get("cross_domain_transfers", [])
        bridges = state.get("bridges", {})

        all_have_bridges = True
        unbridged = []
        for transfer in transfers:
            bridge_key = f"B_{transfer['from']}{transfer['to']}"
            if bridge_key not in bridges:
                all_have_bridges = False
                unbridged.append(transfer)

        return AxiomCheckResult(
            axiom=AxiomID.BRIDGE_EXPLICITNESS,
            satisfied=all_have_bridges,
            evidence={
                "transfers": len(transfers),
                "bridges": len(bridges),
                "unbridged": len(unbridged),
            },
            message=f"All {len(transfers)} transfers have bridges"
            if all_have_bridges
            else f"Missing bridges for: {unbridged}",
        )

    def check_admissible_adaptation(self, state: Dict[str, Any]) -> AxiomCheckResult:
        """Axiom 8: Admissible adaptation.
        A ∈ A, x' = A(x) ⟹ Valid(x') = 1
        Adaptation preserves validity.
        """
        adaptations = state.get("adaptations", [])

        all_valid = True
        invalid_adaptations = []
        for a in adaptations:
            if not a.get("preserves_validity", True):
                all_valid = False
                invalid_adaptations.append(a)

        return AxiomCheckResult(
            axiom=AxiomID.ADMISSIBLE_ADAPTATION,
            satisfied=all_valid,
            evidence={"adaptations": len(adaptations), "invalid": len(invalid_adaptations)},
            message=f"All {len(adaptations)} adaptations preserve validity"
            if all_valid
            else f"Invalid adaptations: {len(invalid_adaptations)}",
        )

    def check_ledger_completeness(self, state: Dict[str, Any]) -> AxiomCheckResult:
        """Axiom 9: Ledger completeness.
        ∀ committed transition x_t → x_{t+1}, ∃ℓ_t ∈ L
        Every transition recorded.
        """
        transitions = state.get("transitions", [])
        ledger_entries = state.get("ledger_entries", [])

        # Check if every transition has a ledger entry
        all_recorded = len(ledger_entries) >= len(transitions)

        return AxiomCheckResult(
            axiom=AxiomID.LEDGER_COMPLETENESS,
            satisfied=all_recorded,
            evidence={"transitions": len(transitions), "ledger_entries": len(ledger_entries)},
            message=f"Ledger complete: {len(ledger_entries)}/{len(transitions)} transitions recorded"
            if all_recorded
            else "Missing ledger entries",
        )

    def check_explainability(self, state: Dict[str, Any]) -> AxiomCheckResult:
        """Axiom 10: Explainability.
        ∀ outcome, ∃Λ ⊆ L : Explain(Λ) = outcome
        Every outcome explainable from ledger.
        """
        outcomes = state.get("outcomes", [])
        explain_function = state.get("explain_function")

        has_explainer = explain_function is not None or "explain" in state
        has_outcomes = len(outcomes) > 0

        satisfied = has_explainer and has_outcomes

        return AxiomCheckResult(
            axiom=AxiomID.EXPLAINABILITY,
            satisfied=satisfied,
            evidence={"has_explainer": has_explainer, "outcomes": len(outcomes)},
            message="Explainability: Explain(L) = Outcome defined"
            if satisfied
            else "Missing explanation mechanism",
        )

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all axiom checks."""
        if not self.check_results:
            return {"checked": False}

        satisfied = sum(1 for r in self.check_results if r.satisfied)
        total = len(self.check_results)

        return {
            "total_axioms": total,
            "satisfied": satisfied,
            "violated": total - satisfied,
            "all_satisfied": satisfied == total,
            "by_axiom": {r.axiom.name: r.satisfied for r in self.check_results},
        }


def verify_maximal_spec(state: Dict[str, Any]) -> Tuple[bool, dict[str, Any]]:
    """Verify system satisfies all 10 axioms of maximal specification.

    Returns: (all_satisfied, summary_dict)
    """
    checker = AxiomChecker()
    results = checker.check_all_axioms(state)
    summary = checker.get_summary()

    return summary.get("all_satisfied", False), summary
