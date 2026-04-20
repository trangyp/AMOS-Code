#!/usr/bin/env python3
"""AMOS Brain - F821 Undefined Name Auto-Fix System V2

Uses cognitive analysis to identify and fix missing typing imports
across the entire AMOS codebase efficiently.
"""

import re
import sys
from pathlib import Path
from typing import Any

# Common undefined names and their fixes
TYPING_IMPORTS = {
    "Optional": "from typing import Optional",
    "Dict": "from typing import Dict",
    "List": "from typing import List",
    "Set": "from typing import Set",
    "Tuple": "from typing import Tuple",
    "Union": "from typing import Union",
    "Callable": "from typing import Callable",
    "Any": "from typing import Any",
    "TypeVar": "from typing import TypeVar",
    "Generic": "from typing import Generic",
    "Protocol": "from typing import Protocol",
    "runtime_checkable": "from typing import runtime_checkable",
    "Final": "from typing import Final",
    "ClassVar": "from typing import ClassVar",
    "Annotated": "from typing import Annotated",
    "Literal": "from typing import Literal",
    "TypedDict": "from typing import TypedDict",
    "NamedTuple": "from typing import NamedTuple",
}

DATETIME_FIXES = {
    "timedelta": "from datetime import timedelta",
}

NUMPY_FIXES = {
    "ndarray": "import numpy as np  # noqa: F401",
}

THREADING_FIXES = {
    "Thread": "from threading import Thread",
    "Lock": "from threading import Lock",
}


def find_insertion_point(content: str) -> int:
    """Find the best place to insert new imports."""
    lines = content.split("\n")
    last_import = 0
    in_docstring = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if stripped.count('"""') == 1 or stripped.count("'''") == 1:
                in_docstring = not in_docstring
            continue
        if in_docstring:
            continue
        if stripped.startswith(("import ", "from ")):
            last_import = i + 1
    return last_import


def fix_file(filepath: Path) -> dict[str, Any]:
    """Fix a single file's F821 errors."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": str(e)}

    original = content
    changes = []
    needs_typing = set()

    # Check for undefined typing names
    for name in TYPING_IMPORTS:
        pattern = rf"\b{name}\b"
        if re.search(pattern, content) and f"from typing import {name}" not in content:
            needs_typing.add(name)

    # Add missing typing imports
    if needs_typing:
        insert_line = find_insertion_point(content)
        lines = content.split("\n")
        import_names = sorted(needs_typing)
        import_stmt = f"from typing import {', '.join(import_names)}"
        lines.insert(insert_line, import_stmt)
        content = "\n".join(lines)
        changes.append(f"added typing imports: {', '.join(import_names)}")

    # Write if changed
    if content != original:
        filepath.write_text(content, encoding="utf-8")
        return {"fixed": True, "changes": changes}

    return {"fixed": False}


def main() -> int:
    """Main entry point."""
    repo_path = Path("/Users/nguyenxuanlinh/Documents/Trang Phan/Downloads/AMOS-code")
    python_files = [
        f for f in repo_path.rglob("*.py") if ".venv" not in str(f) and "__pycache__" not in str(f)
    ]

    print("Brain F821 Fix System V2")
    print("========================")
    print(f"Scanning {len(python_files)} Python files...\n")

    fixed_count = 0
    error_count = 0

    for i, filepath in enumerate(python_files, 1):
        if i % 100 == 0:
            print(f"  Processed {i}/{len(python_files)} files...")

        result = fix_file(filepath)

        if result.get("fixed"):
            fixed_count += 1
            print(f"  Fixed: {filepath.name} - {result['changes']}")
        elif "error" in result:
            error_count += 1

    print(f"\n{'=' * 50}")
    print("Fix Complete!")
    print(f"  Files fixed: {fixed_count}")
    print(f"  Errors: {error_count}")
    print(f"{'=' * 50}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
