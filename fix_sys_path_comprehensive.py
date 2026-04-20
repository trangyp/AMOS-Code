#!/usr/bin/env python3
"""Comprehensive sys.path.insert fixer for AMOS codebase."""

import re
from pathlib import Path


def find_and_fix_file(filepath: Path) -> tuple[bool, str]:
    """Find and fix sys.path.insert in a single file."""
    try:
        content = filepath.read_text()
        original = content

        # Pattern 1: sys.path.insert(0, os.path.dirname(...))
        pattern1 = r"^\s*sys\.path\.insert\(0,\s*os\.path\.[^)]+\)\s*$"

        # Pattern 2: sys.path.insert(0, str(...))
        pattern2 = r"^\s*sys\.path\.insert\(0,\s*str\([^)]+\)\)\s*$"

        # Pattern 3: sys.path.insert(0, "...") or sys.path.insert(0, '...')
        pattern3 = r'^\s*sys\.path\.insert\(0,\s*["\'][^"\']+["\']\)\s*$'

        # Remove all sys.path.insert lines
        lines = content.split("\n")
        new_lines = []
        removed_count = 0

        for line in lines:
            if re.match(pattern1, line) or re.match(pattern2, line) or re.match(pattern3, line):
                removed_count += 1
                continue
            new_lines.append(line)

        if removed_count > 0:
            content = "\n".join(new_lines)
            # Clean up multiple blank lines
            content = re.sub(r"\n{3,}", "\n\n", content)

            if content != original:
                filepath.write_text(content)
                return True, f"Removed {removed_count} sys.path.insert lines"

        return False, "No changes needed"

    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def batch_fix_directory(base_path: Path, max_files: int = 50) -> dict:
    """Batch fix files in directory."""
    results = {"fixed": 0, "skipped": 0, "errors": [], "files_processed": []}

    # Priority files first
    priority_patterns = [
        "amos_*.py",
        "backend/**/*.py",
        "AMOS_ORGANISM_OS/**/*.py",
        "clawspring/**/*.py",
        "_AMOS_BRAIN/**/*.py",
    ]

    files_to_fix = []

    # Find all Python files
    for pattern in ["**/*.py"]:
        for filepath in base_path.glob(pattern):
            # Skip venv and node_modules
            if "venv" in str(filepath) or "node_modules" in str(filepath):
                continue
            if ".git" in str(filepath):
                continue
            files_to_fix.append(filepath)

    # Process up to max_files
    for filepath in files_to_fix[:max_files]:
        was_fixed, msg = find_and_fix_file(filepath)

        if was_fixed:
            results["fixed"] += 1
            results["files_processed"].append(str(filepath.relative_to(base_path)))
        elif "Error" in msg:
            results["errors"].append(f"{filepath}: {msg}")
        else:
            results["skipped"] += 1

    return results


def main():
    base_path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
    results = batch_fix_directory(base_path, max_files=100)

    print("Batch Fix Complete:")
    print(f"  Files fixed: {results['fixed']}")
    print(f"  Files skipped: {results['skipped']}")
    print(f"  Errors: {len(results['errors'])}")

    if results["files_processed"]:
        print("\nFixed files:")
        for f in results["files_processed"][:20]:
            print(f"  - {f}")
        if len(results["files_processed"]) > 20:
            print(f"  ... and {len(results['files_processed']) - 20} more")

    if results["errors"][:5]:
        print("\nErrors (first 5):")
        for e in results["errors"][:5]:
            print(f"  {e}")


if __name__ == "__main__":
    main()
