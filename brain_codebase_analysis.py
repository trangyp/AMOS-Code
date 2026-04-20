#!/usr/bin/env python3
"""
Brain-powered codebase analysis - Uses AMOS brain to analyze and prioritize fixes
"""

import ast
import os

from amos_brain_working import think


def scan_python_files(repo_path: str) -> list:
    """Scan all Python files in repo."""
    files = []
    for root, _, filenames in os.walk(repo_path):
        # Skip hidden dirs and common non-code dirs
        if any(
            x in root for x in [".git", "__pycache__", ".venv", "node_modules", ".pytest_cache"]
        ):
            continue
        for filename in filenames:
            if filename.endswith(".py"):
                files.append(os.path.join(root, filename))
    return files


def check_syntax_errors(filepath: str) -> dict:
    """Check for syntax errors in a Python file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            source = f.read()
        ast.parse(source)
        return {"file": filepath, "valid": True, "error": None}
    except SyntaxError as e:
        return {"file": filepath, "valid": False, "error": str(e)}
    except Exception as e:
        return {"file": filepath, "valid": False, "error": f"Read error: {e}"}


def analyze_with_brain(files_data: list) -> dict:
    """Use brain to prioritize which files to fix first."""

    # Get critical files with errors
    error_files = [f for f in files_data if not f["valid"]]

    # Use brain to analyze and prioritize
    brain_input = {
        "task": "codebase_analysis",
        "total_files": len(files_data),
        "error_files": len(error_files),
        "error_file_paths": [f["file"] for f in error_files[:20]],  # Top 20
        "goal": "prioritize_production_blockers",
    }

    result = think(
        "Analyze this codebase and tell me which files are critical to fix first for production readiness. Prioritize by: 1) Syntax errors, 2) Import errors that break runtime, 3) Core system files. Return a prioritized list of files to fix with specific fix instructions.",
        brain_input,
    )

    return result


if __name__ == "__main__":
    repo_path = "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code"

    print("=" * 70)
    print("🧠 BRAIN-POWERED CODEBASE ANALYSIS")
    print("=" * 70)

    # Scan all Python files
    print("\n[Phase 1] Scanning Python files...")
    all_files = scan_python_files(repo_path)
    print(f"Found {len(all_files)} Python files")

    # Check syntax on all files
    print("\n[Phase 2] Checking syntax errors...")
    file_status = []
    for i, filepath in enumerate(all_files):
        if i % 100 == 0:
            print(f"  Checked {i}/{len(all_files)} files...")
        status = check_syntax_errors(filepath)
        file_status.append(status)

    error_count = sum(1 for f in file_status if not f["valid"])
    print(f"✓ Syntax check complete: {error_count} files with errors")

    # Use brain to analyze and prioritize
    print("\n[Phase 3] Consulting AMOS brain for prioritization...")
    brain_result = analyze_with_brain(file_status)

    print("\n" + "=" * 70)
    print("BRAIN ANALYSIS RESULTS")
    print("=" * 70)

    print(f"\nStatus: {brain_result.get('status', 'unknown')}")
    print(f"Mode: {brain_result.get('mode', 'unknown')}")
    print(f"Brain Used: {brain_result.get('brain_used', False)}")

    if "recommendations" in brain_result:
        print("\n📝 PRIORITIZED FIX LIST:")
        for i, rec in enumerate(brain_result["recommendations"][:10], 1):
            print(f"\n{i}. {rec.get('file', 'Unknown')}")
            print(f"   Priority: {rec.get('priority', 'medium')}")
            print(f"   Action: {rec.get('action', 'Review')}")

    if "kernel_result" in brain_result:
        kr = brain_result["kernel_result"]
        print("\n🔍 KERNEL INSIGHT:")
        if isinstance(kr, dict):
            if "legality" in kr:
                legality = kr["legality"]
                if isinstance(legality, dict):
                    print(f"   Legality Score: {legality.get('score', 'N/A')}")
            print(f"   Operating Mode: {kr.get('operating_mode', 'N/A')}")

    # Show syntax errors found
    if error_count > 0:
        print("\n⚠️  SYNTAX ERRORS FOUND:")
        for status in file_status:
            if not status["valid"]:
                print(f"\n  {status['file']}")
                print(f"    Error: {status['error']}")

    print("\n" + "=" * 70)

    # Save results for next steps
    with open("/tmp/brain_analysis_results.json", "w") as f:
        import json

        json.dump(
            {
                "brain_result": brain_result,
                "error_files": [f for f in file_status if not f["valid"]],
                "total_files": len(all_files),
                "error_count": error_count,
            },
            f,
            indent=2,
            default=str,
        )

    print("Results saved to /tmp/brain_analysis_results.json")
