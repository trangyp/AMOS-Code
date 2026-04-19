#!/usr/bin/env python3
"""Fix common syntax errors in AMOS-CODE Python files."""

import ast
import re
from pathlib import Path


def fix_file(filepath):
    """Fix common syntax errors in a Python file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        original = content

        # Pattern 1: Fix missing closing parenthesis for append calls
        # issues.append(\n    CodeIssue(...\n    )\n        return issues
        content = re.sub(
            r"(\w+\.append\(\s*\n\s*\w+\([^)]+\)\s*\n\s*\))(\s*\n\s+(?:return|if|for|while|def|class))",
            r"\1\2",
            content,
        )

        # Pattern 2: Fix missing closing parenthesis for complex boolean expressions
        content = re.sub(
            r"(\w+\s*=\s*\(\s*\n[^)]+\n\s*\))\s*\n\s*(\n# |\w+ = |if |elif |else:)",
            r"\1\n\2",
            content,
        )

        # Pattern 3: Fix indentation issues - move misindented imports inside functions
        lines = content.split("\n")
        new_lines = []
        in_function = False
        function_indent = None

        for i, line in enumerate(lines):
            stripped = line.strip()
            current_indent = len(line) - len(line.lstrip())

            # Detect function/class start
            if stripped.startswith("def ") or stripped.startswith("class "):
                if ":" in stripped and not stripped.endswith(":"):
                    pass
                elif stripped.endswith(":"):
                    in_function = True
                    function_indent = current_indent

            # Check for misindented imports
            if in_function and function_indent is not None:
                if stripped.startswith("from ") or stripped.startswith("import "):
                    if current_indent <= function_indent:
                        # Misindented import - should be indented more
                        new_lines.append("    " + stripped)
                        continue

            new_lines.append(line)

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
            print(f"Fixed: {filepath}")

    print(f"\nTotal fixed: {fixed}")

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
