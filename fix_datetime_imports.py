#!/usr/bin/env python3
"""Fix datetime.timezone.utc imports for Python 3.9 compatibility."""

import re
import sys
from pathlib import Path


def fix_file(filepath):
    """Fix datetime imports in a single file."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
        original = content

        # Replace timezone.utc with timezone.utc
        content = re.sub(r"\bUTC\b", "timezone.utc", content)

        if content != original:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False


def main():
    base_path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

    # Find all Python files with the issue
    import subprocess

    result = subprocess.run(
        ["grep", "-rl", "from datetime import", "--include=*.py", "."],
        cwd=base_path,
        capture_output=True,
        text=True,
    )

    files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
    # Filter out __pycache__ and .venv
    files = [f for f in files if "__pycache__" not in f and ".venv" not in f]

    fixed = 0
    for rel_path in files:
        filepath = base_path / rel_path.lstrip("./")
        if fix_file(filepath):
            print(f"Fixed: {rel_path}")
            fixed += 1

    print(f"\nFixed {fixed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
