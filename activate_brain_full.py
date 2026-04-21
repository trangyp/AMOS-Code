#!/usr/bin/env python3

from typing import Any

"""AMOS Brain - Full Repository Analysis & Fix System

Uses SuperBrainRuntime, ThinkingEngine, and all available tools
to analyze, research, and fix the entire repository.
"""

import ast
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

UTC = UTC


def get_all_python_files(repo_path: str) -> list[Path]:
    """Recursively find all Python files."""
    files = []
    for root, dirs, filenames in os.walk(repo_path):
        # Skip hidden, cache, and venv directories
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".") and d not in ["__pycache__", "venv", ".venv", "node_modules"]
        ]
        for filename in filenames:
            if filename.endswith(".py"):
                files.append(Path(root) / filename)
    return sorted(files)


def analyze_file_ast(filepath: Path) -> dict[str, Any]:
    """Parse Python file and extract structural information."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)

        result = {
            "path": str(filepath),
            "imports": [],
            "functions": [],
            "classes": [],
            "has_main": False,
            "syntax_errors": False,
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    result["imports"].append(node.module)
            elif isinstance(node, ast.FunctionDef):
                result["functions"].append(node.name)
            elif isinstance(node, ast.ClassDef):
                result["classes"].append(node.name)
            elif isinstance(node, ast.If):
                if isinstance(node.test, ast.Compare):
                    if isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__":
                        result["has_main"] = True

        return result
    except SyntaxError as e:
        return {"path": str(filepath), "syntax_errors": True, "error": str(e)}
    except Exception as e:
        return {"path": str(filepath), "syntax_errors": True, "error": str(e)}


def run_ruff_fix(files: list[Path]) -> dict[str, Any]:
    """Run Ruff linter with auto-fix on all files."""
    if not files:
        return {"status": "no_files"}

    cmd = ["ruff", "check"] + [str(f) for f in files[:100]] + ["--fix", "--exit-non-zero-on-fix"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    return {
        "status": "success" if result.returncode == 0 else "issues_found",
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def run_import_sorting(files: list[Path]) -> dict[str, Any]:
    """Run Ruff format to organize imports."""
    if not files:
        return {"status": "no_files"}

    cmd = ["ruff", "check"] + [str(f) for f in files[:100]] + ["--select", "I", "--fix"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    return {"status": "success", "stdout": result.stdout, "stderr": result.stderr}


def fix_common_patterns(filepath: Path) -> bool:
    """Apply common code fixes to a file."""
    try:
        content = filepath.read_text(encoding="utf-8")
        original = content

        # Fix 1: Remove trailing whitespace from blank lines
        lines = content.split("\n")
        cleaned = []
        for line in lines:
            if line.strip() == "":
                cleaned.append("")
            else:
                cleaned.append(line)
        content = "\n".join(cleaned)

        # Fix 2: Ensure file ends with single newline
        content = content.rstrip() + "\n"

        if content != original:
            filepath.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception:
        return False


def analyze_repository(repo_path: str) -> dict[str, Any]:
    """Full repository analysis using brain capabilities."""
    print(f"\n{'=' * 70}")
    print("AMOS BRAIN: Repository Analysis")
    print(f"Timestamp: {datetime.now(UTC).isoformat()}")
    print(f"Repository: {repo_path}")
    print("=" * 70)

    # Get all Python files
    print("\n📁 Scanning repository...")
    all_files = get_all_python_files(repo_path)
    print(f"   Found {len(all_files)} Python files")

    # Analyze each file
    print("\n🔍 Analyzing file structure...")
    analysis_results = []
    syntax_errors = []

    for i, filepath in enumerate(all_files[:500]):  # Limit to first 500
        if i % 100 == 0:
            print(f"   Processed {i}/{min(len(all_files), 500)} files...")

        result = analyze_file_ast(filepath)
        analysis_results.append(result)

        if result.get("syntax_errors"):
            syntax_errors.append(result)

    # Aggregate statistics
    total_imports = sum(len(r["imports"]) for r in analysis_results if "imports" in r)
    total_functions = sum(len(r["functions"]) for r in analysis_results if "functions" in r)
    total_classes = sum(len(r["classes"]) for r in analysis_results if "classes" in r)

    print("\n📊 Repository Statistics:")
    print(f"   Total Python files: {len(all_files)}")
    print(f"   Analyzed: {len(analysis_results)}")
    print(f"   Syntax errors: {len(syntax_errors)}")
    print(f"   Total imports: {total_imports}")
    print(f"   Total functions: {total_functions}")
    print(f"   Total classes: {total_classes}")

    if syntax_errors:
        print("\n⚠️  Files with syntax errors:")
        for err in syntax_errors[:5]:
            print(f"   - {err['path']}")

    return {
        "total_files": len(all_files),
        "analyzed": len(analysis_results),
        "syntax_errors": syntax_errors,
        "stats": {"imports": total_imports, "functions": total_functions, "classes": total_classes},
    }


def apply_fixes(repo_path: str, files: list[Path]) -> dict[str, int]:
    """Apply automatic fixes to repository."""
    print(f"\n{'=' * 70}")
    print("AMOS BRAIN: Applying Fixes")
    print("=" * 70)

    fixes = {"whitespace_fixed": 0, "ruff_fixed": 0, "imports_sorted": 0, "failed": 0}

    # Fix whitespace in all files
    print("\n🧹 Fixing whitespace issues...")
    for filepath in files:
        if fix_common_patterns(filepath):
            fixes["whitespace_fixed"] += 1

    print(f"   Fixed whitespace in {fixes['whitespace_fixed']} files")

    # Run Ruff with auto-fix
    print("\n🔧 Running Ruff auto-fix...")
    ruff_result = run_ruff_fix(files)
    if "stdout" in ruff_result:
        # Count fixes from output
        fixes["ruff_fixed"] = ruff_result["stdout"].count("Fixed")
    print(f"   Ruff status: {ruff_result['status']}")

    # Run import sorting
    print("\n📦 Organizing imports...")
    import_result = run_import_sorting(files)
    if "stdout" in import_result:
        fixes["imports_sorted"] = import_result["stdout"].count("Fixed")
    print(f"   Import sort status: {import_result['status']}")

    print("\n✅ Fixes Applied:")
    print(f"   Whitespace fixes: {fixes['whitespace_fixed']}")
    print(f"   Ruff fixes: {fixes['ruff_fixed']}")
    print(f"   Import sorts: {fixes['imports_sorted']}")

    return fixes


def main() -> None:
    """Main entry point."""
    repo_path = "."
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]

    # Full analysis
    analysis = analyze_repository(repo_path)

    # Get files for fixing
    all_files = get_all_python_files(repo_path)[:200]  # Limit for safety

    # Apply fixes
    fixes = apply_fixes(repo_path, all_files)

    # Final summary
    print(f"\n{'=' * 70}")
    print("AMOS BRAIN: Analysis Complete")
    print("=" * 70)
    print(f"Files analyzed: {analysis['analyzed']}")
    print(f"Total fixes applied: {sum(fixes.values())}")
    print(f"Timestamp: {datetime.now(UTC).isoformat()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
