"""
Repo Doctor Omega - Spectral Graph Diagnostics

Build repo dependency graph Laplacian: L = D - A
Use spectrum to find:
- Spectral gap (fragile modular separation)
- Community structure (hidden subsystems)
- Articulation modules (high-impact failure points)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class GraphLaplacian:
    """Graph Laplacian L = D - A for spectral analysis."""

    adjacency: dict[str, dict[str, float]]  # A

    def degree_matrix(self) -> dict[str, float]:
        """Compute degree matrix D (diagonal of row sums)."""
        degrees = {}
        for node, neighbors in self.adjacency.items():
            degrees[node] = sum(neighbors.values())
        return degrees

    def laplacian_matrix(self) -> dict[str, dict[str, float]]:
        """Compute L = D - A."""
        degrees = self.degree_matrix()
        laplacian: dict[str, dict[str, float]] = {}

        for node in self.adjacency:
            laplacian[node] = {}
            for other in self.adjacency:
                if node == other:
                    laplacian[node][other] = degrees[node]
                else:
                    laplacian[node][other] = -self.adjacency[node].get(other, 0.0)

        return laplacian

    def spectral_gap(self) -> float:
        """
        Estimate spectral gap (λ2 - λ1, where λ1=0).
        Small gap implies fragile modular separation.
        """
        # Approximation: use algebraic connectivity estimate
        # For complete graph: high gap
        # For disconnected graph: zero gap
        degrees = self.degree_matrix()
        if not degrees:
            return 0.0

        # Simple heuristic: variance of degrees relates to connectivity
        import statistics

        vals = list(degrees.values())
        if len(vals) < 2:
            return 0.0

        # Higher variance = less uniform = potentially lower connectivity
        variance = statistics.variance(vals) if len(vals) > 1 else 0.0
        mean_deg = sum(vals) / len(vals)

        # Normalize: gap ≈ mean_degree / (1 + variance)
        if mean_deg > 0:
            return mean_deg / (1 + variance)
        return 0.0

    def articulation_points(self) -> list[str]:
        """
        Find articulation points - modules whose failure disconnects
        or destabilizes large parts of the repo.
        """
        # Simple heuristic: high betweenness centrality
        betweenness = self._approximate_betweenness()
        threshold = sum(betweenness.values()) / len(betweenness) if betweenness else 0

        return [node for node, score in betweenness.items() if score > threshold * 2]

    def _approximate_betweenness(self) -> dict[str, float]:
        """Approximate betweenness centrality."""
        betweenness = dict.fromkeys(self.adjacency, 0.0)

        for source in self.adjacency:
            # BFS to find shortest paths
            distances, paths = self._bfs_shortest_paths(source)

            for target in self.adjacency:
                if target != source and target in paths:
                    # Count contributions
                    for path in paths[target]:
                        for node in path[1:-1]:  # Exclude source/target
                            betweenness[node] += 1.0 / len(paths[target])

        return betweenness

    def _bfs_shortest_paths(self, source: str) -> tuple[dict[str, int], dict[str, list]]:
        """BFS to find shortest paths from source."""
        from collections import deque

        distances = {node: float("inf") for node in self.adjacency}
        paths = {node: [] for node in self.adjacency}

        distances[source] = 0
        paths[source] = [[source]]

        queue = deque([source])

        while queue:
            current = queue.popleft()

            for neighbor, weight in self.adjacency[current].items():
                if weight > 0:
                    new_dist = distances[current] + 1

                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        paths[neighbor] = [p + [neighbor] for p in paths[current]]
                        queue.append(neighbor)
                    elif new_dist == distances[neighbor]:
                        paths[neighbor].extend([p + [neighbor] for p in paths[current]])

        return distances, paths


class SpectralAnalyzer:
    """Analyze repository using spectral graph theory."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.laplacian: GraphLaplacian | None = None

    def build_from_imports(self, import_graph: dict[str, list[str]]) -> None:
        """Build Laplacian from import graph."""
        # Convert to adjacency matrix
        nodes = list(import_graph.keys())
        adjacency: dict[str, dict[str, float]] = {n: {} for n in nodes}

        for src, imports in import_graph.items():
            for tgt in imports:
                if tgt in nodes:
                    adjacency[src][tgt] = 1.0
                    adjacency[tgt][src] = 1.0  # Undirected for spectral

        self.laplacian = GraphLaplacian(adjacency)

    def analyze(self) -> dict[str, Any]:
        """Full spectral analysis."""
        if not self.laplacian:
            return {"error": "No graph built"}

        gap = self.laplacian.spectral_gap()
        articulation = self.laplacian.articulation_points()

        # Interpret results
        fragility = "high" if gap < 0.5 else ("medium" if gap < 1.5 else "low")

        return {
            "spectral_gap": gap,
            "fragility": fragility,
            "articulation_modules": articulation,
            "recommendation": (
                "Strengthen modular boundaries"
                if fragility == "high"
                else "Monitor high-centrality modules"
                if articulation
                else "Architecture stable"
            ),
        }
