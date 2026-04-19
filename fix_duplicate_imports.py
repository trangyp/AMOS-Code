#!/usr/bin/env python3
"""Fix duplicate typing imports in AMOS codebase."""

import re
from pathlib import Path


def fix_duplicate_imports(content: str) -> str:
    """Remove duplicate imports from typing import statements."""
    lines = content.split("\n")
    new_lines = []

    for line in lines:
        # Match from typing import lines
        if match := re.match(r"^(from typing import\s+)(.+)$", line):
            prefix = match.group(1)
            imports = match.group(2)
            # Split by comma and clean up
            items = [item.strip() for item in imports.split(",")]
            # Remove duplicates while preserving order
            seen = set()
            unique_items = []
            for item in items:
                if item and item not in seen:
                    seen.add(item)
                    unique_items.append(item)

            if unique_items:
                new_line = prefix + ", ".join(unique_items)
                new_lines.append(new_line)
            else:
                new_lines.append(line)  # Keep original if something went wrong
        else:
            new_lines.append(line)

    return "\n".join(new_lines)


def remove_consecutive_duplicate_import_lines(content: str) -> str:
    """Remove consecutive duplicate import lines."""
    lines = content.split("\n")
    new_lines = []
    prev_line = None

    for line in lines:
        stripped = line.strip()
        # Check if this is a typing import line
        if stripped.startswith("from typing import"):
            # If same as previous, skip it
            if stripped == prev_line:
                continue
            prev_line = stripped
        else:
            prev_line = None
        new_lines.append(line)

    return "\n".join(new_lines)


def process_file(filepath: Path) -> bool:
    """Process a single file and fix imports."""
    try:
        content = filepath.read_text(encoding="utf-8")
        original = content

        # Apply fixes
        content = fix_duplicate_imports(content)
        content = remove_consecutive_duplicate_import_lines(content)

        # Only write if changed
        if content != original:
            filepath.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def main():
    """Find and fix all Python files with duplicate imports."""
    root = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

    fixed = 0
    checked = 0

    # Find all Python files
    for py_file in root.rglob("*.py"):
        # Skip virtual environments and caches
        if any(
            part.startswith(".") or part in ["venv", "__pycache__", ".venv"]
            for part in py_file.parts
        ):
            continue

        checked += 1
        if process_file(py_file):
            fixed += 1
            if fixed % 50 == 0:
                print(f"Fixed {fixed} files...")

    print(f"\nChecked: {checked} files")
    print(f"Fixed: {fixed} files")


if __name__ == "__main__":
    main()
