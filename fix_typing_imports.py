#!/usr/bin/env python3
"""Auto-fix typing imports in AMOS codebase.

This script scans Python files and adds missing Dict, List, Optional imports
from typing module where needed.
"""

import re
from pathlib import Path


def fix_file(filepath: Path) -> bool:
    """Fix typing imports in a single file. Returns True if changed."""
    content = filepath.read_text()
    original = content

    # Check if file uses Dict, List, Optional but doesn't import them
    uses_dict = re.search(r"Dict\[", content) is not None
    uses_list = re.search(r"List\[", content) is not None
    uses_optional = re.search(r"Optional\[", content) is not None

    if not (uses_dict or uses_list or uses_optional):
        return False

    # Check current imports
    import_match = re.search(r"from typing import ([^\n]+)", content)
    if not import_match:
        return False

    current_imports = import_match.group(1).split(",")
    current_imports = [i.strip() for i in current_imports]

    needs = []
    if uses_dict and "Dict" not in current_imports:
        needs.append("Dict")
    if uses_list and "List" not in current_imports:
        needs.append("List")
    if uses_optional and "Optional" not in current_imports:
        needs.append("Optional")

    if not needs:
        return False

    # Add missing imports
    new_imports = current_imports + needs
    new_imports.sort()  # Keep consistent ordering

    new_import_line = f"from typing import {', '.join(new_imports)}"

    content = re.sub(r"from typing import [^\n]+", new_import_line, content)

    filepath.write_text(content)
    print(f"Fixed {filepath}: added {needs}")
    return True


def main():
    """Main entry point."""
    changed = 0
    for path in Path("AMOS_ORGANISM_OS").rglob("*.py"):
        if fix_file(path):
            changed += 1
    
    # Also fix repo_doctor
    for path in Path("repo_doctor").rglob("*.py"):
        if fix_file(path):
            changed += 1

    print(f"\nFixed {changed} files")


if __name__ == "__main__":
    main()
