#!/usr/bin/env python3
"""AMOS Brain-driven syntax error fixer - removes misplaced typing imports."""

import ast
from datetime import datetime
from pathlib import Path


def fix_syntax_errors():
    """Find and fix all syntax errors in Python files."""
    repo_root = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

    # Directories to skip
    skip_dirs = {
        ".venv",
        "__pycache__",
        ".git",
        ".ruff_cache",
        ".pytest_cache",
        ".hypothesis",
        ".mypy_cache",
        "node_modules",
        ".git",
    }

    fixed_count = 0
    failed_count = 0
    total_errors = 0

    print(f"🧠 AMOS BRAIN SYNTAX FIXER - {datetime.now().isoformat()}")
    print("=" * 60)

    for pyfile in repo_root.rglob("*.py"):
        # Skip unwanted directories
        if any(skip in str(pyfile) for skip in skip_dirs):
            continue

        try:
            with open(pyfile, encoding="utf-8", errors="ignore") as f:
                original_content = f.read()

            # Try to parse
            try:
                ast.parse(original_content)
                continue  # No syntax error, skip
            except SyntaxError:
                total_errors += 1

            # Fix 1: Remove indented typing imports
            lines = original_content.split("\n")
            fixed_lines = []
            modified = False

            for i, line in enumerate(lines):
                stripped = line.lstrip()
                indent = len(line) - len(stripped)

                # Check for misplaced typing imports (indented)
                if indent > 0 and (
                    stripped.startswith("from typing import")
                    or stripped.startswith("import typing")
                ):
                    modified = True
                    continue  # Skip this line

                fixed_lines.append(line)

            if modified:
                fixed_content = "\n".join(fixed_lines)

                # Verify fix
                try:
                    ast.parse(fixed_content)

                    # Write back
                    with open(pyfile, "w", encoding="utf-8") as f:
                        f.write(fixed_content)

                    fixed_count += 1
                    print(f"✓ FIXED: {pyfile.relative_to(repo_root)}")

                except SyntaxError as e:
                    failed_count += 1
                    print(f"✗ STILL BROKEN: {pyfile.relative_to(repo_root)}:{e.lineno}")

        except Exception as e:
            print(f"✗ ERROR processing {pyfile}: {e}")
            failed_count += 1

    print("=" * 60)
    print(f"🎉 FIXED: {fixed_count} files")
    print(f"⚠️  STILL BROKEN: {failed_count} files")
    print(f"📊 TOTAL SYNTAX ERRORS FOUND: {total_errors}")

    return fixed_count, failed_count


if __name__ == "__main__":
    fix_syntax_errors()
