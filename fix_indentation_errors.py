#!/usr/bin/env python3
"""Fix indentation errors caused by datetime fix script."""

import ast
import re
from pathlib import Path


def fix_file(filepath):
    """Fix indentation errors in a Python file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        original = content

        # Pattern 1: Fix imports at wrong indentation after try:/if __name__ == "__main__":
        # Look for import statements that are at column 0 but should be indented
        lines = content.split("\n")
        new_lines = []
        in_block = False
        block_indent = None
        prev_line = None

        for i, line in enumerate(lines):
            stripped = line.strip()
            current_indent = len(line) - len(line.lstrip())

            # Check if previous line starts a block that needs indentation
            if prev_line and prev_line.rstrip().endswith(":"):
                if (
                    prev_line.strip().startswith(
                        (
                            "try:",
                            "if ",
                            "def ",
                            "class ",
                            "for ",
                            "while ",
                            "with ",
                            "elif ",
                            "else:",
                        )
                    )
                    or prev_line.strip() == "except:"
                    or prev_line.strip().startswith("except ")
                    or prev_line.strip().startswith("finally:")
                ):
                    in_block = True
                    block_indent = len(prev_line) - len(prev_line.lstrip())

            # Check if we exited the block
            if in_block and block_indent is not None:
                if stripped and current_indent <= block_indent and not stripped.startswith("#"):
                    # We exited the block
                    in_block = False
                    block_indent = None

            # Fix misindented imports
            if in_block and block_indent is not None:
                if stripped.startswith(("from ", "import ")) and current_indent <= block_indent:
                    # This import should be indented
                    fixed_line = "    " + stripped
                    new_lines.append(fixed_line)
                    prev_line = fixed_line
                    continue

            new_lines.append(line)
            prev_line = line

        content = "\n".join(new_lines)

        # Pattern 2: Remove duplicate consecutive imports
        content = re.sub(r"(from\s+\S+\s+import\s+[^\n]+)\n\1", r"\1", content)
        content = re.sub(r"(import\s+[^\n]+)\n\1", r"\1", content)

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
