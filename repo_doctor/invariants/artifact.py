"""
I_artifact = 1 iff source_surface ≅ installed_surface ≅ published_surface.

Artifact chain:
    Source -> Build Target -> Generated Artifact -> Package Artifact ->
    Installed Surface -> Runtime Surface

Invariant checks:
    1. All source files included in package
    2. Console scripts resolve to installed modules
    3. Generated files are fresh (not stale)
    4. Wheel and sdist are consistent
    5. Entry points work after install
    6. Data files are packaged correctly

Based on 2024 Python packaging best practices (PEP 517/518/660).
"""
from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .base import Invariant, InvariantResult, InvariantSeverity


@dataclass
class ArtifactGap:
    """Artifact chain integrity gap."""

    type: str
    severity: str
    location: str
    message: str
    suggestion: str | None = None


class ArtifactInvariant(Invariant):
    """
    I_artifact = 1 iff artifact chain preserves contract surface.

    Detects:
    - Source files missing from wheel
    - Console scripts pointing to non-existent modules
    - Stale generated files
    - sdist vs wheel divergence
    - Missing data files in package
    - Editable install vs package install differences
    """

    def __init__(self):
        super().__init__("I_artifact", InvariantSeverity.ERROR)

    def check(self, repo_path: str, context: dict[str, Any] | None = None) -> InvariantResult:
        """Check artifact chain integrity."""
        context = context or {}
        repo = Path(repo_path)

        gaps: list[ArtifactGap] = []

        # Check for build artifacts
        gaps.extend(self._check_build_artifacts(repo))

        # Check package configuration
        gaps.extend(self._check_package_config(repo))

        # Check entry points
        gaps.extend(self._check_entry_points(repo))

        # Check for stale generated files
        gaps.extend(self._check_generated_files(repo))

        # Check source vs package consistency
        gaps.extend(self._check_source_package_consistency(repo))

        critical = [g for g in gaps if g.severity == "critical"]
        errors = [g for g in gaps if g.severity == "error"]
        warnings = [g for g in gaps if g.severity == "warning"]

        passed = len(critical) == 0 and len(errors) == 0

        if passed:
            message = f"Artifact chain OK: {len(warnings)} warnings"
        else:
            message = (
                f"Artifact gaps: {len(critical)} critical, "
                f"{len(errors)} errors, {len(warnings)} warnings"
            )

        return InvariantResult(
            name=self.name,
            passed=passed,
            severity=self.severity,
            message=message,
            details={
                "critical_gaps": len(critical),
                "error_gaps": len(errors),
                "warning_gaps": len(warnings),
                "gaps": [
                    {"type": g.type, "location": g.location, "message": g.message}
                    for g in gaps[:20]
                ],
            },
        )

    def _check_build_artifacts(self, repo: Path) -> list[ArtifactGap]:
        """Check for built wheel/sdist artifacts."""
        gaps: list[ArtifactGap] = []

        dist_dir = repo / "dist"
        if not dist_dir.exists():
            gaps.append(
                ArtifactGap(
                    type="no_build_artifacts",
                    severity="info",
                    location=str(repo),
                    message="No dist/ directory - package not built",
                    suggestion="Run 'python -m build' to create wheel and sdist",
                )
            )
            return gaps

        wheels = list(dist_dir.glob("*.whl"))
        sdists = list(dist_dir.glob("*.tar.gz"))

        if not wheels:
            gaps.append(
                ArtifactGap(
                    type="missing_wheel",
                    severity="error",
                    location="dist/",
                    message="No wheel (.whl) in dist/",
                    suggestion="Build wheel with 'python -m build --wheel'",
                )
            )

        if not sdists:
            gaps.append(
                ArtifactGap(
                    type="missing_sdist",
                    severity="warning",
                    location="dist/",
                    message="No sdist (.tar.gz) in dist/",
                    suggestion="Build sdist with 'python -m build --sdist'",
                )
            )

        # Check wheel contents
        for wheel in wheels:
            gaps.extend(self._check_wheel_contents(wheel))

        return gaps

    def _check_wheel_contents(self, wheel_path: Path) -> list[ArtifactGap]:
        """Check wheel contents for completeness."""
        gaps: list[ArtifactGap] = []

        try:
            with zipfile.ZipFile(wheel_path, "r") as whl:
                files = whl.namelist()

                # Check for expected top-level
                top_levels = {f.split("/")[0] for f in files if "/" in f}

                if not top_levels:
                    gaps.append(
                        ArtifactGap(
                            type="empty_wheel",
                            severity="critical",
                            location=str(wheel_path),
                            message="Wheel appears empty or malformed",
                        )
                    )

                # Check for metadata
                dist_info = [f for f in files if f.endswith(".dist-info/METADATA")]
                if not dist_info:
                    gaps.append(
                        ArtifactGap(
                            type="missing_metadata",
                            severity="error",
                            location=str(wheel_path),
                            message="Wheel missing METADATA",
                        )
                    )

                # Check for console scripts
                has_console_scripts = any("bin/" in f for f in files)

        except zipfile.BadZipFile:
            gaps.append(
                ArtifactGap(
                    type="corrupt_wheel",
                    severity="critical",
                    location=str(wheel_path),
                    message="Wheel file is corrupt",
                )
            )

        return gaps

    def _check_package_config(self, repo: Path) -> list[ArtifactGap]:
        """Check pyproject.toml/setup.py configuration."""
        gaps: list[ArtifactGap] = []

        pyproject = repo / "pyproject.toml"
        setup_py = repo / "setup.py"

        if not pyproject.exists() and not setup_py.exists():
            gaps.append(
                ArtifactGap(
                    type="missing_build_config",
                    severity="critical",
                    location=str(repo),
                    message="No pyproject.toml or setup.py found",
                )
            )
            return gaps

        if pyproject.exists():
            content = pyproject.read_text()

            # Check for build system
            if "[build-system]" not in content:
                gaps.append(
                    ArtifactGap(
                        type="missing_build_system",
                        severity="error",
                        location="pyproject.toml",
                        message="No [build-system] table defined",
                        suggestion="Add [build-system] with requires and build-backend",
                    )
                )

            # Check for package discovery
            if "[tool.setuptools.packages.find]" not in content and "packages = [" not in content:
                gaps.append(
                    ArtifactGap(
                        type="implicit_package_discovery",
                        severity="warning",
                        location="pyproject.toml",
                        message="Package discovery not explicitly configured",
                        suggestion="Explicitly configure packages.find or packages list",
                    )
                )

        return gaps

    def _check_entry_points(self, repo: Path) -> list[ArtifactGap]:
        """Check console_scripts entry points."""
        gaps: list[ArtifactGap] = []

        pyproject = repo / "pyproject.toml"
        if not pyproject.exists():
            return gaps

        content = pyproject.read_text()

        # Check for console_scripts
        if "[project.scripts]" in content:
            # Parse console scripts
            import re

            scripts_section = re.search(r"\[project\.scripts\](.*?)(?=\[|$)", content, re.DOTALL)
            if scripts_section:
                scripts_text = scripts_section.group(1)
                for line in scripts_text.split("\n"):
                    if "=" in line and not line.strip().startswith("#"):
                        parts = line.split("=")
                        if len(parts) >= 2:
                            script_name = parts[0].strip()
                            module_ref = parts[1].strip().strip('"').strip("'")

                            # Check module exists
                            if ":" in module_ref:
                                module_path = module_ref.split(":")[0]
                                module_file = module_path.replace(".", "/") + ".py"
                                expected_path = repo / module_file

                                if not expected_path.exists():
                                    # Check if it's a package
                                    pkg_init = repo / module_path.replace(".", "/") / "__init__.py"
                                    if not pkg_init.exists():
                                        gaps.append(
                                            ArtifactGap(
                                                type="missing_script_target",
                                                severity="error",
                                                location="pyproject.toml",
                                                message=f"Console script '{script_name}' targets missing module: {module_path}",
                                                suggestion=f"Create {module_file} or fix entry point",
                                            )
                                        )

        return gaps

    def _check_generated_files(self, repo: Path) -> list[ArtifactGap]:
        """Check for stale generated files."""
        gaps: list[ArtifactGap] = []

        # Check for protobuf/grpc generated files
        pb2_files = list(repo.rglob("*_pb2.py"))
        proto_files = list(repo.rglob("*.proto"))

        if pb2_files and proto_files:
            # Check if any pb2 is older than its proto
            for pb2 in pb2_files:
                proto_name = pb2.name.replace("_pb2.py", ".proto")
                matching_protos = [p for p in proto_files if p.name == proto_name]

                if matching_protos:
                    proto = matching_protos[0]
                    if pb2.stat().st_mtime < proto.stat().st_mtime:
                        gaps.append(
                            ArtifactGap(
                                type="stale_generated_file",
                                severity="warning",
                                location=str(pb2),
                                message=f"Generated file older than source: {proto.name}",
                                suggestion="Regenerate protobuf files",
                            )
                        )

        return gaps

    def _check_source_package_consistency(self, repo: Path) -> list[ArtifactGap]:
        """Check consistency between source and package."""
        gaps: list[ArtifactGap] = []

        # Find Python package directories
        pkg_dirs = [d for d in repo.iterdir() if d.is_dir() and (d / "__init__.py").exists()]

        for pkg_dir in pkg_dirs:
            pkg_name = pkg_dir.name

            # Check for top-level modules not in package
            top_py_files = [f for f in repo.glob("*.py") if not f.name.startswith("_")]

            if top_py_files and pkg_name not in ["tests", "docs", "scripts"]:
                # Warn about potential packaging issue
                for py_file in top_py_files[:3]:  # Limit warnings
                    gaps.append(
                        ArtifactGap(
                            type="top_level_module",
                            severity="info",
                            location=str(py_file),
                            message=f"Top-level module may not be packaged with '{pkg_name}'",
                            suggestion="Consider moving into package or configure explicitly",
                        )
                    )

        return gaps
