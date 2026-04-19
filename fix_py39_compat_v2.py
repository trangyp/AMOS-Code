#!/usr/bin/env python3
"""Fix Python 3.9 compatibility issues in AMOS codebase."""

import re
import sys
from pathlib import Path


def fix_file(filepath):
    """Fix Python 3.9 compatibility issues in a single file."""
    try:
        with open(filepath, "r") as f:
            content = f.read()
            original_content = content
    except Exception as e:
        return False, f"Error reading file: {e}"

    changes = []

    # Check if file has Python 3.10+ union syntax
    has_union_syntax = bool(re.search(r":\s*\w+\s*\|\s*None|\->\s*\w+\s*\|\s*None", content))

    if has_union_syntax:
        # Add from __future__ import annotations if not present
        if "from __future__ import annotations" not in content:
            lines = content.split("\n")
            insert_idx = 0

            for i, line in enumerate(lines):
                if i == 0 and line.startswith("#!"):
                    insert_idx = i + 1
                    continue
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    insert_idx = i
                    break

            lines.insert(insert_idx, "from __future__ import annotations")
            content = "\n".join(lines)
            changes.append("Added from __future__ import annotations")

    # Fix datetime.UTC import
    if "from datetime import UTC" in content or "from datetime import UTC, datetime" in content:
        content = re.sub(
            r"from datetime import (?:UTC, )?datetime(?:, UTC)?",
            "from datetime import datetime, timezone\nUTC = timezone.utc",
            content
        )
        changes.append("Fixed datetime.UTC import")

    # Fix timezone.utc = timezone.utc
    if "timezone.utc = timezone.utc" in content:
        content = content.replace("timezone.utc = timezone.utc", "UTC = timezone.utc")
        changes.append("Fixed timezone.utc assignment")

    # Write changes if any
    if content != original_content:
        try:
            with open(filepath, "w") as f:
                f.write(content)
            return True, changes
        except Exception as e:
            return False, f"Error writing file: {e}"

    return False, "No changes needed"


def main():
    """Main function to fix all Python files."""
    repo_path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

    # Critical directories to fix
    critical_dirs = [
        "backend",
        "clawspring",
        "amos_brain",
        "amos_self_evolution",
        "amos_model_fabric",
        "AMOS_ORGANISM_OS",
        "_AMOS_BRAIN",
        "axiom_one",
        "multi_agent",
    ]

    fixed = 0
    errors = 0
    no_changes = 0

    for dir_name in critical_dirs:
        dir_path = repo_path / dir_name
        if not dir_path.exists():
            continue

        for py_file in dir_path.rglob("*.py"):
            success, message = fix_file(py_file)
            if success:
                fixed += 1
                print(f"✓ {py_file.relative_to(repo_path)}: {', '.join(message)}")
            elif "Error" in str(message):
                errors += 1
                print(f"✗ {py_file.relative_to(repo_path)}: {message}")
            else:
                no_changes += 1

    print(f"\n=== Summary ===")
    print(f"Fixed: {fixed} files")
    print(f"No changes: {no_changes} files")
    if errors:
        print(f"Errors: {errors} files")


if __name__ == "__main__":
    main()
