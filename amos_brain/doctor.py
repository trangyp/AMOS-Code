#!/usr/bin/env python3
"""AMOS Brain Self-Diagnosis System

Validates the health of the AMOS brain installation and identifies structural issues.

Usage:
    amos-brain doctor              # Run all diagnostics
    amos-brain doctor --imports    # Check import graph only
    amos-brain doctor --build      # Check package build only
    amos-brain doctor --entrypoints # Check entrypoints only
    amos-brain doctor --contract   # Validate contract file
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


def log(msg: str, level: str = "info") -> None:
    colors = {
        "ok": Colors.GREEN,
        "error": Colors.RED,
        "warn": Colors.YELLOW,
        "info": Colors.BLUE,
    }
    color = colors.get(level, Colors.RESET)
    print(f"{color}{msg}{Colors.RESET}")


class DiagnosticResult:
    def __init__(self, name: str, passed: bool, message: str, details: dict | None = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or {}

    def __repr__(self) -> str:
        status = "✓" if self.passed else "✗"
        return f"{status} {self.name}: {self.message}"


class BrainDoctor:
    """Self-diagnosis system for AMOS brain."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: list[DiagnosticResult] = []
        self.contract: dict | None = None

    def diagnose(self, checks: Optional[list[str]] = None) -> bool:
        """Run all or specified diagnostic checks."""
        all_checks = {
            "imports": self.check_imports,
            "build": self.check_build,
            "entrypoints": self.check_entrypoints,
            "contract": self.check_contract,
            "structure": self.check_structure,
            "patterns": self.check_forbidden_patterns,
        }

        to_run = checks if checks else list(all_checks.keys())

        print("\n" + "=" * 60)
        print("AMOS BRAIN SELF-DIAGNOSIS")
        print("=" * 60 + "\n")

        for check_name in to_run:
            if check_name in all_checks:
                all_checks[check_name]()

        return self._print_summary()

    def check_imports(self) -> None:
        """Verify all public imports work."""
        log("Checking import graph...", "info")

        try:
            import amos_brain

            # Test lazy-loaded exports
            exports_to_test = [
                "get_brain",
                "process_task",
                "GlobalLaws",
                "KernelRouter",
                "get_agent_bridge",
                "get_state_manager",
                "get_meta_controller",
            ]

            failed = []
            for export in exports_to_test:
                try:
                    getattr(amos_brain, export)
                except Exception as e:
                    failed.append(f"{export}: {e}")

            if failed:
                self.results.append(
                    DiagnosticResult(
                        "Import Graph",
                        False,
                        f"{len(failed)} exports failed",
                        {"failed": failed},
                    )
                )
            else:
                self.results.append(
                    DiagnosticResult(
                        "Import Graph",
                        True,
                        f"All {len(exports_to_test)} public exports loadable",
                    )
                )

        except Exception as e:
            self.results.append(DiagnosticResult("Import Graph", False, f"Import failed: {e}"))

    def check_build(self) -> None:
        """Check if package builds correctly."""
        log("Checking package build...", "info")

        try:
            # Try to get package metadata
            from importlib.metadata import files, version

            pkg_version = version("amos-brain")
            pkg_files = list(files("amos-brain") or [])[:10]

            self.results.append(
                DiagnosticResult(
                    "Package Build",
                    True,
                    f"Version {pkg_version} installed",
                    {"sample_files": [str(f) for f in pkg_files]},
                )
            )

        except Exception as e:
            self.results.append(
                DiagnosticResult("Package Build", False, f"Build check failed: {e}")
            )

    def check_entrypoints(self) -> None:
        """Verify console scripts are properly configured."""
        log("Checking entrypoints...", "info")

        try:
            from importlib.metadata import entry_points

            eps = entry_points()
            # Handle both dict-style and selectable APIs
            if hasattr(eps, "select"):
                console_scripts = list(eps.select(group="console_scripts"))
            elif isinstance(eps, dict):
                console_scripts = eps.get("console_scripts", [])
            else:
                console_scripts = list(eps)

            amos_eps = [ep for ep in console_scripts if getattr(ep, "name", "").startswith("amos")]

            # Check for duplicates (same name appearing multiple times)
            from collections import Counter

            names = [ep.name for ep in amos_eps]
            name_counts = Counter(names)
            duplicates = [n for n, count in name_counts.items() if count > 1]

            # Check if primary entrypoint exists
            has_primary = "amos-brain" in names

            # Check for deprecated entrypoints
            deprecated = ["amos-cli", "amos-launcher", "amos-tutorial", "amos-cookbook"]
            found_deprecated = [n for n in names if n in deprecated]

            # Non-deprecated, non-primary entrypoints (allowed if different purpose)
            allowed_secondary = ["amosl"]  # AMOSL is a separate DSL, allowed

            # Filter duplicates - exclude allowed secondary and primary
            # (primary may appear from multiple installed versions during dev)
            real_duplicates = [
                d for d in duplicates if d not in allowed_secondary and d != "amos-brain"
            ]

            issues = []
            if real_duplicates:
                issues.append(f"Duplicate entrypoints: {real_duplicates}")
            if not has_primary:
                issues.append("Primary 'amos-brain' entrypoint missing")

            # Find unexpected entrypoints (not primary, not allowed secondary, not deprecated)
            unexpected = [
                n
                for n in names
                if n not in deprecated and n != "amos-brain" and n not in allowed_secondary
            ]

            if issues:
                self.results.append(
                    DiagnosticResult(
                        "Entrypoints",
                        False,
                        "; ".join(issues),
                        {
                            "found": names,
                            "deprecated": found_deprecated,
                        },
                    )
                )
            else:
                # Use unique names for cleaner output
                unique_names = list(dict.fromkeys(names))
                msg = (
                    f"Primary entrypoint OK ({len(unique_names)} unique: {', '.join(unique_names)})"
                )
                if found_deprecated:
                    msg += f", {len(found_deprecated)} deprecated found"
                if unexpected:
                    msg += f", unexpected: {unexpected}"
                self.results.append(
                    DiagnosticResult(
                        "Entrypoints",
                        True,
                        msg,
                        {"entrypoints": unique_names, "deprecated": found_deprecated},
                    )
                )

        except Exception as e:
            self.results.append(DiagnosticResult("Entrypoints", False, f"Check failed: {e}"))

    def check_contract(self) -> None:
        """Validate contract file if it exists."""
        log("Checking contract file...", "info")

        contract_path = Path("amos_brain_contract.json")
        if not contract_path.exists():
            self.results.append(
                DiagnosticResult(
                    "Contract File",
                    False,
                    "amos_brain_contract.json not found",
                    {
                        "suggestion": "Create contract file with: amos-brain doctor --generate-contract"
                    },
                )
            )
            return

        try:
            with open(contract_path) as f:
                self.contract = json.load(f)

            # Validate required fields
            required = ["contract_version", "package", "public_api"]
            missing = [f for f in required if f not in self.contract]

            if missing:
                self.results.append(
                    DiagnosticResult(
                        "Contract File",
                        False,
                        f"Missing required fields: {missing}",
                    )
                )
            else:
                pkg = self.contract.get("package", {})
                self.results.append(
                    DiagnosticResult(
                        "Contract File",
                        True,
                        f"Valid contract v{self.contract.get('contract_version')} for {pkg.get('name', 'unknown')}",
                    )
                )

        except json.JSONDecodeError as e:
            self.results.append(DiagnosticResult("Contract File", False, f"Invalid JSON: {e}"))
        except Exception as e:
            self.results.append(DiagnosticResult("Contract File", False, f"Read failed: {e}"))

    def check_structure(self) -> None:
        """Check package structure is valid."""
        log("Checking package structure...", "info")

        issues = []

        # Check for required files
        required_files = ["pyproject.toml", "README.md", "amos_brain/__init__.py"]
        for f in required_files:
            if not Path(f).exists():
                issues.append(f"Missing: {f}")

        # Check for forbidden root files
        forbidden_patterns = ["amos-cli.py", "amos_brain.py"]
        for pattern in forbidden_patterns:
            matches = list(Path(".").glob(pattern))
            if matches:
                issues.append(f"Forbidden root file: {matches[0]}")

        # Check __init__.py exports
        try:
            with open("amos_brain/__init__.py") as f:
                content = f.read()

            # Check for lazy loading pattern
            has_exports = "__all__" in content or "_lazy_modules" in content

            if not has_exports:
                issues.append("__init__.py missing exports pattern")

        except Exception as e:
            issues.append(f"Cannot read __init__.py: {e}")

        if issues:
            self.results.append(
                DiagnosticResult(
                    "Package Structure", False, f"{len(issues)} issues", {"issues": issues}
                )
            )
        else:
            self.results.append(DiagnosticResult("Package Structure", True, "Structure valid"))

    def check_forbidden_patterns(self) -> None:
        """Scan for forbidden patterns in production code."""
        log("Checking for forbidden patterns...", "info")

        forbidden = {
            "sys.path.insert": [],
            "sys.path.append": [],
            "except:": [],
            "datetime.utcnow()": [],
        }

        # Scan Python files (excluding tests, venv, and this file)
        for py_file in Path("amos_brain").rglob("*.py"):
            # Skip cache and this file (doctor.py checks for patterns as strings)
            if "__pycache__" in str(py_file) or py_file.name == "doctor.py":
                continue

            try:
                with open(py_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    # Skip comments and string literals
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    # Skip lines that are just string literals (definitions)
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        continue
                    # Skip print/logging lines that mention patterns as strings
                    if "print(" in line or "log(" in line or 'f"' in line:
                        continue

                    for pattern in forbidden:
                        if pattern in line:
                            forbidden[pattern].append(f"{py_file}:{i}")

            except Exception:
                pass

        total_violations = sum(len(v) for v in forbidden.values())

        if total_violations > 0:
            details = {k: v[:5] for k, v in forbidden.items() if v}  # Limit output
            self.results.append(
                DiagnosticResult(
                    "Forbidden Patterns",
                    False,
                    f"{total_violations} violations found",
                    details,
                )
            )
        else:
            self.results.append(
                DiagnosticResult("Forbidden Patterns", True, "No forbidden patterns found")
            )

    def _print_summary(self) -> bool:
        """Print diagnostic summary and return overall health."""
        print("\n" + "=" * 60)
        print("DIAGNOSTIC SUMMARY")
        print("=" * 60 + "\n")

        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)

        for result in self.results:
            icon = "✓" if result.passed else "✗"
            color = "ok" if result.passed else "error"
            log(f"{icon} {result.name}: {result.message}", color)

            if self.verbose and result.details:
                for key, val in result.details.items():
                    if isinstance(val, list):
                        for item in val[:5]:  # Limit output
                            print(f"    - {item}")
                        if len(val) > 5:
                            print(f"    ... and {len(val) - 5} more")
                    else:
                        print(f"    {key}: {val}")

        print("\n" + "=" * 60)
        log(f"Passed: {passed}, Failed: {failed}", "ok" if failed == 0 else "error")
        print("=" * 60)

        if failed > 0:
            print("\nRecommended fixes:")
            for result in self.results:
                if not result.passed:
                    if result.name == "Import Graph":
                        print("  - Check amos_brain/__init__.py exports")
                    elif result.name == "Entrypoints":
                        print("  - Update pyproject.toml [project.scripts]")
                    elif result.name == "Contract File":
                        print("  - Create amos_brain_contract.json")
                    elif result.name == "Forbidden Patterns":
                        print("  - Run: python amos_intelligent_modernizer.py --live")

        return failed == 0


