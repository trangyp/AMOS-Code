#!/usr/bin/env python3
"""
AMOS Typing Modernization Script
================================
Bulk replacement of deprecated typing imports with Python 3.10+ native syntax.

Converts:
- X  -> X
- list[X] -> list[X]
- dict[X, Y] -> dict[X, Y]
- set[X] -> set[X]
- tuple[X, ...] -> tuple[X, ...]
- X | Y -> X | Y

Usage:
    python scripts/modernize_typing.py <file_or_directory>
    python scripts/modernize_typing.py --dry-run <file_or_directory>

Author: AMOS Modernization Team
"""

import argparse
import re
import sys
from pathlib import Path

# Patterns for typing modernization
TYPING_PATTERNS = [
    # Remove deprecated imports from typing
    (r"from typing import.*Optional.*\n?", ""),
    (r"from typing import.*List.*\n?", ""),
    (r"from typing import.*Dict.*\n?", ""),
    (r"from typing import.*Set.*\n?", ""),
    (r"from typing import.*Tuple.*\n?", ""),
    (r"from typing import.*Union.*\n?", ""),
    # Replace type annotations
    (r"Optional\[([^\]]+)\]", r"\1 "),
    (r"List\[([^\]]+)\]", r"list[\1]"),
    (r"Dict\[([^,\]]+),\s*([^\]]+)\]", r"dict[\1, \2]"),
    (r"Set\[([^\]]+)\]", r"set[\1]"),
    (r"Tuple\[([^\]]*)\]", r"tuple[\1]"),
    (r"Union\[([^\]]+)\]", lambda m: " | ".join(x.strip() for x in m.group(1).split(","))),
]


def modernize_file(filepath: Path, dry_run: bool = False) -> tuple[int, list[str]]:
    """Modernize typing in a single file."""
    changes = []
    content = filepath.read_text()
    original_content = content

    # Check if file has deprecated typing
    has_deprecated = any(re.search(pattern, content) for pattern, _ in TYPING_PATTERNS)

    if not has_deprecated:
        return 0, []

    # Track what needs to be cleaned from imports
    needs_optional = "" in content
    needs_list = "list[" in content
    needs_dict = "Dict[" in content
    needs_set = "set[" in content
    needs_tuple = "tuple[" in content
    needs_union = "" in content

    # Replace type annotations
    if needs_optional:
        content = re.sub(r"Optional\[([^\ +)\]", r"\1 ", content)
        changes.append("Replaced X  with X ")

    if needs_list:
        content = re.sub(r"List\[([^\]]+)\]", r"list[\1]", content)
        changes.append("Replaced list[X] with list[X]")

    if needs_dict:
        content = re.sub(r"Dict\[([^,\]]+),\s*([^\]]+)\]", r"dict[\1, \2]", content)
        changes.append("Replaced dict[K, V] with dict[K, V]")

    if needs_set:
        content = re.sub(r"Set\[([^\]]+)\]", r"set[\1]", content)
        changes.append("Replaced set[X] with set[X]")

    if needs_tuple:
        content = re.sub(r"Tuple\[([^\]]*)\]", r"tuple[\1]", content)
        changes.append("Replaced tuple[X] with tuple[X]")

    if needs_union:

        def replace_union(m):
            parts = [x.strip() for x in m.group(1).split(",")]
            return " | ".join(parts)

        content = re.sub(r"Union\[([^\]]+)\]", replace_union, content)
        changes.append("Replaced X | Y with X | Y")

    # Clean up typing imports
    if content != original_content:
        # Remove specific imports from typing
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            if line.strip().startswith("from typing import"):
                # Keep only non-deprecated imports
                imports = line.replace("from typing import", "").strip().rstrip(",").split(",")
                new_imports = []
                for imp in imports:
                    imp = imp.strip()
                    if imp and imp not in ["Optional", "List", "Dict", "Set", "Tuple", "Union"]:
                        new_imports.append(imp)

                if new_imports:
                    new_lines.append(f"from typing import {', '.join(new_imports)}")
            else:
                new_lines.append(line)

        content = "\n".join(new_lines)
        if needs_optional or needs_list or needs_dict or needs_set or needs_tuple or needs_union:
            changes.append("Updated typing imports")

    if content != original_content:
        if not dry_run:
            filepath.write_text(content)
        return len(changes), changes

    return 0, []


def modernize_directory(directory: Path, dry_run: bool = False) -> dict:
    """Modernize all Python files in a directory."""
    results = {"files_processed": 0, "files_modified": 0, "total_changes": 0, "changes_by_file": {}}

    for filepath in directory.rglob("*.py"):
        if any(part.startswith(".") or part in ["venv", "__pycache__"] for part in filepath.parts):
            continue

        results["files_processed"] += 1
        count, changes = modernize_file(filepath, dry_run)

        if count > 0:
            results["files_modified"] += 1
            results["total_changes"] += count
            results["changes_by_file"][str(filepath)] = changes

    return results


def main():
    parser = argparse.ArgumentParser(description="Modernize typing in AMOS codebase")
    parser.add_argument("path", type=Path, help="File or directory to modernize")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    parser.add_argument("-v", "--verbose", action="store_true", help="Detailed output")

    args = parser.parse_args()

    if not args.path.exists():
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    if args.path.is_file():
        count, changes = modernize_file(args.path, args.dry_run)
        if count > 0:
            print(f"{'Would modify' if args.dry_run else 'Modified'}: {args.path}")
            if args.verbose:
                for change in changes:
                    print(f"  - {change}")
    else:
        results = modernize_directory(args.path, args.dry_run)

        print(f"\n{'=' * 60}")
        print(f"AMOS Typing Modernization {'(DRY RUN)' if args.dry_run else ''}")
        print(f"{'=' * 60}")
        print(f"Files processed: {results['files_processed']}")
        print(f"Files {'would be ' if args.dry_run else ''}modified: {results['files_modified']}")
        print(f"Total changes: {results['total_changes']}")

        if args.verbose and results["changes_by_file"]:
            print("\nChanges by file:")
            for filepath, changes in results["changes_by_file"].items():
                print(f"\n  {filepath}:")
                for change in changes:
                    print(f"    - {change}")


if __name__ == "__main__":
    main()
