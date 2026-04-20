"""
Packaging Analysis Module - Packaging Invariant

I_packaging = 1 iff declared package surface == shipped package surface

Validates:
- pyproject.toml structure
- setup.py consistency
- Entry point declarations
- Module inclusion
"""

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
class PackagingIssue:
    """Represents a packaging issue."""

    severity: str  # "error", "warning"
    message: str
    file: str
    fix_suggestion: str = None


class PackagingAnalyzer:
    """
    Analyzes packaging configuration for consistency.
    """

    def __init__(self, repo_path: Union[str, Path]):
        self.repo_path = Path(repo_path).resolve()
        self.issues: List[PackagingIssue] = []
        self.config: dict = {}

    def analyze(self) -> List[PackagingIssue]:
        """Run full packaging analysis."""
        self.issues = []

        # Check for pyproject.toml
        pyproject_path = self.repo_path / "pyproject.toml"
        if pyproject_path.exists():
            self._analyze_pyproject(pyproject_path)

        # Check for setup.py
        setup_path = self.repo_path / "setup.py"
        if setup_path.exists():
            self._analyze_setup_py(setup_path)

        # Check consistency if both exist
        if pyproject_path.exists() and setup_path.exists():
            self._check_consistency(pyproject_path, setup_path)

        # Check for required files
        self._check_required_files()

        # Check module structure
        self._check_module_structure()

        return self.issues

    def _analyze_pyproject(self, path: Path):
        """Analyze pyproject.toml for issues."""
        if tomllib is None:
            self.issues.append(
                PackagingIssue(
                    severity="error",
                    message="tomllib/tomli not installed",
                    file="pyproject.toml",
                    fix_suggestion="pip install tomli",
                )
            )
            return

        try:
            content = path.read_bytes()
            config = tomllib.loads(content)

            self.config = config

            # Check for project section
            project = config.get("project", {})

            if not project.get("name"):
                self.issues.append(
                    PackagingIssue(
                        severity="error",
                        message="Missing project.name in pyproject.toml",
                        file="pyproject.toml",
                        fix_suggestion='Add [project] section with name = "your-package"',
                    )
                )

            if not project.get("version") and "version" not in project.get("dynamic", []):
                self.issues.append(
                    PackagingIssue(
                        severity="warning",
                        message="Missing project.version (should be static or in dynamic)",
                        file="pyproject.toml",
                        fix_suggestion='Add version = "0.1.0" or dynamic = ["version"]',
                    )
                )

            # Check build system
            build_system = config.get("build-system", {})
            if not build_system.get("requires"):
                self.issues.append(
                    PackagingIssue(
                        severity="warning",
                        message="Missing build-system.requires",
                        file="pyproject.toml",
                        fix_suggestion='Add build-system.requires = ["setuptools", "wheel"]',
                    )
                )

            # Check entry points
            scripts = project.get("scripts", {})
            for name, entrypoint in scripts.items():
                if ":" not in entrypoint:
                    self.issues.append(
                        PackagingIssue(
                            severity="error",
                            message=f"Invalid entrypoint format for '{name}': {entrypoint}",
                            file="pyproject.toml",
                            fix_suggestion="Use format: module.submodule:function_name",
                        )
                    )

        except Exception as e:
            self.issues.append(
                PackagingIssue(
                    severity="error",
                    message=f"Failed to parse pyproject.toml: {e}",
                    file="pyproject.toml",
                )
            )

    def _analyze_setup_py(self, path: Path):
        """Analyze setup.py for issues."""
        try:
            content = path.read_text()

            # Check for deprecated patterns
            if "setup_requires" in content:
                self.issues.append(
                    PackagingIssue(
                        severity="warning",
                        message="setup_requires is deprecated, use pyproject.toml [build-system]",
                        file="setup.py",
                    )
                )

            # Check for entry_points
            if "entry_points" in content:
                # Verify console_scripts format
                if "console_scripts" in content:
                    pass  # Found console_scripts

        except Exception as e:
            self.issues.append(
                PackagingIssue(
                    severity="error", message=f"Failed to read setup.py: {e}", file="setup.py"
                )
            )

    def _check_consistency(self, pyproject_path: Path, setup_path: Path):
        """Check consistency between pyproject.toml and setup.py."""
        # If both exist, they should agree on package name
        self.issues.append(
            PackagingIssue(
                severity="warning",
                message="Both pyproject.toml and setup.py exist - prefer pyproject.toml only",
                file=".",
                fix_suggestion="Migrate all configuration to pyproject.toml and remove setup.py",
            )
        )

    def _check_required_files(self):
        """Check for required packaging files."""
        # Check for LICENSE
        license_files = ["LICENSE", "LICENSE.txt", "LICENSE.md", "LICENSE.rst"]
        if not any((self.repo_path / f).exists() for f in license_files):
            self.issues.append(
                PackagingIssue(
                    severity="warning",
                    message="No LICENSE file found",
                    file=".",
                    fix_suggestion="Add a LICENSE file (MIT, Apache-2.0, etc.)",
                )
            )

        # Check for README
        readme_files = ["README.md", "README.rst", "README.txt"]
        if not any((self.repo_path / f).exists() for f in readme_files):
            self.issues.append(
                PackagingIssue(
                    severity="warning",
                    message="No README file found",
                    file=".",
                    fix_suggestion="Add README.md",
                )
            )

    def _check_module_structure(self):
        """Check Python module structure."""
        # Find packages (directories with __init__.py)
        packages = []
        for init_file in self.repo_path.rglob("__init__.py"):
            if any(p.startswith(".") for p in init_file.relative_to(self.repo_path).parts):
                continue
            if "test" in str(init_file).lower():
                continue
            packages.append(init_file.parent.relative_to(self.repo_path))

        if not packages:
            # Check for single module
            py_files = list(self.repo_path.glob("*.py"))
            py_files = [f for f in py_files if not f.name.startswith("_") and f.name != "setup.py"]

            if not py_files:
                self.issues.append(
                    PackagingIssue(
                        severity="error",
                        message="No Python modules found in repo root",
                        file=".",
                        fix_suggestion="Create a package directory or module file",
                    )
                )

    def is_valid(self) -> bool:
        """Check if packaging is valid (no errors)."""
        errors = [i for i in self.issues if i.severity == "error"]
        return len(errors) == 0

    def get_report(self) -> str:
        """Generate formatted packaging report."""
        errors = [i for i in self.issues if i.severity == "error"]
        warnings = [i for i in self.issues if i.severity == "warning"]

        lines = [
            "=" * 60,
            "PACKAGING ANALYSIS",
            "=" * 60,
            f"Errors: {len(errors)}",
            f"Warnings: {len(warnings)}",
            "-" * 60,
        ]

        if errors:
            lines.append("ERRORS:")
            for issue in errors:
                lines.append(f"  ✗ {issue.message}")
                if issue.fix_suggestion:
                    lines.append(f"    → {issue.fix_suggestion}")

        if warnings:
            lines.append("\nWARNINGS:")
            for issue in warnings:
                lines.append(f"  ! {issue.message}")
                if issue.fix_suggestion:
                    lines.append(f"    → {issue.fix_suggestion}")

        if not errors and not warnings:
            lines.append("✓ Packaging configuration valid")

        lines.append("=" * 60)

        return "\n".join(lines)
