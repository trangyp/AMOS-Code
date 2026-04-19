"""
Unified Repository Graph

Unified graph representation combining:
- AST containment edges (from Tree-sitter)
- Call edges (from CodeQL/Joern)
- Control-flow edges (from Joern)
- Data-flow edges (from CodeQL/Joern)
- Import edges (static analysis)
- Test-to-code edges (coverage/test mapping)
- Doc-to-code edges (docstring analysis)
- Commit-to-file edges (from Git history)

G_repo = (V, E, Φ, Τ)
Where:
    V: vertices (files, symbols, methods, imports, entrypoints, tests, docs, commits, packages, runtime endpoints)
    E: edges (AST containment, call, control-flow, data-flow, import, test-to-code, doc-to-code, commit-to-file)
    Φ: node properties
    Τ: edge types
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class NodeType(Enum):
    """Types of nodes in the repository graph."""

    FILE = "file"
    DIRECTORY = "directory"
    SYMBOL = "symbol"
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    IMPORT = "import"
    EXPORT = "export"
    ENTRYPOINT = "entrypoint"
    TEST = "test"
    DOC = "documentation"
    COMMIT = "commit"
    PACKAGE = "package"
    RUNTIME_ENDPOINT = "runtime_endpoint"


class EdgeType(Enum):
    """Types of edges in the repository graph."""

    CONTAINS = "contains"  # AST containment
    CALLS = "calls"  # Function call
    IMPORTS = "imports"  # Import relationship
    EXPORTS = "exports"  # Export relationship
    CONTROLS = "controls"  # Control flow
    FLOWS_TO = "flows_to"  # Data flow
    TESTS = "tests"  # Test covers code
    DOCUMENTS = "documents"  # Doc covers code
    COMMITTED_IN = "committed_in"  # File changed in commit
    DEPENDS_ON = "depends_on"  # Package dependency


@dataclass
class RepoNode:
    """A node in the repository graph."""

    id: str
    type: NodeType
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    source_location: Tuple[Path, int, int] = None  # (file, line, col)

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RepoNode):
            return NotImplemented
        return self.id == other.id


@dataclass
class RepoEdge:
    """An edge in the repository graph."""

    source: str
    target: str
    type: EdgeType
    properties: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0


class RepositoryGraph:
    """
    Unified repository graph G_repo = (V, E, Φ, Τ).

    Combines multiple analysis layers:
    - Syntax layer (Tree-sitter AST)
    - Semantic layer (CodeQL database)
    - Control-flow layer (Joern CFG)
    - Data-flow layer (CodeQL/Joern DFG)
    - Import layer (static analysis)
    - Test layer (test mapping)
    - Documentation layer (doc mapping)
    - History layer (Git commits)
    """

    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)
        self.nodes: Dict[str, RepoNode] = {}
        self.edges: List[RepoEdge] = []
        self.edges_by_type: dict[EdgeType, list[RepoEdge]] = {et: [] for et in EdgeType}
        self.adjacency: dict[str, list[str]] = {}  # node_id -> [neighbor_ids]

    def add_node(
        self,
        node_id: str,
        node_type: NodeType,
        name: str,
        properties: Dict[str, Any] = None,
        source_file: Optional[Path] = None,
        line: int = 0,
        col: int = 0,
    ) -> RepoNode:
        """Add a node to the graph."""
        if node_id in self.nodes:
            # Update existing node
            node = self.nodes[node_id]
            if properties:
                node.properties.update(properties)
            return node

        node = RepoNode(
            id=node_id,
            type=node_type,
            name=name,
            properties=properties or {},
            source_location=(source_file, line, col) if source_file else None,
        )
        self.nodes[node_id] = node
        self.adjacency[node_id] = []
        return node

    def add_edge(
        self,
        source: str,
        target: str,
        edge_type: EdgeType,
        properties: Dict[str, Any] = None,
        weight: float = 1.0,
    ) -> RepoEdge:
        """Add an edge to the graph."""
        edge = RepoEdge(
            source=source,
            target=target,
            type=edge_type,
            properties=properties or {},
            weight=weight,
        )
        self.edges.append(edge)
        self.edges_by_type[edge_type].append(edge)

        # Update adjacency
        if source in self.adjacency:
            self.adjacency[source].append(target)

        return edge

    def get_node(self, node_id: str) -> Optional[RepoNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[RepoNode]:
        """Get neighbors of a node, optionally filtered by edge type."""
        if edge_type:
            neighbor_ids = [e.target for e in self.edges_by_type[edge_type] if e.source == node_id]
        else:
            neighbor_ids = self.adjacency.get(node_id, [])

        return [self.nodes[nid] for nid in neighbor_ids if nid in self.nodes]

    def get_callers(self, function_id: str) -> List[RepoNode]:
        """Get all functions that call the given function."""
        caller_ids = [
            e.source for e in self.edges_by_type[EdgeType.CALLS] if e.target == function_id
        ]
        return [self.nodes[cid] for cid in caller_ids if cid in self.nodes]

    def get_callees(self, function_id: str) -> List[RepoNode]:
        """Get all functions called by the given function."""
        callee_ids = [
            e.target for e in self.edges_by_type[EdgeType.CALLS] if e.source == function_id
        ]
        return [self.nodes[cid] for cid in callee_ids if cid in self.nodes]

    def get_imports(self, file_id: str) -> List[RepoNode]:
        """Get all imports in a file."""
        return self.get_neighbors(file_id, EdgeType.IMPORTS)

    def get_imported_by(self, module_id: str) -> List[RepoNode]:
        """Get all files that import a module."""
        importer_ids = [
            e.source for e in self.edges_by_type[EdgeType.IMPORTS] if e.target == module_id
        ]
        return [self.nodes[iid] for iid in importer_ids if iid in self.nodes]

    def find_path(self, source: str, target: str, max_depth: int = 10) -> List[RepoEdge]:
        """Find a path between two nodes using BFS."""
        from collections import deque

        if source not in self.nodes or target not in self.nodes:
            return None

        visited = {source}
        queue = deque([(source, [])])

        while queue:
            current, path = queue.popleft()

            if current == target:
                return path

            if len(path) >= max_depth:
                continue

            for edge in self.edges:
                if edge.source == current and edge.target not in visited:
                    visited.add(edge.target)
                    queue.append((edge.target, path + [edge]))

        return None

    def build_from_treesitter(self, ingest) -> None:
        """Build graph from Tree-sitter ingestion results."""
        for file_path, parsed in ingest.cache.items():
            # Add file node
            file_id = f"file:{file_path}"
            self.add_node(
                file_id,
                NodeType.FILE,
                file_path.name,
                {"language": parsed.language, "path": str(file_path)},
                file_path,
            )

            # Add symbol nodes
            for symbol_name, info in parsed.symbols.items():
                symbol_id = f"symbol:{file_path}:{symbol_name}"
                node_type = NodeType.FUNCTION if info["type"] == "function" else NodeType.CLASS
                self.add_node(
                    symbol_id,
                    node_type,
                    symbol_name,
                    {"type": info["type"]},
                    file_path,
                )
                self.add_edge(file_id, symbol_id, EdgeType.CONTAINS)

            # Add import edges
            for imp in parsed.imports:
                import_id = f"import:{imp}"
                self.add_node(import_id, NodeType.IMPORT, imp)
                self.add_edge(file_id, import_id, EdgeType.IMPORTS)

    def build_from_joern(self, joern_bridge) -> None:
        """Build graph from Joern CPG."""
        if not joern_bridge.current_cpg:
            return

        cpg = joern_bridge.current_cpg

        # Add method nodes
        for node in cpg.get_by_label("METHOD"):
            method_id = f"method:{node.properties.get('name', node.id)}"
            self.add_node(
                method_id,
                NodeType.FUNCTION,
                node.properties.get("name", "unknown"),
                node.properties,
            )

        # Add call edges
        for edge in cpg.edges:
            if edge.label == "CALL":
                source_id = f"method:{edge.source}"
                target_id = f"method:{edge.target}"
                self.add_edge(source_id, target_id, EdgeType.CALLS)

    def calculate_entanglement(self, module_a: str, module_b: str) -> float:
        """
        Calculate entanglement between two modules.

        M_ij = α·Import(i,j) + β·Call(i,j) + γ·TestCoupling(i,j) + δ·GitCoChange(i,j)

        Returns entanglement score [0, 1].
        """
        weights = {"import": 0.3, "call": 0.4, "test": 0.2, "git": 0.1}
        score = 0.0

        # Check import relationships
        a_imports_b = any(
            e.target == module_b
            for e in self.edges_by_type[EdgeType.IMPORTS]
            if e.source == module_a
        )
        b_imports_a = any(
            e.target == module_a
            for e in self.edges_by_type[EdgeType.IMPORTS]
            if e.source == module_b
        )
        if a_imports_b or b_imports_a:
            score += weights["import"]

        # Check call relationships
        a_calls_b = any(
            e.target == module_b for e in self.edges_by_type[EdgeType.CALLS] if e.source == module_a
        )
        b_calls_a = any(
            e.target == module_a for e in self.edges_by_type[EdgeType.CALLS] if e.source == module_b
        )
        if a_calls_b or b_calls_a:
            score += weights["call"]

        # Check test coupling
        # (Would need test coverage data)

        return min(1.0, score)

    def export_dot(self, output_path: Path) -> None:
        """Export graph to Graphviz DOT format."""
        lines = ["digraph Repository {"]

        # Add nodes
        for node in self.nodes.values():
            shape = "box" if node.type == NodeType.FILE else "ellipse"
            lines.append(f'  "{node.id}" [label="{node.name}", shape={shape}];')

        # Add edges
        for edge in self.edges:
            color = {
                EdgeType.CONTAINS: "black",
                EdgeType.CALLS: "blue",
                EdgeType.IMPORTS: "green",
                EdgeType.CONTROLS: "red",
                EdgeType.FLOWS_TO: "orange",
                EdgeType.TESTS: "purple",
            }.get(edge.type, "gray")
            lines.append(
                f'  "{edge.source}" -> "{edge.target}" [color={color}, label="{edge.type.value}"];'
            )

        lines.append("}")

        output_path.write_text("\n".join(lines))

    def export_json(self, output_path: Path) -> None:
        """Export graph to JSON format."""
        data = {
            "nodes": [
                {
                    "id": n.id,
                    "type": n.type.value,
                    "name": n.name,
                    "properties": n.properties,
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "type": e.type.value,
                    "weight": e.weight,
                }
                for e in self.edges
            ],
        }
        output_path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load_json(cls, input_path: Path) -> RepositoryGraph:
        """Load graph from JSON format."""
        with open(input_path) as f:
            data = json.load(f)

        # Need repo_path - extract from first file node
        repo_path = Path(".")
        graph = cls(repo_path)

        for n_data in data["nodes"]:
            graph.add_node(
                n_data["id"],
                NodeType(n_data["type"]),
                n_data["name"],
                n_data.get("properties", {}),
            )

        for e_data in data["edges"]:
            graph.add_edge(
                e_data["source"],
                e_data["target"],
                EdgeType(e_data["type"]),
                weight=e_data.get("weight", 1.0),
            )

        return graph
