from __future__ import annotations

"""Layer 18: Distributed Systems Physics Engine."""

import uuid
from dataclasses import dataclass, field


@dataclass
class InvariantResult:
    invariant_id: str
    name: str
    satisfied: bool
    severity: str
    evidence: list[str] = field(default_factory=list)


class DistributedPhysicsEngine:
    """Validates distributed truth, irreversibility, quiescence, entropy."""

    VERSION = "18.0.0"

    def __init__(self):
        self.engine_id = f"PHYSICS-{uuid.uuid4().hex[:8]}"

    def validate_truth_arbitration(self, domains: list[dict]) -> InvariantResult:
        failures = [
            f"Domain {d.get('name', '?')}: No mechanism"
            for d in domains
            if not d.get("arbitration_mechanism")
        ]
        return InvariantResult(
            "I_truth",
            "Truth Arbitration",
            len(failures) == 0,
            "critical" if failures else "none",
            failures or ["OK"],
        )

    def validate_irreversibility(self, transitions: list[dict]) -> InvariantResult:
        valid = ["reversible", "compensable", "irreversible"]
        failures = [
            f"Trans {t.get('name', '?')}: Not classified"
            for t in transitions
            if t.get("irreversibility_class") not in valid
        ]
        return InvariantResult(
            "I_irrev",
            "Irreversibility",
            len(failures) == 0,
            "critical" if failures else "none",
            failures or ["OK"],
        )

    def validate_compensation(self, transitions: list[dict]) -> InvariantResult:
        failures = [
            f"Trans {t.get('name', '?')}: No compensation"
            for t in transitions
            if t.get("irreversibility_class") == "irreversible" and not t.get("compensation_action")
        ]
        return InvariantResult(
            "I_comp",
            "Compensation",
            len(failures) == 0,
            "critical" if failures else "none",
            failures or ["OK"],
        )

    def validate_quiescence(self, subsystems: list[dict]) -> InvariantResult:
        failures = [
            f"Subsys {s.get('name', '?')}: No quiescent state"
            for s in subsystems
            if not s.get("quiescent_state_defined")
        ]
        return InvariantResult(
            "I_quiesce",
            "Quiescence",
            len(failures) == 0,
            "high" if failures else "none",
            failures or ["OK"],
        )

    def validate_policy_precedence(self, layers: list[dict]) -> InvariantResult:
        failures = [
            f"Layer {l.get('name', '?')}: No precedence"
            for l in layers
            if l.get("precedence_rank") is None
        ]
        return InvariantResult(
            "I_policy",
            "Policy Precedence",
            len(failures) == 0,
            "critical" if failures else "none",
            failures or ["OK"],
        )

    def validate_adaptive_bounds(self, loops: list[dict]) -> InvariantResult:
        failures = [
            f"Loop {l.get('name', '?')}: No drift bound"
            for l in loops
            if l.get("drift_bound") is None
        ]
        return InvariantResult(
            "I_adapt",
            "Adaptive Bounds",
            len(failures) == 0,
            "high" if failures else "none",
            failures or ["OK"],
        )

    def validate_entropy(self, measurements: list[dict]) -> InvariantResult:
        failures = []
        for m in measurements:
            if m.get("entropy_score", 0) > 0.8:
                failures.append(f"{m.get('name', '?')}: High entropy")
        return InvariantResult(
            "I_entropy",
            "Entropy Bounded",
            len(failures) == 0,
            "medium" if failures else "none",
            failures or ["OK"],
        )

    def assess_all(self, context: dict) -> dict:
        results = []
        if "domains" in context:
            results.append(self.validate_truth_arbitration(context["domains"]))
        if "transitions" in context:
            results.append(self.validate_irreversibility(context["transitions"]))
            results.append(self.validate_compensation(context["transitions"]))
        if "subsystems" in context:
            results.append(self.validate_quiescence(context["subsystems"]))
        if "policy_layers" in context:
            results.append(self.validate_policy_precedence(context["policy_layers"]))
        if "adaptive_loops" in context:
            results.append(self.validate_adaptive_bounds(context["adaptive_loops"]))
        if "entropy" in context:
            results.append(self.validate_entropy(context["entropy"]))
        failed = sum(1 for r in results if not r.satisfied)
        return {
            "engine_id": self.engine_id,
            "version": self.VERSION,
            "invariants": len(results),
            "failed": failed,
            "health": (len(results) - failed) / len(results) if results else 1.0,
        }

    def compute_state_vector_amplitudes(self, results: list[InvariantResult]) -> dict[str, float]:
        """
        Map invariant results to state vector amplitudes (Ω∞∞∞∞∞).

        Amplitudes:
        - αTruth: 1.0 if truth arbitration satisfied, else decay based on severity
        - αIrrev: 1.0 if irreversibility classification valid
        - αQui: 1.0 if quiescence defined
        - αPolicy: 1.0 if policy precedence established
        - αAdapt: 1.0 if adaptive bounds set
        - αEntropy: 1.0 - entropy_score (higher score = lower amplitude)
        """
        amplitudes = {}
        for result in results:
            if result.invariant_id == "I_truth":
                amplitudes["TRUTH_ARBITRATION"] = (
                    1.0 if result.satisfied else 0.3 if result.severity == "critical" else 0.6
                )
            elif result.invariant_id == "I_irrev":
                amplitudes["IRREVERSIBILITY_MANAGEMENT"] = 1.0 if result.satisfied else 0.2
            elif result.invariant_id == "I_comp":
                amplitudes["COMPENSATION"] = 1.0 if result.satisfied else 0.1
            elif result.invariant_id == "I_quiesce":
                amplitudes["QUIESCENCE_INTEGRITY"] = 1.0 if result.satisfied else 0.4
            elif result.invariant_id == "I_policy":
                amplitudes["POLICY_PRECEDENCE"] = 1.0 if result.satisfied else 0.25
            elif result.invariant_id == "I_adapt":
                amplitudes["ADAPTIVE_STABILITY"] = 1.0 if result.satisfied else 0.5
            elif result.invariant_id == "I_entropy":
                # Extract entropy score from evidence if available
                entropy_score = 0.0
                for ev in result.evidence:
                    if "High entropy" in ev:
                        entropy_score = 0.85
                amplitudes["ARCHITECTURAL_ENTROPY"] = 1.0 - entropy_score
        return amplitudes

    def generate_repair_actions(self, results: list[InvariantResult]) -> list[dict]:
        """Generate repair actions for failed physics invariants (MEDIC 2024 pattern)."""
        repairs = []
        for result in results:
            if not result.satisfied:
                repair = self._create_repair_for_invariant(result)
                if repair:
                    repairs.append(repair)
        return repairs

    def _create_repair_for_invariant(self, result: InvariantResult) -> dict:
        """Create repair action for a specific physics invariant failure."""
        repair_map = {
            "I_truth": {
                "dimension": "TRUTH_ARBITRATION",
                "priority": 1,
                "description": "Define truth arbitration mechanism",
                "fix_type": "architectural",
                "suggestion": "Add consensus mechanism (raft/paxos) or CRDT merge strategy",
                "auto_fixable": False,
                "risk": "high",
            },
            "I_irrev": {
                "dimension": "IRREVERSIBILITY_MANAGEMENT",
                "priority": 1,
                "description": "Classify transitions by irreversibility",
                "fix_type": "classification",
                "suggestion": "Tag each state transition as reversible/compensable/irreversible",
                "auto_fixable": True,
                "risk": "medium",
            },
            "I_comp": {
                "dimension": "IRREVERSIBILITY_MANAGEMENT",
                "priority": 1,
                "description": "Add compensation for irreversible actions",
                "fix_type": "saga_pattern",
                "suggestion": "Implement compensating transactions for rollback",
                "auto_fixable": False,
                "risk": "high",
            },
            "I_quiesce": {
                "dimension": "QUIESCENCE_INTEGRITY",
                "priority": 2,
                "description": "Define quiescent states for subsystems",
                "fix_type": "state_definition",
                "suggestion": "Add QUIESCENT state to state machine with drain behavior",
                "auto_fixable": True,
                "risk": "medium",
            },
            "I_policy": {
                "dimension": "POLICY_PRECEDENCE",
                "priority": 1,
                "description": "Establish policy hierarchy",
                "fix_type": "precedence",
                "suggestion": "Assign precedence ranks: security > consistency > availability",
                "auto_fixable": True,
                "risk": "high",
            },
            "I_adapt": {
                "dimension": "ADAPTIVE_STABILITY",
                "priority": 3,
                "description": "Set drift bounds for adaptive loops",
                "fix_type": "boundedness",
                "suggestion": "Add max_drift parameter and convergence timeout",
                "auto_fixable": True,
                "risk": "low",
            },
            "I_entropy": {
                "dimension": "ARCHITECTURAL_ENTROPY",
                "priority": 4,
                "description": "Reduce architectural entropy",
                "fix_type": "refactoring",
                "suggestion": "Consolidate scattered business logic, remove dead code",
                "auto_fixable": False,
                "risk": "medium",
            },
        }
        return repair_map.get(result.invariant_id)

    def compute_entanglement_matrix(self, context: dict) -> dict[tuple, float]:
        """
        Compute entanglement between distributed domains (Ω∞ coupling model).

        Entanglement strength indicates how much one domain's failure
        affects another. High entanglement means repairs must be coordinated.
        """
        entanglements = {}
        domains = context.get("domains", [])
        if len(domains) >= 2:
            for i, d1 in enumerate(domains):
                for j, d2 in enumerate(domains[i + 1 :], i + 1):
                    # Entanglement based on shared mechanisms or dependencies
                    shared = set(d1.get("dependencies", [])) & set(d2.get("dependencies", []))
                    mechanism_match = d1.get("arbitration_mechanism") == d2.get(
                        "arbitration_mechanism"
                    )
                    strength = 0.3 + (0.4 if shared else 0) + (0.3 if mechanism_match else 0)
                    entanglements[(d1.get("name"), d2.get("name"))] = round(strength, 2)
        return entanglements

    def get_critical_domains(
        self, entanglements: dict[tuple, float], threshold: float = 0.7
    ) -> list[str]:
        """Identify highly entangled domains that are critical to system stability."""
        domain_scores = {}
        for (d1, d2), strength in entanglements.items():
            if strength >= threshold:
                domain_scores[d1] = domain_scores.get(d1, 0) + strength
                domain_scores[d2] = domain_scores.get(d2, 0) + strength
        # Sort by total entanglement score
        return sorted(domain_scores.keys(), key=lambda d: domain_scores[d], reverse=True)
