"""Import resolution substrate for repository analysis.

Resolves Python imports to verify:
- Absolute imports point to real modules
- Relative imports resolve correctly
- No circular dependencies (optional)
- Import statements are extractable from source

Based on Python import resolution rules (PEP 302, PEP 451).
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ImportStatement:
    """Represents a Python import statement."""

    source_file: str
    module: str
    names: list[str] = field(default_factory=list)
    is_relative: bool = False
    is_from_import: bool = False
    level: int = 0  # Relative import level (0 = absolute)
    line: int = 0
    column: int = 0

    @property
    def is_absolute(self) -> bool:
        """Check if this is an absolute import."""
        return not self.is_relative and self.level == 0

    @property
    def full_module_path(self) -> str:
        """Get the full dotted path for this import."""
        if self.is_relative:
            # Resolve relative to source file
            source_path = Path(self.source_file)
            if source_path.suffix in (".py", ".pyw"):
                # Convert file path to package path
                parts = list(source_path.parts)

                # Find package root (directory with __init__.py)
                package_root = source_path.parent
                while (
                    package_root.parent.exists() and (package_root.parent / "__init__.py").exists()
                ):
                    package_root = package_root.parent

                # Build package path
                rel_path = source_path.relative_to(package_root)
                package_parts = list(rel_path.parent.parts)

                # Go up levels for relative import
                if self.level > 1:
                    package_parts = package_parts[: -(self.level - 1)]

                # Add the module
                if self.module:
                    package_parts.append(self.module)

                return ".".join(package_parts)

            return self.module

        return self.module


@dataclass
class ImportResolution:
    """Result of resolving an import."""

    import_stmt: ImportStatement
    resolved: bool
    target_path: Path | None = None
    is_package: bool = False
    error_message: str = ""

    @property
    def is_unresolved(self) -> bool:
        """Check if import could not be resolved."""
        return not self.resolved


class ImportSubstrate:
    """Import resolution substrate for Python repositories.

    Extracts and resolves import statements to verify they point
    to real modules/packages in the repository or system.

    Usage:
        substrate = ImportSubstrate("/path/to/repo")
        imports = substrate.extract_imports("src/main.py")
        for imp in imports:
            resolution = substrate.resolve_import(imp)
            if not resolution.resolved:
                print(f"Unresolved: {imp.module}")
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self._cache: dict[str, list[ImportStatement]] = {}
        self._python_path: list[Path] = self._build_python_path()

    def _build_python_path(self) -> list[Path]:
        """Build search path for module resolution."""
        paths = [self.repo_path]

        # Add standard library and site-packages
        for p in sys.path:
            if p:  # Skip empty strings
                paths.append(Path(p))

        return paths

    def extract_imports(self, file_path: str | Path) -> list[ImportStatement]:
        """Extract all import statements from a Python file.

        Uses AST parsing for reliable extraction.

        Args:
            file_path: Path to Python file

        Returns:
            List of ImportStatement objects
        """
        file_path = Path(file_path)
        cache_key = str(file_path)

        if cache_key in self._cache:
            return self._cache[cache_key]

        imports = []

        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    # Regular import: import os, import sys.path
                    for alias in node.names:
                        imports.append(
                            ImportStatement(
                                source_file=str(file_path),
                                module=alias.name.split(".")[0],
                                names=[alias.name],
                                is_relative=False,
                                is_from_import=False,
                                level=0,
                                line=node.lineno or 0,
                                column=node.col_offset or 0,
                            )
                        )

                elif isinstance(node, ast.ImportFrom):
                    # From import: from os import path
                    module = node.module or ""
                    level = node.level or 0

                    imports.append(
                        ImportStatement(
                            source_file=str(file_path),
                            module=module,
                            names=[a.name for a in node.names],
                            is_relative=level > 0,
                            is_from_import=True,
                            level=level,
                            line=node.lineno or 0,
                            column=node.col_offset or 0,
                        )
                    )

        except SyntaxError:
            # File has syntax errors - skip import extraction
            pass
        except Exception:
            # Other errors - skip
            pass

        self._cache[cache_key] = imports
        return imports

    def resolve_import(self, import_stmt: ImportStatement) -> ImportResolution:
        """Resolve an import statement to a file path.

        Args:
            import_stmt: Import statement to resolve

        Returns:
            ImportResolution with result
        """
        if import_stmt.is_relative:
            return self._resolve_relative(import_stmt)
        else:
            return self._resolve_absolute(import_stmt)

    def _resolve_absolute(self, import_stmt: ImportStatement) -> ImportResolution:
        """Resolve absolute import (import os, from os import path)."""
        module_parts = import_stmt.module.split(".")

        # Try to find in repository first
        for search_path in self._python_path:
            # Try as module file: package/module.py
            module_file = search_path / "/".join(module_parts[:-1]) / f"{module_parts[-1]}.py"
            if module_file.exists():
                return ImportResolution(
                    import_stmt=import_stmt,
                    resolved=True,
                    target_path=module_file,
                    is_package=False,
                )

            # Try as package: package/module/__init__.py
            package_init = search_path / "/".join(module_parts) / "__init__.py"
            if package_init.exists():
                return ImportResolution(
                    import_stmt=import_stmt,
                    resolved=True,
                    target_path=package_init.parent,
                    is_package=True,
                )

            # Try single module: module.py
            if len(module_parts) == 1:
                single_module = search_path / f"{module_parts[0]}.py"
                if single_module.exists():
                    return ImportResolution(
                        import_stmt=import_stmt,
                        resolved=True,
                        target_path=single_module,
                        is_package=False,
                    )

        # Check if it's a stdlib or installed package
        try:
            # Try importing to check existence
            __import__(import_stmt.module)
            return ImportResolution(
                import_stmt=import_stmt,
                resolved=True,
                target_path=None,  # External package
                is_package=True,
            )
        except ImportError:
            pass

        # Could not resolve
        return ImportResolution(
            import_stmt=import_stmt,
            resolved=False,
            error_message=f"Module '{import_stmt.module}' not found",
        )

    def _resolve_relative(self, import_stmt: ImportStatement) -> ImportResolution:
        """Resolve relative import (from . import x, from .. import y)."""
        source_file = Path(import_stmt.source_file)
        source_dir = source_file.parent

        # Go up levels
        target_dir = source_dir
        for _ in range(import_stmt.level - 1):
            target_dir = target_dir.parent
            if not target_dir.exists():
                return ImportResolution(
                    import_stmt=import_stmt,
                    resolved=False,
                    error_message=f"Relative import goes above package root: level={import_stmt.level}",
                )

        if import_stmt.module:
            # from .module import x
            module_parts = import_stmt.module.split(".")

            # Try as module file
            module_file = target_dir / "/".join(module_parts[:-1]) / f"{module_parts[-1]}.py"
            if module_file.exists():
                return ImportResolution(
                    import_stmt=import_stmt,
                    resolved=True,
                    target_path=module_file,
                    is_package=False,
                )

            # Try as package
            package_init = target_dir / "/".join(module_parts) / "__init__.py"
            if package_init.exists():
                return ImportResolution(
                    import_stmt=import_stmt,
                    resolved=True,
                    target_path=package_init.parent,
                    is_package=True,
                )
        else:
            # from . import x (import from parent package)
            for name in import_stmt.names:
                # Try as module
                module_file = target_dir / f"{name}.py"
                if module_file.exists():
                    return ImportResolution(
                        import_stmt=import_stmt,
                        resolved=True,
                        target_path=module_file,
                        is_package=False,
                    )

                # Try as package
                package_init = target_dir / name / "__init__.py"
                if package_init.exists():
                    return ImportResolution(
                        import_stmt=import_stmt,
                        resolved=True,
                        target_path=package_init.parent,
                        is_package=True,
                    )

        return ImportResolution(
            import_stmt=import_stmt,
            resolved=False,
            error_message=f"Relative import '{import_stmt.module}' not found from {source_file}",
        )

    def analyze_file(self, file_path: str | Path) -> list[ImportResolution]:
        """Analyze a single file and resolve all its imports.

        Args:
            file_path: Path to Python file

        Returns:
            List of import resolutions
        """
        imports = self.extract_imports(file_path)
        return [self.resolve_import(imp) for imp in imports]

    def analyze_repository(self, pattern: str = "*.py") -> dict[str, list[ImportResolution]]:
        """Analyze entire repository for import issues.

        Args:
            pattern: File glob pattern

        Returns:
            Dictionary mapping file paths to their import resolutions
        """
        results = {}

        for file_path in self.repo_path.rglob(pattern):
            if file_path.is_file():
                results[str(file_path)] = self.analyze_file(file_path)

        return results

    def get_unresolved_imports(self, pattern: str = "*.py") -> list[ImportResolution]:
        """Get all unresolved imports in repository.

        Args:
            pattern: File glob pattern

        Returns:
            List of unresolved import resolutions
        """
        unresolved = []

        for file_path, resolutions in self.analyze_repository(pattern).items():
            for res in resolutions:
                if not res.resolved:
                    unresolved.append(res)

        return unresolved
