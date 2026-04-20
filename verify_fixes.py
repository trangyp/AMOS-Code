#!/usr/bin/env python3
"""
Verify syntax fixes using brain analysis
"""

import ast
import os
import sys

from amos_brain_working import think


def check_syntax(filepath: str) -> tuple[bool, str]:
    """Check if file has valid syntax."""
    try:
        with open(filepath, encoding="utf-8") as f:
            source = f.read()
        ast.parse(source)
        return True, ""
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


def main():
    # Files we fixed
    fixed_files = [
        "amos_core.py",
        "amos_github_tool.py",
        "amos_meaning_compiler.py",
        "clawspring/amos_plugin.py",
        "clawspring/amos_runtime.py",
        "clawspring/amos_physics_cosmos_engine.py",
        "clawspring/amos_personality_engine.py",
        "axiom_one/orchestrator.py",
        "backend/analytics/analytics_service.py",
        "axiom_one_brain_bridge.py",
    ]

    repo_path = "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code"

    print("=" * 70)
    print("🔍 VERIFYING FIXED FILES")
    print("=" * 70)

    all_valid = True
    results = []

    for filepath in fixed_files:
        full_path = os.path.join(repo_path, filepath)
        if os.path.exists(full_path):
            valid, error = check_syntax(full_path)
            status = "✓" if valid else "✗"
            print(f"{status} {filepath}")
            if not valid:
                print(f"   Error: {error}")
                all_valid = False
            results.append({"file": filepath, "valid": valid, "error": error})
        else:
            print(f"? {filepath} - FILE NOT FOUND")
            all_valid = False
            results.append({"file": filepath, "valid": False, "error": "File not found"})

    print("\n" + "=" * 70)

    # Use brain to analyze results
    context = {
        "fixed_files": len(results),
        "valid_files": sum(1 for r in results if r["valid"]),
        "invalid_files": sum(1 for r in results if not r["valid"]),
        "results": results,
    }

    brain_result = think(
        "Analyze these fix verification results. All files should have valid syntax. "
        "If any files still have errors, determine the priority for fixing them. "
        "Return specific fix instructions for any remaining errors.",
        context,
    )

    print("\nBrain Analysis:")
    print(f"  Status: {brain_result.get('status', 'unknown')}")
    print(f"  Mode: {brain_result.get('mode', 'unknown')}")
    print(f"  Brain Used: {brain_result.get('brain_used', False)}")

    # Check for brain recommendations
    if "recommendations" in brain_result:
        print("\n📝 Brain Recommendations:")
        for rec in brain_result["recommendations"][:5]:
            print(f"  - {rec.get('action', 'Review')}")

    # Summary
    valid_count = sum(1 for r in results if r["valid"])
    print(f"\nSummary: {valid_count}/{len(results)} files have valid syntax")

    if all_valid:
        print("\n✓ All fixed files compile successfully!")
        return 0
    else:
        print("\n⚠ Some files still have errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())