def generate_contract() -> None:
    """Generate a default contract file."""
    contract = {
        "contract_version": "1.0.0",
        "contract_date": "2026-04-20",
        "package": {
            "name": "amos-brain",
            "version": "14.0.0",
            "canonical_module": "amos_brain",
            "canonical_entrypoint": "amos_brain.cli:main",
            "health_check_module": "amos_brain.health",
            "health_check_function": "check",
        },
        "public_api": {
            "modules": ["amos_brain"],
            "entrypoints": ["amos-brain"],
            "allowed_secondary_entrypoints": ["amosl"],
            "exports": ["get_brain", "process_task", "GlobalLaws", "think", "decide", "validate"],
        },
        "forbidden_patterns": {
            "runtime": ["sys.path.insert", "sys.path.append"],
            "code_quality": ["except:", "datetime.utcnow()"],
        },
        "ci_requirements": {
            "required_checks": [
                "wheel-install",
                "entrypoints",
                "docker-check",
                "import-graph",
                "contract-exists",
                "forbidden-patterns",
            ],
            "python_version": "3.12",
            "workflow_file": ".github/workflows/brain-health.yml",
        },
        "structure": {
            "allowed_root_files": [
                "pyproject.toml",
                "README.md",
                "LICENSE",
                "Dockerfile",
                "docker-compose.yml",
                "amos_brain_contract.json",
            ],
            "forbidden_root_patterns": ["*.py", "amos-*.py"],
        },
    }

    with open("amos_brain_contract.json", "w") as f:
        json.dump(contract, f, indent=2)

    print("Generated: amos_brain_contract.json")


