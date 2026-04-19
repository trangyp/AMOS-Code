"""
Repo Doctor Ω∞ - Collapse Operator

C_fail(|Ψ_repo⟩) = argmin_S { S | I_S = 0 and repair_cost(S) minimal }

Finds the minimal failing cut - the smallest broken subspace.
"""

from dataclasses import dataclass
from typing import Any

from .state.basis import StateDimension


@dataclass
class FailingCut:
    """A minimal failing subspace."""

    root_cause: str
    chain: List[str]
    affected_invariants: List[str]
    repair_cost_estimate: float


class CollapseOperator:
    """
    Collapse the failure surface to minimal cut.
    """

    def __init__(self):
        self.cuts: List[FailingCut] = []

    def find_minimal_cut(
        self,
        failed_invariants: List[str],
        graph_edges: dict[str, list[str]],
        invariant_chains: dict[str, list[str]],
    ) -> FailingCut:
        """
        Find minimal failing cut.

        Examples
        --------
        - launcher -> shell -> missing /dashboard command
        - guide -> tutorial -> stale interactive contract

        """
        # Simple strategy: find longest chain leading to failure
        max_chain = []
        root_cause = ""

        for inv in failed_invariants:
            chain = invariant_chains.get(inv, [inv])
            if len(chain) > len(max_chain):
                max_chain = chain
                root_cause = chain[0] if chain else inv

        return FailingCut(
            root_cause=root_cause,
            chain=max_chain,
            affected_invariants=failed_invariants,
            repair_cost_estimate=len(max_chain) * 10.0,
        )

    def collapse(
        self,
        state_amplitudes: dict[StateDimension, float],
        failed_invariants: List[str],
        threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Collapse state to find minimal broken subspace.
        """
        # Find collapsed dimensions
        collapsed = [dim.value for dim, amp in state_amplitudes.items() if amp < threshold]

        # Find articulation points
        articulation = self._find_articulation_points(collapsed)

        return {
            "collapsed_dimensions": collapsed,
            "articulation_points": articulation,
            "minimal_cut": self.cuts[0] if self.cuts else None,
            "repair_priority": collapsed[:3] if collapsed else [],
        }

    def _find_articulation_points(self, collapsed: List[str]) -> List[str]:
        """Find high-centrality modules that amplify failure."""
        # Simplified: first collapsed dimension is articulation
        return collapsed[:2] if collapsed else []
