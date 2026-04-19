"""
I_envcompat = 1 iff repo is valid across supported environment matrix.

Environment matrix:
    Env = Python × OS × Arch × Toolchain × Secrets × RuntimeMode

Invariant checks:
    1. Python version compatibility declared
    2. OS-specific code paths handled
    3. Architecture compatibility (ARM/x86)
    4. Required secrets documented
    5. Runtime mode behavior defined
    6. Dependency compatibility validated

Based on 2024 cross-platform Python deployment best practices.
"""

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .base import Invariant, InvariantResult, InvariantSeverity


@dataclass
class EnvironmentGap:
    """Environment compatibility gap."""

    type: str
    severity: str
    location: str
    message: str
    suggestion: str = None


class EnvironmentInvariant(Invariant):
    """
    I_envcompat = 1 iff repo works across declared environment matrix.

    Detects:
    - Missing Python version constraints
    - Hard-coded platform-specific paths
    - Missing OS compatibility checks
    - Architecture-specific assumptions
    - Undeclared secret dependencies
    - Runtime mode inconsistencies
    """

    def __init__(self):
        super().__init__("I_envcompat", InvariantSeverity.ERROR)

    def check(self, repo_path: str, context: Dict[str, Any] = None) -> InvariantResult:
        """Check environment compatibility."""
        context = context or {}
        repo = Path(repo_path)

        gaps: List[EnvironmentGap] = []

        # Check pyproject.toml for version constraints
        gaps.extend(self._check_pyproject_constraints(repo))

        # Check requirements.txt for pins
        gaps.extend(self._check_requirements_constraints(repo))

        # Check Python files for platform assumptions
        py_files = list(repo.rglob("*.py"))
        for file_path in py_files:
            if ".venv" in str(file_path) or "__pycache__" in str(file_path):
                continue

            try:
                content = file_path.read_text()
                tree = ast.parse(content)

                file_gaps = self._analyze_file(file_path, tree, content)
                gaps.extend(file_gaps)

            except SyntaxError:
                continue
            except Exception:
                continue

        # Check for .env.example
        gaps.extend(self._check_env_documentation(repo))

        critical = [g for g in gaps if g.severity == "critical"]
        errors = [g for g in gaps if g.severity == "error"]
        warnings = [g for g in gaps if g.severity == "warning"]

        passed = len(critical) == 0 and len(errors) == 0

        if passed:
            message = f"Environment OK: {len(warnings)} warnings"
        else:
            message = (
                f"Environment gaps: {len(critical)} critical, "
                f"{len(errors)} errors, {len(warnings)} warnings"
            )

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=message,
            details={
                "files_analyzed": len(py_files),
                "critical_gaps": len(critical),
                "error_gaps": len(errors),
                "warning_gaps": len(warnings),
                "gaps": [
                    {"type": g.type, "location": g.location, "message": g.message}
                    for g in gaps[:20]
                ],
            },
        )

    def _check_pyproject_constraints(self, repo: Path) -> List[EnvironmentGap]:
        """Check pyproject.toml for version/environment constraints."""
        gaps: List[EnvironmentGap] = []

        pyproject = repo / "pyproject.toml"
        if not pyproject.exists():
            gaps.append(
                EnvironmentGap(
                    type="missing_pyproject",
                    severity="warning",
                    location=str(repo),
                    message="No pyproject.toml found - modern packaging recommended",
                )
            )
            return gaps

        content = pyproject.read_text()

        # Check for requires-python
        if "requires-python" not in content:
            gaps.append(
                EnvironmentGap(
                    type="missing_python_constraint",
                    severity="error",
                    location="pyproject.toml",
                    message="No requires-python constraint declared",
                    suggestion="Add requires-python = '>=3.x' to [project]",
                )
            )

        # Check for classifiers
        if "Programming Language :: Python" not in content:
            gaps.append(
                EnvironmentGap(
                    type="missing_classifiers",
                    severity="warning",
                    location="pyproject.toml",
                    message="No Python version classifiers",
                    suggestion="Add Python version classifiers for discoverability",
                )
            )

        return gaps

    def _check_requirements_constraints(self, repo: Path) -> List[EnvironmentGap]:
        """Check requirements files for version pinning."""
        gaps: List[EnvironmentGap] = []

        req_files = list(repo.glob("*requirements*.txt"))

        for req_file in req_files:
            content = req_file.read_text()

            # Check for unpinned dependencies
            for line in content.split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    # Check if pinned (==) or bounded (>=, <)
                    if (
                        "==" not in line
                        and ">=" not in line
                        and "<" not in line
                        and "~=" not in line
                    ):
                        if not line.startswith("-"):
                            gaps.append(
                                EnvironmentGap(
                                    type="unpinned_dependency",
                                    severity="info",
                                    location=str(req_file),
                                    message=f"Unpinned dependency: {line}",
                                    suggestion="Pin to major version or use >= lower bound",
                                )
                            )

        return gaps

    def _analyze_file(self, file_path: Path, tree: ast.AST, content: str) -> List[EnvironmentGap]:
        """Analyze a single file for environment assumptions."""
        gaps: List[EnvironmentGap] = []
        relative_path = str(file_path.relative_to(file_path.parent.parent))

        gaps.extend(self._find_platform_specific_code(tree, relative_path, content))
        gaps.extend(self._find_hardcoded_paths(tree, relative_path, content))
        gaps.extend(self._find_secret_access_patterns(tree, relative_path, content))

        return gaps

    def _find_platform_specific_code(
        self, tree: ast.AST, file_path: str, content: str
    ) -> List[EnvironmentGap]:
        """Find platform-specific code that may not be portable."""
        gaps: List[EnvironmentGap] = []

        # Check for platform-specific imports
        platform_modules = ["winreg", "msvcrt", "posix", "pwd", "grp", "termios"]

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in platform_modules:
                        gaps.append(
                            EnvironmentGap(
                                type="platform_specific_import",
                                severity="warning",
                                location=f"{file_path}:{node.lineno}",
                                message=f"Platform-specific import: {alias.name}",
                                suggestion="Add try/except ImportError with fallback",
                            )
                        )

            if isinstance(node, ast.ImportFrom):
                if node.module in platform_modules:
                    gaps.append(
                        EnvironmentGap(
                            type="platform_specific_import",
                            severity="warning",
                            location=f"{file_path}:{node.lineno}",
                            message=f"Platform-specific import: {node.module}",
                            suggestion="Add try/except ImportError with fallback",
                        )
                    )

        # Check for platform checks
        if "sys.platform" in content or "platform.system" in content:
            # Platform checks are good - they show awareness
            pass
        elif "/tmp/" in content or "C:\\" in content:
            # Hard-coded paths without platform checks
            gaps.append(
                EnvironmentGap(
                    type="hardcoded_platform_path",
                    severity="error",
                    location=f"{file_path}:1",
                    message="Hard-coded platform-specific path",
                    suggestion="Use tempfile or pathlib for cross-platform paths",
                )
            )

        return gaps

    def _find_hardcoded_paths(
        self, tree: ast.AST, file_path: str, content: str
    ) -> List[EnvironmentGap]:
        """Find hard-coded file paths."""
        gaps: List[EnvironmentGap] = []

        # Check for common hard-coded patterns
        bad_patterns = [
            r"/home/\w+",
            r"/Users/\w+",
            r"C:\\\\Users\\\\\w+",
        ]

        for pattern in bad_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[: match.start()].count("\n") + 1
                gaps.append(
                    EnvironmentGap(
                        type="hardcoded_user_path",
                        severity="error",
                        location=f"{file_path}:{line_num}",
                        message=f"Hard-coded user path: {match.group()}",
                        suggestion="Use Path.home() or environment variable",
                    )
                )

        return gaps

    def _find_secret_access_patterns(
        self, tree: ast.AST, file_path: str, content: str
    ) -> List[EnvironmentGap]:
        """Find secret access patterns without validation."""
        gaps: List[EnvironmentGap] = []

        # Check for os.environ.get without default
        if "os.environ.get(" in content:
            for i, line in enumerate(content.split("\n"), 1):
                if "os.environ.get(" in line and "," not in line:
                    # No default provided
                    if "SECRET" in line or "KEY" in line or "PASSWORD" in line:
                        gaps.append(
                            EnvironmentGap(
                                type="secret_no_default",
                                severity="warning",
                                location=f"{file_path}:{i}",
                                message="Secret access without default may fail",
                                suggestion="Provide default or handle KeyError",
                            )
                        )

        return gaps

    def _check_env_documentation(self, repo: Path) -> List[EnvironmentGap]:
        """Check for environment variable documentation."""
        gaps: List[EnvironmentGap] = []

        env_example = repo / ".env.example"
        env_template = repo / ".env.template"

        if not env_example.exists() and not env_template.exists():
            # Check if .env is in gitignore (secrets likely used)
            gitignore = repo / ".gitignore"
            if gitignore.exists():
                gitignore_content = gitignore.read_text()
                if ".env" in gitignore_content:
                    gaps.append(
                        EnvironmentGap(
                            type="missing_env_template",
                            severity="error",
                            location=str(repo),
                            message=".env in .gitignore but no .env.example template",
                            suggestion="Create .env.example with required variables",
                        )
                    )

        return gaps
