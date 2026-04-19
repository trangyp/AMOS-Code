#!/usr/bin/env python3
"""
AMOS Datetime Modernization Script
==================================
Bulk replacement of deprecated datetime.now(timezone.utc) with timezone-aware datetime.now(timezone.utc)

Usage:
    python scripts/modernize_datetime.py <file_or_directory>
    python scripts/modernize_datetime.py --dry-run <file_or_directory>

Author: AMOS Modernization Team
"""

import argparse
import re
import sys
from pathlib import Path

# Patterns to match and replace
PATTERNS = [
    # Add timezone import
    (r"from datetime import (datetime, timedelta)", r"from datetime import \1, timezone"),
UTC = timezone.utc
    (r"from datetime import datetime$", r"from datetime import datetime, timezone"),
    # Replace utcnow() calls
    (r"datetime\.utcnow\(\)", r"datetime.now(timezone.utc)"),
]


def modernize_file(filepath: Path, dry_run: bool = False) -> tuple[int, list[str]]:
    """
    Modernize datetime usage in a single file.

    Returns:
        Tuple of (number of changes, list of change descriptions)
    """
    changes = []
    content = filepath.read_text()
    original_content = content

    # Check if file has utcnow usage
    if "datetime.utcnow" not in content and "from datetime import datetime" not in content:
        return 0, []

    # Track if we need timezone import
    needs_timezone = False

    # Replace utcnow() calls
    if "datetime.now(timezone.utc)" in content:
        content = re.sub(r"datetime\.utcnow\(\)", "datetime.now(timezone.utc)", content)
        needs_timezone = True
        changes.append("Replaced datetime.now(timezone.utc) with datetime.now(timezone.utc)")

    # Update imports if needed
    if needs_timezone:
        # Check if timezone is already imported
        if "timezone" not in content:
            if "from datetime import datetime, timedelta" in content:
                content = content.replace(
                    "from datetime import datetime, timedelta",
                    "from datetime import datetime, timedelta, timezone",
                )
                changes.append("Added timezone to datetime imports")
            elif "from datetime import datetime" in content:
                content = content.replace(
                    "from datetime import datetime", "from datetime import datetime, timezone"
                )
                changes.append("Added timezone to datetime imports")

    if content != original_content:
        if not dry_run:
            filepath.write_text(content)
        return len(changes), changes

    return 0, []


def modernize_directory(directory: Path, dry_run: bool = False) -> dict:
    """Modernize all Python files in a directory recursively."""
    results = {"files_processed": 0, "files_modified": 0, "total_changes": 0, "changes_by_file": {}}

    for filepath in directory.rglob("*.py"):
        # Skip certain directories
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
    parser = argparse.ArgumentParser(description="Modernize datetime usage in AMOS codebase")
    parser.add_argument("path", type=Path, help="File or directory to modernize")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying them")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")

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
            print(f"No changes needed: {args.path}")
    else:
        results = modernize_directory(args.path, args.dry_run)

        print(f"\n{'='*60}")
        print(f"AMOS Datetime Modernization {'(DRY RUN)' if args.dry_run else ''}")
        print(f"{'='*60}")
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
