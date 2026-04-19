#!/usr/bin/env python3
"""Fix remaining syntax issues in AMOS codebase."""

import re
from pathlib import Path


def fix_file(filepath: Path) -> bool:
    """Fix common issues in a single file."""
    try:
        content = filepath.read_text(encoding="utf-8")
        original = content

        # Fix 1: Remove stray 'from typing import' lines at wrong indentation (not at top level)
        lines = content.split("\n")
        new_lines = []
        in_function = False
        indent_level = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Track if we're inside a function/class
            if (
                stripped.endswith(":")
                and not stripped.startswith("#")
                and not stripped.startswith('"""')
            ):
                if (
                    line.startswith("def ")
                    or line.startswith("class ")
                    or line.startswith("async def")
                ):
                    in_function = True
                    indent_level = len(line) - len(line.lstrip())

            # Check if this is a stray typing import inside a function
            if stripped.startswith("from typing import") or stripped.startswith(
                "from dataclasses import"
            ):
                # Check if this line is indented (inside a function/block)
                if line.startswith("    ") or line.startswith("\t"):
                    # Check if it's at the top of file (before any function)
                    prev_non_empty = None
                    for j in range(i - 1, -1, -1):
                        if lines[j].strip():
                            prev_non_empty = lines[j]
                            break

                    # If previous non-empty line is a def/class or docstring, skip this import
                    if prev_non_empty and (
                        prev_non_empty.strip().endswith(":")
                        or prev_non_empty.strip().startswith('"""')
                        or prev_non_empty.strip().startswith("'''")
                    ):
                        continue  # Skip this line

            new_lines.append(line)

        content = "\n".join(new_lines)

        # Fix 2: Fix Python 3.10+ union syntax | to Optional
        # Pattern: type | None -> Optional[type]
        content = re.sub(r"(\w+):\s+(\w+)\s*\|\s*None\s*=", r"\1: Optional[\2] =", content)

        # Fix 3: Remove duplicate consecutive typing imports
        content = re.sub(
            r"(from typing import [^\n]+)\nfrom typing import ([^\n]+)",
            lambda m: f'from typing import {m.group(1).replace("from typing import ", "")}, {m.group(2)}',
            content,
        )

        if content != original:
            filepath.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"Error in {filepath}: {e}")
        return False


def main():
    root = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
    fixed = 0
    checked = 0

    for py_file in root.rglob("*.py"):
        if any(part.startswith(".") or part in ["venv", "__pycache__"] for part in py_file.parts):
            continue
        checked += 1
        if fix_file(py_file):
            fixed += 1
            if fixed % 100 == 0:
                print(f"Fixed {fixed} files...")

    print(f"Checked: {checked}, Fixed: {fixed}")


if __name__ == "__main__":
    main()
