#!/usr/bin/env python3
"""AMOS Ω — Axiomatic Calculus Implementation

Formal implementation of the 32 axioms from OMEGA_AXIOMS.md.

This module provides:
- Primitive sorts and substrate predicates
- Core relation verification
- Admissibility checking (Z* computation)
- Commit validation
- Runtime step execution

Usage:
    from amos_omega import AMOSOmega, State, Action

    omega = AMOSOmega()
    state = State(classical={'x': 1.0}, quantum=None, biological=None)
    action = Action(name="test", effect={'energy': 0.1})

    # Check admissibility
    is_admissible = omega.check_admissibility(state, action)

    # Execute runtime step
    new_state = omega.runtime_step(state, action, world_context={})
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc
from enum import Enum, auto
from typing import Any, Optional

UTC = UTC

# ============================================================================
# 1. PRIMITIVE UNIVERSE
# ============================================================================


class Sort(Enum):
    """Primitive sorts."""

    INTENT = auto()
    SYNTAX = auto()
    SYMBOL = auto()
    TYPE = auto()
    STATE = auto()
    ACTION = auto()
    OBS = auto()
    BRIDGE = auto()
    EFFECT = auto()
    CONSTRAINT = auto()
    LAW = auto()
    PROOF = auto()
    TRACE = auto()
    WORLD = auto()
    TIME = auto()
    ENERGY = auto()
    IDENTITY = auto()
    UTILITY = auto()


class Substrate(Enum):
    """Substrate classes."""

    CLASSICAL = auto()
    QUANTUM = auto()
    BIOLOGICAL = auto()
    HYBRID = auto()
    META = auto()


# ============================================================================
# 2. CORE DATA STRUCTURES
# ============================================================================


@dataclass
class State:
    """Stratified state X = X_c × X_q × X_b × X_h × ..."""

    classical: dict = None
    quantum: dict = None  # Density matrix representation
    biological: dict = None
    hybrid: dict = None
    world: dict = None
    time: float = None
    utility: float = None
    identity: str = None

    def project(self, substrate: Substrate) -> dict:
        """Projection π_s(x)."""
        projections = {
            Substrate.CLASSICAL: self.classical,
            Substrate.QUANTUM: self.quantum,
            Substrate.BIOLOGICAL: self.biological,
            Substrate.HYBRID: self.hybrid,
        }
        return projections.get(substrate)

    def is_empty(self) -> bool:
        """Check if state has any substrate data."""
        return all(s is None for s in [self.classical, self.quantum, self.biological, self.hybrid])


@dataclass
class Action:
    """Action with explicit effect annotation."""

    name: str
    substrate: Substrate
    effect: dict[str, Any] = field(default_factory=dict)
    energy_cost: float = 0.0
    time_scale: float = 1.0
    pure: bool = False

    def get_effect(self) -> dict[str, Any]:
        """Eff(f) — explicit effect annotation (Axiom 3)."""
        if self.pure:
            return {}
        return self.effect


@dataclass
class Observation:
    """Observation event M: X → Y × Q × Π × X (Axiom 8)."""

    measured_value: Any
    uncertainty: float  # q
    perturbation: float  # π
    new_state: State

    def is_non_neutral(self, original: State) -> bool:
        """Check if observation changed state (Axiom 8: non-neutrality)."""
        return self.new_state != original


@dataclass
class Bridge:
    """Bridge b: X_i → X_j (Axiom 7)."""

    source: Substrate
    target: Substrate
    bridge_map: dict[str, Any]
    uncertainty_transport: float
    time_rescaling: float
    error_budget: float
    perturbation_law: str

    def is_legal(self) -> bool:
        """Check bridge legality (Axiom 7)."""
        return (
            self.source != self.target
            and self.error_budget >= 0
            and self.uncertainty_transport >= 0
        )


@dataclass
class Constraint:
    """Constraint c: X → 𝔹_Q (Axiom 9)."""

    name: str
    constraint_type: str  # 'hard' or 'soft'
    check: Callable[[State], bool]

    def evaluate(self, state: State) -> bool:
        """c_α(x) ∈ 𝔹_Q"""
        try:
            return self.check(state)
        except Exception:
            return False


@dataclass
class LedgerEntry:
    """Ledger element ℓ_t = (x_t, u_t, y_t, q_t, c_t, v_t, x_{t+1}) (Axiom 12)."""

    x_t: State
    u_t: Action
    y_t: Any  # observation result
    q_t: float  # uncertainty
    c_t: bool  # constraint satisfaction
    v_t: bool  # verification
    x_t1: State
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


# ============================================================================
# 3. AMOS Ω IMPLEMENTATION
# ============================================================================


class AMOSOmega:
    """AMOS Ω — Pure Axiomatic Calculus Implementation.

    Implements:
    - Substrate partition (Axiom 1)
    - Typedness (Axiom 2)
    - Effect explicitness (Axiom 3)
    - State stratification (Axiom 4)
    - Lawful dynamics D (Axiom 5)
    - Adaptation A (Axiom 6)
    - Bridge mediation B (Axiom 7)
    - Observation M (Axiom 8)
    - Constraint enforcement C (Axiom 9)
    - Commit validation (Axiom 10)
    - Identity preservation (Axiom 13)
    - Energy accounting (Axiom 14)
    - Multi-regime admissibility Z* (Axiom 21)
    - Runtime step R_t (Axiom 29)
    """

    def __init__(self):
        self.constraints: list[Constraint] = []
        self.ledger: list[LedgerEntry] = []
        self.energy_budget: float = 1000.0
        self.energy_consumed: float = 0.0
        self.identity_history: list[tuple[State, State]] = []

    # --------------------------------------------------------------------
    # AXIOM 1: Substrate Partition
    # --------------------------------------------------------------------

    def substrate_of(self, entity: Any) -> set[Substrate]:
        """∀x (Meaningful(x) → Classical(x) ∨ Quantum(x) ∨ ...)"""
        substrates = set()

        if isinstance(entity, State):
            if entity.classical is not None:
                substrates.add(Substrate.CLASSICAL)
            if entity.quantum is not None:
                substrates.add(Substrate.QUANTUM)
            if entity.biological is not None:
                substrates.add(Substrate.BIOLOGICAL)
            if entity.hybrid is not None:
                substrates.add(Substrate.HYBRID)

        elif isinstance(entity, Action):
            substrates.add(entity.substrate)

        if not substrates:
            substrates.add(Substrate.META)  # Default to meta-level

        return substrates

    def is_primitive_native(self, entity: Any) -> bool:
        """PrimitiveNative(x) → Σ 𝟙ₛ(x) = 1 (exactly one substrate)"""
        substrates = self.substrate_of(entity)
        return len(substrates) == 1

    # --------------------------------------------------------------------
    # AXIOM 2: Typedness
    # --------------------------------------------------------------------

    def has_type(self, entity: Any, type_name: str) -> bool:
        """AdmissibleTerm(e) → ∃τ HasType(e, τ)"""
        if isinstance(entity, State):
            return type_name == "State"
        elif isinstance(entity, Action):
            return type_name == "Action"
        elif isinstance(entity, Bridge):
            return type_name == "Bridge"
        return False

    # --------------------------------------------------------------------
    # AXIOM 3: Effect Explicitness
    # --------------------------------------------------------------------

    def effect_of(self, action: Action) -> dict[str, Any]:
        """Transforms(f) → ∃ε Eff(f) = ε
        Pure(f) ↔ Eff(f) = ∅
        Eff(f ∘ g) = Eff(g) ∪ Eff(f)
        """
        return action.get_effect()

    def is_pure(self, action: Action) -> bool:
        """Pure(f) ↔ Eff(f) = ∅"""
        return action.pure or len(action.get_effect()) == 0

    def compose_effects(self, action1: Action, action2: Action) -> dict[str, Any]:
        """Eff(f ∘ g) = Eff(g) ∪ Eff(f)"""
        eff1 = self.effect_of(action1)
        eff2 = self.effect_of(action2)
        composed = {**eff2, **eff1}  # Union with action1 overriding
        return composed

    # --------------------------------------------------------------------
    # AXIOM 4: State Stratification
    # --------------------------------------------------------------------

    def project_state(self, state: State, substrate: Substrate) -> dict:
        """X = X_c × X_q × X_b × X_h × ...
        x = ⟨π_c(x), π_q(x), π_b(x), π_h(x), ...⟩
        """
        return state.project(substrate)

    def decompose_state(self, state: State) -> dict[Substrate, dict]:
        """Decompose into substrate components."""
        return {
            Substrate.CLASSICAL: state.classical,
            Substrate.QUANTUM: state.quantum,
            Substrate.BIOLOGICAL: state.biological,
            Substrate.HYBRID: state.hybrid,
        }

    # --------------------------------------------------------------------
    # AXIOM 5: Lawful Dynamics (D)
    # --------------------------------------------------------------------

    def D(self, x: State, u: Action, w: dict) -> State:
        """D : X × U × W → X
        D(x, u, w) = x* (candidate next state)
        """
        # Simple classical dynamics for demonstration
        if x.classical is not None:
            new_classical = {**x.classical}
            # Apply action effect
            for key, value in u.effect.items():
                if key in new_classical:
                    if isinstance(value, (int, float)):
                        new_classical[key] += value
                    else:
                        new_classical[key] = value
            return State(
                classical=new_classical,
                quantum=x.quantum,
                biological=x.biological,
                hybrid=x.hybrid,
                time=(x.time or 0) + u.time_scale,
            )
        return x

    # --------------------------------------------------------------------
    # AXIOM 6: Adaptation (A)
    # --------------------------------------------------------------------

    def A(self, x: State, ledger: list[LedgerEntry], w: dict) -> State:
        """A : X × L × W → X
        A(x, ℓ, w) = x' → PreservesId(x, x') ∨ ExplicitReplacement(x, x')
        """
        # Default: identity-preserving adaptation
        x_prime = State(
            classical=x.classical.copy() if x.classical else None,
            quantum=x.quantum,
            biological=x.biological,
            hybrid=x.hybrid,
            identity=x.identity,
            time=x.time,
        )
        return x_prime

    def preserves_identity(self, x: State, x_prime: State) -> bool:
        """I(x, x') — identity predicate (Axiom 13)"""
        # Identity is preserved if core characteristics remain
        if x.identity and x_prime.identity:
            return x.identity == x_prime.identity
        # Default: structural similarity
        return True

    # --------------------------------------------------------------------
    # AXIOM 7: Bridge (B)
    # --------------------------------------------------------------------

    def B(self, bridge: Bridge, x_i: State, x_j: State) -> Optional[State]:
        """Bridges(b, x_i, x_j) → TypeCompat ∧ UnitCompat ∧ TimeCompat ∧ ..."""
        if not bridge.is_legal():
            return None

        # Apply bridge transformation
        if bridge.source == Substrate.CLASSICAL and x_i.classical:
            transformed = {}
            for key, value in x_i.classical.items():
                if key in bridge.bridge_map:
                    transformed[bridge.bridge_map[key]] = value
            return State(classical=transformed)

        return x_j

    # --------------------------------------------------------------------
    # AXIOM 8: Observation (M)
    # --------------------------------------------------------------------

    def M(self, x: State, instrument: str) -> Observation:
        """M : X → Y × Q × Π × X
        Observes(m, x, y, q, π, x') → MeasuredValue = y ∧ Uncertainty = q ∧ Perturbation = π
        """
        # Simulate observation with uncertainty and perturbation
        if x.classical:
            y = x.classical.get("value", 0.0)
            q = 0.1  # uncertainty
            pi = 0.05  # perturbation

            # Perturb state
            new_classical = {**x.classical}
            if "value" in new_classical:
                new_classical["value"] += pi

            x_prime = State(
                classical=new_classical,
                quantum=x.quantum,
                biological=x.biological,
                hybrid=x.hybrid,
                identity=x.identity,
                time=x.time,
            )

            return Observation(y, q, pi, x_prime)

        return Observation(None, 1.0, 0.0, x)

    # --------------------------------------------------------------------
    # AXIOM 9: Constraint (C)
    # --------------------------------------------------------------------

    def add_constraint(self, constraint: Constraint):
        """Add constraint to the system."""
        self.constraints.append(constraint)

    def check_constraints(self, x: State) -> dict[str, bool]:
        """C = {c_α}_{α∈A}, c_α : X → 𝔹_Q
        Valid(x) ↔ ∀α ∈ Hard, c_α(x) = ⊤
        """
        results = {}
        for c in self.constraints:
            results[c.name] = c.evaluate(x)
        return results

    def is_valid(self, x: State, hard_only: bool = True) -> bool:
        """Check if state satisfies all (hard) constraints."""
        for c in self.constraints:
            if hard_only and c.constraint_type != "hard":
                continue
            if not c.evaluate(x):
                return False
        return True

    # --------------------------------------------------------------------
    # AXIOM 10 & 21: Commit and Multi-Regime Admissibility (Z*)
    # --------------------------------------------------------------------

    def Z_star(self, x: State) -> bool:
        """Z* = Z_type ∩ Z_logic ∩ Z_physical ∩ Z_biological ∩ Z_temporal
             ∩ Z_energetic ∩ Z_identity ∩ Z_deontic ∩ Z_epistemic

        Commits(x') ↔ x' ∈ Z*
        """
        checks = {
            "type": self._check_type_admissibility(x),
            "logic": self._check_logic_admissibility(x),
            "physical": self._check_physical_admissibility(x),
            "energetic": self._check_energetic_admissibility(x),
            "identity": self._check_identity_admissibility(x),
            "constraint": self.is_valid(x, hard_only=True),
        }
        return all(checks.values())

    def _check_type_admissibility(self, x: State) -> bool:
        """Z_type — properly typed."""
        return not x.is_empty()

    def _check_logic_admissibility(self, x: State) -> bool:
        """Z_logic — logically consistent."""
        return True  # Placeholder

    def _check_physical_admissibility(self, x: State) -> bool:
        """Z_physical — physically possible."""
        return True  # Placeholder

    def _check_energetic_admissibility(self, x: State) -> bool:
        """Z_energetic — within energy budget."""
        return self.energy_consumed <= self.energy_budget

    def _check_identity_admissibility(self, x: State) -> bool:
        """Z_identity — identity not corrupted."""
        return True  # Placeholder

    def Commit(self, x_star: State) -> Optional[State]:
        """Commit(x*) = x' ↔ x* ∈ Z
        Commits(x*) ↔ Valid(x*) ∧ Verified(x*) ∧ Feasible(x*)
        ¬Valid(x*) → ¬Commits(x*)
        """
        if not self.Z_star(x_star):
            return None
        return x_star

    # --------------------------------------------------------------------
    # AXIOM 14: Energy
    # --------------------------------------------------------------------

    def consume_energy(self, action: Action) -> bool:
        """∀χ ∈ {Action, Obs, Bridge, Adapt}: Occurs(χ) → ∃e ≥ 0 Consumes(χ, e)
        Σ e_i ≤ E_budget
        """
        if self.energy_consumed + action.energy_cost > self.energy_budget:
            return False
        self.energy_consumed += action.energy_cost
        return True

    # --------------------------------------------------------------------
    # AXIOM 29: Runtime Step (R_t)
    # --------------------------------------------------------------------

    def runtime_step(self, x_t: State, u_t: Action, w_t: dict) -> Optional[State]:
        """R_t = Commit_Z* ∘ V_t ∘ M_t ∘ B_t ∘ A_t ∘ D_t
        x_{t+1} = R_t(x_t, u_t, w_t)
        """
        # Check energy feasibility
        if not self.consume_energy(u_t):
            return None

        # D_t: Dynamics
        x_star = self.D(x_t, u_t, w_t)

        # A_t: Adaptation
        x_adapted = self.A(x_star, self.ledger, w_t)

        # B_t: Bridge (if needed)
        # (skipped for single-substrate actions)

        # M_t: Observation
        obs = self.M(x_adapted, "default")

        # V_t: Verification
        verified = self.is_valid(obs.new_state)

        # Commit_Z*: Final validation
        x_t1 = self.Commit(obs.new_state)

        if x_t1 is not None:
            # Record in ledger
            entry = LedgerEntry(
                x_t=x_t,
                u_t=u_t,
                y_t=obs.measured_value,
                q_t=obs.uncertainty,
                c_t=verified,
                v_t=verified,
                x_t1=x_t1,
            )
            self.ledger.append(entry)

            # Track identity
            self.identity_history.append((x_t, x_t1))

        return x_t1

    # --------------------------------------------------------------------
    # AXIOM 30: Ledger Chain
    # --------------------------------------------------------------------

    def get_ledger(self) -> list[LedgerEntry]:
        """ℒ = Σ_t ℓ_t"""
        return self.ledger

    def explain_outcome(self, outcome: Any) -> list[LedgerEntry]:
        """Outcome(o) → ∃Λ ⊆ L : Explains(Λ, o)
        Explain(ℒ) = Outcome
        """
        # Return relevant ledger entries that explain outcome
        return [e for e in self.ledger if e.y_t == outcome]

    def replay(self, ledger_subset: list[LedgerEntry]) -> State:
        """Replay(Λ) = x_n"""
        if not ledger_subset:
            return State()
        return ledger_subset[-1].x_t1

    # --------------------------------------------------------------------
    # AXIOM 32: Grand Realizability
    # --------------------------------------------------------------------

    def is_realizable(self, program: str, initial: State) -> bool:
        """Γ ⊢ P : T
        D : X × U × W → X
        ∀B_ij : Legal(B_ij)
        ∀M : ObsLegal(M)
        Commit(x') ↔ x' ∈ Z*
        Verified(P)
        ∃ℒ : Explain(ℒ) = Outcome
        """
        # Simplified check
        return self.is_valid(initial) and len(self.constraints) > 0 and self.energy_budget > 0


# ============================================================================
# DEMONSTRATION
# ============================================================================


def demo_omega_calculus():
    """Demonstrate AMOS Ω axiomatic calculus."""
    print("=" * 70)
    print("AMOS Ω — Axiomatic Calculus Demonstration")
    print("=" * 70)

    # Initialize system
    omega = AMOSOmega()

    # Add constraints (Axiom 9)
    omega.add_constraint(
        Constraint(
            name="energy_positive",
            constraint_type="hard",
            check=lambda s: s.classical.get("energy", 0) >= 0 if s.classical else True,
        )
    )

    omega.add_constraint(
        Constraint(
            name="time_monotonic",
            constraint_type="hard",
            check=lambda s: s.time is None or s.time >= 0,
        )
    )

    print("\n[Initial State]")
    x0 = State(classical={"value": 0.0, "energy": 100.0}, identity="test_agent", time=0.0)
    print(f"  x₀ = {x0}")

    print("\n[Substrate Check — Axiom 1]")
    substrates = omega.substrate_of(x0)
    print(f"  Substrates: {[s.name for s in substrates]}")
    print(f"  Primitive native: {omega.is_primitive_native(x0)}")

    print("\n[Action Definition — Axiom 3]")
    u0 = Action(
        name="increment",
        substrate=Substrate.CLASSICAL,
        effect={"value": 1.0},
        energy_cost=0.1,
        time_scale=1.0,
        pure=False,
    )
    print(f"  Action: {u0.name}")
    print(f"  Effect: {omega.effect_of(u0)}")
    print(f"  Pure: {omega.is_pure(u0)}")

    print("\n[Constraint Check — Axiom 9]")
    valid = omega.is_valid(x0)
    print(f"  Valid(x₀): {valid}")

    print("\n[Multi-Regime Admissibility — Axiom 21]")
    z_star = omega.Z_star(x0)
    print(f"  x₀ ∈ Z*: {z_star}")

    print("\n[Runtime Step — Axiom 29]")
    x1 = omega.runtime_step(x0, u0, {})
    if x1:
        print(f"  x₁ = {x1}")
        print("  Committed successfully")
    else:
        print("  Commit rejected — state not in Z*")

    print("\n[Ledger — Axiom 12 & 30]")
    ledger = omega.get_ledger()
    print(f"  Ledger entries: {len(ledger)}")
    if ledger:
        print(f"  Last entry: {ledger[-1].timestamp}")

    print("\n[Energy Accounting — Axiom 14]")
    print(f"  Budget: {omega.energy_budget}")
    print(f"  Consumed: {omega.energy_consumed}")
    print(f"  Remaining: {omega.energy_budget - omega.energy_consumed}")

    print("\n[Identity Preservation — Axiom 13]")
    if omega.identity_history:
        x_prev, x_curr = omega.identity_history[-1]
        preserved = omega.preserves_identity(x_prev, x_curr)
        print(f"  Identity preserved: {preserved}")

    print("\n[Grand Realizability — Axiom 32]")
    realizable = omega.is_realizable("test_program", x0)
    print(f"  Program realizable: {realizable}")

    print("\n" + "=" * 70)
    print("AMOS Ω — Governing Equation")
    print("=" * 70)
    print()
    print("  x_{t+1} = Commit_Z* ∘ R ∘ V ∘ M ∘ B ∘ A ∘ D (x_t, u_t, w_t)")
    print()
    print("  Outcome = Explain(ℒ)")
    print()
    print("=" * 70)
    print("✓ Axiomatic calculus demonstration complete")
    print("=" * 70)


if __name__ == "__main__":
    demo_omega_calculus()
