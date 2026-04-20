"""
Repo Doctor Omega - Entanglement Matrix

M_ij = α·Import(i,j) + β·Call(i,j) + γ·SharedTests(i,j) +
       δ·GitCoChange(i,j) + ε·SharedEntrypoints(i,j)

High entanglement means modules should be verified together.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class EntanglementEdge:
    """Single entanglement relationship between two modules."""

    source: str
    target: str
    import_coupling: float = 0.0
    call_coupling: float = 0.0
    test_coupling: float = 0.0
    cochange_coupling: float = 0.0
    entrypoint_coupling: float = 0.0

    @property
    def total(self) -> float:
        """Total entanglement strength."""
        return (
            self.import_coupling * 0.3
            + self.call_coupling * 0.4
            + self.test_coupling * 0.2
            + self.cochange_coupling * 0.1
            + self.entrypoint_coupling * 0.0
        )


class EntanglementMatrix:
    """
    Entanglement matrix M_ij for module coupling.
    """

    def __init__(self, modules: list[str]):
        self.modules = modules
        self.edges: dict[tuple[str, str], EntanglementEdge] = {}

    def add_edge(self, edge: EntanglementEdge) -> None:
        """Add entanglement edge."""
        key = (edge.source, edge.target)
        self.edges[key] = edge

    def get_entanglement(self, module_i: str, module_j: str) -> float:
        """Get entanglement strength between two modules."""
        key = (module_i, module_j)
        if key in self.edges:
            return self.edges[key].total
        # Check reverse
        key = (module_j, module_i)
        if key in self.edges:
            return self.edges[key].total
        return 0.0

    def get_neighbors(self, module: str, threshold: float = 0.1) -> list[tuple[str, float]]:
        """Get modules entangled with given module above threshold."""
        neighbors = []
        for (src, tgt), edge in self.edges.items():
            if src == module and edge.total >= threshold:
                neighbors.append((tgt, edge.total))
            elif tgt == module and edge.total >= threshold:
                neighbors.append((src, edge.total))
        return sorted(neighbors, key=lambda x: -x[1])

    def entropy(self, module: str) -> float:
        """
        Calculate entanglement entropy for a module.
        Ent(S) = - Σ p_j log p_j
        """
        neighbors = self.get_neighbors(module, threshold=0.01)
        if not neighbors:
            return 0.0

        total = sum(weight for _, weight in neighbors)
        if total == 0:
            return 0.0

        entropy = 0.0
        for _, weight in neighbors:
            p = weight / total
            if p > 0:
                entropy -= p * math.log(p)

        return entropy

    def to_matrix(self) -> dict[str, dict[str, float]]:
        """Convert to nested dictionary matrix."""
        matrix: dict[str, dict[str, float]] = {m: {} for m in self.modules}

        for (src, tgt), edge in self.edges.items():
            matrix[src][tgt] = edge.total
            matrix[tgt][src] = edge.total  # Symmetric

        return matrix


class EntanglementAnalyzer:
    """Analyze entanglement patterns in repository."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.matrix: Optional[EntanglementMatrix] = None

    def build_from_imports(self, import_graph: dict[str, list[str]]) -> None:
        """Build entanglement from import relationships."""
        modules = list(import_graph.keys())
        self.matrix = EntanglementMatrix(modules)

        for src, imports in import_graph.items():
            for tgt in imports:
                if tgt in modules:
                    edge = EntanglementEdge(
                        source=src,
                        target=tgt,
                        import_coupling=1.0,
                    )
                    self.matrix.add_edge(edge)

    def build_from_calls(self, call_graph: dict[str, list[str]]) -> None:
        """Build entanglement from call relationships."""
        if self.matrix is None:
            modules = list(call_graph.keys())
            self.matrix = EntanglementMatrix(modules)

        for src, calls in call_graph.items():
            for tgt in calls:
                if tgt in self.matrix.modules:
                    # Check if edge exists
                    key = (src, tgt)
                    if key in self.matrix.edges:
                        self.matrix.edges[key].call_coupling += 1.0
                    else:
                        edge = EntanglementEdge(
                            source=src,
                            target=tgt,
                            call_coupling=1.0,
                        )
                        self.matrix.add_edge(edge)

    def get_high_entanglement_pairs(self, threshold: float = 0.5) -> list[tuple[str, str, float]]:
        """Get pairs of modules with high entanglement."""
        if not self.matrix:
            return []

        pairs = []
        seen = set()

        for (src, tgt), edge in self.matrix.edges.items():
            if edge.total >= threshold:
                key = tuple(sorted([src, tgt]))
                if key not in seen:
                    pairs.append((src, tgt, edge.total))
                    seen.add(key)

        return sorted(pairs, key=lambda x: -x[2])

    def find_clusters(self) -> list[list[str]]:
        """Find tightly coupled module clusters."""
        if not self.matrix:
            return []

        # Simple clustering: connected components above threshold
        visited = set()
        clusters = []

        for module in self.matrix.modules:
            if module not in visited:
                cluster = self._dfs_cluster(module, visited, threshold=0.3)
                if len(cluster) > 1:
                    clusters.append(cluster)

        return clusters

    def _dfs_cluster(self, start: str, visited: set, threshold: float) -> list[str]:
        """DFS to find connected cluster."""
        cluster = []
        stack = [start]

        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                cluster.append(node)

                neighbors = self.matrix.get_neighbors(node, threshold)
                for neighbor, _ in neighbors:
                    if neighbor not in visited:
                        stack.append(neighbor)

        return cluster

    def analyze_patch_scope(self, changed_modules: List[str]) -> List[str]:
        """
        Determine which modules need revalidation given changed modules.
        High entanglement means broader revalidation needed.
        """
        if not self.matrix:
            return changed_modules

        to_check = set(changed_modules)

        for module in changed_modules:
            neighbors = self.matrix.get_neighbors(module, threshold=0.2)
            for neighbor, strength in neighbors:
                if strength > 0.5:
                    to_check.add(neighbor)

        return list(to_check)
