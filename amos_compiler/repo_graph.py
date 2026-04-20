"""
AMOS Compiler: Repo Graph
Builds and maintains the codebase graph for symbol-aware transformations.

This implements the Repo Scanner stage of the AMOS pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class Symbol:
    """A code symbol (function, class, variable, etc.)."""

    name: str
    type: str  # "class", "function", "variable", "constant", "enum", "interface"
    file_path: str
    line_start: int
    line_end: int
    signature: Optional[str] = None
    docstring: Optional[str] = None
    decorators: list[str] = field(default_factory=list)
    is_public: bool = True
    dependencies: list[str] = field(default_factory=list)  # Other symbols this uses

    def full_name(self) -> str:
        """Fully qualified name."""
        return f"{self.file_path}:{self.name}"


@dataclass
class ImportEdge:
    """An import relationship between modules."""

    source: str  # Importing file
    target: str  # Imported module/symbol
    import_type: str  # "module", "symbol", "from"
    is_external: bool = False
    alias: Optional[str] = None


@dataclass
class CallEdge:
    """A function call relationship."""

    caller: str  # Symbol making the call
    callee: str  # Symbol being called
    file_path: str
    line_number: int


@dataclass
class Module:
    """A code module (file)."""

    path: str
    language: str
    symbols: list[Symbol] = field(default_factory=list)
    imports: list[ImportEdge] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)  # Public API
    is_generated: bool = False
    is_test: bool = False

    def get_symbol(self, name: str) -> Optional[Symbol]:
        """Get a symbol by name."""
        for sym in self.symbols:
            if sym.name == name:
                return sym
        return None


@dataclass
class Entrypoint:
    """A system entrypoint."""

    name: str
    type: str  # "cli", "api", "worker", "job", "websocket"
    file_path: str
    symbol: Optional[str] = None
    route: Optional[str] = None  # For APIs
    methods: list[str] = field(default_factory=list)  # HTTP methods


@dataclass
class RepoGraph:
    """
    Complete graph representation of a codebase.

    This is the canonical repo state at time t.
    """

    repo_root: str
    modules: dict[str, Module] = field(default_factory=dict)
    symbols: dict[str, Symbol] = field(default_factory=dict)
    entrypoints: list[Entrypoint] = field(default_factory=list)
    import_graph: list[ImportEdge] = field(default_factory=list)
    call_graph: list[CallEdge] = field(default_factory=list)
    glossary_terms: dict[str, list[str]] = field(default_factory=dict)

    def get_symbol(self, name: str) -> Optional[Symbol]:
        """Find a symbol by name across all modules."""
        if name in self.symbols:
            return self.symbols[name]
        # Search by unqualified name
        for sym in self.symbols.values():
            if sym.name == name:
                return sym
        return None

    def get_module(self, path: str) -> Optional[Module]:
        """Get a module by path."""
        return self.modules.get(path)

    def get_dependents(self, symbol_name: str) -> list[str]:
        """Get all symbols that depend on this one."""
        dependents = []
        for sym in self.symbols.values():
            if symbol_name in sym.dependencies:
                dependents.append(sym.full_name())
        return dependents

    def get_entrypoints_for_path(self, path: str) -> list[Entrypoint]:
        """Get entrypoints that reference a file path."""
        return [ep for ep in self.entrypoints if path in ep.file_path]

    def symbols_matching(self, pattern: str) -> list[Symbol]:
        """Find symbols matching a pattern."""
        import fnmatch

        matches = []
        for sym in self.symbols.values():
            if fnmatch.fnmatch(sym.name, pattern):
                matches.append(sym)
        return matches

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "repo_root": self.repo_root,
            "modules": {
                path: {
                    "path": mod.path,
                    "language": mod.language,
                    "symbol_count": len(mod.symbols),
                    "exports": mod.exports,
                    "is_generated": mod.is_generated,
                    "is_test": mod.is_test,
                }
                for path, mod in self.modules.items()
            },
            "symbol_count": len(self.symbols),
            "entrypoint_count": len(self.entrypoints),
            "glossary_terms": self.glossary_terms,
        }


class RepoScanner:
    """
    Scans a repository and builds the RepoGraph.

    In production, this would use tree-sitter, jedi, or similar
    for accurate AST parsing. This implementation provides the interface.
    """

    def __init__(self, repo_root: str | Path):
        self.repo_root = Path(repo_root)

    def scan(self) -> RepoGraph:
        """
        Build the complete repo graph.

        Returns:
            RepoGraph: Complete representation of the codebase
        """
        graph = RepoGraph(repo_root=str(self.repo_root))

        # Load glossary from .amos/glossary.yaml
        graph.glossary_terms = self._load_glossary()

        # Scan Python files
        self._scan_python_files(graph)

        # Detect entrypoints from .amos/repo.yaml
        self._detect_entrypoints(graph)

        return graph

    def _load_glossary(self) -> dict[str, list[str]]:
        """Load glossary terms from .amos/glossary.yaml."""
        import yaml

        glossary_path = self.repo_root / ".amos" / "glossary.yaml"
        if not glossary_path.exists():
            return {}

        try:
            with open(glossary_path) as f:
                data = yaml.safe_load(f)

            terms = {}
            for term, mapping in data.get("terms", {}).items():
                terms[term] = mapping.get("maps_to", [])

            # Add aliases
            for alias, targets in data.get("aliases", {}).items():
                terms[alias] = targets

            return terms
        except Exception:
            return {}

    def _scan_python_files(self, graph: RepoGraph) -> None:
        """Scan all Python files in the repo."""
        for py_file in self.repo_root.rglob("*.py"):
            # Skip certain directories
            if any(part.startswith(".") for part in py_file.parts):
                continue
            if "node_modules" in py_file.parts:
                continue

            relative_path = str(py_file.relative_to(self.repo_root))

            # Create module
            module = Module(
                path=relative_path,
                language="python",
                is_test=py_file.name.startswith("test_") or "_test.py" in py_file.name,
                is_generated="generated" in py_file.parts,
            )

            # Parse symbols (simplified - would use AST in production)
            self._parse_python_module(py_file, module, graph)

            graph.modules[relative_path] = module

    def _parse_python_module(self, file_path: Path, module: Module, graph: RepoGraph) -> None:
        """Parse a Python module to extract symbols."""
        import ast

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    symbol = Symbol(
                        name=node.name,
                        type="class",
                        file_path=module.path,
                        line_start=node.lineno or 0,
                        line_end=node.end_lineno or node.lineno or 0,
                        docstring=ast.get_docstring(node),
                        decorators=[ast.unparse(d) for d in node.decorator_list],
                    )
                    module.symbols.append(symbol)
                    graph.symbols[symbol.full_name()] = symbol

                    # Add class methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method = Symbol(
                                name=f"{node.name}.{item.name}",
                                type="function",
                                file_path=module.path,
                                line_start=item.lineno or 0,
                                line_end=item.end_lineno or item.lineno or 0,
                                signature=self._get_function_signature(item),
                                docstring=ast.get_docstring(item),
                                decorators=[ast.unparse(d) for d in item.decorator_list],
                            )
                            module.symbols.append(method)
                            graph.symbols[method.full_name()] = method

                elif isinstance(node, ast.FunctionDef):
                    symbol = Symbol(
                        name=node.name,
                        type="function",
                        file_path=module.path,
                        line_start=node.lineno or 0,
                        line_end=node.end_lineno or node.lineno or 0,
                        signature=self._get_function_signature(node),
                        docstring=ast.get_docstring(node),
                        decorators=[ast.unparse(d) for d in node.decorator_list],
                    )
                    module.symbols.append(symbol)
                    graph.symbols[symbol.full_name()] = symbol

                elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    import_edge = self._parse_import(node, module.path)
                    if import_edge:
                        module.imports.append(import_edge)
                        graph.import_graph.append(import_edge)

        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception:
            # Skip files that can't be parsed
            pass

    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Extract function signature."""
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)

        returns = ""
        if node.returns:
            returns = f" -> {ast.unparse(node.returns)}"

        return f"({', '.join(args)}){returns}"

    def _parse_import(self, node: ast.Import | ast.ImportFrom, source: str) -> Optional[ImportEdge]:
        """Parse an import statement."""
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
            return ImportEdge(
                source=source,
                target=names[0] if names else "",
                import_type="module",
                is_external=not names[0].startswith(".") if names else True,
                alias=node.names[0].asname if node.names and node.names[0].asname else None,
            )

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = [alias.name for alias in node.names]
            return ImportEdge(
                source=source,
                target=f"{module}.{names[0]}" if names else module,
                import_type="from",
                is_external=not module.startswith(".") if module else True,
                alias=node.names[0].asname if node.names and node.names[0].asname else None,
            )

        return None

    def _detect_entrypoints(self, graph: RepoGraph) -> None:
        """Detect system entrypoints from repo configuration."""
        import yaml

        repo_yaml = self.repo_root / ".amos" / "repo.yaml"
        if not repo_yaml.exists():
            return

        try:
            with open(repo_yaml) as f:
                config = yaml.safe_load(f)

            entrypoints_config = config.get("repo", {}).get("entrypoints", {})

            # CLI entrypoints
            for cli_file in entrypoints_config.get("cli", []):
                graph.entrypoints.append(
                    Entrypoint(
                        name=cli_file,
                        type="cli",
                        file_path=cli_file,
                    )
                )

            # API entrypoints
            for api_spec in entrypoints_config.get("api", []):
                if ":" in api_spec:
                    file_path, symbol = api_spec.split(":")
                else:
                    file_path, symbol = api_spec, None
                graph.entrypoints.append(
                    Entrypoint(
                        name=api_spec,
                        type="api",
                        file_path=file_path,
                        symbol=symbol,
                    )
                )

        except Exception:
            pass


def build_repo_graph(repo_root: str | Path) -> RepoGraph:
    """Convenience function to build repo graph."""
    scanner = RepoScanner(repo_root)
    return scanner.scan()
