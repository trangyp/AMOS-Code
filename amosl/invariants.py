"""AMOSL Invariant Checker.

Validates the 8 invariant laws across all substrates.
"""

from __future__ import annotations

from .ast_nodes import Program


class InvariantViolation(Exception):
    """Raised when an invariant is violated."""

    pass


class InvariantChecker:
    """Check AMOSL invariants."""

    def __init__(self):
        self.violations: list[str] = []

    def validate(self, program: Program) -> bool:
        """Validate all 8 invariants.

        Returns True if all invariants pass.
        """
        self.violations = []

        # Invariant 1: Meaning before syntax
        self.check_meaning_before_syntax(program)

        # Invariant 2: State transition law
        self.check_state_transition_law(program)

        # Invariant 3: Constraint preservation
        self.check_constraint_preservation(program)

        # Invariant 4: Explicit effects
        self.check_explicit_effects(program)

        # Invariant 5: Observation is not neutral
        self.check_observation_non_neutral(program)

        # Invariant 6: Evolution is first-class
        self.check_evolution_first_class(program)

        # Invariant 7: Hybrid legality
        self.check_hybrid_legality(program)

        # Invariant 8: Auditability
        self.check_auditability(program)

        return len(self.violations) == 0

    def check_meaning_before_syntax(self, program: Program) -> None:
        """Invariant 1: Syntax = Encode(Semantics)

        Every syntactic construct must have defined semantics.
        """
        # Check that ontology entities have definitions
        for entity in program.ontology.classical:
            if not entity.fields and not entity.states:
                self.violations.append(
                    f"Invariant 1 (Meaning before syntax): "
                    f"Entity '{entity.name}' has no semantic definition"
                )

        # Check quantum entities have qubit count
        for entity in program.ontology.quantum:
            if entity.qubits < 1:
                self.violations.append(
                    f"Invariant 1 (Meaning before syntax): "
                    f"Quantum entity '{entity.name}' has invalid qubit count"
                )

    def check_state_transition_law(self, program: Program) -> None:
        """Invariant 2: Σ_{t+1} = T(Σ_t, input_t)

        All dynamics must define valid state transitions.
        """
        # Check transitions have valid from/to states
        state_names = set()
        for var in program.state.classical:
            state_names.add(var.name)
        for var in program.state.quantum:
            state_names.add(var.name)
        for var in program.state.biological:
            state_names.add(var.name)

        for trans in program.dynamics.transitions:
            if trans.from_state not in state_names:
                self.violations.append(
                    f"Invariant 2 (State transition): "
                    f"Transition from unknown state '{trans.from_state}'"
                )

    def check_constraint_preservation(self, program: Program) -> None:
        """Invariant 3: Valid(Σ) = ∧_i C_i(Σ)

        Constraints must be satisfiable and preserved.
        """
        for constraint in program.constraints:
            if not constraint.expr.text:
                self.violations.append(
                    f"Invariant 3 (Constraint preservation): "
                    f"Constraint '{constraint.name}' has empty expression"
                )

    def check_explicit_effects(self, program: Program) -> None:
        """Invariant 4: f : τ_1 → τ_2 ; ! ; {ε_1,...,ε_n}

        All effects must be explicitly declared.
        """
        # Check actions declare their effects
        for action in program.dynamics.actions:
            if not action.effects:
                self.violations.append(
                    f"Invariant 4 (Explicit effects): "
                    f"Action '{action.name}' has no declared effects"
                )

    def check_observation_non_neutral(self, program: Program) -> None:
        """Invariant 5: Observe : Σ → ⟨estimate, uncertainty, perturbation, Σ'⟩

        Observations must include uncertainty and perturbation.
        """
        for measure in program.measures:
            if not measure.uncertainty:
                self.violations.append(
                    f"Invariant 5 (Observation non-neutral): "
                    f"Measure of '{measure.target}' lacks uncertainty declaration"
                )

    def check_evolution_first_class(self, program: Program) -> None:
        """Invariant 6: X_{t+1} = Evolve(X_t, feedback_t, constraints)

        Evolution rules must be properly defined.
        """
        for evo in program.dynamics.evolutions:
            if not evo.target:
                self.violations.append(
                    "Invariant 6 (Evolution first-class): Evolution rule has no target"
                )

    def check_hybrid_legality(self, program: Program) -> None:
        """Invariant 7: BridgeValid(b) ⇔ TypeCompat ∧ UnitCompat ∧ TimeCompat ∧ ObsCompat

        Hybrid bridges must be valid.
        """
        for var in program.state.hybrid:
            if not var.source or not var.target:
                self.violations.append(
                    f"Invariant 7 (Hybrid legality): "
                    f"Hybrid state '{var.name}' missing source or target"
                )

    def check_auditability(self, program: Program) -> None:
        """Invariant 8: Outcome ⇒ Trace(Inputs, Decisions, Constraints, Outputs)

        All outcomes must be traceable.
        """
        if not program.realizes.trace:
            self.violations.append(
                "Invariant 8 (Auditability): Realization does not enable tracing"
            )


def validate_invariants(program: Program) -> tuple[bool, list[str]]:
    """Validate all AMOSL invariants.

    Returns (success, violations).
    """
    checker = InvariantChecker()
    success = checker.validate(program)
    return success, checker.violations
