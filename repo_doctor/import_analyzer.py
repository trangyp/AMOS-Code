"""
Import Dependency Analyzer for Repo Doctor Omega
===================================================

Tree-sitter based import analysis for AMOS repository.
Based on 2024 best practices from Google Importlab and HRT research.

This module addresses the "tangling" problem where dependency cycles
cause performance degradation and reduced reliability.

Usage:
    from repo_doctor.import_analyzer import ImportAnalyzer

    analyzer = ImportAnalyzer("/path/to/repo")
    graph = analyzer.build_dependency_graph()
    cycles = analyzer.find_cycles()
    metrics = analyzer.calculate_coupling_metrics()
"""

import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

# NOTE: tree_sitter imports are lazy-loaded in _ensure_parser() to avoid
# ~70ms import time when the module is imported but not used

if TYPE_CHECKING:
    from tree_sitter import Language, Parser, Query


@dataclass
class ImportInfo:
    """Represents an import statement."""

    source_file: str
    imported_module: str
    is_relative: bool = False
    is_from_import: bool = False
    line_number: int = 0


@dataclass
class DependencyGraph:
    """Dependency graph G = (V, E) for Python modules."""

    vertices: Set[str] = field(default_factory=set)  # Python modules
    edges: list[tuple[str, str]] = field(default_factory=list)  # (importer, imported)

    # Reverse lookup
    in_degree: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    out_degree: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))

    def add_edge(self, importer: str, imported: str) -> None:
        """Add an import relationship to the graph."""
        self.vertices.add(importer)
        self.vertices.add(imported)
        self.edges.append((importer, imported))
        self.out_degree[importer].add(imported)
        self.in_degree[imported].add(importer)

    def get_dependencies(self, module: str) -> set[str]:
        """Get all modules that 'module' imports."""
        return self.out_degree.get(module, set())

    def get_dependents(self, module: str) -> set[str]:
        """Get all modules that import 'module'."""
        return self.in_degree.get(module, set())

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "vertices": list(self.vertices),
            "edges": list(self.edges),
            "in_degree": {k: list(v) for k, v in self.in_degree.items()},
            "out_degree": {k: list(v) for k, v in self.out_degree.items()},
        }


@dataclass
class CouplingMetrics:
    """Coupling analysis results."""

    module: str
    afferent_coupling: int = 0  # In-degree: modules that depend on this
    efferent_coupling: int = 0  # Out-degree: modules this depends on
    instability: float = 0.0  # Eff / (Eff + Aff)
    in_cycle: bool = False

    def calculate_instability(self) -> float:
        """Calculate instability metric (0=stable, 1=unstable)."""
        total = self.efferent_coupling + self.afferent_coupling
        if total == 0:
            self.instability = 0.0
        else:
            self.instability = self.efferent_coupling / total
        return self.instability


