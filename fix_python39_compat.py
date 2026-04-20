#!/usr/bin/env python3
"""Fix Python 3.9 compatibility issues by adding from __future__ import annotations"""

import re
from pathlib import Path


def needs_future_annotations(filepath):
    """Check if file uses Python 3.10+ union syntax."""
    try:
        with open(filepath) as f:
            content = f.read()

        # Check for union syntax patterns
        patterns = [
            r":\s*\w+\s*\|\s*None",  # type | None
            r"->\s*\w+\s*\|\s*None",  # -> Optional[type]
            r"\w+\s*\|\s*\w+",  # type1 | type2 (simplified check)
        ]

        for pattern in patterns:
            if re.search(pattern, content):
                # Check if already has future annotations
                if "from __future__ import annotations" not in content:
                    return True
        return False
    except Exception:
        return False


def add_future_annotations(filepath):
    """Add from __future__ import annotations to a file."""
    with open(filepath) as f:
        content = f.read()

    # Find the right place to insert (after docstring, before other imports)
    lines = content.split("\n")

    # Find the end of docstring
    insert_idx = 0
    in_docstring = False
    docstring_delim = None

    for i, line in enumerate(lines):
        if i == 0 and line.startswith("#!"):
            insert_idx = i + 1
            continue

        stripped = line.strip()

        # Handle docstrings
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                    # Single line docstring
                    insert_idx = i + 1
                else:
                    in_docstring = True
                    docstring_delim = '"""' if '"""' in stripped else "'''"
        else:
            if docstring_delim in stripped:
                in_docstring = False
                insert_idx = i + 1
                break

    # Insert the future import
    lines.insert(insert_idx, "from __future__ import annotations")
    lines.insert(insert_idx + 1, "")

    with open(filepath, "w") as f:
        f.write("\n".join(lines))

    return True


def main():
    """Main function to fix all Python 3.9 compatibility issues."""
    base_path = Path(".")

    # Directories to scan
    dirs_to_scan = ["backend", "axiom_one", "amos_brain", "amos_model_fabric", "clawspring"]

    fixed_files = []

    for dir_name in dirs_to_scan:
        dir_path = base_path / dir_name
        if not dir_path.exists():
            continue

        for py_file in dir_path.rglob("*.py"):
            if needs_future_annotations(py_file):
                print(f"Fixing: {py_file}")
                if add_future_annotations(py_file):
                    fixed_files.append(str(py_file))

    print(f"\nFixed {len(fixed_files)} files:")
    for f in fixed_files:
        print(f"  - {f}")


if __name__ == "__main__":
    main()
