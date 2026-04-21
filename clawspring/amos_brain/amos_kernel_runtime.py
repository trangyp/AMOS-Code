"""AMOS Kernel Runtime - Production implementation of AMOS kernel contracts.

This module provides the concrete implementation of:
- BrainKernel: State-to-branch engine with law binding
- CollapseKernel: Lawful branch selector
- CascadeKernel: Morph execution system

Architecture: Observe → Update → Generate → Simulate → Filter → Collapse → Execute
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone

from enum import Enum, auto
from typing import Any, Optional

# ============================================================================
# Core AMOS Data Structures
# ============================================================================


@dataclass
class StateGraph:
    """U_t = (V_t, E_t, S_t, Λ_t) - Universal state graph at time t."""

    vertices: set[str] = field(default_factory=set)
    edges: dict[tuple[str, str], dict[str, Any]] = field(default_factory=dict)
    state_vars: dict[str, float] = field(default_factory=dict)
    active_laws: set[str] = field(default_factory=set)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def compute_hash(self) -> str:
        """Compute canonical state hash S."""
        data = {
            "vertices": sorted(self.vertices),
            "edges": sorted(str(e) for e in self.edges.items()),
            "state_vars": self.state_vars,
            "active_laws": sorted(self.active_laws),
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]


@dataclass
class Invariant:
    """Mathematical invariant with validation."""

    id: str
    name: str
    check_fn: Callable[[StateGraph], bool]
    priority: int = 1

    def check(self, state: StateGraph) -> bool:
        return self.check_fn(state)


@dataclass
class StateVariables:
    """Core AMOS variables extracted from state."""

    omega: float = 0.0  # Ω: Uncertainty/entropy
    kappa: float = 1.0  # K: Knowledge/confidence
    phi: float = 1.0  # Φ: Coherence score
    invariants: list[Invariant] = field(default_factory=list)  # I: Active constraints
    state_hash: str = ""  # S: Canonical representation

    @property
    def drift(self) -> float:
        """σ = Ω / K"""
        return self.omega / self.kappa if self.kappa > 0 else float("inf")

    @property
    def legality(self) -> float:
        """L = I × S (simplified as active invariant count × coherence)"""
        return len(self.invariants) * self.phi


@dataclass
class LawViolation:
    """Violation of an AMOS law."""

    law_id: str
    description: str
    severity: float


class OperatingMode(Enum):
    """AMOS operating modes."""

    NORMAL = auto()
    CONSERVATIVE = auto()
    RECOVERY = auto()
    EMERGENCY = auto()


@dataclass
class LegalityAssessment:
    """L = I × S computation result."""

    is_legal: bool
    legality_score: float
    drift_coefficient: float
    violations: list[LawViolation]
    required_mode: OperatingMode


@dataclass
class AMOSScores:
    """AMOS-specific branch scoring metrics."""

    goal_fit: float = 0.0
    risk: float = 0.0
    cost: float = 0.0
    coherence: float = 0.0
    drift: float = 0.0
    reversibility: float = 0.0
    confidence: float = 0.0

    @property
    def composite(self) -> float:
        """Weighted aggregate score."""
        return (
            0.3 * self.goal_fit
            + 0.2 * self.coherence
            + 0.2 * self.reversibility
            + 0.15 * self.confidence
            - 0.1 * self.risk
            - 0.05 * self.drift
        )


@dataclass
class Morph:
    """State morphing operation with rollback support."""

    id: str
    target: str
    operation: str
    scope: dict[str, Any] = field(default_factory=dict)
    preconditions: list[str] = field(default_factory=list)
    postconditions: list[str] = field(default_factory=list)
    rollback_fn: Optional[Callable[[], None]] = None
    estimated_cost: float = 1.0
    risk: float = 0.1


@dataclass
class Branch:
    """Candidate branch with scoring and legality."""

    id: str
    source_state: StateGraph
    target_state: StateGraph
    morphs: list[Morph] = field(default_factory=list)
    scores: Optional[AMOSScores] = None
    legality: Optional[LegalityAssessment] = None


# ============================================================================
# BrainKernel: State-to-Branch Engine
# ============================================================================


class BrainKernel:
    """Lawful branch generator + simulator.

    NOT: "thing that thinks in words"
    IS:  "state-to-branch engine"

    Responsibilities:
    1. Ingest state into U_t
    2. Extract Ω, K, Φ, I, S
    3. Apply ULK laws (L = I × S)
    4. Generate candidate branches Ψ_t
    5. Simulate and score branches
    6. Pass lawful branches to collapse
    """

    def __init__(self):
        self.invariant_registry: dict[str, Invariant] = {}
        self._register_default_invariants()

    def _register_default_invariants(self) -> None:
        """Register AMOS core invariants."""
        self.invariant_registry["identity"] = Invariant(
            id="I1",
            name="Identity Preservation",
            check_fn=lambda s: len(s.vertices) > 0,
            priority=1,
        )
        self.invariant_registry["coherence"] = Invariant(
            id="I2",
            name="State Coherence",
            check_fn=lambda s: all(v in s.vertices for e in s.edges for v in e),
            priority=2,
        )

    def ingest(self, observation: dict[str, Any]) -> StateGraph:
        """Stage 1: Ingest current state into U_t.

        Transform raw observation into structured state graph.
        """
        U_t = StateGraph(timestamp=datetime.now(timezone.utc))

        # Extract entities → V_t
        if "entities" in observation:
            U_t.vertices.update(str(e) for e in observation["entities"])

        # Extract relationships → E_t
        if "relations" in observation:
            for rel in observation["relations"]:
                if "source" in rel and "target" in rel:
                    edge_key = (str(rel["source"]), str(rel["target"]))
                    U_t.edges[edge_key] = rel.get("properties", {})

        # Load applicable laws → Λ_t
        U_t.active_laws = {"L1", "L2", "L3", "L4"}

        return U_t

    def extract_variables(self, U_t: StateGraph) -> StateVariables:
        """Stage 2: Extract structural variables.

        Returns Ω, K, Φ, I, S from state graph.
        """
        # Ω: Uncertainty (entropy approximation)
        omega = math.log2(max(1, len(U_t.vertices)))

        # K: Knowledge (inverse of edge sparsity)
        possible_edges = len(U_t.vertices) * (len(U_t.vertices) - 1) / 2
        actual_edges = len(U_t.edges)
        kappa = actual_edges / max(1, possible_edges) if possible_edges > 0 else 1.0

        # Φ: Coherence (graph consistency)
        phi = self._compute_coherence(U_t)

        # I: Active invariants
        active_invariants = [inv for inv in self.invariant_registry.values() if inv.check(U_t)]

        # S: State hash
        state_hash = U_t.compute_hash()

        return StateVariables(
            omega=omega,
            kappa=kappa,
            phi=phi,
            invariants=active_invariants,
            state_hash=state_hash,
        )

    def _compute_coherence(self, U_t: StateGraph) -> float:
        """Compute graph coherence Φ."""
        if not U_t.vertices:
            return 1.0

        # Check edge validity
        valid_edges = sum(
            1 for (src, tgt) in U_t.edges.keys() if src in U_t.vertices and tgt in U_t.vertices
        )
        total_edges = len(U_t.edges)

        return valid_edges / max(1, total_edges)

    def apply_laws(self, vars: StateVariables) -> LegalityAssessment:
        """Stage 3: Apply ULK laws.

        Compute L = I × S and σ = Ω / K.
        """
        # L = I × S (legality = invariant count × coherence)
        legality_score = vars.legality

        # σ = Ω / K (drift)
        sigma = vars.drift

        # Check violations
        violations = []
        if sigma > 1.0:
            violations.append(
                LawViolation(
                    law_id="L1",
                    description=f"Drift σ = {sigma:.2f} > 1",
                    severity=min(1.0, sigma / 2),
                )
            )

        if vars.phi < 0.5:
            violations.append(
                LawViolation(
                    law_id="L2",
                    description=f"Coherence Φ = {vars.phi:.2f} < 0.5",
                    severity=0.5 - vars.phi,
                )
            )

        # Determine required mode
        if sigma > 2.0 or vars.phi < 0.3:
            required_mode = OperatingMode.EMERGENCY
        elif sigma > 1.0 or vars.phi < 0.5:
            required_mode = OperatingMode.CONSERVATIVE
        else:
            required_mode = OperatingMode.NORMAL

        return LegalityAssessment(
            is_legal=legality_score > 0.5 and len(violations) == 0,
            legality_score=legality_score,
            drift_coefficient=sigma,
            violations=violations,
            required_mode=required_mode,
        )

    def generate_branches(
        self, U_t: StateGraph, assessment: LegalityAssessment, goal: dict[str, Any]
    ) -> list[Branch]:
        """Stage 4: Generate candidate branches.

        Create multiple candidate futures B_i.
        Only generate branches that pass law binding.
        """
        branches = []

        # Branch 1: Conservative approach
        if assessment.required_mode in [OperatingMode.NORMAL, OperatingMode.CONSERVATIVE]:
            b1 = self._create_branch("B1", U_t, goal, risk_aversion=0.8, exploration=0.2)
            if b1:
                branches.append(b1)

        # Branch 2: Balanced approach
        b2 = self._create_branch("B2", U_t, goal, risk_aversion=0.5, exploration=0.5)
        if b2:
            branches.append(b2)

        # Branch 3: Exploratory approach (only if drift low)
        if assessment.drift_coefficient < 0.5:
            b3 = self._create_branch("B3", U_t, goal, risk_aversion=0.2, exploration=0.8)
            if b3:
                branches.append(b3)

        return branches

    def _create_branch(
        self,
        branch_id: str,
        U_t: StateGraph,
        goal: dict[str, Any],
        risk_aversion: float,
        exploration: float,
    ) -> Branch | None:
        """Create a single candidate branch."""
        # Generate target state
        target = deepcopy(U_t)

        # Apply exploration to target
        if "add_entities" in goal:
            for entity in goal["add_entities"]:
                if exploration > 0.5 or hash(entity) % 2 == 0:
                    target.vertices.add(str(entity))

        # Generate morphs
        morphs = self._generate_morphs(U_t, target, risk_aversion)

        return Branch(
            id=branch_id,
            source_state=U_t,
            target_state=target,
            morphs=morphs,
            scores=AMOSScores(),  # Will be filled by simulate
            legality=LegalityAssessment(
                is_legal=True,
                legality_score=1.0,
                drift_coefficient=0.0,
                violations=[],
                required_mode=OperatingMode.NORMAL,
            ),
        )

    def _generate_morphs(
        self, source: StateGraph, target: StateGraph, risk_aversion: float
    ) -> list[Morph]:
        """Generate morphs to transform source to target."""
        morphs = []

        # Add operations for new vertices
        new_vertices = target.vertices - source.vertices
        for v in new_vertices:
            morphs.append(
                Morph(
                    id=f"add_{v}",
                    target=v,
                    operation="add_vertex",
                    scope={"vertex": v},
                    preconditions=[lambda s, v=v: v not in s.vertices],
                    postconditions=[lambda s, v=v: v in s.vertices],
                    rollback_fn=lambda v=v: print(f"Rollback: remove {v}"),
                    estimated_cost=1.0,
                    risk=0.1 * (1 - risk_aversion),
                )
            )

        return morphs

    def simulate(
        self, branches: list[Branch], U_t: StateGraph, goal: dict[str, Any]
    ) -> list[Branch]:
        """Stage 5: Simulate each branch.

        Score each B_i on AMOS metrics.
        """
        scored_branches = []

        for branch in branches:
            scores = AMOSScores()

            # Goal fit: How well does target state match goal?
            if "add_entities" in goal:
                target_entities = set(str(e) for e in goal["add_entities"])
                achieved = len(branch.target_state.vertices & target_entities)
                total = len(target_entities)
                scores.goal_fit = achieved / max(1, total)

            # Risk: Aggregate morph risk
            scores.risk = sum(m.risk for m in branch.morphs) / max(1, len(branch.morphs))

            # Cost: Aggregate morph cost
            scores.cost = sum(m.estimated_cost for m in branch.morphs)

            # Coherence: Post-state consistency
            scores.coherence = self._compute_coherence(branch.target_state)

            # Drift: σ after execution
            target_vars = self.extract_variables(branch.target_state)
            scores.drift = target_vars.drift

            # Reversibility: Can we rollback?
            scores.reversibility = sum(1 for m in branch.morphs if m.rollback_fn is not None) / max(
                1, len(branch.morphs)
            )

            # Confidence: Simulation certainty (simplified)
            scores.confidence = 0.8 - 0.1 * scores.drift

            branch.scores = scores
            scored_branches.append(branch)

        # Sort by composite score
        scored_branches.sort(key=lambda b: b.scores.composite, reverse=True)

        return scored_branches

    def pass_to_collapse(self, branches: list[Branch]) -> list[Branch]:
        """Stage 6: Pass lawful branches to collapse.

        Return only branches where legality is confirmed.
        """
        # Filter to lawful branches only
        lawful = [b for b in branches if b.legality.is_legal]

        # Additional filtering by hard constraints
        valid = []
        for b in lawful:
            if b.scores.risk < 0.8 and b.scores.drift < 2.0:
                valid.append(b)

        return valid if valid else lawful  # Return lawful if no valid


# ============================================================================
# CollapseKernel: Lawful Selector
# ============================================================================


class CollapseKernel:
    """Lawful branch selector.

    NOT: "ordinary ranking"
    IS:  "constrained optimization over legal branches"
    """

    def receive_branches(self, branches: list[Branch]) -> list[Branch]:
        """Stage 1: Receive simulated branch field.

        Validate all branches have required data.
        """
        validated = []
        for b in branches:
            if b.scores and b.legality:
                validated.append(b)
        return validated

    def apply_collapse_function(self, branches: list[Branch]) -> Optional[Branch]:
        """Stage 2: Apply lawful collapse.

        B* = argmax [weighted composite score]
        Subject to hard constraints.
        """
        if not branches:
            return None

        # Constraint filtering
        feasible = []
        for b in branches:
            # Hard constraints
            if b.legality.legality_score < 0.3:
                continue
            if b.scores.risk > 0.9:
                continue
            if b.scores.drift > 3.0:
                continue
            feasible.append(b)

        if not feasible:
            feasible = branches  # Relax constraints if none feasible

        # Constrained optimization: select by composite score
        best = max(feasible, key=lambda b: b.scores.composite)
        return best

    def validate_selection(self, selected: Branch, candidates: list[Branch]) -> bool:
        """Stage 3: Verify selection.

        Check selection is from valid candidate set.
        """
        return selected in candidates

    def emit_to_cascade(self, B_star: Branch) -> dict[str, Any]:
        """Stage 4: Emit B* to Cascade.

        Package with verification proof and rollback plan.
        """
        return {
            "branch": B_star,
            "verification": {
                "from_set": True,
                "legality_confirmed": B_star.legality.is_legal,
                "score": B_star.scores.composite,
            },
            "rollback_plan": [m.rollback_fn for m in B_star.morphs],
            "mode": B_star.legality.required_mode.value,
        }


# ============================================================================
# CascadeKernel: Morph Execution System
# ============================================================================


class CascadeKernel:
    """Morph compiler + transaction executor.

    NOT: "workflow chain"
    IS:  "Normalize → Check → Stage → Snapshot → Apply → Verify → Commit"
    """

    def __init__(self):
        self.execution_log: list[dict[str, Any]] = []

    def accept_branch(self, cascade_input: dict[str, Any]) -> list[Morph]:
        """Stage 1: Accept B* from Collapse.

        Convert to typed morphs.
        """
        branch = cascade_input.get("branch")
        return branch.morphs if branch else []

    def normalize(self, morphs: list[Morph]) -> list[Morph]:
        """Stage 2: Normalize morphs.

        Ensure all parameters typed, preconditions explicit.
        """
        normalized = []
        for m in morphs:
            # Ensure scope is serializable
            scope = {k: str(v) for k, v in m.scope.items()}
            normalized.append(
                Morph(
                    id=m.id,
                    target=m.target,
                    operation=m.operation,
                    scope=scope,
                    preconditions=m.preconditions,
                    postconditions=m.postconditions,
                    rollback_fn=m.rollback_fn,
                    estimated_cost=m.estimated_cost,
                    risk=m.risk,
                )
            )
        return normalized

    def check(self, normalized: list[Morph], current_state: StateGraph) -> bool:
        """Stage 3: Check preconditions.

        If any check fails: HALT and return to Brain.
        """
        for m in normalized:
            for precond in m.preconditions:
                if not precond(current_state):
                    return False
        return True

    def stage(self, normalized: list[Morph]) -> dict[str, Any]:
        """Stage 4: Stage execution.

        Prepare resource allocation.
        """
        return {
            "morphs": normalized,
            "resources_reserved": sum(m.estimated_cost for m in normalized),
            "staged_at": datetime.now(timezone.utc).isoformat(),
        }

    def snapshot(self, staged: dict[str, Any], current_state: StateGraph) -> dict[str, Any]:
        """Stage 5: Create rollback snapshot.

        Capture full state for rollback capability.
        """
        return {
            "staged": staged,
            "state_capture": deepcopy(current_state),
            "snapshot_at": datetime.now(timezone.utc).isoformat(),
        }

    def apply(self, snapshot: dict[str, Any]) -> StateGraph:
        """Stage 6: Apply morphs.

        Execute operations.
        """
        state = deepcopy(snapshot["state_capture"])
        morphs = snapshot["staged"]["morphs"]

        for m in morphs:
            # Apply operation
            if m.operation == "add_vertex":
                state.vertices.add(m.target)

            self.execution_log.append(
                {
                    "morph_id": m.id,
                    "operation": m.operation,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        return state

    def verify(self, applied: StateGraph, expected: StateGraph) -> bool:
        """Stage 7: Verify postconditions.

        If verification fails: ROLLBACK.
        """
        # Check all expected vertices present
        if not expected.vertices.issubset(applied.vertices):
            return False

        # Check coherence maintained
        coherence = len([e for e in applied.edges if all(v in applied.vertices for v in e)]) / max(
            1, len(applied.edges)
        )

        return coherence > 0.8

    def commit(self, verified: StateGraph) -> StateGraph:
        """Stage 8: Commit changes.

        Finalize changes, emit U_{t+1}.
        """
        verified.timestamp = datetime.now(timezone.utc)
        return verified

    def rollback(self, snapshot: dict[str, Any], reason: str) -> StateGraph:
        """Rollback Handler.

        Restore from snapshot, emit failure signal.
        """
        # Execute rollback functions
        staged = snapshot["staged"]
        for m in staged["morphs"]:
            if m.rollback_fn:
                m.rollback_fn()

        # Return to previous state
        return snapshot["state_capture"]


# ============================================================================
# Constitution Gate
# ============================================================================


class ConstitutionGate:
    """Mandatory admission gate for ALL actions.

    Position: BEFORE Brain, Collapse, or Cascade operations.
    """

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold

    def admit(self, proposal: Any, context: StateGraph) -> dict[str, Any]:
        """Check proposal against constitution.

        Returns admission decision with legality score.
        """
        # Compute variables
        omega = math.log2(max(1, len(context.vertices)))
        kappa = len(context.edges) / max(1, len(context.vertices) * (len(context.vertices) - 1) / 2)
        sigma = omega / kappa if kappa > 0 else float("inf")

        # Check coherence
        coherence = len([e for e in context.edges if all(v in context.vertices for v in e)]) / max(
            1, len(context.edges)
        )

        # Legality check (always compute)
        legality = coherence * len(context.active_laws)

        # Collapse condition
        if sigma > 1 and coherence < 0.5:
            return {
                "admitted": False,
                "reason": f"COLLAPSE_CONDITION: σ={sigma:.2f} > 1 AND Φ={coherence:.2f} < 0.5",
                "sigma": sigma,
                "coherence": coherence,
                "legality": legality,
                "mode": OperatingMode.EMERGENCY,
            }

        return {
            "admitted": legality > self.threshold,
            "legality": legality,
            "sigma": sigma,
            "coherence": coherence,
            "mode": (OperatingMode.NORMAL if legality > 0.7 else OperatingMode.CONSERVATIVE),
        }


# ============================================================================
# AMOS Runtime Facade
# ============================================================================


class AMOSKernelRuntime:
    """Unified facade for AMOS kernel operations.

    Usage:
        runtime = AMOSKernelRuntime()
        result = runtime.execute_cycle(observation, goal)
    """

    def __init__(self):
        self.brain = BrainKernel()
        self.collapse = CollapseKernel()
        self.cascade = CascadeKernel()
        self.constitution = ConstitutionGate()

    def execute_cycle(self, observation: dict[str, Any], goal: dict[str, Any]) -> dict[str, Any]:
        """Execute full AMOS cycle.

        Observe → Update → Generate → Simulate → Filter → Collapse → Execute
        """
        # OBEY: Constitution gate before any action
        temp_state = self.brain.ingest(observation)
        admission = self.constitution.admit(goal, temp_state)

        if not admission["admitted"]:
            return {
                "status": "REJECTED",
                "reason": admission["reason"],
                "legality": admission["legality"],
                "sigma": admission["sigma"],
            }

        # Stage 1: Ingest
        U_t = self.brain.ingest(observation)

        # Stage 2: Extract variables
        vars = self.brain.extract_variables(U_t)

        # Stage 3: Apply laws
        assessment = self.brain.apply_laws(vars)

        # Stage 4: Generate branches
        branches = self.brain.generate_branches(U_t, assessment, goal)

        # Stage 5: Simulate
        scored = self.brain.simulate(branches, U_t, goal)

        # Stage 6: Filter lawful branches
        lawful = self.brain.pass_to_collapse(scored)

        if not lawful:
            return {
                "status": "NO_LAWFUL_BRANCHES",
                "sigma": vars.drift,
                "legality": assessment.legality_score,
            }

        # Stage 7: Collapse
        validated = self.collapse.receive_branches(lawful)
        B_star = self.collapse.apply_collapse_function(validated)

        if not B_star:
            return {"status": "COLLAPSE_FAILED"}

        # Stage 8: Validate selection
        if not self.collapse.validate_selection(B_star, validated):
            return {"status": "VALIDATION_FAILED"}

        # Stage 9: Emit to cascade
        cascade_input = self.collapse.emit_to_cascade(B_star)

        # Stage 10-17: Cascade execution
        morphs = self.cascade.accept_branch(cascade_input)
        normalized = self.cascade.normalize(morphs)

        if not self.cascade.check(normalized, U_t):
            return {"status": "PRECONDITION_FAILED", "return_to": "BRAIN"}

        staged = self.cascade.stage(normalized)
        snapshot = self.cascade.snapshot(staged, U_t)
        applied = self.cascade.apply(snapshot)

        if not self.cascade.verify(applied, B_star.target_state):
            # ROLLBACK
            recovered = self.cascade.rollback(snapshot, "VERIFICATION_FAILED")
            return {
                "status": "ROLLBACK",
                "reason": "VERIFICATION_FAILED",
                "recovered_state": recovered,
            }

        # COMMIT
        U_t1 = self.cascade.commit(applied)

        return {
            "status": "SUCCESS",
            "U_t": U_t,
            "U_t1": U_t1,
            "selected_branch": B_star.id,
            "scores": B_star.scores,
            "sigma": vars.drift,
            "legality": assessment.legality_score,
            "mode": assessment.required_mode.name,
        }


# Singleton instance
_kernel_runtime: Optional[AMOSKernelRuntime] = None


def get_kernel_runtime() -> AMOSKernelRuntime:
    """Get or create AMOS kernel runtime singleton."""
    global _kernel_runtime
    if _kernel_runtime is None:
        _kernel_runtime = AMOSKernelRuntime()
    return _kernel_runtime
