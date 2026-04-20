#!/usr/bin/env python3
"""Brain-powered fixer for currently open files."""

import ast
from pathlib import Path

from amos_brain_working import think

OPEN_FILES = [
    "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/axiom_one/models.py",
    "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/backend/main.py",
    "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/backend/gateway/api_gateway.py",
    "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/amos_brain/cognitive_engine.py",
    "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/backend/auth.py",
    "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code/backend/real_orchestrator_bridge.py",
]


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
    print("=" * 70)
    print("🧠 BRAIN ANALYZING OPEN FILES")
    print("=" * 70)

    results = []
    for filepath in OPEN_FILES:
        path = Path(filepath)
        if not path.exists():
            print(f"\n? {path.name} - NOT FOUND")
            continue

        valid, error = check_syntax(filepath)
        status = "✓" if valid else "✗"
        print(f"\n{status} {path.name}")

        if not valid:
            print(f"  Error: {error}")

        results.append({"file": path.name, "valid": valid, "error": error, "path": filepath})

    # Use brain to analyze results
    context = {
        "files_checked": len(results),
        "valid_files": sum(1 for r in results if r["valid"]),
        "invalid_files": [r for r in results if not r["valid"]],
    }

    print("\n" + "=" * 70)
    print("CONSULTING BRAIN...")
    print("=" * 70)

    brain_result = think(
        "Analyze these open files and determine what fixes are needed for Python 3.9 compatibility. "
        "Focus on: missing imports, datetime issues, typing compatibility. "
        "Return specific fix instructions for each file that needs work.",
        context,
    )

    print(f"\nBrain Status: {brain_result.get('status', 'unknown')}")
    print(f"Brain Used: {brain_result.get('brain_used', False)}")
    print(f"Mode: {brain_result.get('mode', 'unknown')}")

    # Display recommendations
    if "recommendations" in brain_result:
        print("\n📝 BRAIN FIX RECOMMENDATIONS:")
        for rec in brain_result["recommendations"]:
            print(f"\n→ {rec.get('file', 'Unknown')}")
            print(f"  Action: {rec.get('action', 'Review')}")
            if "fix" in rec:
                print(f"  Fix: {rec['fix']}")

    # Summary
    valid_count = sum(1 for r in results if r["valid"])
    print(f"\n{'=' * 70}")
    print(f"SUMMARY: {valid_count}/{len(results)} files have valid syntax")

    return results


if __name__ == "__main__":
    main()
