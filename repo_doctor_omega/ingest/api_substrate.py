"""API surface analysis substrate.

Extracts and compares:
- A_public: __all__, documented exports, type hints
- A_runtime: actual functions, classes, signatures

Computes API commutator: [A_public, A_runtime] = gap between promised and actual.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class APISymbol:
    """A symbol in the API surface."""

    name: str
    kind: str  # function, class, variable, module
    source_file: str
    line: int = 0
    signature: str = ""
    is_exported: bool = False  # In __all__ or public docs
    docstring: str = ""

    @property
    def full_name(self) -> str:
        """Get fully qualified name."""
        return f"{self.source_file}:{self.name}"


@dataclass
class APIDiscrepancy:
    """Gap between public and runtime API."""

    kind: str  # 'missing_export', 'undocumented', 'signature_mismatch'
    symbol_name: str
    expected: str = ""
    actual: str = ""
    location: str = ""
    severity: float = 0.8

    def to_violation_message(self) -> str:
        """Convert to human-readable violation message."""
        if self.kind == "missing_export":
            return f"Exported symbol '{self.symbol_name}' not found in runtime (expected: {self.expected})"
        elif self.kind == "undocumented":
            return f"Runtime symbol '{self.symbol_name}' not exported in __all__ or public API"
        elif self.kind == "signature_mismatch":
            return f"Signature mismatch for '{self.symbol_name}': expected {self.expected}, got {self.actual}"
        return f"API discrepancy: {self.symbol_name}"


class APISubstrate:
    """API surface analysis substrate.

    Extracts public API claims vs runtime reality to detect:
    - Broken exports (__all__ references missing symbols)
    - Undocumented public API (symbols not in __all__)
    - Type annotation mismatches

    Usage:
        substrate = APISubstrate("/path/to/repo")

        # Get public API claims
        public = substrate.extract_public_api("package/__init__.py")

        # Get runtime reality
        runtime = substrate.extract_runtime_api("package/")

        # Find discrepancies
        gaps = substrate.compute_api_commutator(public, runtime)
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()

    def extract_public_api(self, file_path: str | Path) -> list[APISymbol]:
        """Extract public API surface from __all__ and type hints.

        Args:
            file_path: Path to Python module (typically __init__.py)

        Returns:
            List of exported API symbols
        """
        file_path = Path(file_path)
        symbols = []

        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)

            # Find __all__ assignment
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__":
                            # Extract __all__ contents
                            if isinstance(node.value, (ast.List, ast.Tuple)):
                                for elt in node.value.elts:
                                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                        symbols.append(
                                            APISymbol(
                                                name=elt.value,
                                                kind="exported",
                                                source_file=str(file_path),
                                                line=node.lineno or 0,
                                                is_exported=True,
                                            )
                                        )

            # Also extract top-level definitions with docstrings
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    docstring = ast.get_docstring(node) or ""
                    symbols.append(
                        APISymbol(
                            name=node.name,
                            kind="function",
                            source_file=str(file_path),
                            line=node.lineno or 0,
                            signature=self._get_function_signature(node),
                            is_exported=not node.name.startswith("_"),
                            docstring=docstring[:100],
                        )
                    )
                elif isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node) or ""
                    symbols.append(
                        APISymbol(
                            name=node.name,
                            kind="class",
                            source_file=str(file_path),
                            line=node.lineno or 0,
                            is_exported=not node.name.startswith("_"),
                            docstring=docstring[:100],
                        )
                    )

        except SyntaxError:
            pass
        except Exception:
            pass

        return symbols

    def _get_function_signature(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Extract function signature from AST node."""
        args = []

        # Positional args
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)

        # Defaults
        defaults = [None] * (len(node.args.args) - len(node.args.defaults)) + list(
            node.args.defaults
        )

        # Keyword-only args
        for arg in node.args.kwonlyargs:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)

        # Return annotation
        return_annotation = ""
        if node.returns:
            return_annotation = f" -> {ast.unparse(node.returns)}"

        return f"({', '.join(args)}){return_annotation}"

    def extract_runtime_api(self, package_dir: str | Path) -> list[APISymbol]:
        """Extract actual runtime API from package directory.

        Args:
            package_dir: Path to package directory

        Returns:
            List of runtime API symbols
        """
        package_path = Path(package_dir)
        symbols = []

        for py_file in package_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                # Package init - exports are the public API
                symbols.extend(self.extract_public_api(py_file))
            else:
                # Module - check for public symbols
                try:
                    source = py_file.read_text(encoding="utf-8", errors="replace")
                    tree = ast.parse(source)

                    for node in tree.body:
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            if not node.name.startswith("_"):  # Public
                                symbols.append(
                                    APISymbol(
                                        name=f"{py_file.stem}.{node.name}",
                                        kind="function",
                                        source_file=str(py_file),
                                        line=node.lineno or 0,
                                        signature=self._get_function_signature(node),
                                        is_exported=True,  # Public by convention
                                    )
                                )
                        elif isinstance(node, ast.ClassDef):
                            if not node.name.startswith("_"):  # Public
                                symbols.append(
                                    APISymbol(
                                        name=f"{py_file.stem}.{node.name}",
                                        kind="class",
                                        source_file=str(py_file),
                                        line=node.lineno or 0,
                                        is_exported=True,
                                    )
                                )
                except SyntaxError:
                    pass

        return symbols

    def compute_api_commutator(
        self, public_api: list[APISymbol], runtime_api: list[APISymbol]
    ) -> list[APIDiscrepancy]:
        """Compute API commutator: gap between public and runtime.

        Finds:
        - Missing exports (in __all__ but not in runtime)
        - Undocumented API (in runtime but not exported)

        Args:
            public_api: Public API surface
            runtime_api: Runtime API reality

        Returns:
            List of API discrepancies
        """
        discrepancies = []

        # Build lookup sets
        runtime_names = {s.name for s in runtime_api}
        exported_names = {s.name for s in public_api if s.is_exported}

        # Check for missing exports (in __all__ but not in runtime)
        for symbol in public_api:
            if symbol.is_exported and symbol.name not in runtime_names:
                discrepancies.append(
                    APIDiscrepancy(
                        kind="missing_export",
                        symbol_name=symbol.name,
                        expected=symbol.source_file,
                        actual="not found",
                        location=symbol.source_file,
                        severity=0.95,
                    )
                )

        # Check for undocumented API (significant public symbols not in __all__)
        # Only flag if it's a top-level public symbol
        for symbol in runtime_api:
            if (
                symbol.is_exported
                and symbol.name not in exported_names
                and not symbol.name.startswith("_")
            ):
                # Skip if it's clearly internal
                if any(x in symbol.name.lower() for x in ["internal", "private", "helper"]):
                    continue

                discrepancies.append(
                    APIDiscrepancy(
                        kind="undocumented",
                        symbol_name=symbol.name,
                        location=symbol.source_file,
                        severity=0.4,  # Lower severity - not critical
                    )
                )

        return discrepancies

    def analyze_repository(self) -> dict[str, list[APIDiscrepancy]]:
        """Analyze entire repository for API discrepancies.

        Returns:
            Dictionary mapping package paths to their discrepancies
        """
        results = {}

        # Find all __init__.py files (package entry points)
        for init_file in self.repo_path.rglob("__init__.py"):
            package_dir = init_file.parent

            # Extract public API from __init__.py
            public_api = self.extract_public_api(init_file)

            # Extract runtime API from package
            runtime_api = self.extract_runtime_api(package_dir)

            # Compute commutator
            discrepancies = self.compute_api_commutator(public_api, runtime_api)

            if discrepancies:
                results[str(package_dir)] = discrepancies

        return results

    def get_summary(self, results: dict[str, list[APIDiscrepancy]]) -> dict[str, Any]:
        """Generate summary statistics."""
        total_discrepancies = sum(len(d) for d in results.values())
        missing_exports = sum(1 for d in results.values() for x in d if x.kind == "missing_export")
        undocumented = sum(1 for d in results.values() for x in d if x.kind == "undocumented")

        return {
            "packages_with_issues": len(results),
            "total_discrepancies": total_discrepancies,
            "missing_exports": missing_exports,
            "undocumented_api": undocumented,
            "acceptable": missing_exports == 0,  # Missing exports are critical
        }
