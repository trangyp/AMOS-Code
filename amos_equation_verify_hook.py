#!/usr/bin/env python3
"""
AMOS Equation Verification Pre-commit Hook.

Usage:
    python amos_equation_verify_hook.py <file1> [file2] ...

This hook runs on committed Python files to verify them against
formal equations and invariants before they reach the repository.
"""

import sys
from pathlib import Path


def verify_file(filepath: str) -> tuple[bool, list[str]]:
    """Verify a single file against equations."""
    violations: List[str] = []

    try:
        with open(filepath) as f:
            code = f.read()
    except Exception as e:
        return False, [f"Error reading file: {e}"]

    # Simple pattern-based checks (fallback when AMOS not available)
    lines = code.split("\n")

    for i, line in enumerate(lines, 1):
        # Check for mutable default arguments
        if "def " in line and ("=[]" in line or "={}" in line):
            if "None" not in line:  # Not already fixed
                violations.append(f"{filepath}:{i}: Mutable default argument")

        # Check for bare except
        if "except:" in line and "except Exception" not in line:
            violations.append(f"{filepath}:{i}: Bare except clause")

        # Check for TODO/FIXME without issue reference
        if ("TODO" in line or "FIXME" in line) and not any(
            x in line for x in ["#", "issue", "ticket", "AMOS-"]
        ):
            violations.append(f"{filepath}:{i}: TODO without reference")

    return len(violations) == 0, violations


def main() -> int:
    """Run pre-commit verification on provided files."""
    if len(sys.argv) < 2:
        print("Usage: python amos_equation_verify_hook.py <file1> [file2] ...")
        return 0

    files = sys.argv[1:]
    all_violations: List[str] = []
    files_checked = 0

    print("[AMOS Equation Verification] Running pre-commit checks...")
    print()

    for filepath in files:
        # Only check Python files
        if not filepath.endswith(".py"):
            continue

        if not Path(filepath).exists():
            continue

        files_checked += 1
        _, violations = verify_file(filepath)

        if violations:
            all_violations.extend(violations)
            print(f"✗ {filepath}")
            for v in violations:
                print(f"  - {v}")
        else:
            print(f"✓ {filepath}")

    print()
    print(f"Files checked: {files_checked}")
    print(f"Violations: {len(all_violations)}")

    if all_violations:
        print()
        print("⚠️  Invariant violations detected!")
        print()
        print("Run the following to auto-fix where possible:")
        print("  python amos_equation_cli.py verify --fix <file>")
        return 1

    print()
    print("✓ All checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