def main() -> int:
    """Main entry point for doctor command."""
    parser = argparse.ArgumentParser(
        description="AMOS Brain Self-Diagnosis",
        prog="amos-brain doctor",
    )
    parser.add_argument("--imports", action="store_true", help="Check import graph only")
    parser.add_argument("--build", action="store_true", help="Check package build only")
    parser.add_argument("--entrypoints", action="store_true", help="Check entrypoints only")
    parser.add_argument("--contract", action="store_true", help="Validate contract only")
    parser.add_argument("--structure", action="store_true", help="Check structure only")
    parser.add_argument("--patterns", action="store_true", help="Check forbidden patterns only")
    parser.add_argument(
        "--generate-contract", action="store_true", help="Generate default contract"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.generate_contract:
        generate_contract()
        return 0

    # Determine which checks to run
    specific_checks = []
    if args.imports:
        specific_checks.append("imports")
    if args.build:
        specific_checks.append("build")
    if args.entrypoints:
        specific_checks.append("entrypoints")
    if args.contract:
        specific_checks.append("contract")
    if args.structure:
        specific_checks.append("structure")
    if args.patterns:
        specific_checks.append("patterns")

    doctor = BrainDoctor(verbose=args.verbose)
    healthy = doctor.diagnose(specific_checks if specific_checks else None)

    return 0 if healthy else 1


if __name__ == "__main__":
    sys.exit(main())
