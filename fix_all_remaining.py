#!/usr/bin/env python3
"""Fix all remaining Python 3.9 compatibility issues."""

import re
from pathlib import Path


def fix_file(filepath):
    """Fix common issues in a Python file."""
    content = filepath.read_text()
    original = content

    # Fix 1: Remove duplicate typing imports inside try blocks
    content = re.sub(
        r"try:\s*\n\s*from typing import[^\n]+\nfrom typing import[^\n]+\n\s*",
        "try:\n    ",
        content,
    )

    # Fix 2: Remove orphaned typing imports after try blocks
    content = re.sub(
        r"try:\s*\n\s*from [^\n]+\nfrom typing import[^\n]+\n\s+",
        lambda m: m.group(0).split("from typing")[0] + "    ",
        content,
    )

    # Fix 3: Remove duplicate consecutive imports
    content = re.sub(r"(from typing import[^\n]+)\nfrom typing import[^\n]+\n", r"\1\n", content)

    if content != original:
        filepath.write_text(content)
        print(f"✓ Fixed {filepath.name}")
        return True
    return False


def main():
    """Fix all Python files in the current directory."""
    fixed = 0
    for pyfile in Path(".").glob("*.py"):
        if pyfile.name in ("fix_all_issues.py", "fix_all_remaining.py"):
            continue
        if fix_file(pyfile):
            fixed += 1

    print(f"\nFixed {fixed} files")


if __name__ == "__main__":
    main()
