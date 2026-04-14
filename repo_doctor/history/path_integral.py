"""
Path Integral Blame Assignment

Action: S_k[path] = Στ (a1·||ΔΨ|| + a2·ΔEnt + a3·Δ[A_p, A_r] + a4·ΔH_entry)

Causality: P(t) ∝ exp(-S_k[0→t])
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import math


@dataclass
class PathAction:
    """Action accumulated along a path."""
    
    drift_component: float
    entanglement_component: float
    commutator_component: float
    entrypoint_component: float
    total: float


class PathIntegralBlame:
    """
    Compute action along history paths for blame assignment.
    
    S_k[path] = Στ (a1·||ΔΨ|| + a2·ΔEnt + a3·Δ[A_p, A_r] + a4·ΔH_entry)
    """

    def __init__(
        self,
        drift_weight: float = 1.0,
        entanglement_weight: float = 0.5,
        commutator_weight: float = 2.0,
        entrypoint_weight: float = 1.5,
    ):
        self.w_drift = drift_weight
        self.w_ent = entanglement_weight
        self.w_comm = commutator_weight
        self.w_entry = entrypoint_weight

    def compute_action(
        self,
        path: list[dict[str, Any]],
    ) -> PathAction:
        """
        Compute action along a path.
        
        Returns accumulated action components.
        """
        drift_sum = 0.0
        ent_sum = 0.0
        comm_sum = 0.0
        entry_sum = 0.0
        
        for i in range(1, len(path)):
            prev = path[i-1]
            curr = path[i]
            
            # Drift component
            prev_state = prev.get("state", {})
            curr_state = curr.get("state", {})
            drift = self._compute_drift(prev_state, curr_state)
            drift_sum += drift
            
            # Entanglement change
            prev_ent = prev.get("entanglement_entropy", 0.0)
            curr_ent = curr.get("entanglement_entropy", 0.0)
            ent_sum += abs(curr_ent - prev_ent)
            
            # API commutator change
            prev_comm = prev.get("api_commutator_norm", 0.0)
            curr_comm = curr.get("api_commutator_norm", 0.0)
            comm_sum += abs(curr_comm - prev_comm)
            
            # Entrypoint energy change
            prev_entry = prev.get("entrypoint_energy", 0.0)
            curr_entry = curr.get("entrypoint_energy", 0.0)
            entry_sum += abs(curr_entry - prev_entry)
        
        total = (
            self.w_drift * drift_sum +
            self.w_ent * ent_sum +
            self.w_comm * comm_sum +
            self.w_entry * entry_sum
        )
        
        return PathAction(
            drift_component=drift_sum,
            entanglement_component=ent_sum,
            commutator_component=comm_sum,
            entrypoint_component=entry_sum,
            total=total,
        )

    def _compute_drift(
        self,
        prev_state: dict[str, float],
        curr_state: dict[str, float],
    ) -> float:
        """Compute drift between two states."""
        import math
        total = 0.0
        all_dims = set(prev_state.keys()) | set(curr_state.keys())
        
        for dim in all_dims:
            prev = prev_state.get(dim, 1.0)
            curr = curr_state.get(dim, 1.0)
            total += (curr - prev) ** 2
        
        return math.sqrt(total)


class CausalityRanker:
    """
    Rank commits by causality using path integral.
    
    P(t) ∝ exp(-S_k[0→t])
    """

    def __init__(self, path_integral: PathIntegralBlame):
        self.pi = path_integral

    def rank_causality(
        self,
        history: list[dict[str, Any]],
    ) -> list[tuple[str, float]]:
        """
        Rank commits by causality probability.
        
        Returns: [(commit_hash, probability), ...] sorted by probability desc
        """
        results = []
        
        for i in range(1, len(history) + 1):
            path = history[:i]
            commit = history[i-1].get("hash", "unknown")
            
            action = self.pi.compute_action(path)
            prob = math.exp(-action.total)
            
            results.append((commit, prob))
        
        return sorted(results, key=lambda x: -x[1])

    def find_most_causal(
        self,
        history: list[dict[str, Any]],
        top_n: int = 3,
    ) -> list[tuple[str, float, PathAction]]:
        """
        Find most causally responsible commits.
        
        Returns: [(commit_hash, probability, action), ...]
        """
        results = []
        
        for i in range(1, len(history) + 1):
            path = history[:i]
            commit = history[i-1].get("hash", "unknown")
            
            action = self.pi.compute_action(path)
            prob = math.exp(-action.total)
            
            results.append((commit, prob, action))
        
        results.sort(key=lambda x: -x[1])
        return results[:top_n]
