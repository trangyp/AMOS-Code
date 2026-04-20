"""
Contract Analysis Module - Interface Commutator

Detects API drift with a commutator-style rule:
    [A_public, A_runtime] = A_public·A_runtime - A_runtime·A_public

If [A_public, A_runtime] ≠ 0, you have interface drift.

Operationally:
- A_public = what docs, demos, tests, CLI, MCP, or __init__.py claim
- A_runtime = what code actually exports or accepts
"""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Union


@dataclass
class APIFunction:
    """Represents a function in the public API."""

    name: str
    module: str
    args: list[str] = field(default_factory=list)
    returns: str = None
    found_in: list[str] = field(default_factory=list)


@dataclass
class ContractViolation:
    """Represents a contract mismatch."""

    function_name: str
    claim_source: str  # docs, tests, demos, etc.
    runtime_source: str  # actual code
    claim_sig: APIFunction
    runtime_sig: APIFunction
    violation_type: str  # "missing", "args_mismatch", "return_mismatch"


class ContractAnalyzer:
    """
    Analyzes API contracts across documentation, tests, demos, and code.

    Implements the interface commutator:
        [A_public, A_runtime] = A_public·A_runtime - A_runtime·A_public
    """

    def __init__(self, repo_path: Union[str, Path]):
        self.repo_path = Path(repo_path).resolve()
        self.public_api: Dict[str, APIFunction] = {}
        self.runtime_api: Dict[str, APIFunction] = {}
        self.violations: list[ContractViolation] = []

    def analyze(self) -> list[ContractViolation]:
        """Run full contract analysis."""
        self._collect_public_api()
        self._collect_runtime_api()
        self._compute_commutator()
        return self.violations

    def _collect_public_api(self):
        """
        Collect A_public from:
        - __init__.py exports
        - README examples
        - Test files
        - Demo files
        - Docstrings
        """
        # Collect from __init__.py files
        for init_file in self.repo_path.rglob("__init__.py"):
            if any(p.startswith(".") for p in init_file.relative_to(self.repo_path).parts):
                continue
            self._parse_init_exports(init_file)

        # Collect from README
        readme = self.repo_path / "README.md"
        if readme.exists():
            self._parse_readme_examples(readme)

        # Collect from tests
        test_dir = self.repo_path / "tests"
        if test_dir.exists():
            for test_file in test_dir.rglob("*.py"):
                self._parse_test_usage(test_file)

    def _collect_runtime_api(self):
        """
        Collect A_runtime from actual code:
        - Function definitions
        - Class methods
        - Module exports
        """
        for py_file in self.repo_path.rglob("*.py"):
            if any(p.startswith(".") for p in py_file.relative_to(self.repo_path).parts):
                continue
            if "test" in py_file.name or "__pycache__" in str(py_file):
                continue
            self._parse_runtime_api(py_file)

    def _parse_init_exports(self, init_file: Path):
        """Parse __init__.py for __all__ and imports."""
        try:
            content = init_file.read_text()
            tree = ast.parse(content)

            module = str(init_file.parent.relative_to(self.repo_path)).replace("/", ".")
            if module == ".":
                module = ""

            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__":
                            # Found __all__ definition
                            if isinstance(node.value, (ast.List, ast.Tuple)):
                                for elt in node.value.elts:
                                    if isinstance(elt, ast.Constant):
                                        func_name = elt.value
                                        key = f"{module}.{func_name}" if module else func_name
                                        if key not in self.public_api:
                                            self.public_api[key] = APIFunction(
                                                name=func_name,
                                                module=module,
                                                found_in=[str(init_file)],
                                            )
        except Exception:
            pass

    def _parse_readme_examples(self, readme: Path):
        """Parse README for code examples showing API usage."""
        try:
            content = readme.read_text()
            # Find code blocks
            code_blocks = re.findall(r"```python\n(.*?)\n```", content, re.DOTALL)

            for block in code_blocks:
                # Look for function calls
                calls = re.findall(r"(\w+)\s*\(", block)
                for func_name in calls:
                    key = func_name  # Simplified - may need module resolution
                    if key not in self.public_api:
                        self.public_api[key] = APIFunction(
                            name=func_name, module="", found_in=["README.md"]
                        )
        except Exception:
            pass

    def _parse_test_usage(self, test_file: Path):
        """Parse test files for API usage patterns."""
        try:
            content = test_file.read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        key = func_name
                        if key not in self.public_api:
                            self.public_api[key] = APIFunction(
                                name=func_name, module="", found_in=[str(test_file)]
                            )
        except Exception:
            pass

    def _parse_runtime_api(self, py_file: Path):
        """Parse Python file for actual function/class definitions."""
        try:
            content = py_file.read_text()
            tree = ast.parse(content)

            module = str(py_file.relative_to(self.repo_path)).replace("/", ".").replace(".py", "")

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Skip private functions
                    if node.name.startswith("_"):
                        continue

                    # Get args
                    args = [arg.arg for arg in node.args.args]

                    # Get return annotation if present
                    returns = None
                    if node.returns and isinstance(node.returns, ast.Name):
                        returns = node.returns.id

                    key = f"{module}.{node.name}"
                    self.runtime_api[key] = APIFunction(
                        name=node.name,
                        module=module,
                        args=args,
                        returns=returns,
                        found_in=[str(py_file)],
                    )

                elif isinstance(node, ast.ClassDef):
                    # Skip private classes
                    if node.name.startswith("_"):
                        continue

                    key = f"{module}.{node.name}"
                    self.runtime_api[key] = APIFunction(
                        name=node.name, module=module, found_in=[str(py_file)]
                    )
        except Exception:
            pass

    def _compute_commutator(self):
        """
        Compute [A_public, A_runtime] = A_public·A_runtime - A_runtime·A_public

        Operationally: Find elements in public but not in runtime (missing)
        and elements in runtime but not used in public (untested/undocumented).
        """
        # Find public API not in runtime (broken contracts)
        for key, func in self.public_api.items():
            if key not in self.runtime_api:
                self.violations.append(
                    ContractViolation(
                        function_name=func.name,
                        claim_source=func.found_in[0] if func.found_in else "unknown",
                        runtime_source="runtime",
                        claim_sig=func,
                        runtime_sig=None,
                        violation_type="missing",
                    )
                )

        # Find runtime API not in public (unadvertised - informational)
        for key, func in self.runtime_api.items():
            # Check if this appears in public API
            found = False
            for pub_key in self.public_api:
                if func.name in pub_key or pub_key in key:
                    found = True
                    break

            if not found:
                self.violations.append(
                    ContractViolation(
                        function_name=func.name,
                        claim_source="none",
                        runtime_source=func.found_in[0] if func.found_in else "unknown",
                        claim_sig=None,
                        runtime_sig=func,
                        violation_type="undocumented",
                    )
                )

    def get_report(self) -> str:
        """Generate a formatted contract analysis report."""
        lines = [
            "=" * 60,
            "API CONTRACT ANALYSIS",
            "=" * 60,
            f"Public API surface: {len(self.public_api)} functions",
            f"Runtime API surface: {len(self.runtime_api)} functions",
            f"Violations: {len(self.violations)}",
            "-" * 60,
        ]

        broken = [v for v in self.violations if v.violation_type == "missing"]
        undocumented = [v for v in self.violations if v.violation_type == "undocumented"]

        if broken:
            lines.append("BROKEN CONTRACTS (claimed but missing):")
            for v in broken:
                lines.append(f"  ✗ {v.function_name}")
                lines.append(f"    Claimed in: {v.claim_source}")

        if undocumented:
            lines.append("\nUNDOCUMENTED API (exists but not claimed):")
            for v in undocumented[:10]:  # Limit output
                lines.append(f"  ! {v.function_name} in {v.runtime_source}")
            if len(undocumented) > 10:
                lines.append(f"  ... and {len(undocumented) - 10} more")

        lines.append("=" * 60)

        return "\n".join(lines)
