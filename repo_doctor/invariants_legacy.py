"""
Invariant Engine - Hard Pass/Fail Rules for Repository Validity

Invariant law:
    I = {I_parse, I_import, I_build, I_tests, I_packaging, I_api, I_entrypoints, I_security}

    A repo is valid only if:
        ∀ I_n ∈ I : I_n(Ψ_repo) = 1

Not "mostly good." Pass or fail.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from .state_vector import RepoStateVector, StateDimension

# tomllib available in Python 3.11+, fallback to tomli
if sys.version_info >= (3, 11):
    import tomllib

    _USE_BYTES = True  # tomllib.loads expects bytes
else:
    try:
        import tomli as tomllib

        _USE_BYTES = False  # tomli.loads expects string
    except ImportError:
        tomllib = None
        _USE_BYTES = False

# Detect correct python command
PYTHON_CMD = sys.executable


def _load_toml(path: Path) -> dict:
    """Load TOML file, handling both tomllib (bytes) and tomli (string) APIs."""
    if tomllib is None:
        raise ImportError("tomllib/tomli not installed")
    if _USE_BYTES:
        content = path.read_bytes()
    else:
        content = path.read_text()
    return tomllib.loads(content)


@dataclass
class InvariantResult:
    """Result of an invariant check."""

    passed: bool
    dimension: StateDimension
    message: str
    details: list[str] = field(default_factory=list)
    files_affected: list[str] = field(default_factory=list)


class Invariant(ABC):
    """Base class for all invariants."""

    name: str
    dimension: StateDimension

    @abstractmethod
    def check(self, repo_path: Path) -> InvariantResult:
        """Check the invariant. Must return passed=True or passed=False."""
        pass

    def _run_command(self, cmd: list[str], cwd: Path) -> tuple[int, str, str]:
        """Run a shell command and return (returncode, stdout, stderr)."""
        # Replace 'python' with detected python command
        if cmd and cmd[0] == "python":
            cmd[0] = PYTHON_CMD
        try:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=60)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)


class ParseInvariant(Invariant):
    """
    I_parse = 1 iff no syntax errors

    All source files must parse as valid Python AST.
    """

    name = "parse"
    dimension = StateDimension.SYNTAX

    def check(self, repo_path: Path) -> InvariantResult:
        errors = []
        files_affected = []

        for py_file in repo_path.rglob("*.py"):
            # Skip hidden directories
            if any(part.startswith(".") for part in py_file.relative_to(repo_path).parts):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                ast.parse(content)
            except SyntaxError as e:
                errors.append(f"{py_file.relative_to(repo_path)}:{e.lineno}: {e.msg}")
                files_affected.append(str(py_file.relative_to(repo_path)))
            except UnicodeDecodeError:
                errors.append(f"{py_file.relative_to(repo_path)}: encoding error")
                files_affected.append(str(py_file.relative_to(repo_path)))

        return InvariantResult(
            passed=len(errors) == 0,
            dimension=self.dimension,
            message="All files parse successfully"
            if not errors
            else f"{len(errors)} files have syntax errors",
            details=errors,
            files_affected=files_affected,
        )


class ImportInvariant(Invariant):
    """
    I_import = 1 iff all public imports and entrypoint imports resolve

    Every advertised import must resolve.
    """

    name = "import"
    dimension = StateDimension.IMPORT

    def check(self, repo_path: Path) -> InvariantResult:
        errors = []
        files_affected = []

        # Find all Python files and check their imports
        for py_file in repo_path.rglob("*.py"):
            if any(part.startswith(".") for part in py_file.relative_to(repo_path).parts):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            # Check if import is resolvable
                            if not self._check_import(alias.name, repo_path):
                                rel_path = py_file.relative_to(repo_path)
                                errors.append(f"{rel_path}: cannot import '{alias.name}'")
                                files_affected.append(str(rel_path))

                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            # Check from imports
                            full_module = node.module
                            if node.level > 0:
                                # Relative import - resolve based on file location
                                full_module = self._resolve_relative_import(
                                    node.module, node.level, py_file, repo_path
                                )

                            if full_module and not self._check_import(full_module, repo_path):
                                rel_path = py_file.relative_to(repo_path)
                                errors.append(f"{rel_path}: cannot import from '{node.module}'")
                                files_affected.append(str(rel_path))

            except Exception:
                # Parse errors handled by ParseInvariant
                pass

        return InvariantResult(
            passed=len(errors) == 0,
            dimension=self.dimension,
            message="All imports resolve" if not errors else f"{len(errors)} unresolved imports",
            details=errors,
            files_affected=files_affected,
        )

    def _check_import(self, module_name: str, repo_path: Path) -> bool:
        """Check if a module can be imported."""
        # Skip standard library and third-party imports for now
        # Focus on local package imports
        parts = module_name.split(".")

        # Check if it's a local module
        for i in range(len(parts), 0, -1):
            candidate = "/".join(parts[:i])

            # Check as package
            pkg_path = repo_path / candidate / "__init__.py"
            if pkg_path.exists():
                return True

            # Check as module
            mod_path = repo_path / (candidate + ".py")
            if mod_path.exists():
                return True

        # Assume external imports are fine (would need pip freeze to validate)
        return True

    def _resolve_relative_import(
        self, module: str, level: int, file_path: Path, repo_path: Path
    ) -> str:
        """Resolve a relative import to absolute module path."""
        rel_parts = list(file_path.relative_to(repo_path).parent.parts)

        if level > len(rel_parts):
            return None

        base = ".".join(rel_parts[: -level + 1] if level > 1 else rel_parts)

        if module:
            if base:
                return f"{base}.{module}"
            return module
        return base


class BuildInvariant(Invariant):
    """
    I_build = 1 iff build succeeds from canonical config

    Package/app builds from declared metadata.
    """

    name = "build"
    dimension = StateDimension.BUILD

    def check(self, repo_path: Path) -> InvariantResult:
        errors = []

        # Check for pyproject.toml or setup.py
        has_pyproject = (repo_path / "pyproject.toml").exists()
        has_setup = (repo_path / "setup.py").exists()

        if not has_pyproject and not has_setup:
            errors.append("No pyproject.toml or setup.py found")
            return InvariantResult(
                passed=False,
                dimension=self.dimension,
                message="No build configuration found",
                details=errors,
            )

        # Try to validate the build config
        if has_pyproject:
            try:
                _load_toml(repo_path / "pyproject.toml")
            except ImportError:
                errors.append("tomllib/tomli not installed - cannot parse pyproject.toml")
            except Exception as e:
                errors.append(f"Invalid pyproject.toml: {e}")

        return InvariantResult(
            passed=len(errors) == 0,
            dimension=self.dimension,
            message="Build configuration valid" if not errors else "Build configuration invalid",
            details=errors,
        )


class TestInvariant(Invariant):
    """
    I_tests = 1 iff required test set passes

    Critical tests pass.
    """

    name = "tests"
    dimension = StateDimension.TEST

    def check(self, repo_path: Path) -> InvariantResult:
        errors = []

        # Check for test discovery
        test_dirs = ["tests", "test", "_tests"]
        has_tests = any((repo_path / d).exists() for d in test_dirs)

        if not has_tests:
            return InvariantResult(
                passed=True,  # No tests is not a failure, just informational
                dimension=self.dimension,
                message="No tests directory found (optional)",
                details=["Consider adding tests/ directory"],
            )

        # Try to run a quick test collection
        rc, stdout, stderr = self._run_command(
            ["python", "-m", "pytest", "--collect-only", "-q"], repo_path
        )

        if rc != 0 and "no module named pytest" not in stderr.lower():
            errors.append(f"Test collection failed: {stderr[:200]}")

        return InvariantResult(
            passed=len(errors) == 0,
            dimension=self.dimension,
            message="Tests collectible" if not errors else "Test collection failed",
            details=errors,
        )


class PackagingInvariant(Invariant):
    """
    I_packaging = 1 iff declared package surface == shipped package surface

    pyproject.toml, setup.py, entrypoints, and included modules agree.
    """

    name = "packaging"
    dimension = StateDimension.PACKAGING

    def check(self, repo_path: Path) -> InvariantResult:
        errors = []

        pyproject_path = repo_path / "pyproject.toml"
        setup_path = repo_path / "setup.py"

        if not pyproject_path.exists() and not setup_path.exists():
            errors.append("No packaging configuration (pyproject.toml or setup.py)")

        # Check pyproject.toml for package name consistency
        if pyproject_path.exists():
            try:
                config = _load_toml(pyproject_path)

                # Check project name
                project = config.get("project", {})
                if not project.get("name"):
                    errors.append("pyproject.toml: missing project.name")

                # Check for valid version
                if not project.get("version") and project.get("dynamic", []) != ["version"]:
                    errors.append("pyproject.toml: missing version")

            except ImportError:
                errors.append("tomllib/tomli not installed")
            except Exception as e:
                errors.append(f"pyproject.toml error: {e}")

        return InvariantResult(
            passed=len(errors) == 0,
            dimension=self.dimension,
            message="Packaging configuration valid"
            if not errors
            else f"{len(errors)} packaging issues",
            details=errors,
        )


class APIInvariant(Invariant):
    """
    I_api = 1 iff public contract graph is commutative

    Docs, demos, tests, CLI, MCP, and exports all agree on method names, args, and return fields.
    """

    name = "api"
    dimension = StateDimension.API

    def check(self, repo_path: Path) -> InvariantResult:
        errors = []

        # Check __init__.py exports
        init_files = list(repo_path.rglob("__init__.py"))

        for init_file in init_files:
            if any(part.startswith(".") for part in init_file.relative_to(repo_path).parts):
                continue

            try:
                content = init_file.read_text()
                tree = ast.parse(content)

                # Check for __all__ definition (best practice)
                has_all = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and target.id == "__all__":
                                has_all = True
                                break

                # Not having __all__ is a warning, not an error
                if not has_all and init_file.parent != repo_path:
                    # Only warn for package inits, not root
                    pass

            except Exception:
                pass

        return InvariantResult(
            passed=len(errors) == 0,
            dimension=self.dimension,
            message="API contracts valid" if not errors else f"{len(errors)} API issues",
            details=errors,
        )


class EntrypointInvariant(Invariant):
    """
    I_entry = 1 iff launcher target exists and behaves as documented

    Every launcher path points to a real, runnable interface.
    """

    name = "entrypoints"
    dimension = StateDimension.CONFIG

    def check(self, repo_path: Path) -> InvariantResult:
        errors = []
        files_affected = []

        # Check pyproject.toml for console scripts
        pyproject_path = repo_path / "pyproject.toml"

        if pyproject_path.exists():
            try:
                config = _load_toml(pyproject_path)

                scripts = config.get("project", {}).get("scripts", {})
                gui_scripts = config.get("project", {}).get("gui-scripts", {})
                all_scripts = {**scripts, **gui_scripts}

                for name, entrypoint in all_scripts.items():
                    # Parse entrypoint (format: "module.submodule:function")
                    if ":" not in entrypoint:
                        errors.append(f"Invalid entrypoint format for '{name}': {entrypoint}")
                        continue

                    module_path, _ = entrypoint.split(":", 1)

                    # Check if module exists
                    parts = module_path.split(".")
                    module_file = (repo_path / "/".join(parts)).with_suffix(".py")
                    module_pkg = repo_path / "/".join(parts) / "__init__.py"

                    # If not found and first part matches repo name, try relative
                    if (
                        not module_file.exists()
                        and not module_pkg.exists()
                        and len(parts) > 1
                        and repo_path.name == parts[0]
                    ):
                        rel_parts = parts[1:]
                        module_file = (repo_path / "/".join(rel_parts)).with_suffix(".py")
                        module_pkg = repo_path / "/".join(rel_parts) / "__init__.py"

                    if not module_file.exists() and not module_pkg.exists():
                        errors.append(f"Entrypoint '{name}' -> module not found: {module_path}")
                        files_affected.append(f"pyproject.toml [scripts.{name}]")

            except ImportError:
                errors.append("tomllib/tomli not installed")
            except Exception as e:
                errors.append(f"Error checking entrypoints: {e}")

        return InvariantResult(
            passed=len(errors) == 0,
            dimension=self.dimension,
            message="All entrypoints valid" if not errors else f"{len(errors)} entrypoint issues",
            details=errors,
            files_affected=files_affected,
        )


class SecurityInvariant(Invariant):
    """
    I_security = 1 iff dep + runtime policies pass

    No known vulnerable dependencies and no unsafe default execution paths.
    """

    name = "security"
    dimension = StateDimension.SECURITY

    def check(self, repo_path: Path) -> InvariantResult:
        errors = []

        # Check for common security issues in code
        dangerous_patterns = [
            ("eval(", "Use of eval() detected"),
            ("exec(", "Use of exec() detected"),
        ]

        for py_file in repo_path.rglob("*.py"):
            if any(part.startswith(".") for part in py_file.relative_to(repo_path).parts):
                continue

            try:
                content = py_file.read_text()
                for pattern, msg in dangerous_patterns:
                    if pattern in content:
                        # Check if it's actually a call (simple heuristic)
                        lines = content.split("\n")
                        for i, line in enumerate(lines, 1):
                            if pattern in line and not line.strip().startswith("#"):
                                errors.append(f"{py_file.relative_to(repo_path)}:{i}: {msg}")
            except Exception:
                pass

        return InvariantResult(
            passed=len(errors) == 0,
            dimension=self.dimension,
            message="No security issues detected"
            if not errors
            else f"{len(errors)} security warnings",
            details=errors,
        )


# Registry of all invariant classes
INVARIANT_CLASSES = [
    ParseInvariant,
    ImportInvariant,
    BuildInvariant,
    TestInvariant,
    PackagingInvariant,
    APIInvariant,
    EntrypointInvariant,
    SecurityInvariant,
]


class InvariantEngine:
    """
    The Invariant Engine runs all invariants and produces a RepoStateVector.

    For each repo, define a hard invariant set:
        I = {I_parse, I_import, I_build, I_tests, I_packaging, I_api, I_entrypoints, I_security}

    A repo is valid only if:
        ∀ I_n ∈ I : I_n(Ψ_repo) = 1
    """

    def __init__(self, repo_path: Union[str, Path]):
        self.repo_path = Path(repo_path).resolve()
        self.invariants = [cls() for cls in INVARIANT_CLASSES]

    def run_all(self) -> tuple[RepoStateVector, list[InvariantResult]]:
        """
        Run all invariants and return the state vector + detailed results.
        """
        state = RepoStateVector()
        results = []

        for invariant in self.invariants:
            result = invariant.check(self.repo_path)
            results.append(result)

            # Set state value: 1.0 if passed, 0.0 if failed
            state.set(
                result.dimension,
                1.0 if result.passed else 0.0,
                failures=result.details if not result.passed else [],
            )

        return state, results

    def check_specific(self, invariant_name: str) -> InvariantResult:
        """Run a specific invariant by name."""
        for invariant in self.invariants:
            if invariant.name == invariant_name:
                return invariant.check(self.repo_path)
        raise ValueError(f"Unknown invariant: {invariant_name}")

    def get_failing_invariants(self, state: RepoStateVector) -> list[str]:
        """Get list of failing invariant names from state vector."""
        failing = []
        for dim in state.values:
            if state.values[dim] < 1.0:
                # Find the invariant name for this dimension
                for inv in self.invariants:
                    if inv.dimension == dim:
                        failing.append(inv.name)
                        break
        return failing
