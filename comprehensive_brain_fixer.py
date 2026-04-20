#!/usr/bin/env python3
"""
Comprehensive Brain-Guided Fixer
Uses AMOS brain to scan entire repo and fix all critical Python 3.9 issues
"""

import ast
import os
import re

from amos_brain_working import think

REPO_PATH = "/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code"


def scan_all_python_files():
    """Scan all Python files in repo."""
    python_files = []
    for root, dirs, files in os.walk(REPO_PATH):
        # Skip hidden and cache directories
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".") and d not in ["__pycache__", "node_modules", ".venv"]
        ]
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def check_syntax(filepath):
    """Check file for syntax errors."""
    try:
        with open(filepath, encoding="utf-8") as f:
            source = f.read()
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


def fix_file(filepath):
    """Apply common fixes to a file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return False, "Read error"

    original = content

    # Fix 1: Remove duplicate typing imports
    lines = content.split("\n")
    seen_imports = set()
    new_lines = []
    for line in lines:
        if line.startswith("from typing import"):
            # Normalize and check
            normalized = re.sub(r"\s+", " ", line.strip())
            if normalized in seen_imports:
                continue
            seen_imports.add(normalized)
        new_lines.append(line)
    content = "\n".join(new_lines)

    # Fix 2: Fix timezone.utc to datetime.timezone.utc (in imports)
    content = re.sub(
        r"from datetime import datetime, timezone",
        r"from datetime import datetime, timezone",
        content,
    )
    content = re.sub(r"UTC = timezone.utc", r"UTC = timezone.utc", content)

    # Fix 3: Fix timezone.utc usage
    content = re.sub(r"datetime\.UTC", r"timezone.utc", content)

    # Fix 4: Fix datetime.now(timezone.utc) to datetime.now(timezone.utc)
    content = re.sub(r"datetime\.utcnow\(\)", r"datetime.now(timezone.utc)", content)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True, "Fixed common patterns"

    return False, "No changes needed"


def main():
    print("=" * 70)
    print("🧠 COMPREHENSIVE BRAIN-GUIDED FIXER")
    print("=" * 70)

    # Get all Python files
    print("\n[Phase 1] Scanning repository...")
    all_files = scan_all_python_files()
    print(f"Found {len(all_files)} Python files")

    # Check for syntax errors
    print("\n[Phase 2] Checking syntax...")
    errors = []
    for i, filepath in enumerate(all_files):
        if i % 100 == 0:
            print(f"  Progress: {i}/{len(all_files)}")
        valid, error = check_syntax(filepath)
        if not valid:
            errors.append({"file": filepath, "error": error})

    print(f"\nFound {len(errors)} files with syntax errors")

    # Use brain to prioritize
    if errors:
        print("\n[Phase 3] Consulting brain for prioritization...")
        context = {
            "total_files": len(all_files),
            "error_count": len(errors),
            "error_files": [e["file"].replace(REPO_PATH, "") for e in errors[:20]],
        }

        brain_result = think(
            "Analyze these syntax errors and provide fix strategy. Focus on: "
            "1) Import-related errors are easiest to fix, "
            "2) Core system files have highest priority, "
            "3) Files in backend/, amos_brain/, clawspring/ are critical. "
            "Return top 10 files to fix with specific instructions.",
            context,
        )

        print(f"\nBrain Status: {brain_result.get('status', 'unknown')}")
        print(f"Mode: {brain_result.get('mode', 'unknown')}")
        print(f"Brain Used: {brain_result.get('brain_used', False)}")

        # Show top errors
        print("\n[Phase 4] Top syntax errors to fix:")
        for i, err in enumerate(errors[:10], 1):
            print(f"\n{i}. {err['file'].replace(REPO_PATH + '/', '')}")
            print(f"   {err['error']}")

        # Attempt fixes
        print("\n[Phase 5] Attempting automatic fixes...")
        fixed = 0
        for err in errors[:10]:
            success, msg = fix_file(err["file"])
            if success:
                # Verify fix
                valid, _ = check_syntax(err["file"])
                if valid:
                    print(f"✓ Fixed: {err['file'].replace(REPO_PATH + '/', '')}")
                    fixed += 1
                else:
                    print(f"⚠ Partial fix: {err['file'].replace(REPO_PATH + '/', '')}")

        print(f"\n{'=' * 70}")
        print(f"SUMMARY: Fixed {fixed}/{len(errors)} files with errors")
    else:
        print("\n✓ No syntax errors found!")

    # Final brain analysis
    print("\n[Phase 6] Final brain analysis...")
    final_context = {"files_checked": len(all_files), "errors_remaining": len(errors)}
    final_analysis = think(
        f"Analysis complete. Checked {len(all_files)} files. "
        f"What additional steps should be taken to ensure production readiness?",
        final_context,
    )

    if "recommendations" in final_analysis:
        print("\n📝 Brain Recommendations:")
        for rec in final_analysis["recommendations"][:5]:
            print(f"  - {rec.get('action', 'Continue')}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
