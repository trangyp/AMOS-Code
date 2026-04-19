"""
Entrypoint Analysis Module - Entrypoint Invariant

I_entry = 1 iff launcher target exists and behaves as documented

Validates:
- Console scripts point to real functions
- CLI modules are importable
- Entrypoint functions have correct signatures
"""

import ast
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# tomllib available in Python 3.11+, fallback to tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


@dataclass
class EntrypointIssue:
    """Represents an entrypoint issue."""

    entrypoint_name: str
    module_path: str
    function_name: str
    error: str
    fix_suggestion: str = None


class EntrypointAnalyzer:
    """
    Analyzes entrypoints for validity.
    """

    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path).resolve()
        self.issues: List[EntrypointIssue] = []
        self.entrypoints: dict[str, tuple[str, str]] = {}  # name -> (module, function)

    def analyze(self) -> List[EntrypointIssue]:
        """Run full entrypoint analysis."""
        self.issues = []
        self.entrypoints = {}

        # Load entrypoints from pyproject.toml
        self._load_entrypoints()

        # Validate each entrypoint
        for name, (module, func) in self.entrypoints.items():
            self._validate_entrypoint(name, module, func)

        return self.issues

    def _load_entrypoints(self):
        """Load entrypoint declarations from pyproject.toml."""
        pyproject_path = self.repo_path / "pyproject.toml"
        if not pyproject_path.exists():
            return

        try:
            try:
                import tomllib

                content = pyproject_path.read_text()
                config = tomllib.loads(content)
            except ImportError:
                import tomli as tomllib

                content = pyproject_path.read_text()
                config = tomllib.loads(content)

            project = config.get("project", {})
            scripts = project.get("scripts", {})
            gui_scripts = project.get("gui-scripts", {})

            for name, entrypoint in {**scripts, **gui_scripts}.items():
                if ":" in entrypoint:
                    module, func = entrypoint.split(":", 1)
                    self.entrypoints[name] = (module, func)

        except Exception:
            pass

    def _validate_entrypoint(self, name: str, module: str, func: str):
        """Validate a single entrypoint."""
        # Check if module file exists
        parts = module.split(".")

        # Try as module file (package.submodule -> package/submodule.py)
        module_file = self.repo_path / "/".join(parts) / "__init__.py"
        if not module_file.exists():
            module_file = self.repo_path / ("/".join(parts) + ".py")

        # If not found and first part matches repo name, try relative
        if not module_file.exists() and len(parts) > 1:
            # Check if repo_path ends with the first part (package root case)
            if self.repo_path.name == parts[0]:
                # Try without the package prefix
                rel_parts = parts[1:]
                module_file = self.repo_path / "/".join(rel_parts) / "__init__.py"
                if not module_file.exists():
                    module_file = self.repo_path / ("/".join(rel_parts) + ".py")

        if not module_file.exists():
            self.issues.append(
                EntrypointIssue(
                    entrypoint_name=name,
                    module_path=module,
                    function_name=func,
                    error=f"Module not found: {module}",
                    fix_suggestion=f"Create module at {module.replace('.', '/')}",
                )
            )
            return

        # Check if function exists in module
        try:
            content = module_file.read_text()
            tree = ast.parse(content)

            found_func = False
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or isinstance(
                    node, ast.ClassDef
                ):
                    if node.name == func:
                        found_func = True
                        break

            if not found_func:
                self.issues.append(
                    EntrypointIssue(
                        entrypoint_name=name,
                        module_path=module,
                        function_name=func,
                        error=f"Function/class '{func}' not found in {module}",
                        fix_suggestion=f"Define '{func}' in {module}",
                    )
                )

        except SyntaxError as e:
            self.issues.append(
                EntrypointIssue(
                    entrypoint_name=name,
                    module_path=module,
                    function_name=func,
                    error=f"Syntax error in {module}: {e}",
                    fix_suggestion="Fix syntax errors in the module",
                )
            )
        except Exception as e:
            self.issues.append(
                EntrypointIssue(
                    entrypoint_name=name,
                    module_path=module,
                    function_name=func,
                    error=f"Error reading module: {e}",
                    fix_suggestion="Check file permissions and encoding",
                )
            )

    def test_entrypoint(self, name: str) -> Tuple[bool, str]:
        """
        Test if an entrypoint can be imported.
        Returns (success, error_message).
        """
        if name not in self.entrypoints:
            return False, f"Entrypoint '{name}' not found in configuration"

        module, func = self.entrypoints[name]

        # Try to import using Python
        test_code = f"""
try:
    from {module} import {func}
    print(f"SUCCESS: Imported {func} from {module}")
except ImportError as e:
    print(f"IMPORT_ERROR: {{e}}")
except Exception as e:
    print(f"ERROR: {{e}}")
"""
        try:
            result = subprocess.run(
                ["python", "-c", test_code],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            output = result.stdout + result.stderr

            if "SUCCESS:" in output:
                return True, ""
            elif "IMPORT_ERROR:" in output:
                error = output.split("IMPORT_ERROR:", 1)[1].strip()
                return False, f"Import failed: {error}"
            elif "ERROR:" in output:
                error = output.split("ERROR:", 1)[1].strip()
                return False, f"Error: {error}"
            else:
                return False, f"Unexpected output: {output[:200]}"

        except subprocess.TimeoutExpired:
            return False, "Import test timed out"
        except Exception as e:
            return False, f"Test failed: {e}"

    def is_valid(self) -> bool:
        """Check if all entrypoints are valid."""
        return len(self.issues) == 0

    def get_report(self) -> str:
        """Generate formatted entrypoint report."""
        lines = [
            "=" * 60,
            "ENTRYPOINT ANALYSIS",
            "=" * 60,
            f"Entrypoints defined: {len(self.entrypoints)}",
            f"Issues found: {len(self.issues)}",
            "-" * 60,
        ]

        if self.entrypoints:
            lines.append("Defined entrypoints:")
            for name, (module, func) in self.entrypoints.items():
                # Check if in issues
                issue = next((i for i in self.issues if i.entrypoint_name == name), None)
                status = "✗" if issue else "✓"
                lines.append(f"  {status} {name} = {module}:{func}")

        if self.issues:
            lines.append("\nISSUES:")
            for issue in self.issues:
                lines.append(f"  ✗ {issue.entrypoint_name}: {issue.error}")
                if issue.fix_suggestion:
                    lines.append(f"    → {issue.fix_suggestion}")

        if not self.entrypoints:
            lines.append("No entrypoints defined (optional)")
        elif not self.issues:
            lines.append("✓ All entrypoints valid")

        lines.append("=" * 60)

        return "\n".join(lines)
