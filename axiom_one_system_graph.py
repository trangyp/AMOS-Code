#!/usr/bin/env python3
from __future__ import annotations

"""Axiom One - Real System Graph Analysis.

Builds actual code dependency graph:
- Parse Python files for imports
- Map function/class definitions
- Build dependency tree
- Calculate impact analysis
- Export to JSON/graphviz
"""

import ast
import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

AMOS_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(AMOS_ROOT))

from axiom_one_agent_fleet import tool_read_file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CodeNode:
    """Node in code graph."""

    node_id: str
    node_type: str
    name: str
    path: str
    line: int
    parent: str = None
    children: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImportEdge:
    """Import relationship."""

    source: str
    target: str
    import_type: str
    line: int


class PythonCodeParser:
    """Parse Python files for code analysis."""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.nodes: Dict[str, CodeNode] = {}
        self.edges: List[ImportEdge] = []
        self.files_analyzed = 0
        self.errors: List[str] = []

    def scan_directory(self, pattern: str = "*.py") -> List[Path]:
        """Scan for Python files."""
        files = list(self.root_path.rglob(pattern))
        # Exclude common directories
        exclude = {".venv", "venv", "__pycache__", ".git", "node_modules"}
        return [f for f in files if not any(e in str(f) for e in exclude)]

    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse single Python file."""
        try:
            content = tool_read_file(str(file_path))
            if not content.get("success"):
                return None

            source = content.get("content", "")
            tree = ast.parse(source)

            module_name = self._get_module_name(file_path)

            result = {
                "path": str(file_path),
                "module": module_name,
                "imports": [],
                "definitions": [],
                "size_bytes": len(source.encode("utf-8")),
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        result["imports"].append(
                            {
                                "type": "import",
                                "name": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno,
                            }
                        )

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        result["imports"].append(
                            {
                                "type": "from",
                                "module": module,
                                "name": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno,
                            }
                        )

                elif isinstance(node, ast.ClassDef):
                    result["definitions"].append(
                        {
                            "type": "class",
                            "name": node.name,
                            "line": node.lineno,
                            "bases": [self._get_base_name(b) for b in node.bases],
                        }
                    )

                elif isinstance(node, ast.FunctionDef):
                    result["definitions"].append(
                        {
                            "type": "function",
                            "name": node.name,
                            "line": node.lineno,
                            "args": len(node.args.args),
                        }
                    )

                elif isinstance(node, ast.AsyncFunctionDef):
                    result["definitions"].append(
                        {
                            "type": "async_function",
                            "name": node.name,
                            "line": node.lineno,
                            "args": len(node.args.args),
                        }
                    )

            self.files_analyzed += 1
            return result

        except SyntaxError as e:
            self.errors.append(f"Syntax error in {file_path}: {e}")
            return None
        except Exception as e:
            self.errors.append(f"Error parsing {file_path}: {e}")
            return None

    def _get_module_name(self, file_path: Path) -> str:
        """Get module name from path."""
        rel_path = file_path.relative_to(self.root_path)
        parts = list(rel_path.parts[:-1])  # Exclude filename
        if rel_path.stem != "__init__":
            parts.append(rel_path.stem)
        return ".".join(parts)

    def _get_base_name(self, node: ast.expr) -> str:
        """Get base class name."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_base_name(node.value)}.{node.attr}"
        return "unknown"

    def build_graph(self, max_files: int = 100) -> Dict[str, Any]:
        """Build full code dependency graph."""
        logger.info(f"Building system graph for {self.root_path}")

        # Find all Python files
        py_files = self.scan_directory()
        logger.info(f"Found {len(py_files)} Python files")

        # Parse each file
        modules = {}
        for i, file_path in enumerate(py_files[:max_files]):
            if i % 10 == 0:
                logger.info(f"Parsed {i}/{min(len(py_files), max_files)} files...")

            parsed = self.parse_file(file_path)
            if parsed:
                modules[parsed["module"]] = parsed

        # Build nodes
        for module_name, data in modules.items():
            node_id = f"module:{module_name}"
            self.nodes[node_id] = CodeNode(
                node_id=node_id,
                node_type="module",
                name=module_name,
                path=data["path"],
                line=1,
                metadata={
                    "size_bytes": data["size_bytes"],
                    "import_count": len(data["imports"]),
                    "definition_count": len(data["definitions"]),
                },
            )

            # Add definition nodes
            for defn in data["definitions"]:
                def_id = f"{defn['type']}:{module_name}.{defn['name']}"
                self.nodes[def_id] = CodeNode(
                    node_id=def_id,
                    node_type=defn["type"],
                    name=defn["name"],
                    path=data["path"],
                    line=defn["line"],
                    parent=node_id,
                    metadata={"args": defn.get("args"), "bases": defn.get("bases")},
                )
                self.nodes[node_id].children.append(def_id)

        # Build edges from imports
        for module_name, data in modules.items():
            source_id = f"module:{module_name}"

            for imp in data["imports"]:
                if imp["type"] == "from":
                    target_module = imp["module"]
                else:
                    target_module = imp["name"].split(".")[0]

                target_id = f"module:{target_module}"

                if target_id in self.nodes:
                    self.edges.append(
                        ImportEdge(
                            source=source_id,
                            target=target_id,
                            import_type=imp["type"],
                            line=imp["line"],
                        )
                    )

                    if target_id not in self.nodes[source_id].dependencies:
                        self.nodes[source_id].dependencies.append(target_id)

                    if source_id not in self.nodes[target_id].dependents:
                        self.nodes[target_id].dependents.append(source_id)

        logger.info(f"Graph complete: {len(self.nodes)} nodes, {len(self.edges)} edges")

        return {
            "root_path": str(self.root_path),
            "files_analyzed": self.files_analyzed,
            "nodes_count": len(self.nodes),
            "edges_count": len(self.edges),
            "errors": len(self.errors),
        }

    def find_cycles(self) -> List[list[str]]:
        """Find circular dependencies."""
        visited = set()
        cycles = []

        def dfs(node_id: str, path: List[str]) -> None:
            if node_id in path:
                cycle_start = path.index(node_id)
                cycles.append(path[cycle_start:] + [node_id])
                return

            if node_id in visited:
                return

            visited.add(node_id)
            path.append(node_id)

            node = self.nodes.get(node_id)
            if node:
                for dep in node.dependencies:
                    dfs(dep, path.copy())

        for node_id in self.nodes:
            if node_id.startswith("module:"):
                dfs(node_id, [])

        return cycles

    def calculate_impact(self, target_node: str) -> Dict[str, Any]:
        """Calculate impact of changing a node."""
        if target_node not in self.nodes:
            return {"error": f"Node {target_node} not found"}

        node = self.nodes[target_node]

        # Find all transitive dependents
        all_dependents = set()
        queue = list(node.dependents)

        while queue:
            dep = queue.pop(0)
            if dep not in all_dependents:
                all_dependents.add(dep)
                dep_node = self.nodes.get(dep)
                if dep_node:
                    queue.extend(dep_node.dependents)

        return {
            "node": target_node,
            "direct_dependents": len(node.dependents),
            "total_dependents": len(all_dependents),
            "dependencies": len(node.dependencies),
            "impact_score": len(all_dependents),
            "risk_level": (
                "high"
                if len(all_dependents) > 10
                else "medium"
                if len(all_dependents) > 3
                else "low"
            ),
            "transitive_dependents": list(all_dependents)[:20],  # Limit output
        }

    def export_json(self, output_path: str) -> None:
        """Export graph to JSON."""
        data = {
            "root_path": str(self.root_path),
            "files_analyzed": self.files_analyzed,
            "nodes": {
                nid: {
                    "type": n.node_type,
                    "name": n.name,
                    "path": n.path,
                    "line": n.line,
                    "parent": n.parent,
                    "children": n.children,
                    "dependencies": n.dependencies,
                    "dependents": n.dependents,
                    "metadata": n.metadata,
                }
                for nid, n in self.nodes.items()
            },
            "edges": [
                {"source": e.source, "target": e.target, "type": e.import_type, "line": e.line}
                for e in self.edges
            ],
            "errors": self.errors,
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Graph exported to {output_path}")

    def export_dot(self, output_path: str) -> None:
        """Export to Graphviz DOT format."""
        lines = ["digraph system_graph {", "  rankdir=LR;"]

        # Add nodes
        for node_id, node in self.nodes.items():
            if node.node_type == "module":
                label = node.name.split(".")[-1]
                lines.append(f'  "{node_id}" [label="{label}", shape=box];')

        # Add edges
        for edge in self.edges:
            if edge.source in self.nodes and edge.target in self.nodes:
                lines.append(f'  "{edge.source}" -> "{edge.target}";')

        lines.append("}")

        with open(output_path, "w") as f:
            f.write("\n".join(lines))

        logger.info(f"DOT exported to {output_path}")


def demo():
    """Demonstrate system graph analysis."""
    print("=" * 70)
    print("AXIOM ONE SYSTEM GRAPH ANALYSIS")
    print("=" * 70)

    # Build graph
    print("\n🔨 Building system graph...")
    parser = PythonCodeParser(root_path=".")
    stats = parser.build_graph(max_files=50)

    print("\n📊 Analysis Complete:")
    print(f"  Files analyzed: {stats['files_analyzed']}")
    print(f"  Nodes: {stats['nodes_count']}")
    print(f"  Edges: {stats['edges_count']}")
    print(f"  Errors: {stats['errors']}")

    # Show sample nodes
    print("\n📁 Sample Modules:")
    modules = [n for n in parser.nodes.values() if n.node_type == "module"]
    for m in modules[:5]:
        print(f"  • {m.name}")
        print(f"    Path: {m.path}")
        print(f"    Imports: {len(m.dependencies)}")
        print(f"    Imported by: {len(m.dependents)}")

    # Find most connected
    if modules:
        most_connected = max(modules, key=lambda n: len(n.dependents))
        print("\n🔗 Most Connected Module:")
        print(f"  {most_connected.name}")
        print(f"  Dependents: {len(most_connected.dependents)}")
        print(f"  Dependencies: {len(most_connected.dependencies)}")

        # Impact analysis
        print(f"\n💥 Impact Analysis for {most_connected.name}:")
        impact = parser.calculate_impact(most_connected.node_id)
        print(f"  Direct dependents: {impact['direct_dependents']}")
        print(f"  Total dependents: {impact['total_dependents']}")
        print(f"  Risk level: {impact['risk_level']}")

    # Find cycles
    cycles = parser.find_cycles()
    if cycles:
        print(f"\n🔄 Circular Dependencies Found: {len(cycles)}")
        for i, cycle in enumerate(cycles[:3], 1):
            print(f"  Cycle {i}: {' -> '.join(c[-20:] for c in cycle)}")
    else:
        print("\n✅ No circular dependencies found")

    # Export
    json_path = ".axiom_system_graph.json"
    parser.export_json(json_path)
    print(f"\n💾 Exported to {json_path}")

    dot_path = ".axiom_system_graph.dot"
    parser.export_dot(dot_path)
    print(f"💾 DOT format to {dot_path}")
    print("   (Render with: dot -Tpng .axiom_system_graph.dot -o graph.png)")

    print("\n" + "=" * 70)
    print("GRAPH ANALYSIS COMPLETE")
    print("=" * 70)


class SystemGraphAnalyzer:
    """Analyzes system graph for architecture insights."""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.graph = SystemGraph()

    def analyze(self) -> dict:
        """Analyze the system graph."""
        return {
            "nodes": len(self.graph.nodes),
            "edges": len(self.graph.edges),
            "components": len(self.graph.get_connected_components()),
        }

    def export_json(self, filepath: str) -> None:
        """Export graph to JSON."""
        self.graph.export_json(filepath)

    def export_dot(self, filepath: str) -> None:
        """Export graph to DOT format."""
        self.graph.export_dot(filepath)


if __name__ == "__main__":
    demo()
