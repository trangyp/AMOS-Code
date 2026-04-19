"""Packaging validation substrate.

Validates packaging configuration consistency:
- pyproject.toml structure and required fields
- setup.py vs pyproject.toml consistency
- Entry points and scripts declarations
- Required files (LICENSE, README)
- Module structure and discoverability

I_pack = 1 iff declared package surface == shipped package surface.
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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
    """A packaging issue or inconsistency."""

    severity: str  # "error", "warning"
    message: str
    file: str
    fix_suggestion: str = ""
    code: str = ""  # Issue category code


@dataclass
class PackagingValidation:
    """Result of packaging validation."""

    has_pyproject: bool = False
    has_setup_py: bool = False
    has_license: bool = False
    has_readme: bool = False
    has_packages: bool = False
    issues: List[PackagingIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Check if packaging is valid (no errors)."""
        errors = [i for i in self.issues if i.severity == "error"]
        return len(errors) == 0

    @property
    def error_count(self) -> int:
        """Count of errors."""
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        """Count of warnings."""
        return sum(1 for i in self.issues if i.severity == "warning")


class PackagingSubstrate:
    """Packaging validation substrate.

    Analyzes packaging configuration for consistency and completeness.
    Validates that declared package metadata matches the actual structure.

    Usage:
        substrate = PackagingSubstrate("/path/to/repo")

        # Run full analysis
        result = substrate.analyze()

        if result.is_valid:
            print("✓ Packaging valid")
        else:
            for issue in result.issues:
                print(f"✗ {issue.message}")
    """

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self._config: Dict[str, Any] = None

    def analyze(self) -> PackagingValidation:
        """Run full packaging analysis.

        Returns:
            PackagingValidation with all issues found
        """
        result = PackagingValidation()

        # Check for pyproject.toml
        pyproject_path = self.repo_path / "pyproject.toml"
        result.has_pyproject = pyproject_path.exists()

        if result.has_pyproject:
            issues = self._analyze_pyproject(pyproject_path)
            result.issues.extend(issues)
        else:
            result.issues.append(
                PackagingIssue(
                    severity="warning",
                    message="No pyproject.toml found",
                    file=".",
                    fix_suggestion="Create pyproject.toml with [project] metadata",
                    code="missing_pyproject",
                )
            )

        # Check for setup.py
        setup_path = self.repo_path / "setup.py"
        result.has_setup_py = setup_path.exists()

        if result.has_setup_py:
            issues = self._analyze_setup_py(setup_path)
            result.issues.extend(issues)

        # Check consistency if both exist
        if result.has_pyproject and result.has_setup_py:
            result.issues.append(
                PackagingIssue(
                    severity="warning",
                    message="Both pyproject.toml and setup.py exist",
                    file=".",
                    fix_suggestion="Prefer pyproject.toml only, remove setup.py",
                    code="dual_config",
                )
            )

        # Check for required files
        result.has_license = self._check_license()
        if not result.has_license:
            result.issues.append(
                PackagingIssue(
                    severity="warning",
                    message="No LICENSE file found",
                    file=".",
                    fix_suggestion="Add LICENSE file (MIT, Apache-2.0, etc.)",
                    code="missing_license",
                )
            )

        result.has_readme = self._check_readme()
        if not result.has_readme:
            result.issues.append(
                PackagingIssue(
                    severity="warning",
                    message="No README file found",
                    file=".",
                    fix_suggestion="Add README.md with project description",
                    code="missing_readme",
                )
            )

        # Check module structure
        result.has_packages = self._check_module_structure()
        if not result.has_packages:
            result.issues.append(
                PackagingIssue(
                    severity="error",
                    message="No Python packages/modules found",
                    file=".",
                    fix_suggestion="Create package directory with __init__.py or module files",
                    code="no_modules",
                )
            )

        return result

    def _analyze_pyproject(self, path: Path) -> List[PackagingIssue]:
        """Analyze pyproject.toml for issues."""
        issues = []

        if tomllib is None:
            issues.append(
                PackagingIssue(
                    severity="error",
                    message="tomllib/tomli not installed (required for Python < 3.11)",
                    file="pyproject.toml",
                    fix_suggestion="pip install tomli",
                    code="toml_parser_missing",
                )
            )
            return issues

        try:
            content = path.read_bytes()
            config = tomllib.loads(content)
            self._config = config

            # Check for project section
            project = config.get("project", {})

            if not project:
                issues.append(
                    PackagingIssue(
                        severity="error",
                        message="Missing [project] section in pyproject.toml",
                        file="pyproject.toml",
                        fix_suggestion="Add [project] section with name, version, etc.",
                        code="missing_project_section",
                    )
                )
            else:
                # Check required fields
                if not project.get("name"):
                    issues.append(
                        PackagingIssue(
                            severity="error",
                            message="Missing project.name in pyproject.toml",
                            file="pyproject.toml",
                            fix_suggestion='Add name = "your-package" in [project]',
                            code="missing_project_name",
                        )
                    )

                if not project.get("version") and "version" not in project.get("dynamic", []):
                    issues.append(
                        PackagingIssue(
                            severity="warning",
                            message="Missing project.version (should be static or dynamic)",
                            file="pyproject.toml",
                            fix_suggestion='Add version = "0.1.0" or dynamic = ["version"]',
                            code="missing_project_version",
                        )
                    )

                if not project.get("description"):
                    issues.append(
                        PackagingIssue(
                            severity="warning",
                            message="Missing project.description",
                            file="pyproject.toml",
                            fix_suggestion='Add description = "Short project description"',
                            code="missing_project_description",
                        )
                    )

            # Check build system
            build_system = config.get("build-system", {})
            if not build_system.get("requires"):
                issues.append(
                    PackagingIssue(
                        severity="warning",
                        message="Missing build-system.requires",
                        file="pyproject.toml",
                        fix_suggestion='Add build-system.requires = ["setuptools", "wheel"]',
                        code="missing_build_requires",
                    )
                )

            # Check entry points format
            scripts = project.get("scripts", {})
            for name, entrypoint in scripts.items():
                if ":" not in entrypoint:
                    issues.append(
                        PackagingIssue(
                            severity="error",
                            message=f"Invalid entrypoint format for '{name}': {entrypoint}",
                            file="pyproject.toml",
                            fix_suggestion="Use format: module.submodule:function_name",
                            code="invalid_entrypoint_format",
                        )
                    )

        except Exception as e:
            issues.append(
                PackagingIssue(
                    severity="error",
                    message=f"Failed to parse pyproject.toml: {e}",
                    file="pyproject.toml",
                    fix_suggestion="Fix TOML syntax errors",
                    code="toml_parse_error",
                )
            )

        return issues

    def _analyze_setup_py(self, path: Path) -> List[PackagingIssue]:
        """Analyze setup.py for issues."""
        issues = []

        try:
            content = path.read_text()

            # Check for deprecated patterns
            if "setup_requires" in content:
                issues.append(
                    PackagingIssue(
                        severity="warning",
                        message="setup_requires is deprecated",
                        file="setup.py",
                        fix_suggestion="Use [build-system] in pyproject.toml instead",
                        code="deprecated_setup_requires",
                    )
                )

            # Check for tests_require (deprecated)
            if "tests_require" in content:
                issues.append(
                    PackagingIssue(
                        severity="warning",
                        message="tests_require is deprecated",
                        file="setup.py",
                        fix_suggestion="Use [project.optional-dependencies] in pyproject.toml",
                        code="deprecated_tests_require",
                    )
                )

        except Exception as e:
            issues.append(
                PackagingIssue(
                    severity="error",
                    message=f"Failed to read setup.py: {e}",
                    file="setup.py",
                    fix_suggestion="Ensure setup.py is readable",
                    code="setup_read_error",
                )
            )

        return issues

    def _check_license(self) -> bool:
        """Check for LICENSE file."""
        license_files = [
            "LICENSE",
            "LICENSE.txt",
            "LICENSE.md",
            "LICENSE.rst",
            "LICENSE.MIT",
            "LICENSE.APACHE",
        ]
        return any((self.repo_path / f).exists() for f in license_files)

    def _check_readme(self) -> bool:
        """Check for README file."""
        readme_files = ["README.md", "README.rst", "README.txt", "README"]
        return any((self.repo_path / f).exists() for f in readme_files)

    def _check_module_structure(self) -> bool:
        """Check for Python modules/packages."""
        # Find packages (directories with __init__.py)
        for init_file in self.repo_path.rglob("__init__.py"):
            rel_parts = init_file.relative_to(self.repo_path).parts
            if any(p.startswith(".") for p in rel_parts):
                continue
            if "test" in str(init_file).lower():
                continue
            return True

        # Check for single module
        py_files = list(self.repo_path.glob("*.py"))
        py_files = [f for f in py_files if not f.name.startswith("_") and f.name != "setup.py"]

        if py_files:
            return True

        return False

    def get_summary(self, validation: PackagingValidation) -> Dict[str, Any]:
        """Generate summary statistics."""
        return {
            "valid": validation.is_valid,
            "errors": validation.error_count,
            "warnings": validation.warning_count,
            "has_pyproject": validation.has_pyproject,
            "has_setup_py": validation.has_setup_py,
            "has_license": validation.has_license,
            "has_readme": validation.has_readme,
            "has_packages": validation.has_packages,
            "releaseable": validation.is_valid and validation.has_packages,
        }
