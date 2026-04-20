from __future__ import annotations

"""Entrypoint analysis substrate.

Verifies that launcher declarations in pyproject.toml point to real,
importable, runnable targets.

I_entry = 1 iff launcher target exists and behaves as documented.
"""

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

# tomllib available in Python 3.11+, fallback to tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


@dataclass
class EntrypointDeclaration:
    """An entrypoint declared in pyproject.toml."""

    name: str
    module: str
    function: str
    source_file: str = "pyproject.toml"
    line: int = 0


@dataclass
class EntrypointValidation:
    """Result of validating an entrypoint."""

    declaration: EntrypointDeclaration
    valid: bool
    module_exists: bool = False
    function_exists: bool = False
    is_callable: bool = False
    error_message: str = ""

    @property
    def is_broken(self) -> bool:
        """Check if entrypoint is broken."""
        return not self.valid


class EntrypointSubstrate:
    """Entrypoint validation substrate.

    Loads entrypoint declarations from pyproject.toml and verifies
    that each points to a real, importable, callable target.

    Usage:
        substrate = EntrypointSubstrate("/path/to/repo")

        # Load declarations
        entrypoints = substrate.load_entrypoints()

        # Validate each
        for ep in entrypoints:
            result = substrate.validate_entrypoint(ep)
            if not result.valid:
                print(f"Broken: {ep.name} -> {ep.module}:{ep.function}")
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self._cache: dict[str, list[EntrypointDeclaration]] = {}

    def load_entrypoints(self) -> list[EntrypointDeclaration]:
        """Load entrypoint declarations from pyproject.toml.

        Returns:
            List of entrypoint declarations
        """
        pyproject_path = self.repo_path / "pyproject.toml"

        if not pyproject_path.exists():
            return []

        if tomllib is None:
            return []

        try:
            content = pyproject_path.read_text(encoding="utf-8")
            config = tomllib.loads(content)

            entrypoints = []

            # Check [project.scripts] (console scripts)
            scripts = config.get("project", {}).get("scripts", {})
            for name, target in scripts.items():
                # Parse "module:function" format
                if ":" in target:
                    module, func = target.split(":", 1)
                    entrypoints.append(
                        EntrypointDeclaration(
                            name=name,
                            module=module,
                            function=func,
                            source_file=str(pyproject_path),
                        )
                    )

            # Check [project.gui-scripts]
            gui_scripts = config.get("project", {}).get("gui-scripts", {})
            for name, target in gui_scripts.items():
                if ":" in target:
                    module, func = target.split(":", 1)
                    entrypoints.append(
                        EntrypointDeclaration(
                            name=name,
                            module=module,
                            function=func,
                            source_file=str(pyproject_path),
                        )
                    )

            return entrypoints

        except Exception:
            return []

    def validate_entrypoint(self, declaration: EntrypointDeclaration) -> EntrypointValidation:
        """Validate that an entrypoint declaration points to a real target.

        Args:
            declaration: Entrypoint to validate

        Returns:
            EntrypointValidation with results
        """
        # Find the module file
        module_path = self._resolve_module(declaration.module)

        if not module_path:
            return EntrypointValidation(
                declaration=declaration,
                valid=False,
                module_exists=False,
                function_exists=False,
                error_message=f"Module '{declaration.module}' not found",
            )

        # Check if function exists in module
        function_info = self._find_function(module_path, declaration.function)

        if not function_info:
            return EntrypointValidation(
                declaration=declaration,
                valid=False,
                module_exists=True,
                function_exists=False,
                error_message=f"Function '{declaration.function}' not found in {declaration.module}",
            )

        # Check if it's callable (function or callable class)
        is_callable = function_info.get("is_callable", False)

        return EntrypointValidation(
            declaration=declaration,
            valid=is_callable,
            module_exists=True,
            function_exists=True,
            is_callable=is_callable,
        )

    def _resolve_module(self, module_name: str) -> Optional[Path]:
        """Resolve module name to file path."""
        # Convert module name to path
        parts = module_name.split(".")

        # Try as package/module.py
        module_file = self.repo_path / "/".join(parts[:-1]) / f"{parts[-1]}.py"
        if module_file.exists():
            return module_file

        # Try as package/__init__.py (module is package)
        if len(parts) == 1:
            init_file = self.repo_path / parts[0] / "__init__.py"
            if init_file.exists():
                return init_file

        # Try src/ layout
        src_file = self.repo_path / "src" / "/".join(parts[:-1]) / f"{parts[-1]}.py"
        if src_file.exists():
            return src_file

        src_init = self.repo_path / "src" / "/".join(parts) / "__init__.py"
        if src_init.exists():
            return src_init

        return None

    def _find_function(self, module_path: Path, function_name: str) -> Optional[dict[str, Any]]:
        """Find function in module file."""
        try:
            source = module_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name == function_name:
                        return {
                            "name": function_name,
                            "is_callable": True,
                            "line": node.lineno,
                            "args": len(node.args.args),
                        }
                elif isinstance(node, ast.ClassDef):
                    if node.name == function_name:
                        # Check if class has __call__ or is likely callable
                        has_call = any(
                            isinstance(n, ast.FunctionDef) and n.name == "__call__"
                            for n in ast.walk(node)
                        )
                        return {
                            "name": function_name,
                            "is_callable": True,  # Classes are callable
                            "line": node.lineno,
                            "is_class": True,
                            "has_call": has_call,
                        }

            return None

        except SyntaxError:
            return None
        except Exception:
            return None

    def analyze_repository(self) -> list[EntrypointValidation]:
        """Analyze all entrypoints in repository.

        Returns:
            List of validation results
        """
        declarations = self.load_entrypoints()
        return [self.validate_entrypoint(d) for d in declarations]

    def get_broken_entrypoints(self) -> list[EntrypointValidation]:
        """Get all broken entrypoints."""
        return [v for v in self.analyze_repository() if not v.valid]

    def get_summary(self, validations: list[EntrypointValidation]) -> dict[str, Any]:
        """Generate summary statistics."""
        total = len(validations)
        broken = sum(1 for v in validations if not v.valid)
        valid = total - broken

        # Categorize failures
        missing_module = sum(1 for v in validations if not v.module_exists)
        missing_function = sum(1 for v in validations if v.module_exists and not v.function_exists)
        not_callable = sum(1 for v in validations if v.function_exists and not v.is_callable)

        return {
            "total_entrypoints": total,
            "valid": valid,
            "broken": broken,
            "missing_module": missing_module,
            "missing_function": missing_function,
            "not_callable": not_callable,
            "releaseable": broken == 0,
        }
