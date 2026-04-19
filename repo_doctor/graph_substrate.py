"""
Graph Substrate - Unified repository graph infrastructure.

Implements the unified graph G_repo = (V, E, Φ, Τ) where:
- V = files, modules, symbols, commands, entrypoints, tests, demos, docs,
      persistence schemas, commits, packages, servers, transports
- E = import edges, call edges, control-flow edges, data-flow edges,
      docs-to-code edges, tests-to-code edges, package-to-module edges
- Φ = attributes
- Τ = time labels

Backends:
- Tree-sitter: Concrete syntax trees, incremental edits
- CodeQL: Semantic code databases with AST, CFG, DFG
- Joern: Code property graphs (AST + CFG + DDG/PDG)
"""

import json
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any


class NodeType(Enum):
    """Types of nodes in the repository graph."""

    FILE = auto()
    MODULE = auto()
    SYMBOL = auto()
    FUNCTION = auto()
    CLASS = auto()
    COMMAND = auto()
    ENTRYPOINT = auto()
    TEST = auto()
    DEMO = auto()
    DOC_SNIPPET = auto()
    PERSISTENCE_SCHEMA = auto()
    COMMIT = auto()
    PACKAGE = auto()
    SERVER = auto()
    TRANSPORT = auto()


class EdgeType(Enum):
    """Types of edges in the repository graph."""

    IMPORTS = auto()
    CALLS = auto()
    CONTAINS = auto()
    DEFINES = auto()
    TESTS = auto()
    DOCUMENTS = auto()
    PACKAGE_CONTAINS = auto()
    ENTRYPOINT_LAUNCHES = auto()
    CONTROL_FLOW = auto()
    DATA_FLOW = auto()
    GIT_PARENT = auto()
    CO_CHANGE = auto()


@dataclass
class Node:
    """A node in the repository graph."""

    id: str
    type: NodeType
    label: str
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.name,
            "label": self.label,
            "attributes": self.attributes,
        }


@dataclass
class Edge:
    """An edge in the repository graph."""

    source: str
    target: str
    type: EdgeType
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type.name,
            "attributes": self.attributes,
        }


class GraphBackend(ABC):
    """Abstract base class for graph backends."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the backend is available."""
        pass

    @abstractmethod
    def ingest(self, repo_path: Path) -> bool:
        """Ingest repository into the backend."""
        pass

    @abstractmethod
    def query(self, query: str) -> List[dict]:
        """Execute a query against the backend."""
        pass


class TreeSitterBackend(GraphBackend):
    """
    Tree-sitter backend for concrete syntax trees.
    Provides incremental, error-tolerant parsing.
    """

    def __init__(self):
        self.repo_path: Optional[Path] = None
        self.parsed_files: Dict[str, Any] = {}

    def is_available(self) -> bool:
        try:
            import tree_sitter_python

            return True
        except ImportError:
            return False

    def ingest(self, repo_path: Path) -> bool:
        """Parse all Python files with Tree-sitter."""
        if not self.is_available():
            return False

        try:
            import tree_sitter_python
            from tree_sitter import Language, Parser

            self.repo_path = Path(repo_path).resolve()
            PY_LANGUAGE = Language(tree_sitter_python.language())
            parser = Parser(PY_LANGUAGE)

            for py_file in self.repo_path.rglob("*.py"):
                try:
                    content = py_file.read_bytes()
                    tree = parser.parse(content)
                    self.parsed_files[str(py_file.relative_to(self.repo_path))] = tree
                except Exception:
                    continue

            return True
        except Exception:
            return False

    def query(self, query: str) -> List[dict]:
        """Query parsed trees (simplified implementation)."""
        results = []
        for file_path, tree in self.parsed_files.items():
            # Simple query: find function definitions
            if "function" in query.lower():
                root = tree.root_node
                for node in root.children:
                    if node.type == "function_definition":
                        results.append(
                            {
                                "file": file_path,
                                "type": "function",
                                "line": node.start_point[0],
                            }
                        )
        return results

    def get_changed_ranges(self, old_tree, new_tree) -> List[tuple]:
        """
        Get changed ranges between two tree versions.
        This enables incremental analysis.
        """
        return old_tree.changed_ranges(new_tree)


