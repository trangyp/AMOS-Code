"""
Repo Doctor Ω∞∞∞∞∞ - Entanglement Matrix and Entropy

Entanglement quantifies cross-module coupling and identifies
which failures are truly independent vs. correlated.

Key formulas:
- M_ij = coupling strength between dimensions i and j
- S = -Tr(ρ log ρ) - von Neumann entropy
- dS/dt = drift rate indicating system instability
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..state.basis import StateDimension
    from .substrate import GraphSubstrate


@dataclass
class EntanglementMatrix:
    """
    M_ij - Cross-dimensional coupling matrix.

    For each pair of state dimensions, stores:
    - coupling: strength of dependency (0-1)
    - shared_vertices: vertices involved in both dimensions
    - edge_count: number of cross-edges
    """

    # Matrix storage: (dim_i, dim_j) -> coupling info
    _matrix: dict[tuple[str, str], dict] = None

    def __post_init__(self):
        if self._matrix is None:
            self._matrix = {}

    def set_coupling(
        self,
        dim_i: StateDimension,
        dim_j: StateDimension,
        coupling: float,
        metadata: dict | None = None,
    ) -> None:
        """Set coupling between two dimensions."""
        key = (dim_i.value, dim_j.value)
        self._matrix[key] = {
            "coupling": coupling,
            "metadata": metadata or {},
        }
        # Symmetric matrix
        key_rev = (dim_j.value, dim_i.value)
        self._matrix[key_rev] = self._matrix[key]

    def get_coupling(self, dim_i: StateDimension, dim_j: StateDimension) -> float:
        """Get coupling strength between two dimensions."""
        key = (dim_i.value, dim_j.value)
        entry = self._matrix.get(key, {})
        return entry.get("coupling", 0.0)

    def compute_entropy(self, state_vector: dict[StateDimension, float]) -> float:
        """
        Compute von Neumann entropy: S = -Tr(ρ log ρ)

        For diagonal density matrix: S = -Σ p_i log(p_i)
        """
        entropy = 0.0
        for dim, amplitude in state_vector.items():
            if amplitude > 0:
                # Convert amplitude to probability
                p = amplitude**2
                entropy -= p * math.log(p) if p > 0 else 0
        return entropy

    def find_high_entanglement_pairs(
        self, threshold: float = 0.7
    ) -> list[tuple[StateDimension, StateDimension, float]]:
        """Find dimension pairs with coupling above threshold."""
        high_pairs = []
        seen = set()

        for (dim_i_val, dim_j_val), data in self._matrix.items():
            if dim_i_val >= dim_j_val:  # Avoid duplicates
                continue

            coupling = data.get("coupling", 0.0)
            if coupling >= threshold:
                # Need to reconstruct StateDimensions from values
                pair_key = (dim_i_val, dim_j_val)
                if pair_key not in seen:
                    seen.add(pair_key)
                    # Create tuple without actual StateDimension objects
                    # (they'll be resolved when needed)
                    high_pairs.append((dim_i_val, dim_j_val, coupling))

        return sorted(high_pairs, key=lambda x: x[2], reverse=True)


def compute_entanglement_from_graph(
    graph: GraphSubstrate, dimension_map: dict[str, StateDimension]
) -> EntanglementMatrix:
    """
    Compute entanglement matrix from graph substrate.

    Uses edge crossings between dimension-labeled vertices
    to compute coupling strengths.
    """
    matrix = EntanglementMatrix()

    # Count edges between dimensions
    from collections import defaultdict

    cross_edges = defaultdict(lambda: defaultdict(int))

    # Iterate through all edges
    for edge in graph.edges.values():
        source_dim = dimension_map.get(edge.source)
        target_dim = dimension_map.get(edge.target)

        if source_dim and target_dim and source_dim != target_dim:
            cross_edges[source_dim][target_dim] += 1

    # Normalize to coupling strengths
    for dim_i, targets in cross_edges.items():
        total_edges = sum(targets.values())
        for dim_j, count in targets.items():
            coupling = count / total_edges if total_edges > 0 else 0.0
            matrix.set_coupling(dim_i, dim_j, coupling)

    return matrix


def compute_drift_rate(current_entropy: float, previous_entropy: float, time_delta: float) -> float:
    """
    Compute drift rate: dS/dt

    High positive drift indicates rapid system degradation.
    """
    if time_delta <= 0:
        return 0.0
    return (current_entropy - previous_entropy) / time_delta
