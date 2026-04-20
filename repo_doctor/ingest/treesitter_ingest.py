from __future__ import annotations

"""
Tree-sitter Ingestion Engine

Incremental multi-language parsing using tree-sitter.
Builds concrete syntax trees that can be updated incrementally.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SyntaxNode:
    """A node in the concrete syntax tree."""

    type: str
    start_byte: int
    end_byte: int
    start_point: tuple[int, int]  # (row, col)
    end_point: tuple[int, int]
    text: str = ""
    children: list[SyntaxNode] = field(default_factory=list)
    parent: SyntaxNode | None = None


@dataclass
class ParsedFile:
    """Result of parsing a source file."""

    path: Path
    language: str
    root: SyntaxNode | None = None
    errors: list[dict[str, Any]] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)
    symbols: dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0 and self.root is not None


class TreeSitterIngest:
    """
    Tree-sitter based incremental parser.

    Features:
    - Robust parsing even with syntax errors
    - Incremental updates for changed regions
    - Multi-language support (Python, JS, TS, Go, Rust, etc.)
    - Extraction of imports, exports, symbols
    """

    SUPPORTED_LANGUAGES = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
    }

    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)
        self.parsers: dict[str, Any] = {}
        self.cache: dict[Path, ParsedFile] = {}
        self._init_parsers()

    def _init_parsers(self) -> None:
        """Initialize tree-sitter parsers for supported languages."""
        try:
            import tree_sitter_python as tspython
            from tree_sitter import Language, Parser

            self.Language = Language
            self.Parser = Parser

            # Build language library
            self.parsers["python"] = Parser(Language(tspython.language()))
            logger.info("Tree-sitter Python parser initialized")

        except ImportError as e:
            logger.warning(f"Tree-sitter not available: {e}")
            self.Language = None
            self.Parser = None

    def detect_language(self, file_path: Path) -> str:
        """Detect language from file extension."""
        return self.SUPPORTED_LANGUAGES.get(file_path.suffix.lower())

    def parse_file(self, file_path: Path, use_cache: bool = True) -> ParsedFile:
        """
        Parse a single source file.

        Args:
        ----
            file_path: Path to source file
            use_cache: Whether to use cached result if available

        Returns:
        -------
            ParsedFile with syntax tree and extracted info

        """
        abs_path = self.repo_path / file_path

        # Check cache
        if use_cache and abs_path in self.cache:
            return self.cache[abs_path]

        language = self.detect_language(abs_path)
        if not language:
            return ParsedFile(path=abs_path, language="unknown")

        if not self.parsers:
            # Fallback: basic text parsing
            return self._fallback_parse(abs_path, language)

        try:
            content = abs_path.read_bytes()
            parser = self.parsers.get(language)

            if not parser:
                return self._fallback_parse(abs_path, language)

            tree = parser.parse(content)
            root_node = tree.root_node

            # Extract information from AST
            result = ParsedFile(
                path=abs_path,
                language=language,
                root=self._convert_node(root_node, content),
            )

            # Extract Python-specific constructs
            if language == "python":
                self._extract_python_info(result, root_node, content)

            self.cache[abs_path] = result
            return result

        except Exception as e:
            logger.error(f"Parse error in {abs_path}: {e}")
            return ParsedFile(
                path=abs_path,
                language=language,
                errors=[{"message": str(e), "type": "parse_error"}],
            )

    def _convert_node(
        self, ts_node: Any, content: bytes, parent: SyntaxNode | None = None
    ) -> SyntaxNode:
        """Convert tree-sitter node to our SyntaxNode format."""
        node = SyntaxNode(
            type=ts_node.type,
            start_byte=ts_node.start_byte,
            end_byte=ts_node.end_byte,
            start_point=ts_node.start_point,
            end_point=ts_node.end_point,
            text=content[ts_node.start_byte : ts_node.end_byte].decode("utf-8", errors="replace"),
            parent=parent,
        )

        for child in ts_node.children:
            node.children.append(self._convert_node(child, content, node))

        return node

    def _extract_python_info(self, result: ParsedFile, root_node: Any, content: bytes) -> None:
        """Extract Python-specific info from AST."""
        text = content.decode("utf-8", errors="replace")

        def walk(node: Any) -> None:
            # Imports
            if node.type in ("import_statement", "import_from_statement"):
                import_text = text[node.start_byte : node.end_byte]
                result.imports.append(import_text.strip())

            # Function definitions
            if node.type == "function_definition":
                for child in node.children:
                    if child.type == "identifier":
                        name = text[child.start_byte : child.end_byte]
                        result.symbols[name] = {"type": "function", "node": child}
                        break

            # Class definitions
            if node.type == "class_definition":
                for child in node.children:
                    if child.type == "identifier":
                        name = text[child.start_byte : child.end_byte]
                        result.symbols[name] = {"type": "class", "node": child}
                        break

            for child in node.children:
                walk(child)

        walk(root_node)

    def _fallback_parse(self, file_path: Path, language: str) -> ParsedFile:
        """Fallback parser when tree-sitter unavailable."""
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")

            # Basic regex-based extraction
            import re

            imports = []
            if language == "python":
                imports = re.findall(r"^(?:from|import)\s+([\w.]+)", text, re.MULTILINE)

            return ParsedFile(
                path=file_path,
                language=language,
                imports=imports,
                errors=[{"message": "Using fallback parser (tree-sitter unavailable)"}],
            )
        except Exception as e:
            return ParsedFile(
                path=file_path,
                language=language,
                errors=[{"message": f"Failed to read file: {e}"}],
            )

    def parse_repo(
        self, patterns: list[str] | None = None, exclude_dirs: list[str] | None = None
    ) -> dict[Path, ParsedFile]:
        """
        Parse entire repository.

        Args:
        ----
            patterns: File patterns to include (e.g., ["*.py"])
            exclude_dirs: Directories to exclude

        Returns:
        -------
            Dictionary mapping file paths to ParsedFile results

        """
        if patterns is None:
            patterns = ["*.py", "*.js", "*.ts", "*.go"]

        if exclude_dirs is None:
            exclude_dirs = [".git", "__pycache__", "node_modules", "venv", ".venv"]

        results = {}

        for pattern in patterns:
            for file_path in self.repo_path.rglob(pattern):
                # Skip excluded directories
                if any(excluded in str(file_path) for excluded in exclude_dirs):
                    continue

                result = self.parse_file(file_path)
                results[file_path] = result

        logger.info(f"Parsed {len(results)} files")
        return results

    def check_syntax_errors(self) -> list[dict[str, Any]]:
        """Check all parsed files for syntax errors."""
        errors = []

        for path, parsed in self.cache.items():
            if parsed.errors:
                errors.append(
                    {
                        "file": str(path),
                        "language": parsed.language,
                        "errors": parsed.errors,
                    }
                )

        return errors

    def get_symbol_graph(self) -> dict[str, Any]:
        """
        Build a graph of symbols and their relationships.

        Returns
        -------
            Graph with nodes (symbols) and edges (imports/calls)

        """
        graph = {"nodes": {}, "edges": []}

        for path, parsed in self.cache.items():
            for name, info in parsed.symbols.items():
                node_id = f"{path}:{name}"
                graph["nodes"][node_id] = {
                    "name": name,
                    "type": info["type"],
                    "file": str(path),
                }

            # Import edges
            for imp in parsed.imports:
                graph["edges"].append(
                    {
                        "from": str(path),
                        "to": imp,
                        "type": "import",
                    }
                )

        return graph
