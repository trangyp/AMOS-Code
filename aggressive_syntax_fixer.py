#!/usr/bin/env python3
"""Aggressive syntax error fixer for AMOS codebase."""

import ast
import re
from pathlib import Path


def fix_file(filepath: Path) -> bool:
    """Fix a single file. Returns True if fixed."""
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return False

    original = content

    # Pattern 1: typing import inside parentheses
    content = re.sub(
        r"(from\s+\w+\s+import\s*\([^)]*?)\n\s*from typing import[^\n]+\n", r"\1\n", content
    )

    # Pattern 2: typing import at start of indented block
    content = re.sub(
        r"^(\s+)(from typing import[^\n]+)$",
        lambda m: m.group(2) + "\n",
        content,
        flags=re.MULTILINE,
    )

    # Pattern 3: typing import inside try block
    content = re.sub(
        r"(try:[^\n]*?)\n\s*from typing import[^\n]+\n", r"from typing import\2\n\1\n", content
    )

    if content == original:
        return False

    # Verify syntax
    try:
        ast.parse(content)
    except SyntaxError:
        return False

    # Write back
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def main():
    repo_root = Path(".")
    skip_dirs = {
        ".venv",
        "node_modules",
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".ruff_cache",
        ".hypothesis",
        ".benchmarks",
        "profiling_results",
        "amos_logs",
    }

    fixed = 0
    failed = 0

    for py_file in repo_root.rglob("*.py"):
        if any(skip in py_file.parts for skip in skip_dirs):
            continue

        try:
            with open(py_file, encoding="utf-8", errors="ignore") as f:
                ast.parse(f.read())
        except SyntaxError:
            if fix_file(py_file):
                print(f"✅ Fixed: {py_file}")
                fixed += 1
            else:
                failed += 1

    print(f"\n📈 Fixed: {fixed}, Failed: {failed}")


if __name__ == "__main__":
    main()
