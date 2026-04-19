#!/usr/bin/env python3
"""Fix syntax errors in backend/api directory."""

import ast
from pathlib import Path


def fix_file(filepath: Path) -> bool:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    original = content

    # Fix pattern: typing import inside import parentheses
    lines = content.split("\n")
    fixed_lines = []
    in_import_paren = False
    typing_imports_to_add = []

    for line in lines:
        stripped = line.strip()

        # Check if we enter an import with parentheses
        if "from " in stripped and "import (" in stripped:
            in_import_paren = True

        # Check if we exit the import block
        if in_import_paren and stripped == ")":
            in_import_paren = False

        # If this is a typing import inside parentheses, capture and skip
        if in_import_paren and ("from typing import" in stripped or "import typing" in stripped):
            typing_imports_to_add.append(stripped)
            continue

        fixed_lines.append(line)

    content = "\n".join(fixed_lines)

    # Add collected typing imports at top if any
    if typing_imports_to_add:
        # Find the first non-comment/non-docstring line
        lines = content.split("\n")
        insert_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (
                stripped
                and not stripped.startswith("#")
                and not stripped.startswith('"""')
                and not stripped.startswith("'''")
            ):
                if stripped.startswith("from ") or stripped.startswith("import "):
                    insert_idx = i
                    break
            elif stripped.startswith('"""') or stripped.startswith("'''"):
                # Find end of docstring
                for j in range(i + 1, len(lines)):
                    if '"""' in lines[j] or "'''" in lines[j]:
                        insert_idx = j + 1
                        break

        for imp in typing_imports_to_add:
            lines.insert(insert_idx, imp)
            insert_idx += 1

        content = "\n".join(lines)

    if content == original:
        return False

    # Verify syntax
    try:
        ast.parse(content)
    except SyntaxError:
        return False

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def main():
    api_dir = Path("backend/api")
    if not api_dir.exists():
        print("backend/api directory not found")
        return

    fixed = 0
    failed = 0

    for py_file in api_dir.glob("*.py"):
        try:
            with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                ast.parse(f.read())
        except SyntaxError:
            if fix_file(py_file):
                print(f"✅ Fixed: {py_file.name}")
                fixed += 1
            else:
                print(f"❌ Could not fix: {py_file.name}")
                failed += 1

    print(f"\n📈 Fixed: {fixed}, Failed: {failed}")


if __name__ == "__main__":
    main()
