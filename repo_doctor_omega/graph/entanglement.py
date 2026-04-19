"""Entanglement analysis for repository subsystem coupling.

Computes the entanglement matrix M_ij measuring coupling strength between
repository subsystems (modules, packages, layers).

Entanglement formalism:
    M_ij = coupling(i, j) ∈ [0, 1]

    where:
    - 0 = no coupling (independent)
    - 1 = maximally entangled (inseparable)

Coupling types:
    - Import coupling: Module i imports from module j
    - Call coupling: Functions in i call functions in j
    - Data coupling: Shared data structures
    - Inheritance coupling: Class inheritance across modules
    - Temporal coupling: Commit co-occurrence
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CouplingEdge:
    """A coupling edge between two subsystems."""

    source: str
    target: str
    strength: float  # ∈ [0, 1]
    coupling_type: str  # "import", "call", "data", "inheritance", "temporal"
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EntanglementMatrix:
    """Entanglement matrix M_ij for repository subsystems."""

    subsystems: List[str] = field(default_factory=list)
    edges: List[CouplingEdge] = field(default_factory=list)

    # Cached matrix
    _matrix: dict[tuple[str, str], float] = None

    def get_coupling(self, i: str, j: str) -> float:
        """Get coupling strength M_ij."""
        if self._matrix is None:
            self._build_matrix()

        key = (i, j)
        return self._matrix.get(key, 0.0) if self._matrix else 0.0

    def _build_matrix(self) -> None:
        """Build the coupling matrix from edges."""
        self._matrix = {}

        for edge in self.edges:
            key = (edge.source, edge.target)
            # Aggregate multiple edges (max strength)
            current = self._matrix.get(key, 0.0)
            self._matrix[key] = max(current, edge.strength)

    @property
    def total_entanglement(self) -> float:
        """Compute total repository entanglement."""
        if not self.edges:
            return 0.0
        return sum(e.strength for e in self.edges) / len(self.edges)

    def get_highly_entangled(self, threshold: float = 0.7) -> list[tuple[str, str, float]]:
        """Get pairs with coupling >= threshold."""
        result = []
        for edge in self.edges:
            if edge.strength >= threshold:
                result.append((edge.source, edge.target, edge.strength))
        return sorted(result, key=lambda x: x[2], reverse=True)

    def decoupling_candidates(self, max_coupling: float = 0.5) -> list[tuple[str, str, float]]:
        """Identify edges that should be decoupled (high coupling)."""
        return self.get_highly_entangled(threshold=max_coupling)

    def eigenvalue_approximation(self) -> list[tuple[str, float]]:
        """Approximate eigenvalues of coupling matrix (dominant subsystems)."""
        # Sum coupling per subsystem
        coupling_sums = {}
        for edge in self.edges:
            coupling_sums[edge.source] = coupling_sums.get(edge.source, 0.0) + edge.strength
            coupling_sums[edge.target] = coupling_sums.get(edge.target, 0.0) + edge.strength

        # Sort by total coupling (most entangled first)
        return sorted(coupling_sums.items(), key=lambda x: x[1], reverse=True)


class EntanglementAnalyzer:
    """Analyze entanglement between repository subsystems.

    Usage:
        analyzer = EntanglementAnalyzer("/path/to/repo")
        matrix = analyzer.analyze()

        # Check if two modules are entangled
        coupling = matrix.get_coupling("module_a", "module_b")

        # Find highly coupled pairs
        high = matrix.get_highly_entangled(threshold=0.8)

        # Identify decoupling candidates
        to_decouple = matrix.decoupling_candidates()
    """

    COUPLING_THRESHOLD_HIGH = 0.7
    COUPLING_THRESHOLD_CRITICAL = 0.9

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.edges: List[CouplingEdge] = []

    def analyze(self) -> EntanglementMatrix:
        """Perform complete entanglement analysis.

        Returns:
            EntanglementMatrix with all coupling edges
        """
        # Find Python modules
        modules = self._find_modules()

        # Analyze import coupling
        self._analyze_import_coupling(modules)

        # Analyze inheritance coupling
        self._analyze_inheritance_coupling(modules)

        # Build matrix
        return EntanglementMatrix(
            subsystems=list(modules.keys()),
            edges=self.edges,
        )

    def _find_modules(self) -> dict[str, Path]:
        """Find all Python modules in repository."""
        modules = {}

        for py_file in self.repo_path.rglob("*.py"):
            # Skip hidden, cache, venv
            rel_path = py_file.relative_to(self.repo_path)
            parts = rel_path.parts

            if any(p.startswith(".") or p in ["__pycache__", "venv", ".venv"] for p in parts):
                continue

            # Create module name from path
            module_name = str(rel_path.with_suffix("")).replace("/", ".")
            if module_name.endswith(".__init__"):
                module_name = module_name[:-9]  # Remove .__init__

            modules[module_name] = py_file

        return modules

    def _analyze_import_coupling(self, modules: Dict[str, Path]) -> None:
        """Analyze import-based coupling between modules."""
        import ast

        for module_name, file_path in modules.items():
            try:
                source = file_path.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(source)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            target = alias.name
                            # Check if target is in our modules
                            for mod_name in modules:
                                if target.startswith(mod_name):
                                    self._add_edge(module_name, mod_name, "import", 0.5)

                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            target = node.module
                            # Check if target is in our modules
                            for mod_name in modules:
                                if target.startswith(mod_name):
                                    # Stronger coupling for from imports
                                    self._add_edge(module_name, mod_name, "import", 0.7)

            except SyntaxError:
                continue
            except Exception:
                continue

    def _analyze_inheritance_coupling(self, modules: Dict[str, Path]) -> None:
        """Analyze inheritance-based coupling."""
        import ast

        for module_name, file_path in modules.items():
            try:
                source = file_path.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(source)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        for base in node.bases:
                            if isinstance(base, ast.Name):
                                base_name = base.id
                                # Check if base class is from another module
                                for mod_name in modules:
                                    if mod_name != module_name:
                                        # Check if base class might be from this module
                                        # (simplified - would need full symbol resolution)
                                        self._add_edge(module_name, mod_name, "inheritance", 0.6)

            except SyntaxError:
                continue
            except Exception:
                continue

    def _add_edge(self, source: str, target: str, edge_type: str, strength: float) -> None:
        """Add a coupling edge."""
        # Avoid self-loops
        if source == target:
            return

        self.edges.append(
            CouplingEdge(
                source=source,
                target=target,
                strength=strength,
                coupling_type=edge_type,
            )
        )

    def get_entanglement_report(self) -> Dict[str, Any]:
        """Generate entanglement analysis report."""
        matrix = self.analyze()

        high = matrix.get_highly_entangled(self.COUPLING_THRESHOLD_HIGH)
        critical = matrix.get_highly_entangled(self.COUPLING_THRESHOLD_CRITICAL)

        eigen = matrix.eigenvalue_approximation()[:5]  # Top 5

        return {
            "total_subsystems": len(matrix.subsystems),
            "total_edges": len(matrix.edges),
            "total_entanglement": matrix.total_entanglement,
            "high_entanglement_pairs": len(high),
            "critical_entanglement_pairs": len(critical),
            "top_coupled": eigen,
            "decoupling_candidates": matrix.decoupling_candidates(),
            "is_healthy": len(critical) == 0,
        }


def get_entanglement_analyzer(repo_path: str) -> EntanglementAnalyzer:
    """Factory function to create analyzer."""
    return EntanglementAnalyzer(repo_path)