class ImportAnalyzer:
    """
    Tree-sitter based import dependency analyzer.

    Uses AST queries to extract imports without executing code,
    making it faster and safer than import-time analysis.
    """

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()

        # Lazy-loaded Tree-sitter resources (48ms initialization deferred)
        self._parser: Optional[Parser] = None
        self._import_query: Optional[Query] = None
        self._py_language: Optional[Language] = None

    def _ensure_parser(self) -> None:
        """Lazy initialize tree-sitter parser on first use."""
        if self._parser is not None:
            return

        # Lazy import tree-sitter (expensive - ~70ms at module level)
        import tree_sitter_python as tspython
        from tree_sitter import Language, Parser, Query

        # Initialize Tree-sitter
        self._py_language = Language(tspython.language())
        self._parser = Parser(self._py_language)

        # Tree-sitter query for import statements
        # Matches: import x, from x import y
        self._import_query = Query(
            self._py_language,
            """
            (import_statement
              name: (dotted_name) @import.name)

            (import_from_statement
              module_name: (dotted_name) @from.name)

            (import_from_statement
              module_name: (relative_import) @from.relative)
        """,
        )

    @property
    def parser(self) -> "Parser":
        """Lazy-loaded parser."""
        if self._parser is None:
            self._ensure_parser()
        return self._parser

    @property
    def import_query(self) -> "Query":
        """Lazy-loaded import query."""
        if self._import_query is None:
            self._ensure_parser()
        return self._import_query

    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the repository."""
        py_files = []
        for root, dirs, files in os.walk(self.repo_path):
            # Skip common non-source directories
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["__pycache__", "venv", ".venv", "node_modules"]
            ]

            for file in files:
                if file.endswith(".py"):
                    py_files.append(Path(root) / file)

        return py_files

    def _extract_imports(self, filepath: Path) -> List[ImportInfo]:
        """Extract imports from a Python file using Tree-sitter."""
        imports = []

        try:
            with open(filepath, encoding="utf-8") as f:
                source = f.read()

            tree = self.parser.parse(bytes(source, "utf8"))
            root_node = tree.root_node

            # Execute query
            captures = self.import_query.captures(root_node)

            for node, capture_name in captures:
                import_name = source[node.start_byte : node.end_byte]

                if capture_name == "from.relative":
                    is_relative = True
                    # Clean up relative import notation
                    import_name = import_name.strip(".")
                else:
                    is_relative = False

                imports.append(
                    ImportInfo(
                        source_file=str(filepath.relative_to(self.repo_path)),
                        imported_module=import_name,
                        is_relative=is_relative,
                        is_from_import=(
                            capture_name == "from.name" or capture_name == "from.relative"
                        ),
                        line_number=node.start_point[0] + 1,
                    )
                )

        except Exception as e:
            print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)

        return imports

    def build_dependency_graph(self) -> DependencyGraph:
        """Build complete dependency graph for the repository."""
        graph = DependencyGraph()
        py_files = self._find_python_files()

        print(f"Analyzing {len(py_files)} Python files...")

        for filepath in py_files:
            # Get module name from file path
            relative_path = filepath.relative_to(self.repo_path)
            module_name = str(relative_path.with_suffix("")).replace(os.sep, ".")

            # Extract imports
            imports = self._extract_imports(filepath)

            for imp in imports:
                # Normalize imported module name
                imported_module = imp.imported_module

                # Handle relative imports
                if imp.is_relative:
                    # Resolve relative to importing module
                    base_module = ".".join(module_name.split(".")[:-1])
                    if imported_module:
                        imported_module = f"{base_module}.{imported_module}"
                    else:
                        imported_module = base_module

                graph.add_edge(module_name, imported_module)

        return graph

    def find_cycles(self, graph: Optional[DependencyGraph] = None) -> list[list[str]]:
        """Find circular dependencies in the graph."""
        if graph is None:
            graph = self.build_dependency_graph()

        cycles = []
        visited = set()
        rec_stack = []

        def dfs(node: str, path: List[str]) -> None:
            if node in path:
                # Found cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return

            if node in visited:
                return

            visited.add(node)
            path.append(node)

            for neighbor in graph.get_dependencies(node):
                dfs(neighbor, path)

            path.pop()

        for vertex in graph.vertices:
            if vertex not in visited:
                dfs(vertex, [])

        # Remove duplicate cycles
        unique_cycles = []
        seen = set()
        for cycle in cycles:
            normalized = tuple(sorted(cycle))
            if normalized not in seen:
                seen.add(normalized)
                unique_cycles.append(cycle)

        return unique_cycles

    def calculate_coupling_metrics(
        self, graph: Optional[DependencyGraph] = None
    ) -> dict[str, CouplingMetrics]:
        """Calculate coupling metrics for all modules."""
        if graph is None:
            graph = self.build_dependency_graph()

        # Find cycles first
        cycles = self.find_cycles(graph)
        modules_in_cycles = set()
        for cycle in cycles:
            modules_in_cycles.update(cycle)

        metrics = {}
        for module in graph.vertices:
            aff = len(graph.get_dependents(module))
            eff = len(graph.get_dependencies(module))

            metric = CouplingMetrics(
                module=module,
                afferent_coupling=aff,
                efferent_coupling=eff,
                in_cycle=(module in modules_in_cycles),
            )
            metric.calculate_instability()
            metrics[module] = metric

        return metrics

    def analyze(self) -> dict:
        """Perform complete analysis and return results."""
        print("Building dependency graph...")
        graph = self.build_dependency_graph()

        print(f"Found {len(graph.vertices)} modules, {len(graph.edges)} dependencies")

        print("Finding cycles...")
        cycles = self.find_cycles(graph)
        print(f"Found {len(cycles)} circular dependencies")

        print("Calculating coupling metrics...")
        metrics = self.calculate_coupling_metrics(graph)

        # Find most unstable modules
        unstable = sorted(metrics.values(), key=lambda m: m.instability, reverse=True)[:10]

        return {
            "summary": {
                "total_modules": len(graph.vertices),
                "total_dependencies": len(graph.edges),
                "circular_dependencies": len(cycles),
                "modules_in_cycles": len(set(mod for cycle in cycles for mod in cycle)),
            },
            "graph": graph.to_dict(),
            "cycles": cycles,
            "coupling_metrics": {
                k: {
                    "afferent": v.afferent_coupling,
                    "efferent": v.efferent_coupling,
                    "instability": round(v.instability, 2),
                    "in_cycle": v.in_cycle,
                }
                for k, v in metrics.items()
            },
            "most_unstable": [
                {
                    "module": m.module,
                    "instability": round(m.instability, 2),
                    "efferent": m.efferent_coupling,
                }
                for m in unstable
            ],
        }


def main() -> int:
    """CLI entry point for import analysis."""
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Analyze Python import dependencies using Tree-sitter"
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to Python repository (default: current directory)",
    )
    parser.add_argument("--output", "-o", help="Output file for JSON results")
    parser.add_argument("--cycles", action="store_true", help="Show only circular dependencies")

    args = parser.parse_args()

    analyzer = ImportAnalyzer(args.repo_path)
    results = analyzer.analyze()

    if args.cycles:
        print("\nCircular Dependencies:")
        for i, cycle in enumerate(results["cycles"], 1):
            print(f"  {i}. {' -> '.join(cycle)}")
    else:
        print("\n" + "=" * 70)
        print("IMPORT DEPENDENCY ANALYSIS")
        print("=" * 70)

        summary = results["summary"]
        print(f"\nTotal Modules: {summary['total_modules']}")
        print(f"Total Dependencies: {summary['total_dependencies']}")
        print(f"Circular Dependencies: {summary['circular_dependencies']}")
        print(f"Modules in Cycles: {summary['modules_in_cycles']}")

        print("\nMost Unstable Modules (high efferent coupling):")
        for m in results["most_unstable"][:5]:
            print(f"  {m['module']}: instability={m['instability']}, imports={m['efferent']}")

        if results["cycles"]:
            print("\nCycles detected:")
            for i, cycle in enumerate(results["cycles"][:3], 1):
                print(f"  {i}. {' -> '.join(cycle[:5])}")
                if len(cycle) > 5:
                    print(f"     ... and {len(cycle) - 5} more")

        print("\n" + "=" * 70)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
