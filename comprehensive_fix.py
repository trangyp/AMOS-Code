#!/usr/bin/env python3
"""Comprehensive fix for syntax errors in AMOS-CODE."""

import ast
from pathlib import Path


def fix_misplaced_imports(content):
    """Fix imports that are at wrong indentation level inside try/except blocks."""
    lines = content.split("\n")
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check if this is a try block
        if stripped == "try:":
            try_indent = len(line) - len(line.lstrip())
            new_lines.append(line)
            i += 1

            # Process lines inside try block
            while i < len(lines):
                current_line = lines[i]
                current_stripped = current_line.strip()
                current_indent = len(current_line) - len(current_line.lstrip())

                # Check for except/finally to exit try block
                if current_stripped.startswith("except") or current_stripped.startswith("finally"):
                    break

                # Check for misindented imports at same level as try
                if (
                    current_stripped.startswith(("from ", "import "))
                    and current_indent <= try_indent
                ):
                    # Fix indentation
                    fixed_line = "    " + current_stripped
                    new_lines.append(fixed_line)
                    i += 1
                    continue

                new_lines.append(current_line)
                i += 1
            continue

        new_lines.append(line)
        i += 1

    return "\n".join(new_lines)


def fix_duplicate_imports(content):
    """Remove duplicate import lines."""
    lines = content.split("\n")
    seen_imports = set()
    new_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("from ", "import ")):
            if stripped in seen_imports:
                continue
            seen_imports.add(stripped)
        new_lines.append(line)

    return "\n".join(new_lines)


def fix_missing_closing_parens(content):
    """Fix common missing closing parentheses patterns."""
    # Pattern: append( followed by CodeIssue or similar without closing )
    # This is tricky to fix with regex, will handle case by case
    return content


def fix_file(filepath):
    """Fix all syntax errors in a file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        original = content

        # Apply fixes
        content = fix_misplaced_imports(content)
        content = fix_duplicate_imports(content)
        content = fix_missing_closing_parens(content)

        if content != original:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
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

    print(f"\nTotal files modified: {fixed}")

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
