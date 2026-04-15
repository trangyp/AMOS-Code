#!/usr/bin/env python3
"""Repo Doctor Ω∞∞∞∞ - Validation Script
Checks for critical errors and validates the implementation.
"""

import ast
import sys
from pathlib import Path


def check_syntax(filepath):
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath) as f:
            source = f.read()
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def main():
    print("=" * 70)
    print("REPO DOCTOR Ω∞∞∞∞ - VALIDATION")
    print("=" * 70)

    repo_doctor_dir = Path(__file__).parent / "repo_doctor"

    # Critical files to check
    critical_files = [
        "__init__.py",
        "cli.py",
        "state_vector.py",
        "invariants_legacy.py",
        "sensors.py",
        "repair_plan.py",
        "entrypoints.py",
        "packaging.py",
    ]

    print("\n[1] Syntax Validation")
    all_valid = True
    for filename in critical_files:
        filepath = repo_doctor_dir / filename
        if filepath.exists():
            valid, error = check_syntax(filepath)
            status = "✓" if valid else "✗"
            print(f"  {status} {filename}")
            if error:
                print(f"    Error: {error}")
                all_valid = False
        else:
            print(f"  ✗ {filename} (not found)")
            all_valid = False

    print("\n[2] File Structure")
    subdirs = ["ingest", "graph", "state", "invariants", "solver", "history", "fleet", "output"]
    for subdir in subdirs:
        subdir_path = repo_doctor_dir / subdir
        if subdir_path.exists():
            py_files = list(subdir_path.glob("*.py"))
            print(f"  ✓ {subdir}/ ({len(py_files)} files)")
        else:
            print(f"  ✗ {subdir}/ (missing)")

    print("\n[3] Documentation")
    docs = ["QUICKSTART.md", "ARCHITECTURE.md"]
    for doc in docs:
        doc_path = repo_doctor_dir / doc
        if doc_path.exists():
            size = doc_path.stat().st_size
            print(f"  ✓ {doc} ({size} bytes)")
        else:
            print(f"  ✗ {doc}")

    print("\n[4] VS Code Extension")
    vscode_dir = Path(__file__).parent / "vscode-repo-doctor"
    if vscode_dir.exists():
        print("  ✓ vscode-repo-doctor/ exists")
        for file in ["package.json", "tsconfig.json", "README.md"]:
            file_path = vscode_dir / file
            if file_path.exists():
                print(f"    ✓ {file}")
            else:
                print(f"    ✗ {file}")
    else:
        print("  ✗ vscode-repo-doctor/ (missing)")

    print("\n[5] CI/CD Workflow")
    workflow_path = Path(__file__).parent / ".github" / "workflows" / "repo-doctor.yml"
    if workflow_path.exists():
        print("  ✓ .github/workflows/repo-doctor.yml")
    else:
        print("  ✗ CI workflow (missing)")

    print("\n" + "=" * 70)
    if all_valid:
        print("VALIDATION PASSED - All critical files have valid syntax")
    else:
        print("VALIDATION FAILED - Some files have errors")
    print("=" * 70)

    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
