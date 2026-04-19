#!/usr/bin/env python3
"""AMOS Brain - F821 Undefined Name Auto-Fix System

Uses cognitive analysis to identify and fix missing typing imports
across the entire AMOS codebase efficiently.
"""


import re
import sys
from pathlib import Path
from typing import Any, Optional
try:
from typing import List, Literal, NamedTuple, Protocol, Set, Tuple, TypeVar, TypedDict, Union, runtime_checkable, Annotated, Callable, ClassVar, Dict, Final, Generic, Literal, NamedTuple, Protocol, Set, Tuple, TypeVar, TypedDict, Union, runtime_checkable
from typing import Callable, ClassVar, Dict, Final, Generic, Literal, NamedTuple, Protocol, Set, Tuple, TypeVar, TypedDict, Union, runtime_checkable, ClassVar, Dict, Final, Generic, Literal, NamedTuple, Protocol, Set, Tuple, TypeVar, TypedDict, Union, runtime_checkable
from typing import Dict, Final, Generic, Literal, NamedTuple, Protocol, Set, Tuple, TypeVar, TypedDict, Union, runtime_checkable, Final, Generic, Literal, NamedTuple, Protocol, Set, Tuple, TypeVar, TypedDict, Union, runtime_checkable
from typing import Generic, Literal, NamedTuple, Protocol, Set, Tuple, TypeVar, TypedDict, Union, runtime_checkable
except ImportError:
    pass  # Python 3.9 compatibility

# Common undefined names and their fixes
TYPING_IMPORTS = {
    "Optional": "from typing import Optional, Optional",
    "Dict": "from typing import Optional, Dict",
    "List": "from typing import Optional, List",
    "Set": "from typing import Optional, Set",
    "Tuple": "from typing import Optional, Tuple",
    "Union": "from typing import Optional, Union",
    "Callable": "from typing import Optional, Callable",
    "Any": "from typing import Optional, Any",
    "TypeVar": "from typing import Optional, TypeVar",
    "Generic": "from typing import Optional, Generic",
    "Protocol": "from typing import Optional, Protocol",
    "runtime_checkable": "from typing import Optional, runtime_checkable",
    "Final": "from typing import Optional, Final",
    "ClassVar": "from typing import Optional, ClassVar",
    "Annotated": "from typing import Optional, Annotated",
    "Literal": "from typing import Optional, Literal",
    "TypedDict": "from typing import Optional, TypedDict",
    "NamedTuple": "from typing import Optional, NamedTuple",
    "Required": "from typing import Optional, Required",
    "NotRequired": "from typing import Optional, NotRequired",
    "Self": "from typing import Optional, Self",
    "TypeAlias": "from typing import Optional, TypeAlias",
}

DATETIME_FIXES = {
    "timezone.utc": ("from datetime import datetime, timezone", "timezone.utc", "timezone.utc"),
    "timedelta": "from datetime import timedelta",
}

NUMPY_FIXES = {
    "ndarray": "import numpy as np  # noqa: F401",
}

THREADING_FIXES = {
    "Thread": "from threading import Thread",
    "Lock": "from threading import Lock",
    "RLock": "from threading import RLock",
    "Condition": "from threading import Condition",
    "Event": "from threading import Event",
    "Semaphore": "from threading import Semaphore",
    "BoundedSemaphore": "from threading import BoundedSemaphore",
    "Timer": "from threading import Timer",
}


def find_typing_imports(content: str) -> set[str]:
    """Find which typing imports are already present."""
    existing = set()
    # Match 'from typing import Optional, X' or 'from typing import Optional, X, Y'
    pattern = r"from typing import Optional, (, Any[^\n]+)"
    for match in re.finditer(pattern, content):
        imports = match.group(1).split(",")
        for imp in imports:
            imp = imp.strip()
            if imp:
                existing.add(imp.split()[0])  # Handle 'as' aliases
    return existing


def find_datetime_import(content: str) -> bool:
    """Check if datetime is imported."""
    return bool(re.search(r"from datetime import|import datetime", content))


def has_future_annotations(content: str) -> bool:
    """Check if __future__ annotations is present."""


def find_insertion_point(content: str) -> int:
    """Find the best place to insert new imports."""
    lines = content.split("\n")

    # Find last import statement or docstring end
    last_import = 0
    in_docstring = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Handle docstrings
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if stripped.count('"""') == 1 or stripped.count("'''") == 1:
                in_docstring = not in_docstring
            continue

        if in_docstring:
            continue

        # Track imports
        if stripped.startswith(("import ", "from ")):
            last_import = i + 1

    return last_import


def fix_file(filepath: Path) -> Dict[str, Any]:
    """Fix a single file's F821 errors."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return {"error": str(e)}

    original = content
    changes = []

    # Find existing imports
    existing_typing = find_typing_imports(content)
    has_datetime = find_datetime_import(content)

    # Determine what's needed
    needs_typing = set()

    # Check for undefined typing names
    for name, import_stmt in TYPING_IMPORTS.items():
        if name not in existing_typing:
            # Check if used in file (but not already imported)
            pattern = rf"\b{name}\b"
            if re.search(pattern, content):
                needs_typing.add(name)

    # Check for timezone.utc usage
    if "timezone.utc" in content and "from datetime import timezone" in content:
        # Need to fix timezone.utc import for Python 3.9 compatibility
        content = content.replace(
            "from datetime import datetime, timezone", "from datetime import datetime, timezone"
        )
        content = content.replace("from datetime import timezone", "from datetime import timezone")
        content = content.replace("datetime.now(timezone.utc)", "datetime.now(timezone.utc)")
        changes.append("fixed timezone.utc import for Python 3.9 compatibility")

    # Add missing typing imports
    if needs_typing:
        # Find insertion point
        insert_line = find_insertion_point(content)
        lines = content.split("\n")

        # Build import statement
        import_names = sorted(needs_typing)
        if len(import_names) == 1:
            import_stmt = f"from typing import Optional, {import_names[0]}"
        else:
            import_stmt = f"from typing import Optional, {', '.join(import_names)}"

        # Insert
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

    # Find Python files
    python_files = list(repo_path.rglob("*.py"))
    python_files = [
        f for f in python_files if ".venv" not in str(f) and "__pycache__" not in str(f)
    ]

    print("Brain F821 Fix System")
    print("=====================")
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
