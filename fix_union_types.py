#!/usr/bin/env python3
"""Fix all Python 3.10+ union type syntax to Python 3.9 compatible Optional syntax."""

import re
from pathlib import Path


def fix_file(filepath):
    """Fix union type syntax in a Python file."""
    content = filepath.read_text()
    original = content

    # Pattern 1: Optional[Type] -> Optional[Type]
    # Handle various patterns
    patterns = [
        (r":\s*(\w+)\s*\|\s*None", r": Optional[\1]"),
        (r":\s*([\w\[\]]+)\s*\|\s*None", r": Optional[\1]"),
        (r"->\s*(\w+)\s*\|\s*None", r"-> Optional[\1]"),
        (r"->\s*([\w\[\]]+)\s*\|\s*None", r"-> Optional[\1]"),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    # Add Optional import if needed and not already present
    if "Optional" in content and "from typing import Optional," in content:
        if "Optional" not in content.split("from typing import Optional,")[1].split("\n")[0]:
            content = content.replace(
                "from typing import Optional,", "from typing import Optional, Optional,"
            )
    elif "Optional" in content and "from typing import Optional," not in content:
        # Add typing import at top
        lines = content.split("\n")
        import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                import_idx = i + 1
        lines.insert(import_idx, "from typing import Optional, Optional")
        content = "\n".join(lines)

    if content != original:
        filepath.write_text(content)
        print(f"✓ Fixed {filepath}")
        return True
    return False


def main():
    """Fix all Python files recursively."""
    fixed = 0
    for pyfile in Path(".").rglob("*.py"):
        if ".venv" in str(pyfile) or "node_modules" in str(pyfile):
            continue
        if pyfile.name.startswith("fix_"):
            continue
        if fix_file(pyfile):
            fixed += 1

    print(f"\nFixed {fixed} files")


if __name__ == "__main__":
    main()