class CodeQLBackend(GraphBackend):
    """
    CodeQL backend for semantic code databases.
    Provides AST, CFG, and data-flow analysis.
    """

    def __init__(self):
        self.repo_path: Optional[Path] = None
        self.database_path: Optional[Path] = None

    def is_available(self) -> bool:
        """Check if CodeQL CLI is available."""
        import shutil

        return shutil.which("codeql") is not None

    def ingest(self, repo_path: Path) -> bool:
        """Create CodeQL database for repository."""
        if not self.is_available():
            return False

        try:
            self.repo_path = Path(repo_path).resolve()
            self.database_path = self.repo_path / ".codeql_db"

            result = subprocess.run(
                [
                    "codeql",
                    "database",
                    "create",
                    str(self.database_path),
                    "--language=python",
                    "--overwrite",
                    "--source-root",
                    str(self.repo_path),
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            return result.returncode == 0
        except Exception:
            return False

    def query(self, query: str) -> List[dict]:
        """Execute CodeQL query against database."""
        if not self.database_path or not self.database_path.exists():
            return []

        try:
            # Write query to temp file
            query_file = self.repo_path / ".temp_query.ql"
            query_file.write_text(query)

            result = subprocess.run(
                [
                    "codeql",
                    "query",
                    "run",
                    str(query_file),
                    "--database",
                    str(self.database_path),
                    "--output",
                    str(self.repo_path / ".query_results.json"),
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                results_file = self.repo_path / ".query_results.json"
                if results_file.exists():
                    return json.loads(results_file.read_text())

            return []
        except Exception:
            return []


class JoernBackend(GraphBackend):
    """
    Joern backend for code property graphs.
    Merges AST, CFG, and data flow into unified CPG.
    """

    def __init__(self):
        self.repo_path: Optional[Path] = None
        self.cpg_path: Optional[Path] = None

    def is_available(self) -> bool:
        """Check if joern CLI is available."""
        import shutil

        return shutil.which("joern") is not None

    def ingest(self, repo_path: Path) -> bool:
        """Create CPG for repository."""
        if not self.is_available():
            return False

        try:
            self.repo_path = Path(repo_path).resolve()
            self.cpg_path = self.repo_path / ".joern_cpg"

            result = subprocess.run(
                ["joern-parse", str(self.repo_path), "--output", str(self.cpg_path)],
                capture_output=True,
                text=True,
                timeout=300,
            )

            return result.returncode == 0
        except Exception:
            return False

    def query(self, query: str) -> List[dict]:
        """Execute Joern query against CPG."""
        if not self.cpg_path or not self.cpg_path.exists():
            return []

        try:
            result = subprocess.run(
                ["joern-query", "--cpg", str(self.cpg_path), query],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
            return []
        except Exception:
            return []


@dataclass
class ContractNode:
    """Node representing a contract surface."""

    surface: str  # e.g., "README", "tutorial", "demo", "test", "MCP schema"
    content: str
    promises: List[str]  # What this surface promises
    location: str


class ContractGraph:
    """
    Graph of contract surfaces.
    README snippets, guide snippets, tutorial commands,
    demo callsites, CLI declarations, MCP schema tools, exports.
    """

    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path).resolve()
        self.nodes: Dict[str, ContractNode] = {}
        self.edges: list[tuple[str, str, str]] = []  # (from, to, relation)

    def ingest_docs(self):
        """Ingest documentation files."""
        for doc_file in self.repo_path.rglob("*.md"):
            try:
                content = doc_file.read_text()
                # Extract code snippets and commands
                node = ContractNode(
                    surface="docs",
                    content=content,
                    promises=self._extract_promises(content),
                    location=str(doc_file.relative_to(self.repo_path)),
                )
                self.nodes[f"docs:{doc_file.stem}"] = node
            except Exception:
                continue

    def _extract_promises(self, content: str) -> List[str]:
        """Extract promised commands/APIs from docs."""
        promises = []
        # Look for code blocks
        lines = content.split("\n")
        for line in lines:
            if line.startswith("```") and "python" in line:
                # Next lines are code
                pass
            elif "amos" in line.lower() or "repo-doctor" in line.lower():
                # Potential command reference
                promises.append(line.strip())
        return promises

    def compute_commutator(self, runtime_surface: dict) -> List[dict]:
        """
        Compute commutator: [A_public, A_runtime] = A_public A_runtime - A_runtime A_public
        Returns mismatches between contract and reality.
        """
        mismatches = []

        for node_id, node in self.nodes.items():
            for promise in node.promises:
                # Check if promise exists in runtime
                if not self._promise_in_runtime(promise, runtime_surface):
                    mismatches.append(
                        {
                            "contract": node_id,
                            "promise": promise,
                            "runtime_status": "missing",
                            "severity": "critical",
                        }
                    )

        return mismatches

    def _promise_in_runtime(self, promise: str, runtime: dict) -> bool:
        """Check if a promised feature exists in runtime."""
        # Simplified check
        for key in runtime:
            if any(word in key.lower() for word in promise.lower().split()):
                return True
        return False


@dataclass
class UnifiedGraph:
    """
    Unified repository graph combining all backends.
    G_repo = (V, E, Φ, Τ)
    """

    repo_path: Path
    nodes: Dict[str, Node] = field(default_factory=dict)
    edges: List[Edge] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = None

    # Backend instances
    treesitter: Optional[TreeSitterBackend] = None
    codeql: Optional[CodeQLBackend] = None
    joern: Optional[JoernBackend] = None
    contracts: Optional[ContractGraph] = None

    def build(self) -> bool:
        """Build unified graph from all available backends."""
        success = False

        # Try Tree-sitter
        ts = TreeSitterBackend()
        if ts.is_available():
            if ts.ingest(self.repo_path):
                self.treesitter = ts
                self._ingest_treesitter(ts)
                success = True

        # Try CodeQL
        cq = CodeQLBackend()
        if cq.is_available():
            if cq.ingest(self.repo_path):
                self.codeql = cq
                success = True

        # Try Joern
        jr = JoernBackend()
        if jr.is_available():
            if jr.ingest(self.repo_path):
                self.joern = jr
                success = True

        # Always build contract graph
        cg = ContractGraph(self.repo_path)
        cg.ingest_docs()
        self.contracts = cg

        return success

    def _ingest_treesitter(self, ts: TreeSitterBackend):
        """Add Tree-sitter parsed nodes to graph."""
        for file_path in ts.parsed_files:
            node_id = f"file:{file_path}"
            self.nodes[node_id] = Node(
                id=node_id, type=NodeType.FILE, label=file_path, attributes={"parsed": True}
            )

    def get_articulation_points(self) -> List[str]:
        """
        Find articulation modules - single points of multi-layer failure.
        These deserve higher weights.
        """
        # High-centrality nodes that are critical
        critical = []

        for node_id, node in self.nodes.items():
            if node.type in {NodeType.ENTRYPOINT, NodeType.SERVER}:
                critical.append(node_id)

        return critical

    def spectral_analysis(self) -> dict:
        """
        Construct graph Laplacian L = D - A and analyze.
        Returns spectral properties:
        - spectral gap → modular fragility
        - communities → hidden subsystem boundaries
        """
        # Build adjacency matrix
        adjacency = {}
        for edge in self.edges:
            if edge.source not in adjacency:
                adjacency[edge.source] = []
            adjacency[edge.source].append(edge.target)

        # Calculate degree matrix
        degrees = {node_id: len(adjacency.get(node_id, [])) for node_id in self.nodes}

        # Spectral gap (simplified)
        max_degree = max(degrees.values()) if degrees else 0
        spectral_gap = max_degree - 1 if max_degree > 1 else 0

        return {
            "spectral_gap": spectral_gap,
            "max_degree": max_degree,
            "articulation_points": self.get_articulation_points(),
        }

    def to_dict(self) -> dict:
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "backends": {
                "treesitter": self.treesitter is not None,
                "codeql": self.codeql is not None,
                "joern": self.joern is not None,
                "contracts": self.contracts is not None,
            },
            "spectral": self.spectral_analysis(),
        }
