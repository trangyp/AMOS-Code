#!/usr/bin/env python3
"""Fix missing typing imports in amos_brain module."""

import ast
from pathlib import Path

# Files known to have missing imports
FILES_TO_FIX = [
    "amos_brain/loader.py",
    "amos_brain/agent_bridge.py",
    "amos_brain/facade.py",
]


# Read the file and check for typing imports
def fix_file(filepath: Path) -> bool:
    """Add missing typing imports to a file."""
    with open(filepath) as f:
        content = f.read()

    # Check if already has Optional import
    if "from typing import" in content and "Optional" in content:
        return False  # Already fixed

    # Find the import line and replace it
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("from typing import") or line.startswith("from pathlib import"):
            # Found an import line, check if we need to add more
            if "Optional" not in line and "from typing" in line:
                # Add Optional to existing typing import
                if line.endswith(")"):
                    lines[i] = line[:-1] + ", Optional)"
                else:
                    lines[i] = line + ", Optional"
                break
            elif "from pathlib" in line and "Optional" not in content:
                # Add a new typing import line after this
                lines.insert(i, "from typing import Optional")
                break
        elif line.startswith("import ") and "typing" not in content:
            # Add typing import before first import
            lines.insert(i, "from typing import Optional")
            break

    new_content = "\n".join(lines)

    # Verify syntax
    try:
        ast.parse(new_content)
    except SyntaxError as e:
        print(f"  Syntax error after fix: {e}")
        return False

    with open(filepath, "w") as f:
        f.write(new_content)

    return True


def main():
    repo_root = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")

    fixed = 0
    for filename in FILES_TO_FIX:
        filepath = repo_root / filename
        if filepath.exists():
            print(f"Checking {filename}...")
            if fix_file(filepath):
                print("  ✓ Fixed")
                fixed += 1
            else:
                print("  - No changes needed")
        else:
            print(f"  ✗ File not found: {filename}")

    print(f"\nFixed {fixed} files")


if __name__ == "__main__":
    main()
