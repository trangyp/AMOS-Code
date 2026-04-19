#!/usr/bin/env python3
"""Automated fix for common syntax errors."""

import ast
from pathlib import Path


def fix_file(filepath):
    """Fix common syntax errors in a Python file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        original = content

        # Pattern 1: Fix imports at column 0 inside try/except/if blocks
        lines = content.split("\n")
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Check if this line starts a block
            if stripped.endswith(":") and not stripped.startswith("#"):
                new_lines.append(line)
                i += 1

                # Get expected indentation for block content
                base_indent = len(line) - len(line.lstrip())
                expected_indent = base_indent + 4

                # Process lines inside the block
                while i < len(lines):
                    current_line = lines[i]
                    current_stripped = current_line.strip()

                    if not current_stripped:
                        new_lines.append(current_line)
                        i += 1
                        continue

                    current_indent = len(current_line) - len(current_line.lstrip())

                    # Check if we exited the block
                    if current_indent <= base_indent and not current_stripped.startswith("#"):
                        break

                    # Fix misindented imports
                    if (
                        current_stripped.startswith(("from ", "import "))
                        and current_indent < expected_indent
                    ):
                        fixed_line = " " * expected_indent + current_stripped
                        new_lines.append(fixed_line)
                        i += 1
                        continue

                    new_lines.append(current_line)
                    i += 1
                continue

            new_lines.append(line)
            i += 1

        content = "\n".join(new_lines)

        if content != original:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False
    except Exception:
        return False


def main():
    py_files = list(Path(".").rglob("*.py"))
    py_files = [
        f
        for f in py_files
        if ".venv" not in str(f)
        and "venv" not in str(f)
        and "__pycache__" not in str(f)
        and ".git" not in str(f)
        and "node_modules" not in str(f)
    ]

    fixed = 0
    for filepath in py_files:
        if fix_file(filepath):
            fixed += 1

    print(f"Fixed {fixed} files")

    # Count remaining errors
    errors = 0
    for pyfile in py_files:
        try:
            with open(pyfile, encoding="utf-8") as f:
                ast.parse(f.read())
        except SyntaxError:
            errors += 1

    print(f"Remaining syntax errors: {errors}")


if __name__ == "__main__":
    main()
